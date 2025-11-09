from __future__ import annotations

import copy
from typing import Any, Dict, List

TEST_USER_STORY = "Como usuário, quero fazer login no sistema"
TEST_ANALYSIS_REPORT = "Relatório de análise de teste"
TEST_PLAN_REPORT = "Plano de testes gerado"
TEST_PDF_BYTES = b"fake_pdf_content"
TEST_EXCEL_BYTES = b"fake_excel_content"
TEST_FILENAME = "fake.xlsx"

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

MOCK_COLUMNS_COUNT = {
    "DOWNLOADS": 5,
    "AZURE": 2,
    "FALLBACK": 3,
}

TEST_MESSAGES = {
    "WARNING": "Atenção: User story não fornecida",
    "SUCCESS": "Análise concluída com sucesso",
    "ERROR": "Erro ao processar análise",
}

TEST_EXPORT_CONFIG = {
    "filename": TEST_FILENAME,
    "excel_content": TEST_EXCEL_BYTES,
    "pdf_content": TEST_PDF_BYTES,
}

TEST_EDIT_STATE = {
    "edit_avaliacao": "Nova avaliação editada",
    "edit_pontos": "Novos pontos editados",
    "edit_perguntas": "Novas perguntas editadas",
    "edit_criterios": "Novos critérios editados",
    "edit_riscos": "Novos riscos editados",
}

TEST_CONFIG = {
    "TIMEOUT": 30,
    "RETRY_COUNT": 3,
    "MOCK_RETURN_VALUE": True,
}


def clone(data: Any) -> Any:
    """Retorna uma cópia profunda do objeto informado."""
    return copy.deepcopy(data)


def make_analysis_state() -> Dict[str, Any]:
    """Retorna um estado de análise independente para uso no teste."""
    return clone(TEST_ANALYSIS_STATE)


def make_session_state_basic() -> Dict[str, Any]:
    """Retorna uma cópia do estado de sessão básico."""
    return clone(TEST_SESSION_STATE_BASIC)


def make_session_state_finished() -> Dict[str, Any]:
    """Retorna uma cópia do estado de sessão finalizado."""
    return clone(TEST_SESSION_STATE_FINISHED)


def make_test_plan_records() -> List[Dict[str, Any]]:
    """Retorna registros básicos de plano de teste."""
    return clone(TEST_DF_BASIC)
