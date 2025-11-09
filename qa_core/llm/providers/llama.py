from __future__ import annotations

from typing import Any

from ..config import LLMSettings
from .base import LLMClient, LLMError


class LlamaLLMClient(LLMClient):
    provider_name = "llama"

    def __init__(
        self, *, model: str, api_key: str | None, extra: dict[str, Any]
    ) -> None:
        self._model_name = model
        self._api_key = api_key
        self._extra = extra

        if not api_key:
            raise LLMError(
                "LLAMA_API_KEY não configurada. Defina LLAMA_API_KEY ou LLM_API_KEY para usar os modelos LLaMA."
            )

        raise LLMError(
            "Integração com LLaMA (Meta) ainda não está disponível. Consulte LLM_CONFIG_GUIDE.md para acompanhar o roadmap."
        )

    @classmethod
    def from_settings(cls, settings: LLMSettings) -> "LlamaLLMClient":
        return cls(model=settings.model, api_key=settings.api_key, extra=settings.extra)

    def generate_content(
        self,
        prompt: str,
        *,
        config: dict[str, Any] | None = None,
        trace_id: str | None = None,
        node: str | None = None,
    ) -> Any:  # pragma: no cover - instâncias reais não são criadas
        raise LLMError("LLaMA ainda não suportado nesta versão.")
