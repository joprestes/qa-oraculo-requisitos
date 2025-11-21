import os
import sys

# Adiciona o diretório raiz ao path para importar qa_core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qa_core.graph import grafo_analise
from qa_core.llm import LLMSettings, get_llm_client

# Configura para usar o Mock Provider
os.environ["LLM_PROVIDER"] = "mock"
os.environ["LLM_MODEL"] = "mock-model"
os.environ["LLM_API_KEY"] = "mock-key"


def run_e2e_test():
    print("🚀 Iniciando teste E2E com Mock Provider...")

    # 1. Verifica se o cliente é Mock
    settings = LLMSettings.from_env()
    client = get_llm_client(settings)
    print(f"✅ Cliente LLM carregado: {type(client).__name__}")

    if "MockLLMClient" not in type(client).__name__:
        print("❌ Erro: O cliente não é o MockLLMClient!")
        return

    # 2. Executa o grafo de análise
    user_story = "Como usuário, quero fazer login para acessar minha conta."
    print(f"📝 Input: {user_story}")

    try:
        resultado = grafo_analise.invoke({"user_story": user_story})
        print("✅ Grafo executado com sucesso!")

        analise = resultado.get("analise_da_us", {})
        print(f"📊 Resultado da Análise: {analise}")

        if not analise:
            print("❌ Erro: Análise vazia!")
        else:
            print("🎉 Teste E2E com Mock passou!")

    except Exception as e:
        print(f"❌ Erro durante a execução do grafo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run_e2e_test()
