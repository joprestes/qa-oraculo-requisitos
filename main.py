import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# --- 1. O Cérebro do Oráculo: O Prompt do Especialista ---
PROMPT_ANALISE_SIMPLES = """
Você é um Analista de QA Sênior, especialista em Engenharia de Requisitos.
Sua principal tarefa é analisar um requisito de software e identificar possíveis problemas
que possam levar a bugs ou retrabalho no futuro.

Seja cético, preciso e construtivo.

Para o requisito fornecido, faça o seguinte:
1.  **Avaliação de Clareza:** Aponte se o requisito está claro, ambíguo ou incompleto.
2.  **Identificação de Termos Vagos:** Encontre e liste palavras subjetivas que não podem ser medidas (ex: "rápido", "fácil", "seguro", "melhorar", "bom").
3.  **Sugestão de Melhoria:** Ofereça uma sugestão de como o requisito poderia ser reescrito para ser mais testável e objetivo.
"""

# --- 2. A Função Principal de Análise ---
def analisar_requisito(texto_requisito: str):
    """
    Envia um requisito para a IA do Google com o prompt de especialista e retorna a análise.
    """
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return "Erro: A variável de ambiente GOOGLE_API_KEY não foi encontrada."

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt_completo = f"{PROMPT_ANALISE_SIMPLES}\n\nRequisito para Análise:\n---\n{texto_requisito}"

        print("\n🔮 O Oráculo está analisando o requisito... Por favor, aguarde.\n")
        response = model.generate_content(prompt_completo)

        return response.text

    except Exception as e:
        return f"❌ Ocorreu um erro ao conectar com a IA: {e}"

# --- 3. Ponto de Entrada da Aplicação Interativa ---
if __name__ == "__main__":
    print("--- 🔮 Bem-vindo ao QA Oráculo de Requisitos ---")
    print("Digite o requisito que você deseja analisar.")
    print("Para sair, digite 'sair' ou pressione Ctrl+C.")
    
    # Loop infinito para manter a conversa
    while True:
        # Pede ao usuário para digitar o requisito
        requisito_usuario = input("\nSeu requisito: ")

        # Verifica se o usuário quer sair
        if requisito_usuario.lower() == 'sair':
            print("\nAté a próxima consulta!")
            break
        
        # Verifica se o usuário não digitou nada
        if not requisito_usuario.strip():
            print("Por favor, digite um requisito para analisar.")
            continue

        # Chama a função de análise com o input do usuário
        analise_resultado = analisar_requisito(requisito_usuario)

        # Imprime o resultado
        print("\n--- Relatório de Análise do Oráculo ---")
        print(analise_resultado)
        print("--------------------------------------")