from __future__ import annotations

from typing import Any

from ..config import LLMSettings
from .base import LLMClient, LLMError


class OpenAILLMClient(LLMClient):
    provider_name = "openai"

    def __init__(
        self, *, model: str, api_key: str | None, extra: dict[str, Any]
    ) -> None:
        self._model_name = model
        self._api_key = api_key
        self._extra = extra

        if not api_key:
            raise LLMError(
                "OPENAI_API_KEY não configurada. Defina OPENAI_API_KEY ou LLM_API_KEY para usar OpenAI."
            )

        raise LLMError(
            "Integração com OpenAI GPT ainda não está disponível nesta versão. Confira docs/LLM_CONFIG_GUIDE.md para atualizações."
        )

    @classmethod
    def from_settings(cls, settings: LLMSettings) -> "OpenAILLMClient":
        return cls(model=settings.model, api_key=settings.api_key, extra=settings.extra)

    def generate_content(
        self,
        prompt: str,
        *,
        config: dict[str, Any] | None = None,
        trace_id: str | None = None,
        node: str | None = None,
    ) -> Any:  # pragma: no cover - instâncias reais não são criadas
        raise LLMError("OpenAI GPT ainda não suportado nesta versão.")
