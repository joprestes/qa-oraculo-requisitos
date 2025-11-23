"""Testes unitários para o provedor OpenAI."""

from unittest.mock import MagicMock, patch

import pytest

from qa_core.llm.config import LLMSettings
from qa_core.llm.providers.base import LLMError, LLMRateLimitError
from qa_core.llm.providers.openai import OpenAILLMClient


class TestOpenAILLMClient:
    """Testes para o cliente OpenAI."""

    def test_init_raises_when_missing_api_key(self):
        """Deve lançar erro quando OPENAI_API_KEY está faltando."""
        with pytest.raises(LLMError) as exc:
            OpenAILLMClient(model="gpt-4", api_key=None, extra={})
        assert "OPENAI_API_KEY não configurada" in str(exc.value)

    @patch("qa_core.llm.providers.openai.OpenAI")
    def test_init_succeeds_with_api_key(self, mock_openai):
        """Deve criar cliente com sucesso quando API key está presente."""
        client = OpenAILLMClient(model="gpt-4", api_key="sk-test", extra={})
        assert client._model_name == "gpt-4"
        assert client._api_key == "sk-test"
        mock_openai.assert_called_once()

    @patch("qa_core.llm.providers.openai.OpenAI")
    def test_init_with_organization(self, mock_openai):
        """Deve passar organização para o cliente OpenAI."""
        client = OpenAILLMClient(
            model="gpt-4", api_key="sk-test", extra={"organization": "org-123"}
        )
        assert client._extra["organization"] == "org-123"
        call_kwargs = mock_openai.call_args[1]
        assert call_kwargs["organization"] == "org-123"

    @patch("qa_core.llm.providers.openai.OpenAI")
    def test_from_settings_creates_client(self, mock_openai):
        """Deve criar cliente a partir de LLMSettings."""
        settings = LLMSettings(
            provider="openai", model="gpt-4", api_key="sk-test", extra={}
        )
        client = OpenAILLMClient.from_settings(settings)
        assert client._model_name == "gpt-4"
        assert client._api_key == "sk-test"

    @patch("qa_core.llm.providers.openai.OpenAI")
    def test_generate_content_success(self, mock_openai):
        """Deve gerar conteúdo com sucesso."""
        # Arrange
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Conteúdo gerado"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        client = OpenAILLMClient(model="gpt-4", api_key="sk-test", extra={})

        # Act
        result = client.generate_content("Test prompt")

        # Assert
        assert result == "Conteúdo gerado"
        mock_client.chat.completions.create.assert_called_once()

    @patch("qa_core.llm.providers.openai.OpenAI")
    def test_generate_content_with_config(self, mock_openai):
        """Deve passar configurações para a API."""
        # Arrange
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Resposta"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        client = OpenAILLMClient(model="gpt-4", api_key="sk-test", extra={})

        # Act
        config = {"temperature": 0.7, "max_tokens": 100}
        client.generate_content("Test", config=config)

        # Assert
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["temperature"] == 0.7
        assert call_kwargs["max_tokens"] == 100

    @patch("qa_core.llm.providers.openai.OpenAI")
    def test_generate_content_uses_correct_model(self, mock_openai):
        """Deve usar o modelo correto na chamada da API."""
        # Arrange
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Resposta"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        client = OpenAILLMClient(model="gpt-3.5-turbo", api_key="sk-test", extra={})

        # Act
        client.generate_content("Test")

        # Assert
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "gpt-3.5-turbo"

    @patch("qa_core.llm.providers.openai.OpenAI")
    def test_generate_content_raises_rate_limit_error(self, mock_openai):
        """Deve lançar LLMRateLimitError quando atingir limite de taxa."""
        # Arrange
        from openai import RateLimitError as OpenAIRateLimitError

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = OpenAIRateLimitError(
            "Rate limit exceeded", response=MagicMock(), body=None
        )
        mock_openai.return_value = mock_client

        client = OpenAILLMClient(model="gpt-4", api_key="sk-test", extra={})

        # Act & Assert
        with pytest.raises(LLMRateLimitError) as exc:
            client.generate_content("Test")
        assert "Limite de taxa" in str(exc.value)

    @patch("qa_core.llm.providers.openai.OpenAI")
    def test_generate_content_raises_llm_error_on_exception(self, mock_openai):
        """Deve lançar LLMError para outros erros."""
        # Arrange
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client

        client = OpenAILLMClient(model="gpt-4", api_key="sk-test", extra={})

        # Act & Assert
        with pytest.raises(LLMError) as exc:
            client.generate_content("Test")
        assert "Erro ao chamar OpenAI" in str(exc.value)


def test_openai_init_raises_when_api_key_is_empty_string():
    """Testa que OpenAILLMClient levanta erro com API key vazia."""
    with pytest.raises(LLMError) as exc:
        OpenAILLMClient(model="gpt-4", api_key="", extra={})
    assert "OPENAI_API_KEY não configurada" in str(exc.value)


def test_openai_generate_content_raises_not_supported():
    """Testa que generate_content levanta erro (não deve ser chamado)."""
    # Não podemos instanciar o cliente, mas podemos testar o método diretamente
    # se ele fosse chamado (embora isso nunca aconteça na prática)
    client = object.__new__(OpenAILLMClient)
    with pytest.raises(LLMError) as exc:
        client.generate_content("test prompt")
    # O erro será de atributo faltando, não de "não suportado"
    assert "Erro ao chamar OpenAI" in str(exc.value)
