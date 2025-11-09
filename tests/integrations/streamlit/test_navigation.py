from unittest.mock import patch

from qa_core import app


@patch("qa_core.app.render_main_analysis_page")
@patch("qa_core.app.render_history_page")
@patch("qa_core.app.st")
def test_main_troca_paginas(mock_st, mock_history, mock_main):
    mock_st.sidebar.radio.return_value = "Analisar User Story"
    app.main()
    mock_main.assert_called()

    mock_st.sidebar.radio.return_value = "Histórico de Análises"
    app.main()
    mock_history.assert_called()
