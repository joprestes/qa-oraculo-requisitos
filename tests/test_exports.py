import csv
import io
import locale
import unittest
from io import BytesIO

import pandas as pd
import pytest

from qa_core.app import _ensure_bytes
from qa_core.exports import (
    gerar_csv_azure_from_df,
    gerar_csv_testrail_from_df,
    preparar_df_para_zephyr_xlsx,
    to_excel,
)

EXPECTED_COLUMNS_COUNT = 10
EXPECTED_TEST_CASES_COUNT = 2


class TestExportsFunctions(unittest.TestCase):
    """Classe que testa as funções de exportação."""

    def setUp(self):
        """
         Executa antes de cada teste.
        Cria um DataFrame de exemplo que simula dois casos de teste:
        - Um cenário “feliz” (fluxo principal)
        - Um cenário “infeliz” (erro ou exceção esperada)
        """
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

    def test_preparar_df_para_zephyr_xlsx(self):
        """
         Testa se a função converte corretamente um DataFrame de cenários
        para o formato esperado pelo Jira Zephyr (planilha de importação).
        Espera-se que o número de linhas exportadas seja igual ao número
        de casos de teste + cabeçalho.
        """
        df_zephyr = preparar_df_para_zephyr_xlsx(self.sample_df, "High", "s1", "Desc")
        self.assertEqual(len(df_zephyr), 3)

    def test_to_excel_conversion(self):
        """
        Garante a integridade da função `to_excel`, verificando se:
          1️ O DataFrame é convertido para bytes.
          2️O arquivo pode ser reaberto e contém os mesmos dados originais.
        """
        source_df = pd.DataFrame({"ID": [1, 2], "Nome": ["Teste A", "Teste B"]})
        sheet_name = "MinhaPlanilha"

        #  Converte DataFrame → Excel (em bytes)
        excel_bytes = to_excel(source_df, sheet_name)

        #  Deve retornar bytes válidos
        self.assertIsInstance(excel_bytes, bytes)
        self.assertTrue(len(excel_bytes) > 0)

        #  Converte de volta para DataFrame e compara os dados
        result_df = pd.read_excel(io.BytesIO(excel_bytes), sheet_name=sheet_name)
        pd.testing.assert_frame_equal(source_df, result_df)


def test_gerar_csv_azure_from_df_basico(monkeypatch):
    """Valida estrutura, separador e ID vazio (locale PT-BR)."""
    df = pd.DataFrame(
        [
            {
                "titulo": "Login Válido",
                "prioridade": "Alta",
                "cenario": "Dado que o usuário acessa\nQuando insere credenciais\nEntão o login é bem-sucedido",
            }
        ]
    )

    monkeypatch.setattr(locale, "getlocale", lambda: ("pt_BR", "UTF-8"))
    csv_bytes = gerar_csv_azure_from_df(df, "Area/Teste", "QA Tester")
    csv_text = csv_bytes.decode("utf-8-sig")
    linhas = [linha for linha in csv_text.splitlines() if linha.strip()]

    # Cabeçalho correto
    assert linhas[0].startswith("ID;Work Item Type;Title;Test Step;")
    # Cada linha tem 10 colunas
    for linha in linhas[1:]:
        campos = linha.split(";")
        assert len(campos) == EXPECTED_COLUMNS_COUNT
    # ID vazio
    assert linhas[1].split(";")[0] == ""


def test_gerar_csv_azure_from_df_locale_en(monkeypatch):
    """Garante que o separador mude para vírgula em EN-US."""
    df = pd.DataFrame(
        [
            {
                "titulo": "Cadastro Usuário",
                "prioridade": "Low",
                "cenario": "Dado que o usuário abre o app\nEntão vê a tela inicial",
            },
        ]
    )

    monkeypatch.setattr(locale, "getlocale", lambda: ("en_US", "UTF-8"))
    csv_bytes = gerar_csv_azure_from_df(df, "Area/EN", "QA EN")
    csv_text = csv_bytes.decode("utf-8-sig")
    header = csv_text.splitlines()[0]

    assert "," in header
    assert ";" not in header


def test_gerar_csv_azure_from_df_vazio():
    """Garante que DataFrame vazio gera apenas cabeçalho."""
    df_vazio = pd.DataFrame()
    csv_bytes = gerar_csv_azure_from_df(df_vazio, "", "")
    csv_text = csv_bytes.decode("utf-8-sig").strip()
    linhas = csv_text.splitlines()

    assert len(linhas) == 1


