"""Testes unitários para o provedor LLaMA (Ollama)."""

from unittest.mock import patch

import pytest

from qa_core.llm.config import LLMSettings
from qa_core.llm.providers.base import LLMError
from qa_core.llm.providers.llama import LlamaLLMClient


class TestLlamaLLMClient:
    """Testes para o cliente LLaMA (Ollama)."""

    @patch("qa_core.llm.providers.llama.ollama.list")
    def test_init_succeeds_when_ollama_is_running(self, mock_ollama_list):
        """Deve criar cliente com sucesso quando Ollama está rodando."""
        # Arrange
        mock_ollama_list.return_value = {"models": []}

        # Act
        client = LlamaLLMClient(model="llama2", api_key=None, extra={})

        # Assert
        assert client._model_name == "llama2"
        mock_ollama_list.assert_called_once()

    @patch("qa_core.llm.providers.llama.ollama.list")
    def test_init_raises_when_ollama_not_running(self, mock_ollama_list):
        """Deve lançar erro quando Ollama não está acessível."""
        # Arrange
        mock_ollama_list.side_effect = Exception("Connection refused")

        # Act & Assert
        with pytest.raises(LLMError) as exc:
            LlamaLLMClient(model="llama2", api_key=None, extra={})
        assert "Ollama não está acessível" in str(exc.value)
        assert "https://ollama.ai" in str(exc.value)

    @patch("qa_core.llm.providers.llama.ollama.list")
    def test_init_does_not_require_api_key(self, mock_ollama_list):
        """Deve criar cliente sem API key (Ollama é local)."""
        # Arrange
        mock_ollama_list.return_value = {"models": []}

        # Act
        client = LlamaLLMClient(model="llama2", api_key=None, extra={})

        # Assert
        assert client._api_key is None

    @patch("qa_core.llm.providers.llama.ollama.list")
    def test_from_settings_creates_client(self, mock_ollama_list):
        """Deve criar cliente a partir de LLMSettings."""
        # Arrange
        mock_ollama_list.return_value = {"models": []}
        settings = LLMSettings(provider="llama", model="llama2", api_key=None, extra={})

        # Act
        client = LlamaLLMClient.from_settings(settings)

        # Assert
        assert client._model_name == "llama2"

    @patch("qa_core.llm.providers.llama.ollama.list")
    @patch("qa_core.llm.providers.llama.ollama.generate")
    def test_generate_content_success(self, mock_generate, mock_list):
        """Deve gerar conteúdo com sucesso."""
        # Arrange
        mock_list.return_value = {"models": []}
        mock_generate.return_value = {"response": "Conteúdo gerado"}

        client = LlamaLLMClient(model="llama2", api_key=None, extra={})

        # Act
        result = client.generate_content("Test prompt")

        # Assert
        assert result == "Conteúdo gerado"
        mock_generate.assert_called_once_with(
            model="llama2", prompt="Test prompt", options={}
        )

    @patch("qa_core.llm.providers.llama.ollama.list")
    @patch("qa_core.llm.providers.llama.ollama.generate")
    def test_generate_content_with_config(self, mock_generate, mock_list):
        """Deve passar configurações para Ollama."""
        # Arrange
        mock_list.return_value = {"models": []}
        mock_generate.return_value = {"response": "Resposta"}

        client = LlamaLLMClient(model="llama2", api_key=None, extra={})

        # Act
        config = {"temperature": 0.7, "num_predict": 100}
        client.generate_content("Test", config=config)

        # Assert
        call_kwargs = mock_generate.call_args[1]
        assert call_kwargs["options"]["temperature"] == 0.7
        assert call_kwargs["options"]["num_predict"] == 100

    @patch("qa_core.llm.providers.llama.ollama.list")
    @patch("qa_core.llm.providers.llama.ollama.generate")
    def test_generate_content_uses_correct_model(self, mock_generate, mock_list):
        """Deve usar o modelo correto na chamada do Ollama."""
        # Arrange
        mock_list.return_value = {"models": []}
        mock_generate.return_value = {"response": "Resposta"}

        client = LlamaLLMClient(model="llama2:13b", api_key=None, extra={})

        # Act
        client.generate_content("Test")

        # Assert
        call_kwargs = mock_generate.call_args[1]
        assert call_kwargs["model"] == "llama2:13b"

    @patch("qa_core.llm.providers.llama.ollama.list")
    @patch("qa_core.llm.providers.llama.ollama.generate")
    def test_generate_content_handles_empty_response(self, mock_generate, mock_list):
        """Deve retornar string vazia se resposta não tiver conteúdo."""
        # Arrange
        mock_list.return_value = {"models": []}
        mock_generate.return_value = {}  # Sem campo 'response'

        client = LlamaLLMClient(model="llama2", api_key=None, extra={})

        # Act
        result = client.generate_content("Test")

        # Assert
        assert result == ""

    @patch("qa_core.llm.providers.llama.ollama.list")
    @patch("qa_core.llm.providers.llama.ollama.generate")
    def test_generate_content_raises_on_model_not_found(self, mock_generate, mock_list):
        """Deve lançar erro quando modelo não está instalado."""
        # Arrange
        mock_list.return_value = {"models": []}
        mock_generate.side_effect = Exception("model 'llama3' not found")

        client = LlamaLLMClient(model="llama3", api_key=None, extra={})

        # Act & Assert
        with pytest.raises(LLMError) as exc:
            client.generate_content("Test")
        assert "Erro ao chamar Ollama" in str(exc.value)
        assert "ollama pull llama3" in str(exc.value)

    @patch("qa_core.llm.providers.llama.ollama.list")
    @patch("qa_core.llm.providers.llama.ollama.generate")
    def test_generate_content_raises_llm_error_on_exception(
        self, mock_generate, mock_list
    ):
        """Deve lançar LLMError para outros erros."""
        # Arrange
        mock_list.return_value = {"models": []}
        mock_generate.side_effect = Exception("Ollama error")

        client = LlamaLLMClient(model="llama2", api_key=None, extra={})

        # Act & Assert
        with pytest.raises(LLMError) as exc:
            client.generate_content("Test")
        assert "Erro ao chamar Ollama" in str(exc.value)
