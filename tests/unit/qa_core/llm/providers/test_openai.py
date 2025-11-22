import pytest
from qa_core.llm import LLMSettings
from qa_core.llm.providers.openai import OpenAILLMClient
from qa_core.llm.providers.base import LLMError


def test_openai_init_raises_without_api_key():
    """Testa que OpenAILLMClient levanta erro sem API key."""
    with pytest.raises(LLMError) as exc:
        OpenAILLMClient(model="gpt-4", api_key=None, extra={})
    assert "OPENAI_API_KEY não configurada" in str(exc.value)


def test_openai_init_raises_not_supported():
    """Testa que OpenAILLMClient levanta erro de integração não disponível."""
    with pytest.raises(LLMError) as exc:
        OpenAILLMClient(model="gpt-4", api_key="sk-test", extra={})
    assert "ainda não está disponível" in str(exc.value)


def test_openai_from_settings_creates_client():
    """Testa que from_settings tenta criar o cliente."""
    settings = LLMSettings(
        provider="openai", model="gpt-4", api_key="sk-test", extra={}
    )
    with pytest.raises(LLMError) as exc:
        OpenAILLMClient.from_settings(settings)
    assert "ainda não está disponível" in str(exc.value)


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
    assert "ainda não suportado" in str(exc.value)
