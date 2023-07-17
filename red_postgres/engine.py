import asyncio
import inspect
import logging
import os
import subprocess
from pathlib import Path

from discord.ext.commands import Cog
from piccolo.engine.postgres import PostgresEngine
from piccolo.table import Table, create_db_tables

log = logging.getLogger("red.red-postgres.engine")


async def create_database(cog: Cog, config: dict) -> bool:
    """Create cog's database if it doesnt exist

    Args:
        cog (Cog): Cog instance
        config (dict): Postgres connection information

    Returns:
        bool: whether a new database was created
    """
    engine = await asyncio.to_thread(_acquire_db_engine, config)
    await engine.start_connection_pool()

    # Check if the database exists
    created = False
    database_name = _root(cog).name.lower()
    databases = await engine._run_in_pool("SELECT datname FROM pg_database;")
    if database_name not in [db["datname"] for db in databases]:
        # Create the database
        log.info(f"First time running {database_name}! Creating new database!")
        await engine._run_in_pool(f"CREATE DATABASE {database_name};")
        created = True

    # Close old database connection
    await engine.close_connection_pool()
    return created


async def create_tables(
    cog: Cog, config: dict, tables: list[type[Table]], max_size: int = 20
) -> PostgresEngine:
    """Connect to postgres, create database/tables and return engine

    Args:
        cog (Cog): Cog instance
        config (dict): database connection info
        tables (list[type[Table]]): list of piccolo table subclasses
        max_size (int): maximum number of database connections, 20 by default

    Returns:
        PostgresEngine instance
    """
    temp_config = config.copy()
    temp_config["database"] = _root(cog).name.lower()
    engine = await asyncio.to_thread(_acquire_db_engine, temp_config)
    await engine.start_connection_pool(max_size=max_size)

    # Update table engines
    for table_class in tables:
        table_class._meta.db = engine

    # Create any tables that don't already exist
    await create_db_tables(*tables, if_not_exists=True)
    return engine


async def run_migrations(cog: Cog, config: dict) -> str:
    """
    Run any existing migrations programatically.

    There might be a better way to do this that subprocess, but haven't tested yet.

    Args:
        cog (Cog): Cog instance
        config (dict): database connection info

    Returns:
        str: Results of the migration
    """

    def run():
        root = _root(cog)
        temp_config = config.copy()
        temp_config["database"] = root.name.lower()
        return subprocess.run(
            ["piccolo", "migrations", "forward", root.name.lower()],
            env=_get_env(temp_config),
            cwd=root,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ).stdout.decode()

    return await asyncio.to_thread(run)


async def diagnose(cog: Cog, config: dict) -> str:
    """
    Diagnose any issues with Piccolo

    Args:
        cog (Cog): Cog instance
        config (dict): database connection info
    """

    def run():
        root = _root(cog)
        temp_config = config.copy()
        temp_config["database"] = root.name.lower()
        return subprocess.run(
            ["piccolo", "--diagnose"],
            env=_get_env(temp_config),
            cwd=root,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ).stdout.decode()

    return await asyncio.to_thread(run)


async def register_cog(
    cog: Cog, config: dict, tables: list[type[Table]], max_size: int = 20
) -> PostgresEngine:
    """Registers a cog by creating a database for it and initializing any tables it has

    Args:
        cog (Cog): Cog instance
        config (dict): database connection info
        tables (list[type[Table]]): list of piccolo table subclasses
        max_size (int): maximum number of database connections, 20 by default

    Returns:
        PostgresEngine
    """
    # Create databse under root folder name
    await create_database(cog, config)
    # Run any migrations
    result = await run_migrations(cog, config)
    log.info(result)
    # Create any tables and fetch postgres engine
    return await create_tables(cog, config, tables, max_size)


def _acquire_db_engine(config: dict) -> PostgresEngine:
    """This is ran in executor since it blocks if connection info is bad"""
    return PostgresEngine(config=config)


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


def _root(cog: Cog) -> Path:
    """Get root directory of cog, used for path and database name"""
    return Path(inspect.getfile(cog.__class__)).parent
