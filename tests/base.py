"""
Base Test Configuration for Isolated Test Execution
"""

import os
import unittest
from app import create_app
from app.db import init_db, seed_sample_data_if_empty


class BaseTestCase(unittest.TestCase):
    """Base class for all portal unit and integration tests."""

    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Initialize fresh test database schema and seed data
        init_db(self.app)
        seed_sample_data_if_empty(self.app)

    def tearDown(self):
        self.app_context.pop()
        db_path = self.app.config.get("DB_PATH")
        if db_path and os.path.exists(db_path) and "test_" in os.path.basename(db_path):
            try:
                os.remove(db_path)
            except OSError:
                pass
