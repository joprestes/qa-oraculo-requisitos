# conftest.py
import os
import sqlite3

import pandas as pd
import pytest
import streamlit as st

from database import DB_NAME, clear_history


# --------------------------
# FIXTURE GLOBAL DE LIMPEZA
# --------------------------
@pytest.fixture(scope="session", autouse=True)
def cleanup_after_tests():
    """
    Roda APÓS toda a suíte de testes.
    Garante que o histórico usado nos testes não vaze para a interface real.
    """
    yield
    try:
        apagados = clear_history()
        print(
            f"[CLEANUP] Histórico limpo após testes ({apagados} registros removidos)."
        )
    except Exception as e:
        print(
            f"[CLEANUP] Falha ao limpar com clear_history(): {e}. Removendo arquivo físico..."
        )
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
            print(f"[CLEANUP] Banco {DB_NAME} removido.")


# --------------------------
# FIXTURE: STUB DO STREAMLIT
# --------------------------
@pytest.fixture
def st_session_state(monkeypatch):
    """Simula streamlit.st.session_state e funções básicas para testes unitários."""
    fake_st = type("FakeSt", (), {})()
    fake_st.session_state = {}
    fake_st.button = lambda *a, **kw: False
    fake_st.text_area = lambda *a, **kw: ""
    fake_st.warning = lambda *a, **kw: None
    fake_st.spinner = lambda *a, **kw: (lambda x: x)
    monkeypatch.setattr(st, "session_state", fake_st.session_state)
    return fake_st


# --------------------------
# FIXTURE: BANCO EM MEMÓRIA
# --------------------------
@pytest.fixture
def db_in_memory(monkeypatch):
    """Substitui o banco real por uma instância SQLite em memória."""
    conn = sqlite3.connect(":memory:")
    monkeypatch.setattr("database.get_db_connection", lambda: conn)
    return conn


# --------------------------
# FIXTURE: DATAFRAME EXEMPLO
# --------------------------
@pytest.fixture
def sample_dataframe():
    """Retorna um DataFrame de exemplo para testes de exportação e PDF."""
    return pd.DataFrame([{"coluna1": "valor1", "coluna2": 123}])
