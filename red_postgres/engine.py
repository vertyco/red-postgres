import asyncio
import logging
import os
import subprocess
from pathlib import Path

from piccolo.engine.postgres import PostgresEngine
from piccolo.table import Table, sort_table_classes

from .errors import ConnectionTimeoutError, DirectoryError, UNCPathError

log = logging.getLogger("red.red-postgres.engine")


async def create_database(cog: Path, config: dict) -> bool:
    """
    Create cog's database if it doesnt exist.

    Args:
        cog (Path): Cog folder path
        config (dict): Postgres connection information

    Returns:
        bool: whether a new database was created
    """
    _check(cog)
    log.debug("Acquiring engine for db creation")
    engine = await _acquire_db_engine(config)
    log.debug("Starting connection pool")
    await engine.start_connection_pool()

    # Check if the database exists
    created = False
    database_name = cog.name.lower()
    databases = await engine._run_in_pool("SELECT datname FROM pg_database;")
    if database_name not in [db["datname"] for db in databases]:
        # Create the database
        log.info(f"New cog detected, Creating database for {database_name}")
        await engine._run_in_pool(f"CREATE DATABASE {database_name};")
        created = True

    # Close old database connection
    await engine.close_connection_pool()
    return created


async def fetch_cog_engine(cog: Path, config: dict, tables: list[type[Table]], max_size: int = 20) -> PostgresEngine:
    """
    Connect to postgres, start pool, and return engine.

    Args:
        cog (Path): Cog folder path
        config (dict): database connection info
        tables (list[type[Table]]): list of piccolo table subclasses
        max_size (int): maximum number of database connections, 20 by default

    Returns:
        PostgresEngine instance
    """
    _check(cog)
    temp_config = config.copy()
    temp_config["database"] = cog.name.lower()
    log.debug("Fetching engine")
    engine = await _acquire_db_engine(temp_config)
    log.debug("Starting connection pool")
    await engine.start_connection_pool(max_size=max_size)
    log.debug("Assigning engines to tables")
    # Update table engines
    for table_class in tables:
        table_class._meta.db = engine
    return engine


async def create_tables(cog: Path, config: dict, tables: list[type[Table]], max_size: int = 20) -> PostgresEngine:
    """
    Connect to postgres, create database/tables, start pool, and return engine.

    Args:
        cog (Path): Cog folder path
        config (dict): database connection info
        tables (list[type[Table]]): list of piccolo table subclasses
        max_size (int): maximum number of database connections, 20 by default

    Returns:
        PostgresEngine instance
    """
    _check(cog)
    engine = await fetch_cog_engine(cog, config, tables, max_size)

    log.debug("Creating tables if they don't exist")
    try:
        async with asyncio.timeout(15):
            log.debug("Sorting table classes")
            sorted_tables = await asyncio.to_thread(sort_table_classes, tables)
            for table in sorted_tables:
                log.debug(f"Creating table {table._meta.tablename}")
                await table.create_table(if_not_exists=True)
    except asyncio.TimeoutError:
        log.info("Table creation took too long")
    except Exception as e:
        log.info("Failed to run create tables", exc_info=e)

    return engine


async def run_migrations(cog: Path, config: dict, trace: bool = False) -> str:
    """
    Run any existing migrations programatically.

    There might be a better way to do this that subprocess, but haven't tested yet.

    Args:
        cog (Path): Cog folder path
        config (dict): database connection info
        trace (bool, optional): include --trace in the command for debugging

    Returns:
        str: _description_
    """
    _check(cog)
    if _is_unc_path(str(cog)):
        error = f"Migrations cannot run for the {cog.name} cog because it is located on a UNC path!"
        raise UNCPathError(error)

    def run():
        temp_config = config.copy()
        temp_config["database"] = cog.name.lower()
        commands = ["piccolo", "migrations", "forward", cog.name.lower()]
        if trace:
            commands.append("--trace")
        return subprocess.run(
            commands,
            env=_get_env(temp_config),
            cwd=str(cog),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ).stdout.decode()

    return await asyncio.to_thread(run)


async def diagnose(cog: Path, config: dict) -> str:
    """
    Diagnose any issues with Piccolo

    Args:
        cog (Path): Cog folder path
        config (dict): database connection info
    """
    _check(cog)

    def run():
        temp_config = config.copy()
        temp_config["database"] = cog.name.lower()
        return subprocess.run(
            ["piccolo", "--diagnose"],
            env=_get_env(temp_config),
            cwd=str(cog),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ).stdout.decode()

    return await asyncio.to_thread(run)


async def register_cog(
    cog: Path,
    config: dict,
    tables: list[type[Table]],
    max_size: int = 20,
    trace: bool = False,
) -> PostgresEngine:
    """Registers a cog by creating a database for it and initializing any tables it has

    Args:
        cog (Path): Cog folder path
        config (dict): database connection info
        tables (list[type[Table]]): list of piccolo table subclasses
        max_size (int): maximum number of database connections, 20 by default
        trace (bool, optional): include --trace in the command for debugging

    Returns:
        PostgresEngine
    """
    log.info(f"Registering {cog.name}")
    _check(cog)
    # Create databse under root folder name
    created = await create_database(cog, config)

    if _is_unc_path(str(cog)):
        txt = (
            f"The {cog.name} cog is located on a UNC path, which is not supported."
            " Migrations cannot until the cog files are relocated to a local path."
        )
        log.warning(txt)
    else:
        log.debug("Running migrations, if any")
        result = await run_migrations(cog, config, trace)
        result = result.replace("👍", "✓")
        log.info(f"Migration result...\n{result}")

    if created:
        # Create any tables and fetch postgres engine in case there was no initial migration
        engine = await create_tables(cog, config, tables, max_size)
    else:
        # Just fetch the engine
        engine = await fetch_cog_engine(cog, config, tables, max_size)

    return engine


async def _acquire_db_engine(config: dict) -> PostgresEngine:
    """This is ran in executor since it blocks if connection info is bad"""

    def _acquire(config: dict) -> PostgresEngine:
        return PostgresEngine(config=config)

    try:
        async with asyncio.timeout(10):
            engine = await asyncio.to_thread(_acquire, config)
            return engine
    except asyncio.TimeoutError:
        raise ConnectionTimeoutError("Database took longer than 10 seconds to connect!")


def _get_env(config: dict) -> dict:
    """Create mock environment for subprocess"""
    env = os.environ.copy()
    env["PICCOLO_CONF"] = "db.piccolo_conf"
    env["POSTGRES_HOST"] = config.get("host")
    env["POSTGRES_PORT"] = config.get("port")
    env["POSTGRES_USER"] = config.get("user")
    env["POSTGRES_PASSWORD"] = config.get("password")
    env["POSTGRES_DATABASE"] = config.get("database")
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def _check(cog: Path) -> Path:
    """Verify that the cog path passed is a directory and not a file"""
    if not cog.is_dir():
        raise DirectoryError("Cog path is not a directory!")


def _is_unc_path(path: Path) -> bool:
    return path.is_absolute() and str(path).startswith(r"\\\\")
