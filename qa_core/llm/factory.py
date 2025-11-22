from __future__ import annotations

import time
from typing import Any, Callable, Dict, Tuple

from .config import LLMSettings
from .providers.base import LLMClient
from .providers.azure_openai import AzureOpenAILLMClient
from .providers.google import GoogleLLMClient
from .providers.llama import LlamaLLMClient
from .providers.mock import MockLLMClient
from .providers.openai import OpenAILLMClient

ProviderBuilder = Callable[[LLMSettings], LLMClient]

_PROVIDER_BUILDERS: Dict[str, ProviderBuilder] = {
    "google": GoogleLLMClient.from_settings,
    "azure": AzureOpenAILLMClient.from_settings,
    "azure_openai": AzureOpenAILLMClient.from_settings,
    "openai": OpenAILLMClient.from_settings,
    "gpt": OpenAILLMClient.from_settings,
    "llama": LlamaLLMClient.from_settings,
    "mock": MockLLMClient.from_settings,
}


class CachedLLMClient:
    """Wrapper para cache em memória de chamadas LLM com suporte a TTL opcional.

    O cache armazena resultados de chamadas LLM para evitar requisições duplicadas.
    Suporta TTL (Time To Live) configurável para expiração automática de entradas.

    Args:
        client: Cliente LLM base a ser cacheado.
        max_size: Tamanho máximo do cache antes de limpeza (padrão: 100).
        ttl_seconds: Tempo de vida em segundos para entradas do cache.
            Se None, as entradas não expiram (padrão: None).
    """

    def __init__(
        self,
        client: LLMClient,
        max_size: int = 100,
        ttl_seconds: int | None = None,
    ):
        self._client = client
        # Cache armazena (valor, timestamp) para suporte a TTL
        self._cache: Dict[Tuple[str, Tuple | None], Tuple[Any, float]] = {}
        self._max_size = max_size
        self._ttl_seconds = ttl_seconds

    @property
    def provider_name(self) -> str:
        return self._client.provider_name

    def _cleanup_expired(self) -> None:
        """Remove entradas expiradas do cache baseado no TTL."""
        if self._ttl_seconds is None:
            return  # Cache sem TTL não precisa limpeza por expiração

        now = time.time()
        expired_keys = [
            key
            for key, (_, timestamp) in self._cache.items()
            if now - timestamp > self._ttl_seconds
        ]

        for key in expired_keys:
            del self._cache[key]

    def _cleanup_full_cache(self) -> None:
        """Limpa o cache quando atinge o tamanho máximo."""
        if len(self._cache) >= self._max_size:
            # Se TTL está configurado, remove apenas entradas expiradas primeiro
            if self._ttl_seconds is not None:
                self._cleanup_expired()
                # Se ainda estiver cheio após limpar expirados, limpa tudo
                if len(self._cache) >= self._max_size:
                    self._cache.clear()
            else:
                # Sem TTL, simplesmente limpa tudo quando encher
                self._cache.clear()

    def generate_content(
        self,
        prompt: str,
        *,
        config: Dict[str, Any] | None = None,
        trace_id: str | None = None,
        node: str | None = None,
    ) -> Any:
        """Gera conteúdo usando o cliente LLM com cache.

        Se o resultado já estiver em cache e não expirado (se TTL configurado),
        retorna o valor cacheado. Caso contrário, faz a chamada ao cliente e armazena
        o resultado no cache.

        Args:
            prompt: Prompt a ser enviado ao LLM.
            config: Configurações opcionais para a geração.
            trace_id: ID de rastreamento opcional.
            node: Nome do nó opcional para rastreamento.

        Returns:
            Resposta do LLM (cacheada ou nova).
        """
        # Cria uma chave de cache baseada no prompt e config
        # Convertemos config para tupla de itens ordenados para ser hashable
        config_key = tuple(sorted(config.items())) if config else None
        cache_key = (prompt, config_key)

        # Limpa entradas expiradas se TTL configurado
        if self._ttl_seconds is not None:
            self._cleanup_expired()

        # Verifica se existe no cache e não está expirado
        if cache_key in self._cache:
            cached_value, timestamp = self._cache[cache_key]

            # Verifica expiração
            if (
                self._ttl_seconds is None
                or (time.time() - timestamp) <= self._ttl_seconds
            ):
                return cached_value
            else:
                # Entrada expirada, remove do cache
                del self._cache[cache_key]

        # Cache miss ou entrada expirada - faz chamada real
        result = self._client.generate_content(
            prompt, config=config, trace_id=trace_id, node=node
        )

        # Limpa cache se necessário antes de adicionar novo item
        self._cleanup_full_cache()

        # Armazena no cache com timestamp atual
        self._cache[cache_key] = (result, time.time())
        return result


def get_llm_client(settings: LLMSettings) -> LLMClient:
    """
    Retorna uma instância de cliente LLM configurada com base nas configurações fornecidas.

    Esta função atua como uma Factory, instanciando o cliente correto (Google, OpenAI, Azure, etc.)
    com base no campo `provider` das configurações.

    Args:
        settings: Objeto LLMSettings contendo provedor, modelo e chaves de API.

    Returns:
        Uma instância que implementa o protocolo LLMClient (envolta em cache).

    Raises:
        ValueError: Se o provedor especificado nas configurações não for suportado.
    """
    provider_key = settings.provider.lower()
    try:
        builder = _PROVIDER_BUILDERS[provider_key]
    except (
        KeyError
    ) as exc:  # pragma: no cover - proteção contra provedores desconhecidos
        raise ValueError(f"LLM provider '{settings.provider}' não suportado.") from exc

    client = builder(settings)
    return CachedLLMClient(client)
