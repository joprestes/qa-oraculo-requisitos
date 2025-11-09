import datetime
from unittest.mock import MagicMock, patch

from qa_core import app

TWO_COLUMN_COUNT = 2


def _make_context():
    ctx = MagicMock()
    ctx.__enter__.return_value = MagicMock()
    ctx.__exit__.return_value = False
    return ctx


@patch("qa_core.app.st")
def test_render_history_page_com_historico(mock_st):
    mock_st.session_state = {}
    mock_st.query_params.get.return_value = [None]
    mock_st.columns.return_value = [MagicMock(), MagicMock()]

    history = [{"id": 1, "created_at": "2025-09-26", "user_story": "US exemplo"}]
    with patch("qa_core.app.get_all_analysis_history", return_value=history):
        app.render_history_page()

    calls = [str(mock_call) for mock_call in mock_st.markdown.call_args_list]
    assert any("2025-09-26" in call_str for call_str in calls)


@patch("qa_core.app.st")
def test_render_history_page_detalhes(mock_st):
    mock_st.session_state = {}
    mock_st.query_params.get.return_value = ["1"]

    entry = {
        "id": 1,
        "created_at": "2025-09-26",
        "user_story": "Teste",
        "analysis_report": "Relatório",
        "test_plan_report": "Plano",
    }
    with patch("qa_core.app.get_analysis_by_id", return_value=entry):
        app.render_history_page()
        mock_st.markdown.assert_any_call("### Análise de 2025-09-26")
        mock_st.code.assert_called_once_with("Teste", language="gherkin")


def test_render_history_sem_historico(mocked_st):
    mocked_st.query_params.get.return_value = [None]

    with patch("qa_core.app.get_all_analysis_history", return_value=[]):
        app.render_history_page()

    mocked_st.info.assert_called_with(
        "Ainda não há análises no histórico. Realize uma nova análise para começar."
    )


def test_render_history_com_historico_lista(mocked_st):
    mocked_st.query_params.get.return_value = [None]
    history = [{"id": 1, "created_at": "2025-09-26", "user_story": "US exemplo"}]
    with patch("qa_core.app.get_all_analysis_history", return_value=history):
        app.render_history_page()
    mocked_st.container.assert_called()


def test_render_history_com_analysis_id_valido(mocked_st):
    mocked_st.query_params.get.return_value = ["1"]
    analysis_entry = {
        "id": 1,
        "created_at": "2025-09-26",
        "user_story": "User Story completa",
        "analysis_report": "Relatório IA",
        "test_plan_report": "Plano gerado",
    }
    with patch("qa_core.app.get_analysis_by_id", return_value=analysis_entry):
        app.render_history_page()
    mocked_st.markdown.assert_any_call("### Análise de 2025-09-26")
    mocked_st.code.assert_called_with("User Story completa", language="gherkin")


def test_render_history_com_analysis_id_invalido(mocked_st):
    mocked_st.query_params.get.return_value = ["99"]
    with patch("qa_core.app.get_analysis_by_id", return_value=None):
        app.render_history_page()
    mocked_st.error.assert_called_with("Análise não encontrada.")


def test_render_history_confirm_delete_sem_sucesso(mocked_st):
    mocked_st.session_state.clear()
    mocked_st.session_state["confirm_delete_id"] = 7
    mocked_st.query_params.get.return_value = None
    mocked_st.container.side_effect = lambda *args, **kwargs: _make_context()

    original_columns = mocked_st.columns.side_effect

    def columns_side_effect(arg):
        if arg == 2:
            confirm_col, cancel_col = MagicMock(), MagicMock()
            confirm_col.button.return_value = True
            cancel_col.button.return_value = False
            return (confirm_col, cancel_col)
        return original_columns(arg)

    mocked_st.columns.side_effect = columns_side_effect

    with (
        patch("qa_core.app.delete_analysis_by_id", return_value=False),
        patch("qa_core.app.get_all_analysis_history", return_value=[]),
        patch("qa_core.app.announce") as mock_announce,
    ):
        app.render_history_page()

    mock_announce.assert_any_call(
        "Não foi possível excluir a análise selecionada.", "error", st_api=mocked_st
    )
    mocked_st.columns.side_effect = original_columns


