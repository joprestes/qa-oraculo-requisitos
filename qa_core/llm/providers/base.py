from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


class LLMError(Exception):
    """Erro genérico ao interagir com um provedor LLM."""


class LLMRateLimitError(LLMError):
    """Erro lançado quando o provedor sinaliza limite de requisições."""


@runtime_checkable
class LLMClient(Protocol):
    """Contrato mínimo para um cliente LLM."""

    provider_name: str

    def generate_content(
        self,
        prompt: str,
        *,
        config: dict[str, Any] | None = None,
        trace_id: str | None = None,
        node: str | None = None,
    ) -> Any:
        """Gera conteúdo a partir do prompt fornecido."""
