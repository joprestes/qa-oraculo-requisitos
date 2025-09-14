import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
# Isso torna a chave de API disponível para nosso código
load_dotenv()

def testar_conexao_ia():
    """
    Função simples para verificar se a API do Google está configurada corretamente.
    """
    try:
        # Configura o SDK do Google com a chave de API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("Erro: A variável de ambiente GOOGLE_API_KEY não foi encontrada.")
            print("Verifique se você criou o arquivo .env e inseriu sua chave corretamente.")
            return

        genai.configure(api_key=api_key)

        # Escolhe o modelo que vamos usar
        model = genai.GenerativeModel('gemini-2.5-flash')

        print("Conectando ao Gemini... Por favor, aguarde.")

        # Envia um prompt simples para o modelo
        response = model.generate_content("Qual é a tarefa mais importante de um Analista de QA?")

        # Imprime a resposta
        print("\n--- Resposta do Gemini ---")
        print(response.text)
        print("--------------------------\n")
        print("✅ Conexão com a IA bem-sucedida!")

    except Exception as e:
        print(f"❌ Ocorreu um erro ao conectar com a IA: {e}")

# Este bloco garante que a função só será executada quando o script for rodado diretamente
if __name__ == "__main__":
    testar_conexao_ia()