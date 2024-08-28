from unittest import TestCase

from pathlib import Path
from piccolo.engine.postgres import PostgresEngine
from tests.tables import TABLES
from piccolo.utils.sync import run_sync
import os
from red_postgres.engine import register_cog, run_migrations, create_migrations, diagnose_issues, ensure_database_exists, acquire_db_engine


config={
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
    "database": os.environ.get("POSTGRES_DATABASE"),
    "host": os.environ.get("POSTGRES_HOST"),
    "port": os.environ.get("POSTGRES_PORT"),
}
root = Path(__file__).parent

class TestCrud(TestCase):

    def setUp(self):
        engine = run_sync(acquire_db_engine(config))
        run_sync(engine._run_in_new_connection("DROP DATABASE IF EXISTS tests WITH (FORCE)"))

    def tearDown(self):
        engine = run_sync(acquire_db_engine(config))
        run_sync(engine._run_in_new_connection("DROP DATABASE IF EXISTS tests WITH (FORCE)"))
        
    def test_ensure_database_exists(self):
        created = run_sync(ensure_database_exists(root, config))
        self.assertTrue(created, "Should return True if database was created")
        
    def test_register_cog(self):
        cog_engine = run_sync(register_cog(root, config, TABLES))
        self.assertIsInstance(cog_engine, PostgresEngine, "Should return a PostgresEngine instance")
        
    def test_make_migrations(self):
        res = run_sync(create_migrations(root, config))
        self.assertIsInstance(res, str, "Should return a string")
        
    def test_run_migrations(self):
        res = run_sync(run_migrations(root, config))
        self.assertIsInstance(res, str, "Should return a string")
        
    def test_diagnose_issues(self):
        res = run_sync(diagnose_issues(root, config))
        self.assertIsInstance(res, str, "Should return a string")
        
        
        
        
        
        





