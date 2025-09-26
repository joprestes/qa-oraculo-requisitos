import unittest
import sqlite3
import os
from unittest.mock import patch

from database import init_db, save_analysis_to_history, get_all_analysis_history, get_analysis_by_id, get_db_connection, DB_NAME

class TestDatabaseInitialization(unittest.TestCase):
    
    DB_TEST_FILE = f"test_{DB_NAME}"

    def setUp(self):
        # Garante que nenhum arquivo de teste antigo exista
        if os.path.exists(self.DB_TEST_FILE):
            os.remove(self.DB_TEST_FILE)

    def tearDown(self):
        # Limpa o arquivo de teste após a execução
        if os.path.exists(self.DB_TEST_FILE):
            os.remove(self.DB_TEST_FILE)

    @patch('database.DB_NAME', DB_TEST_FILE)
    def test_real_init_and_get_connection(self):
        """
        Testa se init_db e get_db_connection funcionam com um arquivo de verdade.
        Isso garante 100% de cobertura.
        """
        # Arrange: O banco de dados de teste não deve existir
        self.assertFalse(os.path.exists(self.DB_TEST_FILE))

        # Act: Chamamos a função init_db real. O patch faz ela usar nosso nome de arquivo de teste.
        init_db()

        # Assert: O arquivo de banco de dados foi criado?
        self.assertTrue(os.path.exists(self.DB_TEST_FILE))

        # Act: Chamamos a get_db_connection real.
        conn = get_db_connection()
        
        # Assert: A conexão é válida e a tabela existe dentro dela?
        self.assertIsInstance(conn, sqlite3.Connection)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analysis_history';")
        table = cursor.fetchone()
        self.assertIsNotNone(table)
        conn.close()

# --- Testes de Lógica com Banco de Dados em Memória  ---

class TestDatabaseLogic(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP NOT NULL,
            user_story TEXT NOT NULL,
            analysis_report TEXT,
            test_plan_report TEXT
        );
        """)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    @patch('database.get_db_connection')
    def test_save_and_get_by_id(self, mock_get_conn):
        mock_get_conn.return_value = self.conn
        us = "Como um usuário, eu quero..."
        analysis = "Relatório de análise."
        plan = "Plano de testes."
        save_analysis_to_history(us, analysis, plan)
        retrieved_entry = get_analysis_by_id(1)
        self.assertIsNotNone(retrieved_entry)
        self.assertEqual(retrieved_entry['id'], 1)
        self.assertEqual(retrieved_entry['user_story'], us)

    @patch('database.get_db_connection')
    def test_get_all_analysis_history_order(self, mock_get_conn):
        mock_get_conn.return_value = self.conn
        save_analysis_to_history("US 1", "Análise 1", "Plano 1")
        save_analysis_to_history("US 2", "Análise 2", "Plano 2")
        all_entries = get_all_analysis_history()
        self.assertEqual(len(all_entries), 2)
        self.assertEqual(all_entries[0]['id'], 2)
        self.assertEqual(all_entries[1]['id'], 1)

    @patch('database.get_db_connection')
    def test_get_nonexistent_entry(self, mock_get_conn):
        mock_get_conn.return_value = self.conn
        retrieved_entry = get_analysis_by_id(999)
        self.assertIsNone(retrieved_entry)