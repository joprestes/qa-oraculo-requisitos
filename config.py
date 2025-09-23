# config.py

NOME_MODELO = "gemini-1.5-flash-latest"

# Configuração para geração de JSONs.
# A adição de response_mime_type força a IA a retornar um JSON válido.
CONFIG_GERACAO_ANALISE = {
    "temperature": 0.2,
    "response_mime_type": "application/json",
}

# Configuração para geração de relatórios em Markdown.
CONFIG_GERACAO_RELATORIO = {
    "temperature": 0.3
}