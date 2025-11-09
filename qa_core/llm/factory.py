from __future__ import annotations

from typing import Callable, Dict

from .config import LLMSettings
from .providers.base import LLMClient
from .providers.azure_openai import AzureOpenAILLMClient
from .providers.google import GoogleLLMClient
from .providers.llama import LlamaLLMClient
from .providers.openai import OpenAILLMClient

ProviderBuilder = Callable[[LLMSettings], LLMClient]

_PROVIDER_BUILDERS: Dict[str, ProviderBuilder] = {
    "google": GoogleLLMClient.from_settings,
    "azure": AzureOpenAILLMClient.from_settings,
    "azure_openai": AzureOpenAILLMClient.from_settings,
    "openai": OpenAILLMClient.from_settings,
    "gpt": OpenAILLMClient.from_settings,
    "llama": LlamaLLMClient.from_settings,
}


def get_llm_client(settings: LLMSettings) -> LLMClient:
    provider_key = settings.provider.lower()
    try:
        builder = _PROVIDER_BUILDERS[provider_key]
    except (
        KeyError
    ) as exc:  # pragma: no cover - proteção contra provedores desconhecidos
        raise ValueError(f"LLM provider '{settings.provider}' não suportado.") from exc
    return builder(settings)
