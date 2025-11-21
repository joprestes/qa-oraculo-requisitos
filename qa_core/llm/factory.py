from __future__ import annotations

from typing import Any, Callable, Dict

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
    """Wrapper simples para cache em memória de chamadas LLM."""

    def __init__(self, client: LLMClient, max_size: int = 100):
        self._client = client
        self._cache: Dict[tuple, Any] = {}
        self._max_size = max_size

    @property
    def provider_name(self) -> str:
        return self._client.provider_name

    def generate_content(
        self,
        prompt: str,
        *,
        config: Dict[str, Any] | None = None,
        trace_id: str | None = None,
        node: str | None = None,
    ) -> Any:
        # Cria uma chave de cache baseada no prompt e config
        # Convertemos config para tupla de itens ordenados para ser hashable
        config_key = (
            tuple(sorted(config.items())) if config else None
        )
        cache_key = (prompt, config_key)

        if cache_key in self._cache:
            return self._cache[cache_key]

        result = self._client.generate_content(
            prompt, config=config, trace_id=trace_id, node=node
        )

        # Estratégia simples de limpeza: se encher, limpa tudo
        if len(self._cache) >= self._max_size:
            self._cache.clear()

        self._cache[cache_key] = result
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

