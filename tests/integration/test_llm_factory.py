import pytest
from qa_core.llm import get_llm_client, LLMSettings
from qa_core.llm.providers.google import GoogleLLMClient
from qa_core.llm.providers.mock import MockLLMClient
from qa_core.llm.providers.base import LLMClient

def test_factory_returns_google_client():
    settings = LLMSettings(
        provider="google",
        model="gemini-pro",
        api_key="secret",
        extra={}
    )
    client = get_llm_client(settings)
    assert isinstance(client, GoogleLLMClient)
    assert isinstance(client, LLMClient)

def test_factory_returns_mock_client():
    settings = LLMSettings(
        provider="mock",
        model="mock-model",
        api_key="secret",
        extra={}
    )
    client = get_llm_client(settings)
    assert isinstance(client, MockLLMClient)

def test_factory_raises_error_for_unknown_provider():
    settings = LLMSettings(
        provider="unknown_provider",
        model="model",
        api_key="secret",
        extra={}
    )
    # O factory tenta acessar o dicionário e levanta ValueError se falhar
    with pytest.raises(ValueError) as exc:
        get_llm_client(settings)
    assert "não suportado" in str(exc.value)

def test_factory_case_insensitive():
    settings = LLMSettings(
        provider="GOOGLE",
        model="gemini-pro",
        api_key="secret",
        extra={}
    )
    client = get_llm_client(settings)
    assert isinstance(client, GoogleLLMClient)
