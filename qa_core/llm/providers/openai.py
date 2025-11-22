from __future__ import annotations

from typing import Any

from openai import OpenAI
from openai import RateLimitError as OpenAIRateLimitError

from ..config import LLMSettings
from .base import LLMClient, LLMError, LLMRateLimitError


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

        # Inicializar cliente OpenAI
        try:
            self._client = OpenAI(
                api_key=self._api_key,
                organization=self._extra.get("organization"),  # Opcional
            )
        except Exception as exc:
            raise LLMError(f"Erro ao inicializar OpenAI: {exc}") from exc

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
    ) -> Any:
        """Gera conteúdo usando OpenAI GPT.

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

            # Chamar API OpenAI
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                **generation_config,
            )

            # Extrair e retornar conteúdo
            return response.choices[0].message.content

        except OpenAIRateLimitError as exc:
            raise LLMRateLimitError(
                f"Limite de taxa atingido no OpenAI: {exc}"
            ) from exc
        except Exception as exc:
            raise LLMError(f"Erro ao chamar OpenAI: {exc}") from exc
