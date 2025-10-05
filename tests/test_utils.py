# test/test_utils.py
import datetime
import io
import unittest
from io import BytesIO
from unittest.mock import patch

import pandas as pd
import pytest

import utils
from app import _ensure_bytes
from utils import (
    clean_markdown_report,
    gerar_nome_arquivo_seguro,
    get_flexible,
    normalizar_string,
    parse_json_strict,
    preparar_df_para_azure_xlsx,
    preparar_df_para_zephyr_xlsx,
    to_excel,
)


class TestUtilsFunctions(unittest.TestCase):
    def setUp(self):
        """Configura dados de teste antes de cada execução."""
        print("\n--- Configurando dados de teste para utils ---")
        self.sample_df = pd.DataFrame(
            [
                {
                    "titulo": "Caminho Feliz",
                    "prioridade": "alta",
                    "cenario": "Passo 1\nPasso 2",
                },
                {
                    "titulo": "Caminho Infeliz",
                    "prioridade": "média",
                    "cenario": "Passo A",
                },
            ]
        )

    def test_normalizar_string(self):
        print("--- Testando a normalização de strings ---")
        self.assertEqual(
            normalizar_string("usuário e relatório com ç e ã"),
            "usuario e relatorio com c e a",
        )

    def test_get_flexible(self):
        print("--- Testando a busca flexível de chaves ---")
        data = {"avaliacao_geral": "Bom", "riscos": ["Risco 1"]}

        # Caso 1: Encontra a chave primária
        self.assertEqual(
            get_flexible(data, ["avaliacao_geral", "avaliacao"], "Padrão"), "Bom"
        )

        # Caso 2: Encontra a chave alternativa
        self.assertEqual(
            get_flexible(data, ["riscos_e_dependencias", "riscos"], []), ["Risco 1"]
        )

        # Caso 3: Nenhuma chave encontrada, retorna o padrão
        self.assertEqual(
            get_flexible(data, ["pontos_ambiguos", "ambiguidades"], []), []
        )

        # Caso 4: A entrada não é um dicionário, retorna o padrão
        self.assertEqual(get_flexible(None, ["chave"], "Padrão"), "Padrão")
        self.assertEqual(get_flexible([], ["chave"], "Padrão"), "Padrão")

    def test_preparar_df_para_azure_xlsx(self):
        print("--- Testando a formatação para Azure DevOps ---")
        df_azure = preparar_df_para_azure_xlsx(self.sample_df, "P\\T", "J")
        self.assertEqual(len(df_azure), 2 + 2 + 1)

    def test_preparar_df_para_zephyr_xlsx(self):
        print("--- Testando a formatação para Jira Zephyr ---")
        df_zephyr = preparar_df_para_zephyr_xlsx(self.sample_df, "High", "s1", "Desc")
        self.assertEqual(len(df_zephyr), 2 + 1)

    @patch("utils.datetime")
    def test_gerar_nome_arquivo_seguro(self, mock_datetime):
        print("--- Testando a geração de nome de arquivo seguro ---")
        mock_now = datetime.datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        self.assertEqual(
            gerar_nome_arquivo_seguro("usuário", "txt"), "usuario_20240101_120000.txt"
        )
        self.assertEqual(gerar_nome_arquivo_seguro("", "md"), "relatorio_qa_oraculo.md")

    def test_preparar_df_azure_com_cenario_vazio(self):
        df = pd.DataFrame([{"titulo": "CT Vazio", "cenario": ""}])
        self.assertEqual(len(preparar_df_para_azure_xlsx(df, "P", "A")), 1)

    def test_preparar_df_zephyr_com_cenario_vazio(self):
        df = pd.DataFrame([{"titulo": "CT Vazio", "cenario": ""}])
        self.assertTrue(preparar_df_para_zephyr_xlsx(df, "L", "b", "D").empty)

    def test_preparar_df_azure_com_cenario_em_lista(self):
        df = pd.DataFrame([{"cenario": ["Passo 1", "Passo 2"]}])
        self.assertEqual(len(preparar_df_para_azure_xlsx(df, "P", "A")), 3)

    def test_preparar_df_azure_com_dados_ausentes(self):
        df = pd.DataFrame([{"cenario": "Passo"}])
        df_azure = preparar_df_para_azure_xlsx(df, "P", "A")
        self.assertEqual(df_azure.iloc[0]["Title"], "Caso de Teste 1")
        self.assertEqual(df_azure.iloc[0]["Priority"], "2")
        df_inv = pd.DataFrame([{"prioridade": "urgente", "cenario": "Passo"}])
        self.assertEqual(
            preparar_df_para_azure_xlsx(df_inv, "P", "A").iloc[0]["Priority"], "2"
        )

    def test_preparar_df_zephyr_com_dados_ausentes(self):
        df = pd.DataFrame([{"cenario": "Passo"}])
        self.assertEqual(
            preparar_df_para_zephyr_xlsx(df, "L", "b", "D").iloc[0]["Summary"],
            "Caso de Teste 1",
        )

    def test_to_excel_conversion(self):
        source_df = pd.DataFrame({"ID": [1, 2], "Nome": ["Teste A", "Teste B"]})
        sheet_name = "MinhaPlanilha"
        excel_bytes = to_excel(source_df, sheet_name)
        self.assertIsInstance(excel_bytes, bytes)
        self.assertTrue(len(excel_bytes) > 0)
        result_df = pd.read_excel(io.BytesIO(excel_bytes), sheet_name=sheet_name)
        pd.testing.assert_frame_equal(source_df, result_df)


