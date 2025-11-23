"""
Testes para o módulo de métricas.
"""

import pytest
from unittest.mock import patch
from qa_core.metrics import (
    MetricsCollector,
    get_metrics_collector,
    track_analysis,
    track_export,
    track_llm_call,
)


class TestMetricsCollector:
    """Testes para MetricsCollector."""

    def test_metrics_disabled_when_prometheus_not_available(self):
        """Testa que métricas são desabilitadas se Prometheus não estiver disponível."""
        with patch("qa_core.metrics.PROMETHEUS_AVAILABLE", False):
            collector = MetricsCollector()
            assert collector.enabled is False

    def test_metrics_can_be_explicitly_disabled(self):
        """Testa que métricas podem ser explicitamente desabilitadas."""
        collector = MetricsCollector(enabled=False)
        assert collector.enabled is False

    @patch("qa_core.metrics.PROMETHEUS_AVAILABLE", True)
    @patch("qa_core.metrics.Counter")
    @patch("qa_core.metrics.Histogram")
    @patch("qa_core.metrics.Gauge")
    def test_metrics_initialization(self, mock_gauge, mock_histogram, mock_counter):
        """Testa inicialização de métricas quando Prometheus está disponível."""
        collector = MetricsCollector(enabled=True)
        assert collector.enabled is True

        # Verifica que métricas foram criadas
        assert mock_counter.call_count >= 4  # analyses, exports, llm_calls, errors
        assert mock_histogram.call_count >= 3  # analysis, export, llm durations
        assert mock_gauge.call_count >= 2  # cache_size, active_analyses

    def test_record_analysis_when_disabled(self):
        """Testa que record_analysis não falha quando desabilitado."""
        collector = MetricsCollector(enabled=False)
        collector.record_analysis(status="success")  # Não deve lançar exceção

    def test_record_export_when_disabled(self):
        """Testa que record_export não falha quando desabilitado."""
        collector = MetricsCollector(enabled=False)
        collector.record_export(format="markdown", status="success")

    def test_record_llm_call_when_disabled(self):
        """Testa que record_llm_call não falha quando desabilitado."""
        collector = MetricsCollector(enabled=False)
        collector.record_llm_call(provider="google", status="success")

    def test_record_error_when_disabled(self):
        """Testa que record_error não falha quando desabilitado."""
        collector = MetricsCollector(enabled=False)
        collector.record_error(error_type="ValidationError")

    def test_context_managers_when_disabled(self):
        """Testa que context managers funcionam quando desabilitados."""
        collector = MetricsCollector(enabled=False)

        with collector.time_analysis():
            pass

        with collector.time_export(format="pdf"):
            pass

        with collector.time_llm_call(provider="openai"):
            pass

    def test_set_cache_size_when_disabled(self):
        """Testa que set_cache_size não falha quando desabilitado."""
        collector = MetricsCollector(enabled=False)
        collector.set_cache_size(10)

    def test_inc_dec_active_analyses_when_disabled(self):
        """Testa que inc/dec active_analyses não falham quando desabilitados."""
        collector = MetricsCollector(enabled=False)
        collector.inc_active_analyses()
        collector.dec_active_analyses()


class TestDecorators:
    """Testes para decorators de métricas."""

    def test_track_analysis_decorator_success(self):
        """Testa decorator track_analysis em caso de sucesso."""

        @track_analysis
        def dummy_analysis():
            return "resultado"

        result = dummy_analysis()
        assert result == "resultado"

    def test_track_analysis_decorator_error(self):
        """Testa decorator track_analysis em caso de erro."""

        @track_analysis
        def failing_analysis():
            raise ValueError("Erro de teste")

        with pytest.raises(ValueError, match="Erro de teste"):
            failing_analysis()

    def test_track_export_decorator_success(self):
        """Testa decorator track_export em caso de sucesso."""

        @track_export(format="markdown")
        def dummy_export():
            return "conteúdo exportado"

        result = dummy_export()
        assert result == "conteúdo exportado"

    def test_track_export_decorator_error(self):
        """Testa decorator track_export em caso de erro."""

        @track_export(format="pdf")
        def failing_export():
            raise IOError("Erro de I/O")

        with pytest.raises(IOError, match="Erro de I/O"):
            failing_export()

    def test_track_llm_call_decorator_success(self):
        """Testa decorator track_llm_call em caso de sucesso."""

        @track_llm_call(provider="google")
        def dummy_llm_call():
            return "resposta do LLM"

        result = dummy_llm_call()
        assert result == "resposta do LLM"

    def test_track_llm_call_decorator_error(self):
        """Testa decorator track_llm_call em caso de erro."""

        @track_llm_call(provider="openai")
        def failing_llm_call():
            raise ConnectionError("Erro de conexão")

        with pytest.raises(ConnectionError, match="Erro de conexão"):
            failing_llm_call()


class TestGlobalCollector:
    """Testes para coletor global de métricas."""

    def test_get_metrics_collector_returns_singleton(self):
        """Testa que get_metrics_collector retorna sempre a mesma instância."""
        collector1 = get_metrics_collector()
        collector2 = get_metrics_collector()
        assert collector1 is collector2