def test_render_history_clear_all_sem_registros(mocked_st):
    mocked_st.session_state.clear()
    mocked_st.session_state["confirm_clear_all"] = True
    mocked_st.query_params.get.return_value = None
    mocked_st.container.side_effect = lambda *args, **kwargs: _make_context()

    original_columns = mocked_st.columns.side_effect

    def columns_side_effect(arg):
        if arg == 2:
            confirm_col, cancel_col = MagicMock(), MagicMock()
            confirm_col.button.return_value = True
            cancel_col.button.return_value = False
            return (confirm_col, cancel_col)
        return original_columns(arg)

    mocked_st.columns.side_effect = columns_side_effect

    with (
        patch("qa_core.app.clear_history", return_value=0),
        patch("qa_core.app.get_all_analysis_history", return_value=[]),
        patch("qa_core.app.announce") as mock_announce,
    ):
        app.render_history_page()

    mock_announce.assert_any_call(
        "Nenhuma análise foi removida.", "warning", st_api=mocked_st
    )
    mocked_st.columns.side_effect = original_columns


def test_render_history_clear_all_cancelado(mocked_st):
    mocked_st.session_state.clear()
    mocked_st.session_state["confirm_clear_all"] = True
    mocked_st.query_params.get.return_value = None
    mocked_st.container.side_effect = lambda *args, **kwargs: _make_context()

    original_columns = mocked_st.columns.side_effect

    def columns_side_effect(arg):
        if arg == 2:
            confirm_col, cancel_col = MagicMock(), MagicMock()
            confirm_col.button.return_value = False
            cancel_col.button.return_value = True
            return (confirm_col, cancel_col)
        return original_columns(arg)

    mocked_st.columns.side_effect = columns_side_effect

    with (
        patch("qa_core.app.get_all_analysis_history", return_value=[]),
        patch("qa_core.app.announce") as mock_announce,
    ):
        app.render_history_page()

    mock_announce.assert_any_call(
        "Nenhuma exclusão foi realizada.", "info", st_api=mocked_st
    )
    mocked_st.columns.side_effect = original_columns


def test_render_history_id_invalido_tratado(mocked_st):
    mocked_st.query_params.get.return_value = ["abc"]
    with (
        patch("qa_core.app.get_all_analysis_history", return_value=[]),
        patch("qa_core.app.announce") as mock_announce,
    ):
        app.render_history_page()
    mock_announce.assert_called_with(
        "Ainda não há análises no histórico. Realize uma nova análise para começar.",
        "info",
        st_api=mocked_st,
    )


def test_render_history_sem_plano_exibe_aviso(mocked_st):
    mocked_st.query_params.get.return_value = ["1"]
    mocked_st.container.side_effect = lambda *args, **kwargs: _make_context()
    mocked_st.session_state.clear()

    with (
        patch(
            "qa_core.app.get_analysis_by_id",
            return_value={
                "created_at": "2025-10-01",
                "user_story": "História",
                "analysis_report": "Relatório",
            },
        ),
        patch("qa_core.app.get_all_analysis_history", return_value=[]),
        patch("qa_core.app.announce") as mock_announce,
    ):
        app.render_history_page()
    mock_announce.assert_any_call(
        "Nenhum plano de testes foi gerado para esta análise.",
        "info",
        st_api=mocked_st,
    )


def test_render_history_lista_formata_datas(mocked_st):
    mocked_st.query_params.get.return_value = None
    history = [
        {"id": 1, "created_at": "2025-10-01 10:00", "user_story": "Story 1"},
        {
            "id": 2,
            "created_at": datetime.datetime(2025, 10, 2, 11, 30),
            "user_story": "Story 2",
        },
        {"id": 3, "created_at": 123456, "user_story": "Story 3"},
    ]
    with patch("qa_core.app.get_all_analysis_history", return_value=history):
        app.render_history_page()
    mocked_st.markdown.assert_any_call("**🕒 Data:** 02/10/2025 11:30")
    mocked_st.markdown.assert_any_call("**🕒 Data:** 123456")


