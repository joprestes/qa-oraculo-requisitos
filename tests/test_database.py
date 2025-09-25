import unittest
import sqlite3
from unittest.mock import patch

# Importamos as funções que queremos testar
from database import init_db, save_analysis_to_history, get_all_analysis_history, get_analysis_by_id

class TestDatabaseFunctions(unittest.TestCase):

    def setUp(self):
        """
        Esta função roda ANTES de cada teste.
        Ela cria um banco de dados temporário na memória para testes.
        """
        # :memory: garante que cada setUp cria um banco de dados novo na RAM
        self.conn = sqlite3.connect(':memory:')
        self.conn.row_factory = sqlite3.Row
        
        # Precisamos de um cursor para criar a tabela manualmente aqui
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
        """
        Esta função roda DEPOIS de cada teste.
        Fecha a conexão com o banco de dados temporário.
        """
        self.conn.close()

    @patch('database.get_db_connection')
    def test_save_and_get_by_id(self, mock_get_conn):
        """
        Testa se conseguimos salvar uma análise e depois buscá-la pelo ID.
        """
        # Arrange: Configuramos o "engano" para este teste específico.
        mock_get_conn.return_value = self.conn

        us = "Como um usuário, eu quero..."
        analysis = "Relatório de análise."
        plan = "Plano de testes."

        # Act
        save_analysis_to_history(us, analysis, plan)
        retrieved_entry = get_analysis_by_id(1)

        # Assert
        self.assertIsNotNone(retrieved_entry)
        self.assertEqual(retrieved_entry['id'], 1)
        self.assertEqual(retrieved_entry['user_story'], us)

    @patch('database.get_db_connection')
    def test_get_all_analysis_history_order(self, mock_get_conn):
        """
        Testa se a função que busca todo o histórico retorna as entradas na ordem correta.
        """
        # Arrange
        mock_get_conn.return_value = self.conn
        
        # Act
        save_analysis_to_history("US 1", "Análise 1", "Plano 1")
        save_analysis_to_history("US 2", "Análise 2", "Plano 2")
        all_entries = get_all_analysis_history()

        # Assert
        self.assertEqual(len(all_entries), 2)
        self.assertEqual(all_entries[0]['id'], 2) # Mais novo primeiro
        self.assertEqual(all_entries[1]['id'], 1)

    @patch('database.get_db_connection')
    def test_get_nonexistent_entry(self, mock_get_conn):
        """
        Testa o que acontece se pedirmos um ID que não existe.
        """
        # Arrange
        mock_get_conn.return_value = self.conn

        # Act
        retrieved_entry = get_analysis_by_id(999)

        # Assert
        self.assertIsNone(retrieved_entry)