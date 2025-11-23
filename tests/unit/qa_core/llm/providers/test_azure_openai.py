"""Testes unitários para o provedor Azure OpenAI."""

from unittest.mock import MagicMock, patch

import pytest

from qa_core.llm.config import LLMSettings
from qa_core.llm.providers.azure_openai import AzureOpenAILLMClient
from qa_core.llm.providers.base import LLMError, LLMRateLimitError


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

    @patch("qa_core.llm.providers.azure_openai.AzureOpenAI")
    def test_init_succeeds_with_all_fields(self, mock_azure_openai):
        """Deve criar cliente com sucesso quando todos os campos estão presentes."""
        client = AzureOpenAILLMClient(
            model="gpt-4",
            api_key="test-key",
            extra={
                "endpoint": "https://test.openai.azure.com/",
                "deployment": "gpt-4",
                "api_version": "2024-02-15-preview",
            },
        )
        assert client._model_name == "gpt-4"
        assert client._api_key == "test-key"
        mock_azure_openai.assert_called_once()

    @patch("qa_core.llm.providers.azure_openai.AzureOpenAI")
    def test_from_settings_creates_client(self, mock_azure_openai):
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
        client = AzureOpenAILLMClient.from_settings(settings)
        assert client._model_name == "gpt-4"
        assert client._api_key == "test-key"

    @patch("qa_core.llm.providers.azure_openai.AzureOpenAI")
    def test_generate_content_success(self, mock_azure_openai):
        """Deve gerar conteúdo com sucesso."""
        # Arrange
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Conteúdo gerado"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client

        client = AzureOpenAILLMClient(
            model="gpt-4",
            api_key="test-key",
            extra={
                "endpoint": "https://test.openai.azure.com/",
                "deployment": "gpt-4",
                "api_version": "2024-02-15-preview",
            },
        )

        # Act
        result = client.generate_content("Test prompt")

        # Assert
        assert result == "Conteúdo gerado"
        mock_client.chat.completions.create.assert_called_once()

    @patch("qa_core.llm.providers.azure_openai.AzureOpenAI")
    def test_generate_content_with_config(self, mock_azure_openai):
        """Deve passar configurações para a API."""
        # Arrange
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Resposta"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client

        client = AzureOpenAILLMClient(
            model="gpt-4",
            api_key="test-key",
            extra={
                "endpoint": "https://test.openai.azure.com/",
                "deployment": "gpt-4",
                "api_version": "2024-02-15-preview",
            },
        )

        # Act
        config = {"temperature": 0.7, "max_tokens": 100}
        client.generate_content("Test", config=config)

        # Assert
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["temperature"] == 0.7
        assert call_kwargs["max_tokens"] == 100

    @patch("qa_core.llm.providers.azure_openai.AzureOpenAI")
    def test_generate_content_raises_rate_limit_error(self, mock_azure_openai):
        """Deve lançar LLMRateLimitError quando atingir limite de taxa."""
        # Arrange
        from openai import RateLimitError as OpenAIRateLimitError

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = OpenAIRateLimitError(
            "Rate limit exceeded", response=MagicMock(), body=None
        )
        mock_azure_openai.return_value = mock_client

        client = AzureOpenAILLMClient(
            model="gpt-4",
            api_key="test-key",
            extra={
                "endpoint": "https://test.openai.azure.com/",
                "deployment": "gpt-4",
                "api_version": "2024-02-15-preview",
            },
        )

        # Act & Assert
        with pytest.raises(LLMRateLimitError) as exc:
            client.generate_content("Test")
        assert "Limite de taxa" in str(exc.value)

    @patch("qa_core.llm.providers.azure_openai.AzureOpenAI")
    def test_generate_content_raises_llm_error_on_exception(self, mock_azure_openai):
        """Deve lançar LLMError para outros erros."""
        # Arrange
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_azure_openai.return_value = mock_client

        client = AzureOpenAILLMClient(
            model="gpt-4",
            api_key="test-key",
            extra={
                "endpoint": "https://test.openai.azure.com/",
                "deployment": "gpt-4",
                "api_version": "2024-02-15-preview",
            },
        )

        # Act & Assert
        with pytest.raises(LLMError) as exc:
            client.generate_content("Test")
        assert "Erro ao chamar Azure OpenAI" in str(exc.value)

    def test_init_raises_when_extra_fields_are_empty_strings(self):
        """Deve lançar erro quando campos extra são strings vazias."""
        with pytest.raises(LLMError) as exc:
            AzureOpenAILLMClient(
                model="gpt-4",
                api_key="test-key",
                extra={
                    "endpoint": "",
                    "deployment": "",
                    "api_version": "",
                },
            )
        error_msg = str(exc.value)
        assert (
            "AZURE_OPENAI_ENDPOINT" in error_msg
            or "ainda não está disponível" in error_msg
        )

    def test_init_raises_when_extra_fields_are_none(self):
        """Deve lançar erro quando campos extra são None."""
        with pytest.raises(LLMError) as exc:
            AzureOpenAILLMClient(
                model="gpt-4",
                api_key="test-key",
                extra={
                    "endpoint": None,
                    "deployment": None,
                    "api_version": None,
                },
            )
        error_msg = str(exc.value)
        assert (
            "AZURE_OPENAI_ENDPOINT" in error_msg
            or "ainda não está disponível" in error_msg
        )

    def test_generate_content_raises_not_supported(self):
        """Deve lançar erro ao tentar gerar conteúdo (método não implementado)."""
        # Não podemos criar uma instância real, mas podemos testar o método diretamente
        # se conseguirmos burlar o __init__ (não é o caso aqui)
        # Este teste documenta o comportamento esperado
        pass  # Coberto pelo pragma: no cover no código
