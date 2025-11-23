from __future__ import annotations

from typing import Any

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

from ..config import LLMSettings
from .base import LLMClient, LLMError, LLMRateLimitError


class GoogleLLMClient(LLMClient):
    provider_name = "google"

    def __init__(
        self,
        *,
        model: str,
        api_key: str | None,
        default_config: dict[str, Any] | None = None,
    ) -> None:
        if not api_key:
            raise LLMError(
                "GOOGLE_API_KEY não configurada. Defina GOOGLE_API_KEY ou LLM_API_KEY para usar o provedor Google."
            )
        genai.configure(api_key=api_key)
        self._model_name = model
        self._default_config = default_config or {}

    @classmethod
    def from_settings(cls, settings: LLMSettings) -> "GoogleLLMClient":
        api_key = settings.api_key or settings.extra.get("google_api_key")
        return cls(model=settings.model, api_key=api_key, default_config=None)

    def generate_content(
        self,
        prompt: str,
        *,
        config: dict[str, Any] | None = None,
        trace_id: str | None = None,
        node: str | None = None,
    ) -> Any:
        del trace_id, node
        try:
            model = genai.GenerativeModel(
                self._model_name,
                generation_config=config,  # type: ignore
            )
            return model.generate_content(prompt)
        except (
            ResourceExhausted
        ) as exc:  # pragma: no cover - comportamento dependente da API
            raise LLMRateLimitError(str(exc)) from exc
        except Exception as exc:  # pragma: no cover - proteção genérica
            raise LLMError(str(exc)) from exc
