"""
Módulo de métricas para QA Oráculo.

Este módulo fornece métricas Prometheus para monitoramento da aplicação.
As métricas são opcionais e só funcionam se prometheus-client estiver instalado.
"""

import logging
from functools import wraps
from typing import Optional

logger = logging.getLogger(__name__)

# Imports condicionais para não quebrar se prometheus não estiver instalado
try:
    from prometheus_client import Counter, Gauge, Histogram, Info, start_http_server

    PROMETHEUS_AVAILABLE = True
except ImportError:
    logger.info(
        "prometheus-client não está instalado. Métricas desabilitadas. "
        "Para habilitar, instale: pip install -r requirements-observability.txt"
    )
    PROMETHEUS_AVAILABLE = False


def start_metrics_server(port: int = 8000):
    """Inicia servidor HTTP para expor métricas Prometheus.

    Args:
        port: Porta para expor as métricas (padrão: 8000).
    """
    if not PROMETHEUS_AVAILABLE:
        logger.warning("Prometheus não disponível, servidor de métricas não iniciado")
        return

    try:
        start_http_server(port)
        logger.info(f"Servidor de métricas iniciado na porta {port}")
    except Exception as e:
        # Se a porta já estiver em uso (ex: reload do Streamlit), apenas loga
        logger.warning(
            f"Não foi possível iniciar servidor de métricas na porta {port}: {e}"
        )


class MetricsCollector:
    """
    Coletor de métricas para QA Oráculo.

    Fornece métricas sobre:
    - Análises realizadas
    - Exportações
    - Chamadas LLM
    - Performance
    - Erros
    """

    def __init__(self, enabled: bool = True):
        """
        Inicializa o coletor de métricas.

        Args:
            enabled: Se False, métricas são no-ops (útil para testes)
        """
        self.enabled = enabled and PROMETHEUS_AVAILABLE

        if not self.enabled:
            logger.info("Métricas desabilitadas")
            return

        # === Contadores ===
        self.analyses_total = Counter(
            "qa_oraculo_analyses_total",
            "Total de análises de User Stories realizadas",
            ["status"],  # success, error
        )

        self.exports_total = Counter(
            "qa_oraculo_exports_total",
            "Total de exportações realizadas",
            ["format", "status"],  # format: markdown, pdf, csv, etc.
        )

        self.llm_calls_total = Counter(
            "qa_oraculo_llm_calls_total",
            "Total de chamadas ao LLM",
            ["provider", "status"],  # provider: google, openai, etc.
        )

        self.errors_total = Counter(
            "qa_oraculo_errors_total",
            "Total de erros ocorridos",
            ["error_type"],  # validation, llm, database, etc.
        )

        # === Histogramas (para latência) ===
        self.analysis_duration = Histogram(
            "qa_oraculo_analysis_duration_seconds",
            "Tempo de análise de User Story em segundos",
            buckets=[1, 2, 5, 10, 20, 30, 60, 120],
        )

        self.export_duration = Histogram(
            "qa_oraculo_export_duration_seconds",
            "Tempo de exportação em segundos",
            ["format"],
            buckets=[0.1, 0.5, 1, 2, 5, 10],
        )

        self.llm_call_duration = Histogram(
            "qa_oraculo_llm_call_duration_seconds",
            "Tempo de chamada ao LLM em segundos",
            ["provider"],
            buckets=[1, 2, 5, 10, 20, 30, 60],
        )

        # === Gauges (valores instantâneos) ===
        self.cache_size = Gauge(
            "qa_oraculo_cache_size",
            "Número de itens no cache de LLM",
        )

        self.active_analyses = Gauge(
            "qa_oraculo_active_analyses",
            "Número de análises em andamento",
        )

        # === Info (metadados) ===
        self.app_info = Info(
            "qa_oraculo_app",
            "Informações sobre a aplicação QA Oráculo",
        )

        logger.info("Métricas Prometheus inicializadas com sucesso")

    def record_analysis(self, status: str = "success"):
        """Registra uma análise realizada."""
        if self.enabled:
            self.analyses_total.labels(status=status).inc()

    def record_export(self, format: str, status: str = "success"):
        """Registra uma exportação realizada."""
        if self.enabled:
            self.exports_total.labels(format=format, status=status).inc()

    def record_llm_call(self, provider: str, status: str = "success"):
        """Registra uma chamada ao LLM."""
        if self.enabled:
            self.llm_calls_total.labels(provider=provider, status=status).inc()

    def record_error(self, error_type: str):
        """Registra um erro ocorrido."""
        if self.enabled:
            self.errors_total.labels(error_type=error_type).inc()

    def time_analysis(self):
        """Context manager para medir tempo de análise."""
        if self.enabled:
            return self.analysis_duration.time()
        else:
            return _NoOpContextManager()

    def time_export(self, format: str):
        """Context manager para medir tempo de exportação."""
        if self.enabled:
            return self.export_duration.labels(format=format).time()
        else:
            return _NoOpContextManager()

    def time_llm_call(self, provider: str):
        """Context manager para medir tempo de chamada LLM."""
        if self.enabled:
            return self.llm_call_duration.labels(provider=provider).time()
        else:
            return _NoOpContextManager()

    def set_cache_size(self, size: int):
        """Atualiza o tamanho do cache."""
        if self.enabled:
            self.cache_size.set(size)

    def inc_active_analyses(self):
        """Incrementa contador de análises ativas."""
        if self.enabled:
            self.active_analyses.inc()

    def dec_active_analyses(self):
        """Decrementa contador de análises ativas."""
        if self.enabled:
            self.active_analyses.dec()

    def set_app_info(self, version: str, python_version: str):
        """Define informações da aplicação."""
        if self.enabled:
            self.app_info.info({"version": version, "python_version": python_version})


class _NoOpContextManager:
    """Context manager que não faz nada (usado quando métricas estão desabilitadas)."""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


# Instância global do coletor de métricas
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """
    Retorna a instância global do coletor de métricas.

    Returns:
        MetricsCollector: Instância do coletor
    """
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def track_analysis(func):
    """
    Decorator para rastrear análises de User Stories.

    Registra métricas de contagem e duração.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        metrics = get_metrics_collector()
        metrics.inc_active_analyses()

        try:
            with metrics.time_analysis():
                result = func(*args, **kwargs)
            metrics.record_analysis(status="success")
            return result
        except Exception as e:
            metrics.record_analysis(status="error")
            metrics.record_error(error_type=type(e).__name__)
            raise
        finally:
            metrics.dec_active_analyses()

    return wrapper


def track_export(format: str):
    """
    Decorator para rastrear exportações.

    Args:
        format: Formato da exportação (markdown, pdf, csv, etc.)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()

            try:
                with metrics.time_export(format=format):
                    result = func(*args, **kwargs)
                metrics.record_export(format=format, status="success")
                return result
            except Exception as e:
                metrics.record_export(format=format, status="error")
                metrics.record_error(error_type=type(e).__name__)
                raise

        return wrapper

    return decorator


def track_llm_call(provider: str):
    """
    Decorator para rastrear chamadas ao LLM.

    Args:
        provider: Nome do provedor (google, openai, etc.)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metrics = get_metrics_collector()

            try:
                with metrics.time_llm_call(provider=provider):
                    result = func(*args, **kwargs)
                metrics.record_llm_call(provider=provider, status="success")
                return result
            except Exception as e:
                metrics.record_llm_call(provider=provider, status="error")
                metrics.record_error(error_type=type(e).__name__)
                raise

        return wrapper

    return decorator
