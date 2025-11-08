# =========================================================
# test_database.py
# =========================================================

import os
import sqlite3
import unittest
from unittest.mock import patch

from qa_core import database
from qa_core.database import (
    DB_NAME,
    clear_history,
    delete_analysis_by_id,
    get_all_analysis_history,
    get_analysis_by_id,
    get_db_connection,
    init_db,
    save_analysis_to_history,
)


class _NoCloseConnection:
    """Wrapper para conexões que não devem ser fechadas automaticamente nos testes."""

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def __getattr__(self, item):
        return getattr(self._conn, item)

    def close(self):
        """Override sem fechar a conexão real (fechada no tearDown)."""
        pass


class TestDatabaseInitialization(unittest.TestCase):
    DB_TEST_FILE = f"test_{DB_NAME}"

    def setUp(self):
        if os.path.exists(self.DB_TEST_FILE):
            os.remove(self.DB_TEST_FILE)

    def tearDown(self):
        if os.path.exists(self.DB_TEST_FILE):
            os.remove(self.DB_TEST_FILE)

    @patch("qa_core.database.DB_NAME", DB_TEST_FILE)
    def test_real_init_and_get_connection(self):
        self.assertFalse(os.path.exists(self.DB_TEST_FILE))
        # Testa a idempotência chamando duas vezes
        init_db()
        init_db()
        self.assertTrue(os.path.exists(self.DB_TEST_FILE))
        conn = get_db_connection()
        self.assertIsInstance(conn, sqlite3.Connection)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='analysis_history';"
        )
        table = cursor.fetchone()
        self.assertIsNotNone(table)
        conn.close()


