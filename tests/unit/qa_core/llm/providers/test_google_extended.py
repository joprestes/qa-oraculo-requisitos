from unittest.mock import Mock, patch

import pytest
from qa_core.llm import LLMSettings
from qa_core.llm.providers.google import GoogleLLMClient


def test_google_from_settings_creates_client():
    """Testa que from_settings cria o cliente corretamente."""
    settings = LLMSettings(
        provider="google", model="gemini-2.0-flash", api_key="test-key", extra={}
    )

    with patch("qa_core.llm.providers.google.genai.configure"):
        with patch("qa_core.llm.providers.google.genai.GenerativeModel") as _:
            client = GoogleLLMClient.from_settings(settings)
            assert client is not None
            assert client._model_name == "gemini-2.0-flash"


def test_google_generate_content_success():
    """Testa geração de conteúdo com sucesso."""
    with patch("qa_core.llm.providers.google.genai.configure"):
        with patch(
            "qa_core.llm.providers.google.genai.GenerativeModel"
        ) as mock_model_class:
            mock_model = Mock()
            mock_response = Mock()
            mock_response.text = "Test response"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model

            client = GoogleLLMClient(model="gemini-2.0-flash", api_key="test-key")
            result = client.generate_content("test prompt")

            assert result.text == "Test response"
            mock_model.generate_content.assert_called_once()


def test_google_generate_content_with_config():
    """Testa geração com configuração customizada."""
    with patch("qa_core.llm.providers.google.genai.configure"):
        with patch(
            "qa_core.llm.providers.google.genai.GenerativeModel"
        ) as mock_model_class:
            mock_model = Mock()
            mock_response = Mock()
            mock_response.text = "Response"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model

            client = GoogleLLMClient(model="gemini-2.0-flash", api_key="test-key")
            config = {"temperature": 0.5, "max_tokens": 1000}
            result = client.generate_content("prompt", config=config)

            assert result.text == "Response"


def test_google_generate_content_with_trace_id():
    """Testa geração com trace_id para observabilidade."""
    with patch("qa_core.llm.providers.google.genai.configure"):
        with patch(
            "qa_core.llm.providers.google.genai.GenerativeModel"
        ) as mock_model_class:
            mock_model = Mock()
            mock_response = Mock()
            mock_response.text = "Response"
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model

            client = GoogleLLMClient(model="gemini-2.0-flash", api_key="test-key")
            result = client.generate_content(
                "prompt", trace_id="trace-123", node="test-node"
            )

            # Verifica que a resposta foi retornada
            assert result.text == "Response"


def test_google_init_raises_without_api_key():
    """Testa que __init__ lança erro quando não há API key (linha 23)."""
    from qa_core.llm.providers.google import GoogleLLMClient, LLMError

    with pytest.raises(LLMError, match="GOOGLE_API_KEY não configurada"):
        GoogleLLMClient(model="gemini-2.0-flash", api_key=None)
