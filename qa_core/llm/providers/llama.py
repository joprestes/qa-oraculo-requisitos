from __future__ import annotations

from typing import Any

import ollama

from ..config import LLMSettings
from .base import LLMClient, LLMError


class LlamaLLMClient(LLMClient):
    provider_name = "llama"

    def __init__(
        self, *, model: str, api_key: str | None, extra: dict[str, Any]
    ) -> None:
        self._model_name = model
        self._api_key = api_key  # Não usado com Ollama
        self._extra = extra

        # Ollama não requer API key, mas vamos validar se está instalado
        try:
            # Tentar listar modelos para verificar se Ollama está rodando
            ollama.list()
        except Exception as exc:
            raise LLMError(
                f"Ollama não está acessível. Certifique-se de que o Ollama está instalado e rodando. "
                f"Visite https://ollama.ai para instruções de instalação. Erro: {exc}"
            ) from exc

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
    ) -> Any:
        """Gera conteúdo usando LLaMA via Ollama.

        Args:
            prompt: Prompt para geração
            config: Configurações opcionais (temperature, num_predict, etc.)
            trace_id: ID de rastreamento (não usado)
            node: Nome do nó (não usado)

        Returns:
            Conteúdo gerado como string

        Raises:
            LLMError: Para erros de geração
        """
        del trace_id, node  # Não utilizados nesta implementação

        try:
            # Preparar configurações (Ollama usa 'options' para parâmetros)
            options = config or {}

            # Chamar Ollama
            response = ollama.generate(
                model=self._model_name,
                prompt=prompt,
                options=options,
            )

            # Extrair e retornar conteúdo
            return response.get("response", "")

        except Exception as exc:
            raise LLMError(
                f"Erro ao chamar Ollama (LLaMA): {exc}. "
                f"Verifique se o modelo '{self._model_name}' está instalado. "
                f"Use 'ollama pull {self._model_name}' para baixá-lo."
            ) from exc