def test_render_history_analysis_entry_convertido_dict(mocked_st):
    mocked_st.query_params.get.return_value = ["5"]
    mocked_st.container.side_effect = lambda *args, **kwargs: _make_context()
    entry_as_list = [
        ("id", 5),
        ("created_at", datetime.datetime(2025, 10, 3, 14, 0)),
        ("user_story", "História convertida"),
        ("analysis_report", "Relatório detalhado"),
        ("test_plan_report", "Plano convertido"),
    ]

    with (
        patch("qa_core.app.get_analysis_by_id", return_value=entry_as_list),
        patch("qa_core.app.get_all_analysis_history", return_value=[]),
        patch("qa_core.app.accessible_button", return_value=False),
    ):
        app.render_history_page()

    mocked_st.markdown.assert_any_call("### Análise de 2025-10-03")


def test_render_history_selected_id_type_error(mocked_st):
    mocked_st.query_params.get.return_value = ["7"]
    mocked_st.container.side_effect = lambda *args, **kwargs: _make_context()

    with (
        patch("qa_core.app.get_analysis_by_id", side_effect=TypeError("boom")),
        patch("qa_core.app.get_all_analysis_history", return_value=[]),
        patch("qa_core.app.accessible_button", return_value=False),
        patch("qa_core.app.announce") as mock_announce,
    ):
        app.render_history_page()

    mock_announce.assert_any_call("Análise não encontrada.", "error", st_api=mocked_st)


def test_render_history_page_test_mode_com_plano():
    st_api = MagicMock()
    st_api.session_state = {}
    st_api.query_params = MagicMock(get=lambda key: ["1"])

    with patch(
        "qa_core.app.get_analysis_by_id",
        return_value={
            "created_at": "2025-10-02",
            "user_story": "US",
            "analysis_report": "Rel",
            "test_plan_report": "Plano",
        },
    ):
        app._render_history_page_test_mode(st_api)

    st_api.markdown.assert_any_call("### Análise de 2025-10-02")
    st_api.markdown.assert_any_call("Plano")


@patch("qa_core.app.announce")
@patch("qa_core.app.delete_analysis_by_id", return_value=True)
@patch("qa_core.app.get_all_analysis_history", return_value=[])
@patch("qa_core.app.st")
def test_render_history_page_impl_confirma_exclusao(
    mock_st, mock_get_history, mock_delete, mock_announce
):
    mock_st.session_state = {"confirm_delete_id": 5}
    mock_st.query_params.get.return_value = None
    mock_st.container.side_effect = lambda *args, **kwargs: _make_context()
    mock_st.expander.side_effect = lambda *args, **kwargs: _make_context()
    confirm_col, cancel_col = MagicMock(), MagicMock()

    def columns_side_effect(arg):
        if arg == TWO_COLUMN_COUNT:
            return (confirm_col, cancel_col)
        if isinstance(arg, int):
            return tuple(MagicMock() for _ in range(arg))
        return tuple(MagicMock() for _ in range(len(arg)))

    mock_st.columns.side_effect = columns_side_effect
    confirm_col.button.return_value = True
    cancel_col.button.return_value = False
    mock_st.rerun = MagicMock()

    app._render_history_page_impl()

    mock_delete.assert_called_once_with(5)
    assert "confirm_delete_id" not in mock_st.session_state
    mock_announce.assert_any_call(
        "Análise 5 removida com sucesso.", "success", st_api=mock_st
    )
    mock_st.rerun.assert_called_once()


