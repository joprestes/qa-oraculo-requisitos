# test_app_history_delete.py

import pytest
from unittest.mock import patch, MagicMock
import app


def make_button_side_effect(mapping):
    """
    mapping: dict onde a chave é o 'key' ou label do botão,
    e o valor é o retorno esperado (True/False).
    Todos os outros botões retornam False por padrão.
    """

    def _side_effect(*args, **kwargs):
        key = kwargs.get("key")
        label = args[0] if args else None
        if key in mapping:
            return mapping[key]
        if label in mapping:
            return mapping[label]
        return False

    return _side_effect


@pytest.fixture
def mock_st():
    """Mock do streamlit usado em app.py"""
    with patch("app.st") as mock_st:
        mock_st.session_state = {}
        mock_st.query_params = {}
        mock_st.columns.return_value = (MagicMock(), MagicMock())
        yield mock_st


# ------------------------------
# Exclusão individual
# ------------------------------


@patch("app.delete_analysis_by_id", return_value=True)
def test_excluir_individual_confirmado(mock_delete, mock_st):
    mock_st.session_state["confirm_delete_id"] = 1
    mock_st.button.side_effect = make_button_side_effect(
        {"confirmar_delete": True, "cancelar_delete": False}
    )

    app.render_history_page()

    mock_delete.assert_called_once_with(1)
    assert "confirm_delete_id" not in mock_st.session_state


@patch("app.delete_analysis_by_id", return_value=False)
def test_excluir_individual_falha(mock_delete, mock_st):
    mock_st.session_state["confirm_delete_id"] = 42
    mock_st.button.side_effect = make_button_side_effect({"confirmar_delete": True})

    app.render_history_page()

    mock_delete.assert_called_once_with(42)
    mock_st.error.assert_called()
    assert "confirm_delete_id" not in mock_st.session_state


def test_excluir_individual_cancelado(mock_st):
    mock_st.session_state["confirm_delete_id"] = 99
    mock_st.button.side_effect = make_button_side_effect({"cancelar_delete": True})

    app.render_history_page()

    assert "confirm_delete_id" not in mock_st.session_state


# ------------------------------
# Exclusão total do histórico
# ------------------------------


@patch("app.clear_history", return_value=3)
def test_excluir_todo_confirmado(mock_clear, mock_st):
    mock_st.session_state["confirm_clear_all"] = True
    mock_st.button.side_effect = make_button_side_effect({"confirmar_delete_all": True})

    app.render_history_page()

    mock_clear.assert_called_once()
    mock_st.success.assert_called_with("3 análises foram removidas.")
    assert "confirm_clear_all" not in mock_st.session_state


@patch("app.clear_history", return_value=0)
def test_excluir_todo_falha(mock_clear, mock_st):
    mock_st.session_state["confirm_clear_all"] = True
    mock_st.button.side_effect = make_button_side_effect({"confirmar_delete_all": True})

    app.render_history_page()

    mock_clear.assert_called_once()
    mock_st.success.assert_called_with("0 análises foram removidas.")
    assert "confirm_clear_all" not in mock_st.session_state


def test_excluir_todo_cancelado(mock_st):
    mock_st.session_state["confirm_clear_all"] = True
    mock_st.button.side_effect = make_button_side_effect({"cancelar_delete_all": True})

    app.render_history_page()

    assert "confirm_clear_all" not in mock_st.session_state
