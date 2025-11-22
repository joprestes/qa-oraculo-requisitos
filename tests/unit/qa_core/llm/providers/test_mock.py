"""Testes unitários para o provedor Mock."""

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

    def test_mock_client_sleeps_on_generate(self):
        """Testa que MockLLMClient simula delay de rede."""
        from unittest.mock import patch

        client = MockLLMClient(model="mock", api_key=None, extra={})

        with patch("time.sleep") as mock_sleep:
            client.generate_content("test prompt")
            # Verifica que time.sleep foi chamado com ~1.5 segundos
            mock_sleep.assert_called_once()
            call_args = mock_sleep.call_args[0][0]
            assert 1.0 <= call_args <= 2.0  # Permite pequena variação

    def test_mock_client_uses_default_api_key(self):
        """Testa que MockLLMClient usa 'mock-key' como padrão quando api_key é None."""
        client = MockLLMClient(model="mock", api_key=None, extra={})
        assert client._api_key == "mock-key"

    def test_mock_client_analise_via_prompt_keyword(self):
        """Testa detecção de análise apenas pela keyword no prompt."""
        client = MockLLMClient(model="mock", api_key=None, extra={})
        result = client.generate_content("Analisar a User Story fornecida")
        assert "analise" in result.text.lower()

    def test_mock_client_plano_via_prompt_keyword(self):
        """Testa detecção de plano apenas pela keyword no prompt."""
        client = MockLLMClient(model="mock", api_key=None, extra={})
        result = client.generate_content("Criar um Plano de Testes detalhado")
        assert "plano_testes" in result.text.lower() or "plano" in result.text.lower()