class TestUtilsExtras(unittest.TestCase):
    def test_clean_markdown_report_completo(self):
        texto = "```markdown\n# Título\n```"
        esperado = "# Título"
        self.assertEqual(clean_markdown_report(texto), esperado)

    def test_clean_markdown_report_sem_cercas(self):
        texto = "# Apenas texto normal"
        self.assertEqual(clean_markdown_report(texto), "# Apenas texto normal")

    def test_clean_markdown_report_nao_string(self):
        self.assertEqual(clean_markdown_report(None), "")

    def test_parse_json_strict_valido(self):
        texto = '{"key": "value"}'
        self.assertEqual(parse_json_strict(texto), {"key": "value"})

    def test_parse_json_strict_com_cercas(self):
        texto = '```json\n{"key": "value"}\n```'
        self.assertEqual(parse_json_strict(texto), {"key": "value"})

    def test_parse_json_strict_invalido(self):
        # Especifica o tipo de exceção esperado (ValueError), evitando o erro B017
        with self.assertRaises(ValueError):
            parse_json_strict("não é json")


def test_parse_json_strict_com_cercas_incompletas():
    texto = '```json\n{"key": "value"}'
    assert utils.parse_json_strict(texto) == {"key": "value"}


def test_parse_json_strict_invalido_levanta():
    # Usa o tipo de exceção específico para evitar B017
    with pytest.raises(ValueError):
        utils.parse_json_strict("não é json válido")


def test_gerar_nome_arquivo_seguro_caracteres_invalidos():
    nome = gerar_nome_arquivo_seguro("História/Inválida:*?", "txt")
    assert nome.endswith(".txt")
    assert "/" not in nome and ":" not in nome


def test_to_excel_dataframe_vazio():
    df = pd.DataFrame()
    buf = to_excel(df, sheet_name="Vazio")
    assert isinstance(buf, (bytes, bytearray))


def test_ensure_bytes_com_getvalue():
    """Testa se _ensure_bytes funciona com objetos tipo BytesIO."""
    obj = BytesIO(b"dados em bytes")
    assert _ensure_bytes(obj) == b"dados em bytes"


def test_ensure_bytes_com_bytes_diretos():
    """Testa se _ensure_bytes lida corretamente com bytes e bytearray."""
    assert _ensure_bytes(b"ja sou bytes") == b"ja sou bytes"
    assert _ensure_bytes(bytearray(b"sou bytearray")) == b"sou bytearray"


# ============================================================
# 🔥 Cobertura 100% dos ramos de preparar_df_para_azure_xlsx
# ============================================================

EXPECTED_AZURE_ROWS_WHEN_ONLY_QUANDO = 2  # 1 abertura + 1 step "Quando"
EXPECTED_ZEPHYR_STEPS_LIST = 2  # Dois passos na lista de cenário


def test_azure_quando_sem_entao():
    """Cobre o caso em que há 'Quando' sem 'Então'."""
    df = pd.DataFrame(
        [{"titulo": "CT Sem Então", "cenario": ["Quando clico no botão"]}]
    )
    result = preparar_df_para_azure_xlsx(df, "Area", "Dev")
    assert len(result) == EXPECTED_AZURE_ROWS_WHEN_ONLY_QUANDO
    assert any("Quando clico" in str(x) for x in result["Step Action"])


def test_azure_com_e_entre_quando_e_entao():
    """Cobre o caso com 'E' entre 'Quando' e 'Então'."""
    df = pd.DataFrame(
        [
            {
                "titulo": "CT E Entre",
                "cenario": [
                    "Quando faço login",
                    "E preencho dados",
                    "Então vejo mensagem",
                ],
            }
        ]
    )
    result = preparar_df_para_azure_xlsx(df, "Area", "Dev")
    assert any("E preencho" in str(x) for x in result["Step Action"])


def test_azure_com_e_apos_entao():
    """Cobre o caso com 'E' após 'Então'."""
    df = pd.DataFrame(
        [
            {
                "titulo": "CT E Depois",
                "cenario": [
                    "Dado que estou logado",
                    "Então vejo a tela",
                    "E a cor está correta",
                ],
            }
        ]
    )
    result = preparar_df_para_azure_xlsx(df, "Area", "Dev")
    assert any("E a cor está correta" in str(x) for x in result["Step Expected"])


def test_azure_entao_sem_quando():
    """Cobre o caso em que há 'Então' sem 'Quando' anterior."""
    df = pd.DataFrame([{"titulo": "CT Entao", "cenario": ["Então algo acontece"]}])
    result = preparar_df_para_azure_xlsx(df, "Area", "Dev")
    assert any("Então algo acontece" in str(x) for x in result["Step Expected"])


def test_azure_fallback_step():
    """Cobre o caso de fallback (nenhum Dado/Quando/Então/E)."""
    df = pd.DataFrame([{"titulo": "CT Outro", "cenario": ["Verifico o sistema"]}])
    result = preparar_df_para_azure_xlsx(df, "Area", "Dev")
    assert any("Verifico o sistema" in str(x) for x in result["Step Action"])


def test_zephyr_cenario_lista():
    """Garante cobertura de cenario em lista no Zephyr."""
    df = pd.DataFrame([{"titulo": "CT Lista", "cenario": ["Passo 1", "Passo 2"]}])
    result = preparar_df_para_zephyr_xlsx(df, "High", "QA", "Descrição")
    assert len(result) == EXPECTED_ZEPHYR_STEPS_LIST


def test_zephyr_cenario_none():
    """Cobre o caso de cenário None em Zephyr (retorna vazio)."""
    df = pd.DataFrame([{"titulo": "CT None", "cenario": None}])
    result = preparar_df_para_zephyr_xlsx(df, "High", "QA", "Desc")
    assert result.empty
