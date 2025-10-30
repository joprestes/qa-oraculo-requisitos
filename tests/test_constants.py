# ==========================================================
# test_constants.py — Constantes para Testes
# ==========================================================
# 📘 Constantes e dados de teste reutilizáveis para evitar
# valores hardcoded nos testes e melhorar manutenibilidade.
# ==========================================================

# === Dados de Teste ===
TEST_USER_STORY = "Como usuário, quero fazer login no sistema"
TEST_ANALYSIS_REPORT = "Relatório de análise de teste"
TEST_PLAN_REPORT = "Plano de testes gerado"
TEST_PDF_BYTES = b"fake_pdf_content"
TEST_EXCEL_BYTES = b"fake_excel_content"
TEST_FILENAME = "fake.xlsx"

# === Dados de Sessão ===
TEST_ANALYSIS_STATE = {
    "user_story": TEST_USER_STORY,
    "analise_da_us": {
        "avaliacao_geral": "Avaliação geral da user story",
        "pontos_ambiguos": ["Ponto ambíguo 1", "Ponto ambíguo 2"],
        "perguntas_para_po": ["Pergunta 1", "Pergunta 2"],
        "sugestao_criterios_aceite": ["Critério 1", "Critério 2"],
        "riscos_e_dependencias": ["Risco 1", "Risco 2"],
    },
    "relatorio_analise_inicial": TEST_ANALYSIS_REPORT,
}

TEST_SESSION_STATE_BASIC = {
    "analysis_finished": False,
    "analysis_state": TEST_ANALYSIS_STATE,
    "show_generate_plan_button": False,
    "user_story_input": TEST_USER_STORY,
}

TEST_SESSION_STATE_FINISHED = {
    "analysis_finished": True,
    "analysis_state": TEST_ANALYSIS_STATE,
    "test_plan_report": TEST_PLAN_REPORT,
    "test_plan_df": None,
    "pdf_report_bytes": TEST_PDF_BYTES,
    "user_story_input": TEST_USER_STORY,
    "area_path_input": "Área QA",
    "assigned_to_input": "Joelma",
}

# === DataFrames de Teste ===
TEST_DF_BASIC = [
    {
        "titulo": "CT 1",
        "cenario": "Dado que estou na tela de login\nQuando preencho os campos\nEntão sou redirecionado",
    },
    {
        "titulo": "CT 2",
        "cenario": "Dado que estou logado\nQuando clico em sair\nEntão sou deslogado",
    },
]

# === Configurações de Mock ===
MOCK_COLUMNS_COUNT = {
    "DOWNLOADS": 5,
    "AZURE": 2,
    "FALLBACK": 3,
}

# === Mensagens de Teste ===
TEST_MESSAGES = {
    "WARNING": "Atenção: User story não fornecida",
    "SUCCESS": "Análise concluída com sucesso",
    "ERROR": "Erro ao processar análise",
}

# === Configurações de Exportação ===
TEST_EXPORT_CONFIG = {
    "filename": TEST_FILENAME,
    "excel_content": TEST_EXCEL_BYTES,
    "pdf_content": TEST_PDF_BYTES,
}

# === Estados de Edição ===
TEST_EDIT_STATE = {
    "edit_avaliacao": "Nova avaliação editada",
    "edit_pontos": "Novos pontos editados",
    "edit_perguntas": "Novas perguntas editadas",
    "edit_criterios": "Novos critérios editados",
    "edit_riscos": "Novos riscos editados",
}

# === Configurações de Teste ===
TEST_CONFIG = {
    "TIMEOUT": 30,
    "RETRY_COUNT": 3,
    "MOCK_RETURN_VALUE": True,
}
