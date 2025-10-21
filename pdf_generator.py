# ==========================================================
# pdf_generator.py — Gerador de Relatórios PDF Acessíveis
# ==========================================================
# 📘 Responsável por criar relatórios em PDF a partir das análises
#    e planos de teste gerados pela IA.
# ----------------------------------------------------------
#  • Compatível com Unicode (fonte DejaVu)
#  • Inclui capa, seções e tabela única de casos de teste
#  • Padrão QA Oráculo: acessível, limpo e automatizável
# ==========================================================

from datetime import datetime
from typing import Any

import matplotlib.font_manager as fm
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos


# ==========================================================
# Constantes internas
# ==========================================================

_ANALYSIS_FALLBACK_MESSAGE = "⚠️ Relatório de análise não disponível."


# ==========================================================
# Classe base do PDF
# ==========================================================
class PDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("DejaVu", "B", 12)
            self.cell(
                0,
                10,
                "Relatório de Análise de QA - QA Oráculo",
                border=0,
                align="C",
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
            self.ln(5)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("DejaVu", "I", 8)
            self.set_text_color(100, 100, 100)
            generation_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.cell(
                0,
                10,
                f"Gerado em: {generation_date}",
                border=0,
                align="L",
                new_x=XPos.RIGHT,
                new_y=YPos.TOP,
            )
            self.cell(
                0,
                10,
                f"Página {self.page_no()-1}",
                border=0,
                align="R",
                new_x=XPos.RIGHT,
                new_y=YPos.TOP,
            )
            self.set_text_color(0, 0, 0)

    def divider(self):
        """Desenha uma linha divisória suave."""
        self.ln(3)
        self.set_draw_color(220, 220, 220)
        self.cell(0, 1, "", border="T", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)
        self.set_draw_color(0, 0, 0)


# ==========================================================
# Funções auxiliares
# ==========================================================
def clean_text_for_pdf(text: str) -> str:
    """Limpa emojis e garante que o texto seja uma string."""
    text = str(text)
    replacements = {
        "📌": "- ",
        "✅": "[OK] ",
        "🎯": "-> ",
        "•": "-",
        "🔍": "[Análise] ",
        "❓": "[?] ",
        "🚩": "[Alerta] ",
    }
    for emoji, replacement in replacements.items():
        text = text.replace(emoji, replacement)
    return text


def add_cover(pdf: FPDF):
    """Cria a página de capa do relatório."""
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 24)
    pdf.cell(0, 80, "", border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 20, "Relatório de Análise de QA", border=0, align="C")
    pdf.ln(10)
    pdf.set_font("DejaVu", "B", 18)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "QA Oráculo", border=0, align="C")
    pdf.ln(20)
    pdf.set_font("DejaVu", "I", 12)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(
        0,
        10,
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        border=0,
        align="C",
    )
    pdf.set_text_color(0, 0, 0)


def add_section_title(pdf: FPDF, text: str):
    """Adiciona um título de seção formatado."""
    pdf.set_font("DejaVu", "B", 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 12, text, border=0, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)


# ==========================================================
# Nova função — Tabela única e completa de casos de teste
# ==========================================================
def add_test_case_table(pdf: FPDF, df: pd.DataFrame):
    """Adiciona uma tabela única com todas as informações dos casos de teste (ordem corrigida)."""
    if df.empty:
        return

    # 🔹 Remove possíveis duplicatas ou cabeçalhos residuais vindos do Markdown da IA
    df = df.loc[:, ~df.columns.duplicated()].copy()

    add_section_title(pdf, "2. Casos de Teste (Resumo Completo)")
    pdf.set_font("DejaVu", "B", 10)
    pdf.set_fill_color(230, 230, 230)

    headers = [
        "ID",
        "Título",
        "Prioridade",
        "Critério de Aceitação Relacionado",
        "Cenário (Gherkin)",
        "Justificativa de Acessibilidade",
    ]
    col_widths = [18, 45, 22, 55, 70, 55]

    # Cabeçalho
    for header, width in zip(headers, col_widths, strict=False):
        pdf.cell(width, 8, header, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("DejaVu", "", 9)

    for _, row in df.iterrows():
        pdf.cell(col_widths[0], 8, str(row.get("id", "")), border=1)
        pdf.cell(col_widths[1], 8, str(row.get("titulo", ""))[:40], border=1)
        pdf.cell(col_widths[2], 8, str(row.get("prioridade", "")), border=1)

        pdf.cell(
            col_widths[3],
            8,
            str(row.get("criterio_de_aceitacao_relacionado", ""))[:40],
            border=1,
        )

        # Cenário (multi-linha)
        cenario = row.get("cenario", "")
        if isinstance(cenario, list):
            cenario = "\n".join(cenario)
        pdf.multi_cell(col_widths[4], 6, clean_text_for_pdf(str(cenario)), border=1)

        pdf.cell(
            col_widths[5],
            8,
            str(row.get("justificativa_acessibilidade", ""))[:40],
            border=1,
        )
        pdf.ln()


# ==========================================================
# Funções internas auxiliares
# ==========================================================


def _normalize_test_plan_df(test_plan_df: Any) -> pd.DataFrame:
    """Garante que os dados do plano de testes sejam convertidos para DataFrame."""

    if test_plan_df is None:
        return pd.DataFrame()

    if isinstance(test_plan_df, pd.DataFrame):
        return test_plan_df

    if isinstance(test_plan_df, list):
        return pd.DataFrame(test_plan_df)

    if isinstance(test_plan_df, dict):
        return pd.DataFrame([test_plan_df])

    raise TypeError(
        "test_plan_df deve ser um pandas.DataFrame, uma lista de registros ou um dicionário."
    )


# ==========================================================
# Função principal de geração do PDF
# ==========================================================
def generate_pdf_report(
    analysis_report: str | None,
    test_plan_df: pd.DataFrame | list[dict[str, Any]] | dict[str, Any] | None,
) -> bytes:
    """Gera o relatório PDF completo (Análise + Casos de Teste)."""
    pdf = PDF()

    try:
        font_path = fm.findfont("DejaVu Sans")
        pdf.add_font("DejaVu", "", font_path)
        pdf.add_font("DejaVu", "B", font_path)
        pdf.add_font("DejaVu", "I", font_path)
    except Exception as e:
        raise RuntimeError("Fonte 'DejaVu Sans' não encontrada.") from e

    # 1. Capa
    add_cover(pdf)

    # 2. Conteúdo principal
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- Seção 1: Análise da User Story ---
    add_section_title(pdf, "1. Análise de Qualidade da User Story")
    pdf.set_font("DejaVu", "", 12)
    analysis_text = clean_text_for_pdf(analysis_report or _ANALYSIS_FALLBACK_MESSAGE)
    if not analysis_text.strip():
        analysis_text = clean_text_for_pdf(_ANALYSIS_FALLBACK_MESSAGE)
    pdf.multi_cell(0, 8, analysis_text)
    pdf.ln(10)

    # --- Seção 2: Casos de Teste ---
    normalized_df = _normalize_test_plan_df(test_plan_df)
    if not normalized_df.empty:
        add_test_case_table(pdf, normalized_df)

    return bytes(pdf.output())
