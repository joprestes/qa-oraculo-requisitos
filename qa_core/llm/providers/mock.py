from typing import Any, Dict
import time
from qa_core.llm.providers.base import LLMClient
from qa_core.llm.config import LLMSettings


class MockLLMClient(LLMClient):
    provider_name = "mock"

    def __init__(
        self, *, model: str, api_key: str | None, extra: Dict[str, Any]
    ) -> None:
        self._model_name = model
        self._api_key = api_key or "mock-key"
        self._extra = extra

    @classmethod
    def from_settings(cls, settings: LLMSettings) -> "MockLLMClient":
        return cls(model=settings.model, api_key=settings.api_key, extra=settings.extra)

    def generate_content(
        self,
        prompt: str,
        *,
        config: Dict[str, Any] | None = None,
        trace_id: str | None = None,
        node: str | None = None,
    ) -> Any:
        # Simula um pequeno delay de rede
        time.sleep(1.5)

        # Retorna um JSON simulado dependendo do prompt ou contexto
        # Como o prompt é complexo, vamos retornar uma resposta genérica válida para o sistema

        if "Analisar a User Story" in prompt or "node_analisar_historia" in str(node):
            return MockResponse(
                """```json
{
  "analise": {
    "clareza": "A User Story está clara e bem definida.",
    "criterios_aceite": "Os critérios de aceite cobrem os cenários principais.",
    "dependencias": "Nenhuma dependência externa identificada.",
    "riscos": "Baixo risco, alteração pontual na interface.",
    "sugestoes": "Adicionar validação de acessibilidade."
  }
}
```"""
            )

        if (
            "Criar um Plano de Testes" in prompt
            or "node_criar_plano_e_casos_de_teste" in str(node)
        ):
            return MockResponse(
                """```json
{
  "plano_testes": [
    {
      "id": "CT001",
      "titulo": "Validar login com sucesso",
      "pre_condicoes": "Usuário cadastrado e ativo",
      "passos": [
        "Acessar a página de login",
        "Inserir e-mail válido",
        "Inserir senha válida",
        "Clicar em Entrar"
      ],
      "resultado_esperado": "Redirecionamento para dashboard",
      "prioridade": "Alta",
      "tipo": "Funcional"
    },
    {
      "id": "CT002",
      "titulo": "Validar login com senha inválida",
      "pre_condicoes": "Usuário cadastrado",
      "passos": [
        "Acessar a página de login",
        "Inserir e-mail válido",
        "Inserir senha incorreta",
        "Clicar em Entrar"
      ],
      "resultado_esperado": "Mensagem de erro 'Credenciais inválidas'",
      "prioridade": "Alta",
      "tipo": "Funcional"
    },
    {
      "id": "CT003",
      "titulo": "Validar exclusão de cenário (Teste de Edição)",
      "pre_condicoes": "Cenário existente",
      "passos": ["Selecionar cenário", "Clicar excluir"],
      "resultado_esperado": "Cenário removido",
      "prioridade": "Média",
      "tipo": "Funcional"
    }
  ]
}
```"""
            )

        # Fallback
        return MockResponse("Resposta Mock Genérica")


class MockResponse:
    def __init__(self, text):
        self.text = text
