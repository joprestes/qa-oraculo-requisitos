import pytest
from qa_core.llm import get_llm_client, LLMSettings
from qa_core.llm.factory import CachedLLMClient
from qa_core.llm.providers.google import GoogleLLMClient
from qa_core.llm.providers.mock import MockLLMClient
from qa_core.llm.providers.base import LLMClient


def test_factory_returns_google_client():
    settings = LLMSettings(
        provider="google", model="gemini-pro", api_key="secret", extra={}
    )
    client = get_llm_client(settings)
    assert isinstance(client, CachedLLMClient)
    assert isinstance(client._client, GoogleLLMClient)
    # Verifica se ainda respeita o protocolo (duck typing ou runtime check)
    # Como CachedLLMClient não herda explicitamente de LLMClient na definição (mas implementa),
    # o isinstance(client, LLMClient) pode falhar se LLMClient for Protocol sem runtime_checkable
    # Mas LLMClient é @runtime_checkable. Vamos verificar.
    assert isinstance(client, LLMClient)


def test_factory_returns_mock_client():
    settings = LLMSettings(
        provider="mock", model="mock-model", api_key="secret", extra={}
    )
    client = get_llm_client(settings)
    assert isinstance(client, CachedLLMClient)
    assert isinstance(client._client, MockLLMClient)


def test_factory_raises_error_for_unknown_provider():
    settings = LLMSettings(
        provider="unknown_provider", model="model", api_key="secret", extra={}
    )
    # O factory tenta acessar o dicionário e levanta ValueError se falhar
    with pytest.raises(ValueError) as exc:
        get_llm_client(settings)
    assert "não suportado" in str(exc.value)


def test_factory_case_insensitive():
    settings = LLMSettings(
        provider="GOOGLE", model="gemini-pro", api_key="secret", extra={}
    )
    client = get_llm_client(settings)
    assert isinstance(client, CachedLLMClient)
    assert isinstance(client._client, GoogleLLMClient)
