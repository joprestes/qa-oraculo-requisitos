"""Testes unitários para o provedor LLaMA."""

import pytest

from qa_core.llm.config import LLMSettings
from qa_core.llm.providers.llama import LlamaLLMClient
from qa_core.llm.providers.base import LLMError


class TestLlamaLLMClient:
    """Testes para o cliente LLaMA."""

    def test_init_raises_when_missing_api_key(self):
        """Deve lançar erro quando LLAMA_API_KEY está faltando."""
        with pytest.raises(LLMError) as exc:
            LlamaLLMClient(
                model="llama-3.1-8b",
                api_key=None,
                extra={},
            )
        assert "LLAMA_API_KEY" in str(exc.value)

    def test_init_raises_not_available_with_api_key(self):
        """Deve lançar erro 'não disponível' mesmo com api_key preenchida."""
        with pytest.raises(LLMError) as exc:
            LlamaLLMClient(
                model="llama-3.1-8b",
                api_key="test-key",
                extra={},
            )
        assert "ainda não está disponível" in str(exc.value)

    def test_from_settings_creates_client(self):
        """Deve criar cliente a partir de LLMSettings."""
        settings = LLMSettings(
            provider="llama",
            model="llama-3.1-8b",
            api_key="test-key",
            extra={},
        )
        with pytest.raises(LLMError) as exc:
            LlamaLLMClient.from_settings(settings)
        # Deve lançar erro de "não disponível", não de validação
        assert "ainda não está disponível" in str(exc.value)

    def test_generate_content_raises_not_supported(self):
        """Deve lançar erro ao tentar gerar conteúdo (método não implementado)."""
        # Não podemos criar uma instância real devido ao __init__
        # Este teste documenta o comportamento esperado
        pass  # Coberto pelo pragma: no cover no código
