# conftest.py

import os
import pytest
from database import DB_NAME, clear_history


@pytest.fixture(scope="session", autouse=True)
def cleanup_after_tests():
    """
    Fixture global que roda APÓS toda a suite de testes.
    Garante que o histórico usado nos testes não vaze para a interface real.

    - Primeiro tenta limpar a tabela via clear_history().
    - Se der erro, remove o arquivo físico do DB como fallback.
    """
    yield  # espera os testes rodarem
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
