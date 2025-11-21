from __future__ import annotations

from typing import Callable, Dict

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


def get_llm_client(settings: LLMSettings) -> LLMClient:
    """
    Retorna uma instância de cliente LLM configurada com base nas configurações fornecidas.

    Esta função atua como uma Factory, instanciando o cliente correto (Google, OpenAI, Azure, etc.)
    com base no campo `provider` das configurações.

    Args:
        settings: Objeto LLMSettings contendo provedor, modelo e chaves de API.

    Returns:
        Uma instância que implementa o protocolo LLMClient.

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
    return builder(settings)
