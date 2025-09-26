import unittest
import sqlite3
import os
from unittest.mock import patch

from database import init_db, save_analysis_to_history, get_all_analysis_history, get_analysis_by_id, get_db_connection, DB_NAME

class TestDatabaseInitialization(unittest.TestCase):
    DB_TEST_FILE = f"test_{DB_NAME}"

    def setUp(self):
        if os.path.exists(self.DB_TEST_FILE):
            os.remove(self.DB_TEST_FILE)
    def tearDown(self):
        if os.path.exists(self.DB_TEST_FILE):
            os.remove(self.DB_TEST_FILE)

    @patch('database.DB_NAME', DB_TEST_FILE)
    def test_real_init_and_get_connection(self):
        self.assertFalse(os.path.exists(self.DB_TEST_FILE))
        # Testa a idempotência chamando duas vezes
        init_db()
        init_db()
        self.assertTrue(os.path.exists(self.DB_TEST_FILE))
        conn = get_db_connection()
        self.assertIsInstance(conn, sqlite3.Connection)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analysis_history';")
        table = cursor.fetchone()
        self.assertIsNotNone(table)
        conn.close()

class TestDatabaseLogic(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute("CREATE TABLE analysis_history (id INTEGER PRIMARY KEY, created_at TIMESTAMP, user_story TEXT, analysis_report TEXT, test_plan_report TEXT);")
        self.conn.commit()
    def tearDown(self):
        self.conn.close()

    @patch('database.get_db_connection')
    def test_save_and_get_by_id(self, mock_get_conn):
        mock_get_conn.return_value = self.conn
        save_analysis_to_history("us", "analysis", "plan")
        retrieved = get_analysis_by_id(1)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['user_story'], "us")

    @patch('database.get_db_connection')
    def test_get_all_analysis_history_order(self, mock_get_conn):
        mock_get_conn.return_value = self.conn
        save_analysis_to_history("US 1", "A 1", "P 1")
        save_analysis_to_history("US 2", "A 2", "P 2")
        all_entries = get_all_analysis_history()
        self.assertEqual(len(all_entries), 2)
  
        self.assertEqual(all_entries[0]['id'], 2)

    @patch('database.get_db_connection')
    def test_get_all_history_on_empty_db(self, mock_get_conn):
  
        mock_get_conn.return_value = self.conn
        all_entries = get_all_analysis_history()
        self.assertEqual(len(all_entries), 0)
        self.assertIsInstance(all_entries, list)

    @patch('database.get_db_connection')
    def test_get_nonexistent_entry(self, mock_get_conn):
        mock_get_conn.return_value = self.conn
        retrieved = get_analysis_by_id(999)
        self.assertIsNone(retrieved)