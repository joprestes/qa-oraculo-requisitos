import pytest
import pandas as pd
import pdf_generator

def test_generate_pdf_report_quando_fonte_nao_existe(monkeypatch):
    def fake_findfont(name):
        raise Exception("Fonte não encontrada")
    monkeypatch.setattr("matplotlib.font_manager.findfont", fake_findfont)

    with pytest.raises(RuntimeError):
        pdf_generator.generate_pdf_report("Relatório", pd.DataFrame())