@patch("qa_core.app.announce")
@patch("qa_core.app.delete_analysis_by_id", return_value=False)
@patch("qa_core.app.get_all_analysis_history", return_value=[])
@patch("qa_core.app.st")
def test_render_history_page_impl_cancela_exclusao(
    mock_st, mock_get_history, mock_delete, mock_announce
):
    mock_st.session_state = {"confirm_delete_id": 42}
    mock_st.query_params.get.return_value = None
    mock_st.container.side_effect = lambda *args, **kwargs: _make_context()
    mock_st.expander.side_effect = lambda *args, **kwargs: _make_context()
    confirm_col, cancel_col = MagicMock(), MagicMock()

    def columns_side_effect(arg):
        if arg == TWO_COLUMN_COUNT:
            return (confirm_col, cancel_col)
        if isinstance(arg, int):
            return tuple(MagicMock() for _ in range(arg))
        return tuple(MagicMock() for _ in range(len(arg)))

    mock_st.columns.side_effect = columns_side_effect
    confirm_col.button.return_value = False
    cancel_col.button.return_value = True
    mock_st.rerun = MagicMock()

    app._render_history_page_impl()

    mock_delete.assert_not_called()
    assert "confirm_delete_id" not in mock_st.session_state
    mock_announce.assert_any_call(
        "Nenhuma exclusão foi realizada.", "info", st_api=mock_st
    )
    mock_st.rerun.assert_called_once()


@patch("qa_core.app.announce")
@patch("qa_core.app.clear_history", return_value=3)
@patch("qa_core.app.get_all_analysis_history", return_value=[])
@patch("qa_core.app.st")
def test_render_history_page_impl_confirma_limpeza_total(
    mock_st, mock_get_history, mock_clear_history, mock_announce
):
    mock_st.session_state = {"confirm_clear_all": True}
    mock_st.query_params.get.return_value = None
    mock_st.container.side_effect = lambda *args, **kwargs: _make_context()
    mock_st.expander.side_effect = lambda *args, **kwargs: _make_context()
    confirm_col, cancel_col = MagicMock(), MagicMock()

    def columns_side_effect(arg):
        if arg == TWO_COLUMN_COUNT:
            return (confirm_col, cancel_col)
        if isinstance(arg, int):
            return tuple(MagicMock() for _ in range(arg))
        return tuple(MagicMock() for _ in range(len(arg)))

    mock_st.columns.side_effect = columns_side_effect
    confirm_col.button.return_value = True
    cancel_col.button.return_value = False
    mock_st.rerun = MagicMock()

    app._render_history_page_impl()

    mock_clear_history.assert_called_once()
    assert "confirm_clear_all" not in mock_st.session_state
    mock_announce.assert_any_call(
        "3 análises foram removidas.", "success", st_api=mock_st
    )
    mock_st.rerun.assert_called_once()


@patch("qa_core.app.accessible_button")
@patch("qa_core.app.get_all_analysis_history")
@patch("qa_core.app.st")
def test_render_history_page_impl_lista_dispara_confirm_clear_all(
    mock_st, mock_get_history, mock_accessible_button
):
    mock_st.session_state = {}
    mock_st.query_params.get.return_value = None
    mock_st.container.side_effect = lambda *args, **kwargs: _make_context()
    mock_st.expander.side_effect = lambda *args, **kwargs: _make_context()

    def columns_side_effect(arg):
        if isinstance(arg, int):
            return tuple(MagicMock() for _ in range(arg))
        if isinstance(arg, (list | tuple)):
            return tuple(MagicMock() for _ in arg)
        return (MagicMock(), MagicMock())

    mock_st.columns.side_effect = columns_side_effect

    mock_get_history.return_value = [
        {"id": 1, "created_at": "2024-01-01", "user_story": "Como usuário..."}
    ]

    def accessible_button_side_effect(*args, **kwargs):
        label = kwargs.get("label") or (args[0] if args else "")
        return label == "🗑️ Excluir TODO o Histórico"

    mock_accessible_button.side_effect = accessible_button_side_effect
    mock_st.rerun = MagicMock()

    app._render_history_page_impl()

    assert mock_st.session_state["confirm_clear_all"] is True
    mock_st.rerun.assert_called_once()
