from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict

from dotenv import load_dotenv

from ..config import NOME_MODELO

load_dotenv()

DEFAULT_PROVIDER = "google"


@dataclass(frozen=True)
class LLMSettings:
    """Representa a configuração para um cliente LLM."""

    provider: str = DEFAULT_PROVIDER
    model: str = NOME_MODELO
    api_key: str | None = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "LLMSettings":
        provider = os.getenv("LLM_PROVIDER", DEFAULT_PROVIDER).strip().lower()
        model = os.getenv("LLM_MODEL", NOME_MODELO).strip()

        # Chave padrão compartilhada entre provedores
        api_key = os.getenv("LLM_API_KEY")

        extra: Dict[str, Any] = {}

        if provider == "google":
            google_api_key = os.getenv("GOOGLE_API_KEY")
            api_key = api_key or google_api_key
            if google_api_key:
                extra["google_api_key"] = google_api_key

        # Garante que não devolvemos strings vazias
        api_key = api_key or None

        return cls(provider=provider, model=model, api_key=api_key, extra=extra)
