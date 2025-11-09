from unittest.mock import patch

from qa_core import app


def test_run_analysis_graph():
    with patch("qa_core.app.grafo_analise") as mock_grafo:
        mock_grafo.invoke.return_value = {"ok": True}
        result = app.run_analysis_graph("US Teste")

        assert result == {"ok": True}
        mock_grafo.invoke.assert_called_once()
        args, _ = mock_grafo.invoke.call_args
        assert args[0]["user_story"] == "US Teste"
        assert "trace_id" in args[0]


def test_run_test_plan_graph():
    with patch("qa_core.app.grafo_plano_testes") as mock_grafo:
        mock_grafo.invoke.return_value = {"plano": True}
        result = app.run_test_plan_graph({"analise": "x"})

        assert result == {"plano": True}
        mock_grafo.invoke.assert_called_once()
        args, _ = mock_grafo.invoke.call_args
        assert args[0]["analise"] == "x"
        assert "trace_id" in args[0]