class TestDatabaseLogic(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn_wrapper = _NoCloseConnection(self.conn)
        cursor = self.conn.cursor()
        cursor.execute(
            "CREATE TABLE analysis_history (id INTEGER PRIMARY KEY, created_at TIMESTAMP, user_story TEXT, analysis_report TEXT, test_plan_report TEXT);"
        )
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    @patch("qa_core.database.get_db_connection")
    def test_save_and_get_by_id(self, mock_get_conn):
        mock_get_conn.return_value = self.conn_wrapper
        save_analysis_to_history("us", "analysis", "plan")
        retrieved = get_analysis_by_id(1)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["user_story"], "us")

    @patch("qa_core.database.get_db_connection")
    def test_get_all_analysis_history_order(self, mock_get_conn):
        mock_get_conn.return_value = self.conn_wrapper
        save_analysis_to_history("US 1", "A 1", "P 1")
        save_analysis_to_history("US 2", "A 2", "P 2")
        all_entries = get_all_analysis_history()
        self.assertEqual(len(all_entries), 2)

        self.assertEqual(all_entries[0]["id"], 2)

    @patch("qa_core.database.get_db_connection")
    def test_get_all_history_on_empty_db(self, mock_get_conn):
        mock_get_conn.return_value = self.conn_wrapper
        all_entries = get_all_analysis_history()
        self.assertEqual(len(all_entries), 0)
        self.assertIsInstance(all_entries, list)

    @patch("qa_core.database.get_db_connection")
    def test_get_nonexistent_entry(self, mock_get_conn):
        mock_get_conn.return_value = self.conn_wrapper
        retrieved = get_analysis_by_id(999)
        self.assertIsNone(retrieved)

    @patch("qa_core.database.get_db_connection")
    def test_save_analysis_to_history_with_fallback_text(self, mock_get_conn):
        connection = sqlite3.connect(
            ":memory:", detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False
        )
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP NOT NULL,
                user_story TEXT NOT NULL,
                analysis_report TEXT,
                test_plan_report TEXT
            );
            """
        )
        connection.commit()

        mock_get_conn.return_value = _NoCloseConnection(connection)

        try:
            save_analysis_to_history(None, None, None)
            retrieved = get_analysis_by_id(1)

            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved["user_story"], "⚠️ User Story não disponível.")
            self.assertEqual(
                retrieved["analysis_report"], "⚠️ Relatório de análise não disponível."
            )
            self.assertEqual(
                retrieved["test_plan_report"],
                "⚠️ Plano de Testes não disponível ou não pôde ser gerado.",
            )
        finally:
            connection.close()


class TestDatabaseDelete(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn_wrapper = _NoCloseConnection(self.conn)
        cursor = self.conn.cursor()
        cursor.execute(
            "CREATE TABLE analysis_history (id INTEGER PRIMARY KEY, created_at TIMESTAMP, user_story TEXT, analysis_report TEXT, test_plan_report TEXT);"
        )
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    @patch("qa_core.database.get_db_connection")
    def test_delete_analysis_by_id(self, mock_get_conn):
        mock_get_conn.return_value = self.conn_wrapper
        save_analysis_to_history("US Teste", "A", "P")
        delete_analysis_by_id(1)
        result = get_analysis_by_id(1)
        self.assertIsNone(result)

    @patch("qa_core.database.get_db_connection")
    def test_clear_history(self, mock_get_conn):
        mock_get_conn.return_value = self.conn_wrapper
        save_analysis_to_history("US 1", "A", "P")
        save_analysis_to_history("US 2", "A", "P")
        clear_history()
        all_entries = get_all_analysis_history()
        self.assertEqual(len(all_entries), 0)


def test_init_db_com_erro(monkeypatch, capsys):
    def fail_connect(*args, **kwargs):
        raise sqlite3.Error("DB fail")

    monkeypatch.setattr(database.sqlite3, "connect", fail_connect)

    database.init_db()

    captured = capsys.readouterr()
    assert "[DB ERROR] Falha ao inicializar DB: DB fail" in captured.out


def test_save_analysis_to_history_com_erro(monkeypatch, capsys):
    def fail_connect(*args, **kwargs):
        raise sqlite3.Error("DB fail")

    monkeypatch.setattr(database.sqlite3, "connect", fail_connect)

    database.save_analysis_to_history("us", "report", "plan")

    captured = capsys.readouterr()
    assert "[DB ERROR] Falha ao salvar análise: DB fail" in captured.out


def test_get_all_analysis_history_com_erro(monkeypatch):
    def fail_connect(*args, **kwargs):
        raise sqlite3.Error("DB fail")

    monkeypatch.setattr(database.sqlite3, "connect", fail_connect)

    assert database.get_all_analysis_history() == []


def test_get_analysis_by_id_com_erro(monkeypatch):
    def fail_connect(*args, **kwargs):
        raise sqlite3.Error("DB fail")

    monkeypatch.setattr(database.sqlite3, "connect", fail_connect)

    assert database.get_analysis_by_id(1) is None


def test_get_analysis_by_id_com_id_invalido(monkeypatch):
    def _make_conn():
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr(database, "get_db_connection", _make_conn)

    assert database.get_analysis_by_id("abc") is None


def test_delete_analysis_by_id_com_erro(monkeypatch):
    def fail_connect(*args, **kwargs):
        raise sqlite3.Error("DB fail")

    monkeypatch.setattr(database.sqlite3, "connect", fail_connect)

    assert database.delete_analysis_by_id(1) is False


def test_clear_history_com_erro(monkeypatch):
    def fail_connect(*args, **kwargs):
        raise sqlite3.Error("DB fail")

    monkeypatch.setattr(database.sqlite3, "connect", fail_connect)

    assert database.clear_history() == 0


def test_get_all_analysis_history_vazio(monkeypatch):
    """Força o caso onde o banco está vazio"""
    monkeypatch.setattr(
        database, "get_db_connection", lambda: sqlite3.connect(":memory:")
    )

    # Inicializa schema mas não insere nada
    conn = database.get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY,
            created_at TEXT,
            user_story TEXT,
            analysis_report TEXT,
            test_plan_report TEXT
        )
    """
    )
    conn.commit()
    conn.close()

    history = database.get_all_analysis_history()
    assert history == []
