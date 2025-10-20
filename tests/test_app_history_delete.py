"""Testes do módulo de histórico — exclusão de análises e limpeza total."""

import pytest
from unittest.mock import MagicMock, patch
import app


def make_button_side_effect(expected_buttons):
    """Cria um side_effect para simular cliques em botões Streamlit."""
    def side_effect(label, **kwargs):
        key = kwargs.get("key")
        return expected_buttons.get(key, False)
    return side_effect


@pytest.fixture
def mock_st():
    """Mock do módulo Streamlit."""
    mock = MagicMock()
    mock.session_state = {}
    return mock


# ============================================================
# Cenários: exclusão individual
# ============================================================

@patch("app.delete_analysis_by_id", return_value=True)
def test_excluir_individual_sucesso(mock_delete, mock_st):
    """Valida exclusão bem-sucedida de uma análise específica."""
    mock_st.session_state["confirm_delete_id"] = 42
    mock_st.button.side_effect = make_button_side_effect({"confirmar_delete": True})

    app.render_history_page(st_api=mock_st)

    mock_delete.assert_called_once_with(42)
    mock_st.success.assert_called_once_with("Análise 42 removida com sucesso.")


@patch("app.delete_analysis_by_id", return_value=False)
def test_excluir_individual_falha(mock_delete, mock_st):
    """Valida feedback de erro quando a exclusão individual falha."""
    mock_st.session_state["confirm_delete_id"] = 42
    mock_st.button.side_effect = make_button_side_effect({"confirmar_delete": True})

    app.render_history_page(st_api=mock_st)

    mock_delete.assert_called_once_with(42)
    mock_st.error.assert_called_once_with("Não foi possível excluir a análise selecionada.")


# ============================================================
# Cenários: exclusão de todo o histórico
# ============================================================

@patch("app.clear_history", return_value=3)
def test_excluir_todo_confirmado(mock_clear, mock_st):
    """Valida exclusão total confirmada com sucesso."""
    mock_st.session_state["confirm_clear_all"] = True
    mock_st.button.side_effect = make_button_side_effect({"confirmar_delete_all": True})

    app.render_history_page(st_api=mock_st)

    mock_clear.assert_called_once()
    mock_st.success.assert_called_once_with("3 análises foram removidas.")


@patch("app.clear_history", return_value=0)
def test_excluir_todo_falha(mock_clear, mock_st):
    """Valida feedback quando a limpeza total não remove nenhuma análise."""
    mock_st.session_state["confirm_clear_all"] = True
    mock_st.button.side_effect = make_button_side_effect({"confirmar_delete_all": True})

    app.render_history_page(st_api=mock_st)

    mock_clear.assert_called_once()
    mock_st.warning.assert_called_once_with("Nenhuma análise foi removida.")


# ============================================================
# Cenário: cancelamento de exclusão
# ============================================================

def test_cancelar_exclusao(mock_st):
    """Valida que nenhuma exclusão ocorre quando o usuário cancela."""
    mock_st.session_state["confirm_delete_id"] = 99
    mock_st.session_state["confirm_clear_all"] = False
    mock_st.button.side_effect = make_button_side_effect({
        "confirmar_delete": False,
        "confirmar_delete_all": False,
    })

    with patch("app.delete_analysis_by_id") as mock_delete, patch("app.clear_history") as mock_clear:
        app.render_history_page(st_api=mock_st)

        mock_delete.assert_not_called()
        mock_clear.assert_not_called()
        mock_st.info.assert_called_once_with("Nenhuma exclusão foi realizada.")
