from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class SessionState(dict):
    """Simula o st.session_state com suporte a dot notation."""

    def __getattr__(self, key):
        return self.get(key, None)

    def __setattr__(self, key, value):
        self[key] = value


def _make_context_manager():
    """Cria um mock com protocolo de context manager."""
    context = MagicMock()
    context.__enter__.return_value = MagicMock()
    context.__exit__.return_value = False
    return context


def _columns_factory(arg, default_columns=2):
    """Gera mocks para st.columns respeitando o argumento recebido."""
    if isinstance(arg, int):
        count = max(arg, 1)
        return tuple(MagicMock() for _ in range(count))

    if isinstance(arg, (list, tuple)):
        return tuple(MagicMock() for _ in arg)

    return tuple(MagicMock() for _ in range(default_columns))


def _create_columns_mock():
    columns_mock = MagicMock(side_effect=_columns_factory)
    columns_mock._factory = _columns_factory  # tipo: ignore[attr-defined]
    return columns_mock


def _apply_common_streamlit_mocks(mock_st):
    """Configura retornos e atributos comuns usados pelos testes."""
    mock_st.button = MagicMock(return_value=False)
    mock_st.columns = _create_columns_mock()
    mock_st.container.side_effect = lambda *args, **kwargs: _make_context_manager()
    mock_st.expander.side_effect = lambda *args, **kwargs: _make_context_manager()
    mock_st.form.side_effect = lambda *args, **kwargs: _make_context_manager()
    mock_st.spinner.side_effect = lambda *args, **kwargs: _make_context_manager()
    mock_st.sidebar = MagicMock()
    mock_st.sidebar.radio = MagicMock(return_value="Analisar User Story")
    mock_st.sidebar.button = MagicMock(return_value=False)
    mock_st.sidebar.checkbox = MagicMock(return_value=False)
    mock_st.query_params = MagicMock()
    mock_st.query_params.get.return_value = [None]
    mock_st.toast = MagicMock()
    mock_st.rerun = MagicMock()
    mock_st.experimental_rerun = MagicMock()

    mocked_attrs = [
        "checkbox",
        "code",
        "dataframe",
        "download_button",
        "error",
        "form_submit_button",
        "info",
        "markdown",
        "radio",
        "selectbox",
        "subheader",
        "success",
        "text_area",
        "warning",
    ]

    for attr in mocked_attrs:
        setattr(mock_st, attr, MagicMock())

    return mock_st


@pytest.fixture
def mocked_st():
    """Fixture compatível com testes legados que esperam um mock simples do streamlit."""
    with patch("qa_core.app.st") as mock_st:
        mock_st.session_state = {}
        _apply_common_streamlit_mocks(mock_st)
        yield mock_st


@pytest.fixture
def mock_streamlit_session():
    """Fixture voltada para fluxos complexos que usam SessionState customizado."""
    with patch("qa_core.app.st") as mock_st:
        mock_st.session_state = SessionState()

        def columns_side_effect(arg):
            base_factory = getattr(mock_st.columns, "_factory", _columns_factory)
            if arg == [1, 1, 2]:
                return [MagicMock(), MagicMock(), MagicMock()]
            if arg == 4:
                return [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
            if arg == 2:
                return [MagicMock(), MagicMock()]
            return list(base_factory(arg))

        _apply_common_streamlit_mocks(mock_st)
        mock_st.columns.side_effect = columns_side_effect  # type: ignore[attr-defined]
        yield mock_st


@pytest.fixture
def context_manager_factory():
    """Disponibiliza factory para context managers mockados em testes específicos."""
    return _make_context_manager
