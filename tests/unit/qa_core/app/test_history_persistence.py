import json
import sqlite3
from unittest.mock import MagicMock, patch


from qa_core import app


def _build_session_state_para_historia_valida():
    registros = [
        {"id": "CT-1", "titulo": "Caso padrão", "cenario": "Dado X\nQuando Y\nEntão Z"}
    ]
    return {
        "user_story_input": "  Como tester quero validar  ",
        "analysis_state": {
            "user_story": "História original",
            "relatorio_analise_inicial": "  Relatório inicial  ",
        },
        "test_plan_report": "  Plano completo  ",
        "test_plan_report_intro": "Plano completo",
        "test_plan_df_records": registros,
        "test_plan_df_json": json.dumps(registros, ensure_ascii=False),
        "history_saved": False,
    }


@patch("qa_core.database.get_db_connection")
@patch("qa_core.app.announce")
@patch("qa_core.app.st")
def test_save_current_analysis_to_history_sem_dados_suficientes(
    mock_st, mock_announce, mock_get_conn
):
    mock_st.session_state = {
        "user_story_input": "",
        "analysis_state": {},
        "test_plan_report": None,
    }

    app._save_current_analysis_to_history()

    mock_get_conn.assert_not_called()
    mock_announce.assert_not_called()


@patch("qa_core.database.get_db_connection")
@patch("qa_core.app.st")
def test_save_current_analysis_to_history_atualiza_existente(mock_st, mock_get_conn):
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn

    session_state = _build_session_state_para_historia_valida()
    session_state["last_saved_id"] = 42
    mock_st.session_state = session_state

    app._save_current_analysis_to_history(update_existing=True)

    update_calls = [
        mock_call
        for mock_call in mock_cursor.execute.call_args_list
        if "UPDATE" in mock_call.args[0]
    ]
    assert update_calls, "Deve executar UPDATE ao atualizar registro existente"

    _, params = update_calls[0].args
    assert params[1] == "Como tester quero validar"
    assert params[2] == "Relatório inicial"
    assert params[3] == "Plano completo"
    assert params[4] == "Plano completo"
    assert params[5] == session_state["test_plan_df_json"]

    assert all(
        "INSERT" not in mock_call.args[0]
        for mock_call in mock_cursor.execute.call_args_list
    )
    mock_conn.commit.assert_called_once()


@patch("qa_core.database.get_db_connection")
@patch("qa_core.app.announce")
@patch("qa_core.app.st")
def test_save_current_analysis_to_history_sqlite_error(
    mock_st, mock_announce, mock_get_conn
):
    mock_st.session_state = _build_session_state_para_historia_valida()
    mock_get_conn.side_effect = sqlite3.Error("db locked")

    app._save_current_analysis_to_history()

    mock_announce.assert_called_once()
    args, kwargs = mock_announce.call_args
    assert args[1] == "error"
    assert kwargs["st_api"] is mock_st


@patch("qa_core.database.get_db_connection")
@patch("qa_core.app.announce")
@patch("qa_core.app.st")
def test_save_current_analysis_to_history_erro_generico(
    mock_st, mock_announce, mock_get_conn
):
    class ExplodingConn:
        def __enter__(self):
            raise RuntimeError("boom")

        def __exit__(self, exc_type, exc, tb):
            return False

    mock_st.session_state = _build_session_state_para_historia_valida()
    mock_get_conn.return_value = ExplodingConn()

    app._save_current_analysis_to_history()

    mock_announce.assert_called_once()
    args, kwargs = mock_announce.call_args
    assert args[1] == "warning"
    assert kwargs["st_api"] is mock_st


@patch("qa_core.app._save_current_analysis_to_history", return_value="ok")
def test_save_analysis_to_history_wrapper_chama_privado(mock_save):
    assert app.save_analysis_to_history(update_existing=True) == "ok"
    mock_save.assert_called_once_with(update_existing=True)


@patch("qa_core.database.get_db_connection")
@patch("qa_core.app.announce")
@patch("qa_core.app.st")
def test_save_current_analysis_to_history_with_invalid_json_records(
    mock_st, mock_announce, mock_get_conn
):
    """Testa que TypeError/ValueError ao converter records para JSON é tratado (linha 165)."""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_get_conn.return_value = mock_conn

    # Cria records que não podem ser serializados em JSON
    # (ex: objetos complexos, funções, etc)
    invalid_records = [
        {
            "id": "CT-1",
            "titulo": "Caso",
            "cenario": "Dado X",
            "objeto_nao_serializavel": object(),  # Não serializável
        }
    ]

    session_state = {
        "user_story_input": "Como tester quero validar",
        "analysis_state": {
            "user_story": "História",
            "relatorio_analise_inicial": "Relatório",
        },
        "test_plan_report": "Plano",
        "test_plan_df_records": invalid_records,
        # Não define test_plan_df_json para forçar tentativa de conversão
    }

    mock_st.session_state = session_state

    # Deve tratar o erro e continuar sem quebrar
    app._save_current_analysis_to_history()

    # Verifica que tentou salvar (pode falhar no json.dumps mas não quebra)
    assert mock_get_conn.called
