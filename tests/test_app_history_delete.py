# =========================================================
# test_app_history_delete.py
# =========================================================

"""Testes do módulo de histórico — exclusão de análises e limpeza total."""

from unittest.mock import MagicMock, patch

import pytest

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
    mock.query_params = {}
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
    mock_st.error.assert_called_once_with(
        "Não foi possível excluir a análise selecionada."
    )


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


def test_cancelar_exclusao_individual_botao(mock_st):
    """Garante que o botão de cancelamento interrompe a exclusão individual."""
    mock_st.session_state["confirm_delete_id"] = 99
    mock_st.button.side_effect = make_button_side_effect(
        {
            "confirmar_delete": False,
            "cancelar_delete": True,
        }
    )

    with patch("app.delete_analysis_by_id") as mock_delete:
        app.render_history_page(st_api=mock_st)

        mock_delete.assert_not_called()
        assert "confirm_delete_id" not in mock_st.session_state
        mock_st.info.assert_called_once_with("Nenhuma exclusão foi realizada.")


def test_cancelar_limpeza_total_botao(mock_st):
    """Garante que o botão de cancelamento interrompe a limpeza total."""
    mock_st.session_state["confirm_clear_all"] = True
    mock_st.button.side_effect = make_button_side_effect(
        {
            "confirmar_delete_all": False,
            "cancelar_delete_all": True,
        }
    )

    with patch("app.clear_history") as mock_clear:
        app.render_history_page(st_api=mock_st)

        mock_clear.assert_not_called()
        assert "confirm_clear_all" not in mock_st.session_state
        mock_st.info.assert_called_once_with("Nenhuma exclusão foi realizada.")


# ============================================================
# Cenário: cancelamento de exclusão
# ============================================================


def test_cancelar_exclusao(mock_st):
    """Valida que nenhuma exclusão ocorre quando o usuário cancela."""
    mock_st.session_state["confirm_delete_id"] = 99
    mock_st.session_state["confirm_clear_all"] = False
    mock_st.button.side_effect = make_button_side_effect(
        {
            "confirmar_delete": False,
            "confirmar_delete_all": False,
        }
    )

    with (
        patch("app.delete_analysis_by_id") as mock_delete,
        patch("app.clear_history") as mock_clear,
    ):
        app.render_history_page(st_api=mock_st)

        mock_delete.assert_not_called()
        mock_clear.assert_not_called()
        mock_st.info.assert_called_once_with("Nenhuma exclusão foi realizada.")


# ============================================================
# Cenários: visualização de histórico
# ============================================================


@patch("app.get_analysis_by_id")
@patch("app.get_all_analysis_history")
def test_visualizar_analise_por_query_param(mock_get_all, mock_get_by_id, mock_st):
    """Garante que uma análise específica seja mostrada via query param."""

    mock_get_all.return_value = [
        {
            "id": 1,
            "created_at": "2024-01-01",
            "user_story": "Como usuário, quero ...",
            "analysis_report": "Relatório disponível.",
            "test_plan_report": "",
        }
    ]
    mock_get_by_id.return_value = {
        "id": 1,
        "created_at": "2024-01-01",
        "user_story": "Como usuário, quero ...",
        "analysis_report": "Relatório disponível.",
        "test_plan_report": "",
    }
    mock_st.query_params = {"analysis_id": ["1"]}

    app.render_history_page(st_api=mock_st)

    mock_get_all.assert_called_once()
    mock_get_by_id.assert_called_once_with(1)
    mock_st.code.assert_called_once_with("Como usuário, quero ...", language="gherkin")
    mock_st.info.assert_called_once_with(
        "Nenhum plano de testes foi gerado para esta análise."
    )


@patch("app.get_analysis_by_id", return_value=None)
@patch("app.get_all_analysis_history", return_value=[{"id": 10}])
def test_visualizar_analise_inexistente_exibe_erro(
    mock_get_all, mock_get_by_id, mock_st
):
    """Simula query param inexistente e verifica mensagem de erro apropriada."""

    mock_st.query_params = {"analysis_id": ["999"]}

    app.render_history_page(st_api=mock_st)

    mock_get_all.assert_called_once()
    mock_get_by_id.assert_called_once_with(999)
    mock_st.error.assert_called_once_with("Análise não encontrada.")


@patch("app.get_all_analysis_history", return_value=[])
def test_visualizar_historico_vazio_query_param_invalido(mock_get_all, mock_st):
    """Força fallback para histórico vazio quando o parâmetro é inválido."""

    mock_st.query_params = {"analysis_id": ["abc"]}

    app.render_history_page(st_api=mock_st)

    mock_get_all.assert_called_once()
    mock_st.info.assert_called_once_with(
        "Ainda não há análises no histórico. Realize uma nova análise para começar."
    )


def test_wrapper_usa_modo_teste_em_cancelamento(mock_st):
    """Assegura que o wrapper delega para o modo de teste ao cancelar exclusões."""

    mock_st.session_state["confirm_delete_id"] = 55
    mock_st.button.side_effect = make_button_side_effect(
        {
            "confirmar_delete": False,
            "cancelar_delete": True,
        }
    )

    original = app._render_history_page_test_mode
    with patch("app._render_history_page_test_mode", wraps=original) as spy_test_mode:
        app.render_history_page(st_api=mock_st)

        spy_test_mode.assert_called_once_with(mock_st)
        mock_st.info.assert_called_once_with("Nenhuma exclusão foi realizada.")


@patch("app.get_all_analysis_history", return_value=[])
def test_visualizar_historico_vazio(mock_get_all, mock_st):
    """Garante mensagem informativa quando não há análises armazenadas."""

    app.render_history_page(st_api=mock_st)

    mock_get_all.assert_called_once()
    mock_st.info.assert_called_once_with(
        "Ainda não há análises no histórico. Realize uma nova análise para começar."
    )