def test_gerar_csv_testrail_from_df_completo():
    """Valida que o CSV do TestRail contém todas as colunas e mapeia passos/expected."""
    df = pd.DataFrame(
        [
            {
                "titulo": "Cadastro válido",
                "cenario": "Dado que o usuário acessa\nQuando preenche dados\nEntão recebe confirmação",
            },
            {
                "titulo": "Fluxo com lista",
                "cenario": ["Dado contexto", "Então resultado"],
            },
            {
                "titulo": "Fluxo sem passos",
                "cenario": None,
            },
            {
                "titulo": "Fluxo iniciando com então",
                "cenario": "Então deve exibir mensagem inicial",
            },
        ]
    )

    csv_bytes = gerar_csv_testrail_from_df(
        df,
        section="Backoffice",
        priority="High",
        template="Test Case (Steps)",
        references="PROJ-1",
    )
    csv_text = csv_bytes.decode("utf-8")
    reader = csv.reader(io.StringIO(csv_text))
    rows = list(reader)

    header = [
        "Title",
        "Section",
        "Template",
        "Type",
        "Priority",
        "Estimate",
        "References",
        "Steps",
        "Expected Result",
    ]
    assert rows[0] == header

    primeira = rows[1]
    assert primeira[0] == "Cadastro válido"
    assert primeira[1] == "Backoffice"
    assert primeira[2] == "Test Case (Steps)"
    assert primeira[3] == "Functional"
    assert primeira[4] == "High"
    assert primeira[6] == "PROJ-1"
    assert "Quando preenche dados" in primeira[7]
    assert primeira[7].count("\n") == 2
    assert "Então recebe confirmação" in primeira[8]

    segunda = rows[2]
    assert segunda[0] == "Fluxo com lista"
    assert segunda[7] == "Dado contexto\nEntão resultado"
    assert segunda[8] == "Então resultado"

    terceira = rows[3]
    assert terceira[0] == "Fluxo sem passos"
    assert terceira[7] == ""
    assert terceira[8] == ""

    quarta = rows[4]
    assert quarta[0] == "Fluxo iniciando com então"
    assert quarta[7] == "Então deve exibir mensagem inicial"
    assert quarta[8] == "Então deve exibir mensagem inicial"


def test_gerar_csv_testrail_from_df_vazio():
    """DataFrame vazio ou None deve retornar apenas o cabeçalho."""
    vazio = pd.DataFrame()
    texto = gerar_csv_testrail_from_df(vazio).decode("utf-8")
    reader = csv.reader(io.StringIO(texto))
    rows_vazio = list(reader)
    assert rows_vazio == [
        [
            "Title",
            "Section",
            "Template",
            "Type",
            "Priority",
            "Estimate",
            "References",
            "Steps",
            "Expected Result",
        ]
    ]

    texto_none = gerar_csv_testrail_from_df(None).decode("utf-8")
    reader_none = csv.reader(io.StringIO(texto_none))
    rows_none = list(reader_none)
    assert rows_none == rows_vazio


def test_gerar_csv_azure_from_df_multiplos_casos(monkeypatch):
    """Cada linha do DF deve gerar um Test Case separado."""
    df = pd.DataFrame(
        [
            {
                "titulo": "CT 1",
                "prioridade": "Alta",
                "cenario": "Dado passo 1\nEntão ok",
            },
            {
                "titulo": "CT 2",
                "prioridade": "Baixa",
                "cenario": "Dado passo 2\nEntão outro ok",
            },
        ]
    )

    monkeypatch.setattr(locale, "getlocale", lambda: ("pt_BR", "UTF-8"))
    csv_bytes = gerar_csv_azure_from_df(df, "Area", "QA")
    csv_text = csv_bytes.decode("utf-8-sig")
    linhas = [linha for linha in csv_text.splitlines() if "Test Case" in linha]

    assert len(linhas) == EXPECTED_TEST_CASES_COUNT


def test_to_excel_dataframe_vazio():
    """
     Mesmo um DataFrame vazio deve gerar um arquivo Excel válido.
    A função deve retornar um buffer de bytes, não lançar exceção.
    """
    df = pd.DataFrame()
    buf = to_excel(df, sheet_name="Vazio")
    assert isinstance(buf, (bytes | bytearray))


def test_ensure_bytes_com_getvalue():
    """
     Testa a função `_ensure_bytes` com objetos que possuem
    o método `getvalue()`, como `BytesIO`.
    O retorno deve ser exatamente o conteúdo em bytes.
    """
    obj = BytesIO(b"dados em bytes")
    assert _ensure_bytes(obj) == b"dados em bytes"


def test_ensure_bytes_com_bytes_diretos():
    """
     Verifica o comportamento de `_ensure_bytes` quando recebe
    diretamente valores já em bytes ou bytearray.
    A função deve apenas retorná-los sem modificações.
    """
    assert _ensure_bytes(b"ja sou bytes") == b"ja sou bytes"
    assert _ensure_bytes(bytearray(b"sou bytearray")) == b"sou bytearray"


def test_ensure_bytes_tipo_invalido():
    """
     Força `_ensure_bytes` a lidar com tipos inesperados (int, dict).
    A função deve converter qualquer tipo não suportado em bytes
    chamando `str()` internamente.
    """
    assert _ensure_bytes(123) == b"123"
    # Para dicionários, o retorno deve conter o caractere “{”
    assert b"{" in _ensure_bytes({"a": 1})


