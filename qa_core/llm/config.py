from __future__ import annotations

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator

from ..config import NOME_MODELO

load_dotenv()

DEFAULT_PROVIDER = "google"


class LLMSettings(BaseModel):
    """Representa a configuração para um cliente LLM com validação."""

    provider: str = Field(default=DEFAULT_PROVIDER)
    model: str = Field(default=NOME_MODELO)
    api_key: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_api_key(self) -> "LLMSettings":
        provider = self.provider.lower()
        api_key = self.api_key

        # Se for mock, não precisa de chave
        if provider == "mock":
            return self

        # Verifica chaves específicas no extra se a principal não estiver definida
        if not api_key:
            if provider == "google":
                api_key = self.extra.get("google_api_key")
            elif provider in {"openai", "gpt"}:
                api_key = self.extra.get("openai_api_key")  # Ajustado para consistência
            elif provider == "llama":
                api_key = self.extra.get("llama_api_key")

        if not api_key:
            raise ValueError(
                f"API Key is required for provider '{provider}'. Please set LLM_API_KEY or provider-specific key (e.g., GOOGLE_API_KEY)."
            )

        return self

    @classmethod
    def from_env(cls) -> "LLMSettings":
        provider = os.getenv("LLM_PROVIDER", DEFAULT_PROVIDER).strip().lower()
        model = os.getenv("LLM_MODEL", NOME_MODELO).strip()

        # Chave padrão compartilhada entre provedores
        api_key = os.getenv("LLM_API_KEY")

        extra: Dict[str, Any] = {}

        if provider == "google":
            google_api_key = os.getenv("GOOGLE_API_KEY")
            if google_api_key:
                extra["google_api_key"] = google_api_key
            # Se api_key genérica não existe, tenta usar a específica como principal
            if not api_key and google_api_key:
                api_key = google_api_key

        elif provider in {"openai", "gpt"}:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                extra["openai_api_key"] = openai_key

            if not api_key and openai_key:
                api_key = openai_key

            base_url = os.getenv("OPENAI_BASE_URL")
            organization = os.getenv("OPENAI_ORGANIZATION")
            if base_url:
                extra["base_url"] = base_url
            if organization:
                extra["organization"] = organization

        elif provider == "llama":
            llama_key = os.getenv("LLAMA_API_KEY")
            if llama_key:
                extra["llama_api_key"] = llama_key

            if not api_key and llama_key:
                api_key = llama_key

            endpoint = os.getenv("LLAMA_ENDPOINT")
            project_id = os.getenv("LLAMA_PROJECT_ID")
            if endpoint:
                extra["endpoint"] = endpoint
            if project_id:
                extra["project_id"] = project_id

        # Garante que não devolvemos strings vazias
        api_key = api_key or None

        return cls(provider=provider, model=model, api_key=api_key, extra=extra)
