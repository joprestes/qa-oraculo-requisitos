from __future__ import annotations

from typing import Any

from openai import AzureOpenAI
from openai import RateLimitError as OpenAIRateLimitError

from ..config import LLMSettings
from .base import LLMClient, LLMError, LLMRateLimitError


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

        # Inicializar cliente Azure OpenAI
        try:
            self._client = AzureOpenAI(
                api_key=self._api_key,
                api_version=self._extra["api_version"],
                azure_endpoint=self._extra["endpoint"],
            )
        except Exception as exc:
            raise LLMError(f"Erro ao inicializar Azure OpenAI: {exc}") from exc

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
    ) -> Any:
        """Gera conteúdo usando Azure OpenAI.

        Args:
            prompt: Prompt para geração
            config: Configurações opcionais (temperature, max_tokens, etc.)
            trace_id: ID de rastreamento (não usado)
            node: Nome do nó (não usado)

        Returns:
            Conteúdo gerado como string

        Raises:
            LLMRateLimitError: Se atingir limite de taxa
            LLMError: Para outros erros
        """
        del trace_id, node  # Não utilizados nesta implementação

        try:
            # Preparar configurações
            generation_config = config or {}

            # Criar mensagens no formato esperado pela API
            messages = [{"role": "user", "content": prompt}]

            # Chamar API Azure OpenAI
            response = self._client.chat.completions.create(
                model=self._extra["deployment"],
                messages=messages,
                **generation_config,
            )

            # Extrair e retornar conteúdo
            return response.choices[0].message.content

        except OpenAIRateLimitError as exc:
            raise LLMRateLimitError(
                f"Limite de taxa atingido no Azure OpenAI: {exc}"
            ) from exc
        except Exception as exc:
            raise LLMError(f"Erro ao chamar Azure OpenAI: {exc}") from exc
