# pdf_generator.py (Sua versão, com a correção final)

from fpdf import FPDF
import pandas as pd
from datetime import datetime
import matplotlib.font_manager as fm

# -------------------------------
# Classe PDF com cabeçalho/rodapé
# -------------------------------
class PDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('DejaVu', 'B', 12)
            self.cell(0, 10, 'Relatório de Análise de QA - QA Oráculo', 0, 1, 'C')
            self.ln(5)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font('DejaVu', 'I', 8)
            self.set_text_color(100, 100, 100)
            generation_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.cell(0, 10, f'Gerado em: {generation_date}', 0, 0, 'L')
            self.cell(0, 10, f'Página {self.page_no()-1}', 0, 0, 'R')
            self.set_text_color(0, 0, 0)

# -------------------------------
# Funções utilitárias
# -------------------------------
def clean_text_for_pdf(text: str) -> str:
    """Limpa emojis não suportados e substitui por símbolos/textos."""
    replacements = {
        "📌": "- ", "✅": "[OK] ", "🎯": "-> ", "•": "-",
        "🔍": "[Análise] ", "❓": "[?] ", "🚩": "[Alerta] "
    }
    for emoji, replacement in replacements.items():
        text = text.replace(emoji, replacement)
    return text

def add_cover(pdf: PDF):
    """Cria uma página de capa para o relatório."""
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 24)
    pdf.cell(0, 80, '', 0, 1) # Espaçador
    pdf.cell(0, 20, 'Relatório de Análise de QA', 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font('DejaVu', 'B', 18)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, 'QA Oráculo', 0, 1, 'C')
    pdf.ln(20)
    pdf.set_font('DejaVu', 'I', 12)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 10, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 1, 'C')
    pdf.set_text_color(0, 0, 0)
    # A próxima página é adicionada automaticamente no fluxo principal

def add_section_title(pdf: PDF, text: str):
    """Adiciona um título de seção formatado."""
    pdf.set_font('DejaVu', 'B', 16)
    pdf.set_text_color(0, 51, 102) # Azul escuro
    pdf.cell(0, 12, text, border=0, ln=1, align='L')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

# -------------------------------
# Função principal do relatório
# -------------------------------
def generate_pdf_report(analysis_report: str, test_plan_df: pd.DataFrame) -> bytes:
    pdf = PDF()
    
    try:
        font_path = fm.findfont('DejaVu Sans')
    except Exception:
        raise RuntimeError("Fonte 'DejaVu Sans' não encontrada.")
        
    pdf.add_font('DejaVu', '', font_path, uni=True)
    pdf.add_font('DejaVu', 'B', font_path, uni=True)
    pdf.add_font('DejaVu', 'I', font_path, uni=True)

    # Capa
    add_cover(pdf)

    # Inicia a primeira página de conteúdo
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- Seção 1: Análise da User Story ---
    add_section_title(pdf, "1. Análise de Qualidade da User Story")
    pdf.set_font('DejaVu', '', 12)
    analysis_report_cleaned = clean_text_for_pdf(analysis_report)
    pdf.multi_cell(0, 8, analysis_report_cleaned)
    pdf.ln(10)

    # --- Seção 2: Plano de Testes Detalhado ---
    add_section_title(pdf, "2. Plano de Testes Detalhado")

    if not test_plan_df.empty and len(test_plan_df.columns) > 0:
        page_width = pdf.w - pdf.l_margin - pdf.r_margin
        col_count = len(test_plan_df.columns)

        if col_count == 4:
            weights = [0.08, 0.22, 0.45, 0.25]
        else:
            weights = [1/col_count] * col_count
        
        col_widths = [w * page_width for w in weights]

        pdf.set_font('DejaVu', 'B', 10)
        pdf.set_fill_color(200, 220, 255)
        for i, header in enumerate(test_plan_df.columns):
            pdf.cell(col_widths[i], 10, str(header), 1, 0, 'C', fill=True)
        pdf.ln()

        pdf.set_font('DejaVu', '', 10)
        for row_index, row in test_plan_df.iterrows():
            cleaned_row = [clean_text_for_pdf(str(item)) for item in row]
            
            # Define a cor de preenchimento para a linha
            if row_index % 2 == 0:
                pdf.set_fill_color(245, 245, 245)
                fill = True
            else:
                fill = False

            max_lines = 0
            for i, item in enumerate(cleaned_row):
                lines = len(pdf.multi_cell(col_widths[i], 5, item, split_only=True))
                if lines > max_lines:
                    max_lines = lines
            
            row_height = max(10, max_lines * 5.5) # Garante uma altura mínima

            for i, item in enumerate(cleaned_row):
                align = 'C' if i == 0 else 'L'
                pdf.multi_cell(col_widths[i], row_height, item, border=1, align=align,
                               new_x="RIGHT", new_y="TOP", fill=fill)
            pdf.ln(row_height)

    return bytes(pdf.output())