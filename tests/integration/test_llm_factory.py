import os
import unittest
from unittest.mock import patch

from qa_core.llm import LLMSettings, get_llm_client
from qa_core.llm.providers.base import LLMError
from qa_core.llm.providers.google import GoogleLLMClient


class TestLLMFactoryIntegration(unittest.TestCase):
    """Testes de integração para a Factory de LLMs."""

    def test_get_llm_client_google(self):
        """Verifica se a factory retorna um cliente GoogleLLMClient corretamente."""
        settings = LLMSettings(
            provider="google",
            model="gemini-pro",
            api_key="fake-key",
            extra={"google_api_key": "fake-key"},
        )
        client = get_llm_client(settings)
        self.assertIsInstance(client, GoogleLLMClient)
        # O modelo é privado (_model_name), mas podemos verificar se não explodiu

    def test_get_llm_client_openai(self):
        """
        Verifica se a factory tenta criar um cliente OpenAI.
        Atualmente, o OpenAIClient lança erro no init, o que confirma que a factory
        escolheu a classe certa.
        """
        settings = LLMSettings(
            provider="openai",
            model="gpt-4",
            api_key="fake-key",
            extra={"base_url": None, "organization": None},
        )
        # Esperamos LLMError pois a implementação atual do OpenAI lança erro propositalmente
        with self.assertRaisesRegex(LLMError, "ainda não está disponível"):
            get_llm_client(settings)

    def test_get_llm_client_provider_invalido(self):
        """Verifica se a factory lança erro para provedor desconhecido."""
        settings = LLMSettings(
            provider="desconhecido",
            model="modelo-x",
            api_key="fake-key",
        )
        with self.assertRaises(ValueError):
            get_llm_client(settings)

    @patch.dict(os.environ, {"LLM_PROVIDER": "google", "GOOGLE_API_KEY": "env-key"})
    def test_llm_settings_from_env(self):
        """Verifica se as configurações são carregadas corretamente do ambiente."""
        settings = LLMSettings.from_env()
        self.assertEqual(settings.provider, "google")
        self.assertEqual(settings.api_key, "env-key")
