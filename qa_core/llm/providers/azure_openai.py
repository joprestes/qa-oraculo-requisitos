from __future__ import annotations

from typing import Any

from ..config import LLMSettings
from .base import LLMClient, LLMError


class AzureOpenAILLMClient(LLMClient):
    provider_name = "azure"

    REQUIRED_EXTRA_FIELDS = {
        "endpoint": "AZURE_OPENAI_ENDPOINT",
        "deployment": "AZURE_OPENAI_DEPLOYMENT",
        "api_version": "AZURE_OPENAI_API_VERSION",
    }

    def __init__(
        self, *, model: str, api_key: str | None, extra: dict[str, Any]
    ) -> None:
        self._model_name = model
        self._api_key = api_key
        self._extra = extra

        missing: list[str] = []
        if not api_key:
            missing.append("AZURE_OPENAI_API_KEY")

        for field, env_name in self.REQUIRED_EXTRA_FIELDS.items():
            if not extra.get(field):
                missing.append(env_name)

        if missing:
            raise LLMError(
                "Azure OpenAI requer variáveis adicionais. Falta(m): "
                + ", ".join(sorted(missing))
            )

        raise LLMError(
            "Integração com Azure OpenAI ainda não está disponível nesta versão. Confira docs/LLM_CONFIG_GUIDE.md para atualizações."
        )

    @classmethod
    def from_settings(cls, settings: LLMSettings) -> "AzureOpenAILLMClient":
        return cls(model=settings.model, api_key=settings.api_key, extra=settings.extra)

    def generate_content(
        self,
        prompt: str,
        *,
        config: dict[str, Any] | None = None,
        trace_id: str | None = None,
        node: str | None = None,
    ) -> Any:  # pragma: no cover - instâncias reais não são criadas
        raise LLMError("Azure OpenAI ainda não suportado nesta versão.")
