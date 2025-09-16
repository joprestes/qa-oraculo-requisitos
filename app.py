import re
import datetime
from pathlib import Path

# Importa nosso grafo compilado do novo módulo 'graph'
from graph import grafo

# --- Funções de Interação com o Usuário ---

def obter_user_story_do_usuario() -> str:
    """
    Solicita que o usuário cole uma User Story, permitindo múltiplas linhas.
    A entrada termina quando o usuário digita 'analisar' em uma nova linha.
    """
    print("\nPor favor, cole sua User Story abaixo.")
    print("Quando terminar, digite 'analisar' em uma linha separada e pressione Enter.")
    print("--------------------------------------------------------------------")
    
    linhas_da_us = []
    while True:
        try:
            linha = input()
            if linha.strip().lower() == 'analisar':
                break
            linhas_da_us.append(linha)
        except EOFError:
            break
            
    return "\n".join(linhas_da_us).strip()

def salvar_relatorio_em_arquivo(relatorio: str, user_story: str):
    """
    Salva o relatório em um arquivo Markdown na pasta 'output'.
    O nome do arquivo é gerado dinamicamente.
    """
    try:
        # Garante que a pasta 'output' exista
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        # Gera um nome de arquivo seguro a partir do título da US
        primeira_linha_us = user_story.split('\n')[0].lower()
        nome_base = re.sub(r'[^\w\s-]', '', primeira_linha_us).strip()
        nome_base = re.sub(r'[-\s]+', '-', nome_base)[:50] # Limita o tamanho

        # Adiciona um timestamp para garantir que o nome seja único
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"{nome_base}_{timestamp}.md"
        
        caminho_arquivo = output_dir / nome_arquivo

        # Escreve o conteúdo do relatório no arquivo
        caminho_arquivo.write_text(relatorio, encoding="utf-8")
        
        print(f"\n✅ Relatório salvo com sucesso em: {caminho_arquivo}")

    except Exception as e:
        print(f"\n❌ Ocorreu um erro ao salvar o relatório: {e}")

def main():
    """Função principal que executa o workflow do Oráculo de forma interativa."""
    print("--- 🔮 Bem-vindo ao QA Oráculo de User Stories ---")
    
    user_story = obter_user_story_do_usuario()
    
    if not user_story:
        print("\nNenhuma User Story fornecida. Encerrando.")
        return

    print("\nUser Story recebida. Iniciando análise...")
    print("-----------------------------------------")

    inputs = {"user_story": user_story}
    resultado_final = grafo.invoke(inputs)
    
    print("\n--- 🚀 Processo Finalizado ---")

    # Determina qual relatório exibir e salvar
    relatorio_final = None
    if "relatorio_final_completo" in resultado_final:
        print("\n--- ✅ Relatório Completo Gerado com Sucesso ---")
        relatorio_final = resultado_final.get("relatorio_final_completo")
        print(relatorio_final)
        print("---------------------------------------------")
    else:
        # Se o usuário disse 'n', o relatório inicial já foi impresso no nó.
        relatorio_final = resultado_final.get("relatorio_analise_inicial")
        print("Finalizado após a análise inicial.")

    # Lógica para salvar o arquivo
    if relatorio_final:
        resposta_salvar = input("\nDeseja salvar este relatório em um arquivo? (s/n): ").lower()
        if resposta_salvar == 's':
            salvar_relatorio_em_arquivo(relatorio_final, user_story)

if __name__ == "__main__":
    main()