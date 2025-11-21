"""Testes unitários para o provedor Mock."""

import pytest

from qa_core.llm.config import LLMSettings
from qa_core.llm.providers.mock import MockLLMClient


class TestMockLLMClient:
    """Testes para o cliente Mock."""

    def test_init_creates_client_without_api_key(self):
        """Deve criar cliente Mock sem necessidade de API key."""
        client = MockLLMClient(
            model="mock-model",
            api_key=None,
            extra={},
        )
        assert client is not None
        assert client._model_name == "mock-model"

    def test_init_creates_client_with_api_key(self):
        """Deve criar cliente Mock mesmo com API key fornecida."""
        client = MockLLMClient(
            model="mock-model",
            api_key="dummy-key",
            extra={},
        )
        assert client is not None

    def test_from_settings_creates_client(self):
        """Deve criar cliente a partir de LLMSettings."""
        settings = LLMSettings(
            provider="mock",
            model="mock-model",
            api_key="dummy",
            extra={},
        )
        client = MockLLMClient.from_settings(settings)
        assert client is not None
        assert client._model_name == "mock-model"

    def test_generate_content_returns_mock_response(self):
        """Deve retornar resposta mockada ao gerar conteúdo."""
        client = MockLLMClient(
            model="mock-model",
            api_key=None,
            extra={},
        )
        
        class MockResponse:
            text = "Mock response"
        
        response = client.generate_content("test prompt")
        assert response is not None
        assert hasattr(response, "text")
        assert "Mock" in response.text or "mock" in response.text.lower()

    def test_generate_content_with_config(self):
        """Deve aceitar configuração opcional ao gerar conteúdo."""
        client = MockLLMClient(
            model="mock-model",
            api_key=None,
            extra={},
        )
        
        response = client.generate_content(
            "test prompt",
            config={"temperature": 0.5},
        )
        assert response is not None

    def test_generate_content_with_trace_id(self):
        """Deve aceitar trace_id opcional ao gerar conteúdo."""
        client = MockLLMClient(
            model="mock-model",
            api_key=None,
            extra={},
        )
        
        response = client.generate_content(
            "test prompt",
            trace_id="test-trace-123",
        )
        assert response is not None

    def test_generate_content_with_node(self):
        """Deve aceitar node opcional ao gerar conteúdo."""
        client = MockLLMClient(
            model="mock-model",
            api_key=None,
            extra={},
        )
        
        response = client.generate_content(
            "test prompt",
            node="test-node",
        )
        assert response is not None
