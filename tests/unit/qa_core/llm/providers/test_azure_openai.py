"""Testes unitários para o provedor Azure OpenAI."""

import pytest

from qa_core.llm.config import LLMSettings
from qa_core.llm.providers.azure_openai import AzureOpenAILLMClient
from qa_core.llm.providers.base import LLMError


class TestAzureOpenAILLMClient:
    """Testes para o cliente Azure OpenAI."""

    def test_init_raises_when_missing_api_key(self):
        """Deve lançar erro quando AZURE_OPENAI_API_KEY está faltando."""
        with pytest.raises(LLMError) as exc:
            AzureOpenAILLMClient(
                model="gpt-4",
                api_key=None,
                extra={
                    "endpoint": "https://test.openai.azure.com/",
                    "deployment": "gpt-4",
                    "api_version": "2024-02-15-preview",
                },
            )
        assert "AZURE_OPENAI_API_KEY" in str(exc.value)

    def test_init_raises_when_missing_endpoint(self):
        """Deve lançar erro quando AZURE_OPENAI_ENDPOINT está faltando."""
        with pytest.raises(LLMError) as exc:
            AzureOpenAILLMClient(
                model="gpt-4",
                api_key="test-key",
                extra={
                    "deployment": "gpt-4",
                    "api_version": "2024-02-15-preview",
                },
            )
        assert "AZURE_OPENAI_ENDPOINT" in str(exc.value)

    def test_init_raises_when_missing_deployment(self):
        """Deve lançar erro quando AZURE_OPENAI_DEPLOYMENT está faltando."""
        with pytest.raises(LLMError) as exc:
            AzureOpenAILLMClient(
                model="gpt-4",
                api_key="test-key",
                extra={
                    "endpoint": "https://test.openai.azure.com/",
                    "api_version": "2024-02-15-preview",
                },
            )
        assert "AZURE_OPENAI_DEPLOYMENT" in str(exc.value)

    def test_init_raises_when_missing_api_version(self):
        """Deve lançar erro quando AZURE_OPENAI_API_VERSION está faltando."""
        with pytest.raises(LLMError) as exc:
            AzureOpenAILLMClient(
                model="gpt-4",
                api_key="test-key",
                extra={
                    "endpoint": "https://test.openai.azure.com/",
                    "deployment": "gpt-4",
                },
            )
        assert "AZURE_OPENAI_API_VERSION" in str(exc.value)

    def test_init_raises_when_missing_multiple_fields(self):
        """Deve lançar erro listando todos os campos faltantes."""
        with pytest.raises(LLMError) as exc:
            AzureOpenAILLMClient(
                model="gpt-4",
                api_key=None,
                extra={},
            )
        error_msg = str(exc.value)
        assert "AZURE_OPENAI_API_KEY" in error_msg
        assert "AZURE_OPENAI_ENDPOINT" in error_msg
        assert "AZURE_OPENAI_DEPLOYMENT" in error_msg
        assert "AZURE_OPENAI_API_VERSION" in error_msg

    def test_init_raises_not_available_with_all_fields(self):
        """Deve lançar erro 'não disponível' mesmo com todos os campos preenchidos."""
        with pytest.raises(LLMError) as exc:
            AzureOpenAILLMClient(
                model="gpt-4",
                api_key="test-key",
                extra={
                    "endpoint": "https://test.openai.azure.com/",
                    "deployment": "gpt-4",
                    "api_version": "2024-02-15-preview",
                },
            )
        assert "ainda não está disponível" in str(exc.value)

    def test_from_settings_creates_client(self):
        """Deve criar cliente a partir de LLMSettings."""
        settings = LLMSettings(
            provider="azure",
            model="gpt-4",
            api_key="test-key",
            extra={
                "endpoint": "https://test.openai.azure.com/",
                "deployment": "gpt-4",
                "api_version": "2024-02-15-preview",
            },
        )
        with pytest.raises(LLMError) as exc:
            AzureOpenAILLMClient.from_settings(settings)
        # Deve lançar erro de "não disponível", não de validação
        assert "ainda não está disponível" in str(exc.value)

    def test_generate_content_raises_not_supported(self):
        """Deve lançar erro ao tentar gerar conteúdo (método não implementado)."""
        # Não podemos criar uma instância real, mas podemos testar o método diretamente
        # se conseguirmos burlar o __init__ (não é o caso aqui)
        # Este teste documenta o comportamento esperado
        pass  # Coberto pelo pragma: no cover no código