def test_gerar_csv_azure_df_vazio_e_prioridade_invalida():
    df_vazio = pd.DataFrame()
    csv_bytes = gerar_csv_azure_from_df(df_vazio, "Area", "Dev")
    assert b"Work Item Type" in csv_bytes  # só header

    df_invalida = pd.DataFrame(
        [{"titulo": "CT", "cenario": "Dado algo", "prioridade": "urgente"}]
    )
    csv_bytes2 = gerar_csv_azure_from_df(df_invalida, "Area", "Dev")
    text = csv_bytes2.decode("utf-8-sig")
    # deve cair no default_priority ("2")
    assert ";2;" in text or ",2," in text


def test_gerar_csv_azure_locale_invalido(monkeypatch):
    """
     Força uma exceção na detecção do locale para garantir que
    a função `gerar_csv_azure_from_df` utilize o fallback padrão.
    Mesmo sem locale válido, o CSV deve ser gerado corretamente.
    """
    df = pd.DataFrame([{"titulo": "CT", "cenario": "Quando faço algo"}])

    # Simula falha no locale.getlocale()
    monkeypatch.setattr("locale.getlocale", lambda: (None, None))

    csv_bytes = gerar_csv_azure_from_df(df, "Area", "QA")

    #  Ainda deve retornar um arquivo válido
    assert isinstance(csv_bytes, (bytes | bytearray))
    assert b"Test Case" in csv_bytes


def test_to_excel_erro_salvar(monkeypatch):
    """
     Força um erro interno no salvamento do Excel para cobrir o bloco `except`.
    Garante que o erro seja propagado corretamente como ValueError.
    """

    df = pd.DataFrame({"A": [1]})

    # Classe fictícia que simula uma falha ao salvar o arquivo
    class DummyWriter:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def save(self):
            raise ValueError("Erro simulado")

    # Substitui o ExcelWriter do pandas pela classe DummyWriter
    monkeypatch.setattr("pandas.ExcelWriter", lambda *a, **k: DummyWriter())

    with pytest.raises(ValueError):
        to_excel(df, "Sheet1")


def test_gerar_csv_azure_quando_sem_entao():
    """
     Cobre o cenário em que existe um passo 'Quando' mas não há
    passo 'Então'. O CSV ainda deve ser gerado e conter o passo único.
    """
    df = pd.DataFrame(
        [{"titulo": "CT incompleto", "cenario": ["Quando clico no botão"]}]
    )

    csv_bytes = gerar_csv_azure_from_df(df, "Area", "QA")
    text = csv_bytes.decode("utf-8-sig")

    #  Deve conter o passo 'Quando' no conteúdo final
    assert "Quando clico no botão" in text


def test_preparar_df_para_zephyr_cenario_vazio_cobre_continue():
    """
     Cobre o ramo da linha 96 em `preparar_df_para_zephyr_xlsx`:
    `if not cenario_steps: continue`
    Garante que cenários vazios (string vazia ou None) sejam ignorados
    sem gerar erro ou linha indevida no resultado.
    """
    df = pd.DataFrame(
        [
            {"titulo": "CT sem passos", "cenario": ""},
            {"titulo": "CT None", "cenario": None},
        ]
    )

    result = preparar_df_para_zephyr_xlsx(df, "High", "QA", "Desc")

    #  Nenhum cenário válido → resultado vazio
    assert result.empty


def test_gerar_csv_azure_cenario_tipo_invalido_cobre_linha_227():
    """
     Cobre o trecho da linha 227 de `gerar_csv_azure_from_df`:
    `if not isinstance(cenario_steps, list)`
    Garante que valores de cenário não-lista (como inteiros) sejam
    tratados de forma segura, sem lançar erro.
    """
    df = pd.DataFrame(
        [{"titulo": "CT tipo inválido", "prioridade": "baixa", "cenario": 123}]
    )

    csv_bytes = gerar_csv_azure_from_df(df, "Area/Teste", "QA")
    text = csv_bytes.decode("utf-8-sig")

    #  O título deve existir, mas sem passos (cenário ignorado)
    assert "CT tipo inválido" in text
    assert "Dado" not in text and "Quando" not in text


def test_gerar_csv_azure_com_passos_com_e_cobre_279_288():
    """
     Cobre o bloco das linhas 279-288 em `gerar_csv_azure_from_df`,
    que trata passos começando com 'E ' (continuação de ações anteriores).
    O teste garante cobertura para:
      - 'E' após um passo 'Quando'
      - 'E' isolado (sem passo anterior de mesma categoria)
    """

    df = pd.DataFrame(
        [
            {
                "titulo": "CT com E após Quando",
                "prioridade": "baixa",
                "cenario": [
                    "Dado que o usuário entra",
                    "Quando clica",
                    "E vê a tela inicial",
                ],
            },
            {
                "titulo": "CT com E isolado",
                "prioridade": "baixa",
                "cenario": ["Dado algo", "E outro passo"],
            },
        ]
    )

    csv_bytes = gerar_csv_azure_from_df(df, "Area/Teste", "QA")
    text = csv_bytes.decode("utf-8-sig")

    #  Ambos os passos com 'E' devem estar presentes
    assert "E vê a tela inicial" in text
    assert "E outro passo" in text
