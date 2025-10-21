# tests/test_pdf_generator.py

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from fpdf.enums import XPos, YPos

import pdf_generator
from pdf_generator import (
    PDF,
    add_cover,
    add_section_title,
    clean_text_for_pdf,
    generate_pdf_report,
)

# ===================================================================
# 1. Testes para Funções Simples
# ===================================================================


def test_clean_text_for_pdf():
    assert clean_text_for_pdf("Texto com 📌 emoji") == "Texto com -  emoji"
    assert clean_text_for_pdf(123) == "123"
    assert clean_text_for_pdf(None) == ""
    assert clean_text_for_pdf(float("nan")) == ""


# ===================================================================
# 2. Testes para Funções que Manipulam o PDF
#    (Usaremos um MagicMock para simular o objeto PDF)
# ===================================================================


def test_add_cover():
    mock_pdf = MagicMock()
    add_cover(mock_pdf)
    mock_pdf.add_page.assert_called_once()
    assert mock_pdf.set_font.called
    assert mock_pdf.cell.called


def test_add_section_title():
    mock_pdf = MagicMock()
    add_section_title(mock_pdf, "Título Teste")
    mock_pdf.cell.assert_called_with(
        0, 12, "Título Teste", border=0, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT
    )


# ===================================================================
# 3. Testes para os Métodos da Nossa Classe PDF Customizada
#    (Testamos os métodos como funções normais, passando 'self' como um mock)
# ===================================================================


def test_pdf_header():
    mock_self = MagicMock()

    # Cenário 1: Primeira página, não deve fazer nada
    mock_self.page_no.return_value = 1
    PDF.header(mock_self)
    mock_self.cell.assert_not_called()

    # Cenário 2: Segunda página, deve adicionar o header
    mock_self.page_no.return_value = 2
    PDF.header(mock_self)
    mock_self.cell.assert_called_once()
    mock_self.set_font.assert_called_once()


def test_pdf_footer():
    mock_self = MagicMock()

    # Cenário 1: Primeira página, não faz nada
    mock_self.page_no.return_value = 1
    PDF.footer(mock_self)
    mock_self.cell.assert_not_called()

    # Cenário 2: Segunda página, deve adicionar o footer
    mock_self.page_no.return_value = 2
    PDF.footer(mock_self)
    assert mock_self.cell.call_count == 2  # noqa: PLR2004
    mock_self.set_font.assert_called_once()


def test_pdf_divider():
    mock_self = MagicMock()
    PDF.divider(mock_self)
    mock_self.cell.assert_called_with(
        0, 1, "", border="T", new_x=XPos.LMARGIN, new_y=YPos.NEXT
    )
    assert mock_self.ln.called


# ===================================================================
# 4. Testes para a Função Principal (Fluxo Geral)
# ===================================================================


@patch("pdf_generator.PDF")
@patch("matplotlib.font_manager.findfont", return_value="dummy_path.ttf")
def test_generate_pdf_report_fluxo_completo(mock_findfont, mock_PDF):
    mock_pdf_instance = MagicMock()
    mock_PDF.return_value = mock_pdf_instance
    analysis_report = "Relatório"
    test_plan_df = pd.DataFrame([{"id": "CT-001"}])

    mock_pdf_instance.output.return_value = b"pdf"

    generate_pdf_report(analysis_report, test_plan_df)

    mock_PDF.assert_called_once()
    mock_pdf_instance.add_font.assert_called()
    assert mock_pdf_instance.multi_cell.called
    mock_pdf_instance.output.assert_called_once()


@patch("pdf_generator.PDF")
@patch("matplotlib.font_manager.findfont", return_value="dummy_path.ttf")
def test_generate_pdf_report_df_vazio(mock_findfont, mock_PDF):
    mock_pdf_instance = MagicMock()
    mock_PDF.return_value = mock_pdf_instance

    mock_pdf_instance.output.return_value = b"pdf"

    generate_pdf_report("Relatório", pd.DataFrame())

    # O loop do DataFrame não deve ser executado
    mock_pdf_instance.divider.assert_not_called()
    mock_pdf_instance.output.assert_called_once()


def test_generate_pdf_report_sem_fonte(monkeypatch):
    def _raise_font_error(_):
        raise ValueError("Fonte não encontrada")

    monkeypatch.setattr(pdf_generator.fm, "findfont", _raise_font_error)

    with pytest.raises(RuntimeError, match=r"Fonte 'DejaVu Sans' não encontrada\."):
        generate_pdf_report("Relatório", pd.DataFrame())


def test_pdf_falha_fonte(monkeypatch):
    def _raise_generic_error(_):
        raise Exception("Fonte não encontrada")

    monkeypatch.setattr(pdf_generator.fm, "findfont", _raise_generic_error)

    with pytest.raises(RuntimeError, match=r"Fonte 'DejaVu Sans' não encontrada\."):
        generate_pdf_report("texto", pd.DataFrame())


@patch("pdf_generator.add_test_case_table")
@patch("pdf_generator.PDF")
@patch("matplotlib.font_manager.findfont", return_value="dummy_path.ttf")
def test_generate_pdf_report_trata_entradas_vazias(
    mock_findfont, mock_PDF, mock_add_table
):
    mock_pdf_instance = MagicMock()
    mock_pdf_instance.output.return_value = b"pdf"
    mock_PDF.return_value = mock_pdf_instance

    resultado = generate_pdf_report(None, None)

    assert resultado == b"pdf"
    mock_pdf_instance.multi_cell.assert_called_with(
        0, 8, "⚠️ Relatório de análise não disponível."
    )
    mock_add_table.assert_not_called()


@patch("pdf_generator.add_test_case_table")
@patch("pdf_generator.PDF")
@patch("matplotlib.font_manager.findfont", return_value="dummy_path.ttf")
def test_generate_pdf_report_normaliza_iteraveis(
    mock_findfont, mock_PDF, mock_add_table
):
    mock_pdf_instance = MagicMock()
    mock_pdf_instance.output.return_value = b"pdf"
    mock_PDF.return_value = mock_pdf_instance

    generate_pdf_report("Relatório", [{"id": "CT-1", "titulo": "Caso"}])

    assert mock_add_table.call_count == 1
    _, df_passado = mock_add_table.call_args[0]
    assert isinstance(df_passado, pd.DataFrame)
    assert not df_passado.empty
