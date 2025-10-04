# config.py
# Configurações centrais do projeto

NOME_MODELO = "gemini-2.0-flash-lite-001"

# Configurações para tarefas que exigem criatividade e estrutura (JSONs complexos)
CONFIG_GERACAO_ANALISE = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",  # Força a saída em JSON
}

# Configurações para tarefas que exigem formatação de texto (Markdown)
CONFIG_GERACAO_RELATORIO = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 8192,
}
