from fpdf import FPDF
from fpdf.enums import XPos, YPos
import pandas as pd
from datetime import datetime
import matplotlib.font_manager as fm


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
        self.cell(
            0,
            1,
            "",
            border="T",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.ln(5)
        self.set_draw_color(0, 0, 0)


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


def add_cover(pdf: PDF):
    """Cria a página de capa do relatório."""
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 24)
    pdf.cell(0, 80, "", border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(
        0,
        20,
        "Relatório de Análise de QA",
        border=0,
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(10)
    pdf.set_font("DejaVu", "B", 18)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(
        0,
        10,
        "QA Oráculo",
        border=0,
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(20)
    pdf.set_font("DejaVu", "I", 12)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(
        0,
        10,
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        border=0,
        align="C",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_text_color(0, 0, 0)


def add_section_title(pdf: PDF, text: str):
    """Adiciona um título de seção formatado."""
    pdf.set_font("DejaVu", "B", 16)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(
        0,
        12,
        text,
        border=0,
        align="L",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)


def generate_pdf_report(analysis_report: str, test_plan_df: pd.DataFrame) -> bytes:
    pdf = PDF()

    try:
        font_path = fm.findfont("DejaVu Sans")
        pdf.add_font("DejaVu", "", font_path)
        pdf.add_font("DejaVu", "B", font_path)
        pdf.add_font("DejaVu", "I", font_path)
    except Exception:
        raise RuntimeError("Fonte 'DejaVu Sans' não encontrada.")

    # 1. Adiciona a capa
    add_cover(pdf)

    # 2. Adiciona a primeira página de conteúdo
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- Seção 1: Análise ---
    add_section_title(pdf, "1. Análise de Qualidade da User Story")
    pdf.set_font("DejaVu", "", 12)
    pdf.multi_cell(0, 8, clean_text_for_pdf(analysis_report))
    pdf.ln(10)

    # --- Seção 2: Plano de Testes Detalhado ---
    add_section_title(pdf, "2. Plano de Testes Detalhado")

    if not test_plan_df.empty:
        friendly_names = {
            "criterio_de_aceitacao_relacionado": "Critérios Relacionados",
            "justificativa_acessibilidade": "Justificativa de Acessibilidade",
            "titulo": "Título",
            "prioridade": "Prioridade",
            "cenario": "Cenário",
        }

        for index, row in test_plan_df.iterrows():
            test_id = row.get("id", f"CT-{index+1:03d}")
            test_id = clean_text_for_pdf(test_id)

            pdf.set_font("DejaVu", "B", 12)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(
                0,
                10,
                f"Caso de Teste: {test_id}",
                border=1,
                fill=True,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )

            for col_name in test_plan_df.columns:
                if col_name.lower() == "id":
                    continue

                cell_value = row.get(col_name, "")
                cell_value_str = str(cell_value)
                if cell_value_str.strip() == "" or cell_value_str.lower() == "nan":
                    continue

                label = friendly_names.get(
                    col_name, col_name.replace("_", " ").title()
                )

                pdf.set_font("DejaVu", "B", 11)
                pdf.cell(50, 8, f"{label}:", border=0)

                pdf.set_font("DejaVu", "", 11)
                pdf.multi_cell(0, 8, clean_text_for_pdf(cell_value_str), border=0)
                pdf.ln(2)

            pdf.divider()

    return bytes(pdf.output())
