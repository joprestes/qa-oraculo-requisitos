from __future__ import annotations

from typing import Callable, Dict

from .config import LLMSettings
from .providers.base import LLMClient
from .providers.google import GoogleLLMClient

ProviderBuilder = Callable[[LLMSettings], LLMClient]

_PROVIDER_BUILDERS: Dict[str, ProviderBuilder] = {
    "google": GoogleLLMClient.from_settings,
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
