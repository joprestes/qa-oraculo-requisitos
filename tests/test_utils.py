# ============================================================
# 📘 test/test_utils.py — Testes de unidade do módulo utils
# ============================================================
# Este arquivo contém testes de unidade que validam o comportamento
# das funções utilitárias do projeto QA Oráculo.
#
# Nesta seção, testamos as funções fundamentais relacionadas a:
#   - Normalização de strings
#   - Busca flexível de chaves em dicionários
#   - Preparação de dados para exportação (Zephyr e Excel)
#   - Geração de nomes de arquivos seguros
#
# Cada teste aqui garante que as funções utilitárias mantenham
# a consistência e robustez da aplicação em operações básicas.
# ============================================================

import datetime
import io
import locale
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
    gerar_relatorio_md_dos_cenarios,
    get_flexible,
    normalizar_string,
    parse_json_strict,
    preparar_df_para_zephyr_xlsx,
    to_excel,
)

#  Variáveis globais para testes de CSV Azure

EXPECTED_COLUMNS_COUNT = 10
EXPECTED_TEST_CASES_COUNT = 2
MAX_FILENAME_BASE = 50

# ============================================================
#  Testes gerais de funções utilitárias
# ============================================================
# Esta classe agrupa os testes principais das funções utilitárias.
# Ela cobre os comportamentos de transformação de dados,
# manipulação de texto e exportação de planilhas.
# ============================================================


class TestUtilsFunctions(unittest.TestCase):
    """Classe que testa as principais funções do módulo utils."""

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

    def test_normalizar_string(self):
        """
         Verifica se caracteres acentuados e cedilhas são convertidos
        para suas versões sem acentuação.
        Exemplo: 'usuário' → 'usuario', 'ç' → 'c'
        """
        self.assertEqual(
            normalizar_string("usuário e relatório com ç e ã"),
            "usuario e relatorio com c e a",
        )

    def test_get_flexible(self):
        """
         Garante que a função `get_flexible` consegue encontrar
        chaves alternativas em dicionários com diferentes nomes de campos.
        Inclui validação de fallback e tipos inválidos.
        """
        data = {"avaliacao_geral": "Bom", "riscos": ["Risco 1"]}

        #  Caso 1 — Encontra a chave primária
        self.assertEqual(
            get_flexible(data, ["avaliacao_geral", "avaliacao"], "Padrão"), "Bom"
        )

        #  Caso 2 — Encontra a chave alternativa
        self.assertEqual(
            get_flexible(data, ["riscos_e_dependencias", "riscos"], []), ["Risco 1"]
        )

        #  Caso 3 — Nenhuma chave encontrada (retorna valor padrão)
        self.assertEqual(
            get_flexible(data, ["pontos_ambiguos", "ambiguidades"], []), []
        )

        #  Caso 4 — Entrada inválida (não é dict)
        self.assertEqual(get_flexible(None, ["chave"], "Padrão"), "Padrão")
        self.assertEqual(get_flexible([], ["chave"], "Padrão"), "Padrão")

    def test_preparar_df_para_zephyr_xlsx(self):
        """
         Testa se a função converte corretamente um DataFrame de cenários
        para o formato esperado pelo Jira Zephyr (planilha de importação).
        Espera-se que o número de linhas exportadas seja igual ao número
        de casos de teste + cabeçalho.
        """
        df_zephyr = preparar_df_para_zephyr_xlsx(self.sample_df, "High", "s1", "Desc")
        self.assertEqual(len(df_zephyr), 3)

    @patch("utils.datetime")
    def test_gerar_nome_arquivo_seguro(self, mock_datetime):
        """
        Garante que o nome de arquivo gerado:
          - Remove caracteres especiais
          - Inclui timestamp de data/hora
          - Usa o padrão `relatorio_qa_oraculo` quando o nome estiver vazio
        """
        #  Define uma data fixa para prever o resultado
        mock_now = datetime.datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now

        # Testa geração com nome customizado
        self.assertEqual(
            gerar_nome_arquivo_seguro("usuário", "txt"), "usuario_20240101_120000.txt"
        )

        # Testa fallback padrão (sem nome)
        self.assertEqual(gerar_nome_arquivo_seguro("", "md"), "relatorio_qa_oraculo.md")

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


# ============================================================
#  Testes extras — Markdown, JSON e _ensure_bytes
# ============================================================
# Esta seção valida funções auxiliares do módulo utils,
# responsáveis por:
#   - Limpar relatórios em Markdown removendo cercas de código
#   - Fazer parsing seguro de JSON retornado por IA (com e sem cercas)
#   - Converter objetos em bytes de forma resiliente
#
# Esses testes são importantes pois garantem robustez na
# manipulação de texto, exportação e comunicação entre módulos.
# ============================================================


class TestUtilsExtras(unittest.TestCase):
    """Testa funções auxiliares de limpeza e parsing do módulo utils."""

    def test_clean_markdown_report_completo(self):
        """
        Garante que o texto entre cercas ```markdown e ``` seja extraído corretamente.
        O conteúdo fora dessas marcações deve ser removido.
        """
        texto = "```markdown\n# Título\n```"
        esperado = "# Título"
        self.assertEqual(clean_markdown_report(texto), esperado)

    def test_clean_markdown_report_sem_cercas(self):
        """
         Verifica o comportamento quando o texto não contém cercas de markdown.
        Nesse caso, o conteúdo deve ser retornado inalterado.
        """
        texto = "# Apenas texto normal"
        self.assertEqual(clean_markdown_report(texto), "# Apenas texto normal")

    def test_clean_markdown_report_nao_string(self):
        """
        Se o valor passado não for uma string (ex: None),
        a função deve retornar uma string vazia, evitando exceções.
        """
        self.assertEqual(clean_markdown_report(None), "")

    def test_parse_json_strict_valido(self):
        """
         Testa o parsing de um JSON puro, sem formatação adicional.
        O resultado deve ser um dicionário Python equivalente.
        """
        texto = '{"key": "value"}'
        self.assertEqual(parse_json_strict(texto), {"key": "value"})

    def test_parse_json_strict_com_cercas(self):
        """
         Valida o comportamento com JSONs delimitados por ```json ... ```.
        A função deve ignorar as cercas e decodificar o conteúdo corretamente.
        """
        texto = '```json\n{"key": "value"}\n```'
        self.assertEqual(parse_json_strict(texto), {"key": "value"})

    def test_parse_json_strict_invalido(self):
        """
         Quando o texto não é JSON válido, a função deve lançar ValueError,
        mantendo a robustez contra entradas inesperadas.
        """
        with self.assertRaises(ValueError):
            parse_json_strict("não é json")


def test_gerar_relatorio_md_dos_cenarios_completo():
    """
    Valida a função `gerar_relatorio_md_dos_cenarios`, garantindo que:
      - Gere texto Markdown com blocos Gherkin
      - Inclua os campos principais de cada caso de teste
      - Trate corretamente DataFrames vazios
    """
    df = pd.DataFrame(
        [
            {
                "titulo": "Login válido",
                "prioridade": "Alta",
                "criterio_de_aceitacao_relacionado": "Usuário faz login com sucesso",
                "cenario": "Cenário: Login válido\nDado que o usuário acessa\nQuando insere credenciais\nEntão o login é bem-sucedido",
            },
            {
                "titulo": "Login inválido",
                "prioridade": "Baixa",
                "criterio_de_aceitacao_relacionado": "Usuário insere senha incorreta",
                "cenario": "Cenário: Login inválido\nDado que o usuário acessa\nQuando insere senha errada\nEntão deve ver mensagem de erro",
            },
        ]
    )

    md = gerar_relatorio_md_dos_cenarios(df)

    # Deve conter seções Markdown formatadas corretamente
    assert "### 🧩 Login válido" in md
    assert "### 🧩 Login inválido" in md
    assert "```gherkin" in md
    assert "Dado que o usuário acessa" in md

    # Mesmo DF vazio deve retornar texto padrão, não erro
    vazio = pd.DataFrame()
    vazio_md = gerar_relatorio_md_dos_cenarios(vazio)
    assert "Nenhum cenário disponível" in vazio_md


# ============================================================
#  Testes complementares independentes
# ============================================================
# Estes testes não fazem parte da classe acima, mas cobrem
# variações e exceções adicionais, garantindo cobertura total
# do módulo e de comportamentos extremos.
# ============================================================


def test_parse_json_strict_com_cercas_incompletas():
    """
     Cobre o caso em que há apenas a abertura das cercas ```json,
    mas sem o fechamento final. A função deve conseguir parsear o conteúdo.
    """
    texto = '```json\n{"key": "value"}'
    assert utils.parse_json_strict(texto) == {"key": "value"}


def test_parse_json_strict_invalido_levanta():
    """
     Caso o conteúdo seja ilegível como JSON, o método
    deve lançar uma exceção ValueError, indicando falha no parsing.
    """
    with pytest.raises(ValueError):
        utils.parse_json_strict("não é json válido")


def test_gerar_nome_arquivo_seguro_caracteres_invalidos():
    """
     Garante que caracteres inválidos em nomes de arquivo
    (como /, :, *, ?) sejam removidos e que a extensão final seja mantida.
    """
    nome = gerar_nome_arquivo_seguro("História/Inválida:*?", "txt")
    assert nome.endswith(".txt")
    assert "/" not in nome and ":" not in nome


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


# ============================================================
#  TESTES — gerar_csv_azure_from_df
# ============================================================


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
    csv_bytes = utils.gerar_csv_azure_from_df(df, "Area/Teste", "QA Tester")
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
    csv_bytes = utils.gerar_csv_azure_from_df(df, "Area/EN", "QA EN")
    csv_text = csv_bytes.decode("utf-8-sig")
    header = csv_text.splitlines()[0]

    assert "," in header
    assert ";" not in header


def test_gerar_csv_azure_from_df_vazio():
    """Garante que DataFrame vazio gera apenas cabeçalho."""
    df_vazio = pd.DataFrame()
    csv_bytes = utils.gerar_csv_azure_from_df(df_vazio, "", "")
    csv_text = csv_bytes.decode("utf-8-sig").strip()
    linhas = csv_text.splitlines()

    assert len(linhas) == 1
    assert "Work Item Type" in linhas[0]
    assert linhas[0].startswith("ID")


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
    csv_bytes = utils.gerar_csv_azure_from_df(df, "Area", "QA")
    csv_text = csv_bytes.decode("utf-8-sig")
    linhas = [linha for linha in csv_text.splitlines() if "Test Case" in linha]

    assert len(linhas) == EXPECTED_TEST_CASES_COUNT


def test_normalizar_string_vazia_ou_none():
    assert utils.normalizar_string("") == ""
    assert utils.normalizar_string("áéíóú") == "aeiou"
    # None deve levantar AttributeError (pois não é string)
    with pytest.raises(TypeError):
        utils.normalizar_string(None)


def test_gerar_nome_arquivo_seguro_truncamento():
    us = "História muito longa " * 10  # cria um nome >50 chars
    nome = utils.gerar_nome_arquivo_seguro(us, "csv")
    assert nome.endswith(".csv")
    # o nome base deve ter no máximo 50 caracteres antes do timestamp
    assert len(nome.split("_")[0]) <= MAX_FILENAME_BASE


def test_parse_json_strict_lixo_ao_redor():
    """
    Garante que parse_json_strict lança ValueError quando
    o texto contém lixo antes ou depois das cercas de código.
    Isso cobre o ramo de exceção (json.JSONDecodeError).
    """
    texto = 'início```json\n{"ok": true}\n```fim'
    with pytest.raises(ValueError):
        utils.parse_json_strict(texto)


def test_clean_markdown_report_cercas_incompletas():
    texto = "```markdown\n# Título sem fechamento"
    result = utils.clean_markdown_report(texto)
    assert "# Título" in result


def test_gerar_csv_azure_df_vazio_e_prioridade_invalida():
    df_vazio = pd.DataFrame()
    csv_bytes = utils.gerar_csv_azure_from_df(df_vazio, "Area", "Dev")
    assert b"Work Item Type" in csv_bytes  # só header

    df_invalida = pd.DataFrame(
        [{"titulo": "CT", "cenario": "Dado algo", "prioridade": "urgente"}]
    )
    csv_bytes2 = utils.gerar_csv_azure_from_df(df_invalida, "Area", "Dev")
    text = csv_bytes2.decode("utf-8-sig")
    # deve cair no default_priority ("2")
    assert ";2;" in text or ",2," in text


# ============================================================
#  Testes complementares —
# ============================================================
# Esta seção garante a cobertura completa do módulo utils.
# São incluídos testes de exceções, fluxos alternativos e
# comportamentos de borda. O objetivo é validar que todas
# as ramificações lógicas das funções sejam exercitadas.
# ============================================================


def test_ensure_bytes_tipo_invalido():
    """
     Força `_ensure_bytes` a lidar com tipos inesperados (int, dict).
    A função deve converter qualquer tipo não suportado em bytes
    chamando `str()` internamente.
    """
    assert _ensure_bytes(123) == b"123"
    # Para dicionários, o retorno deve conter o caractere “{”
    assert b"{" in _ensure_bytes({"a": 1})


def test_clean_markdown_report_com_fechamento_de_cercas():
    """
     Verifica se a função `clean_markdown_report` remove corretamente
    o fechamento de cercas de código (```), mantendo apenas o conteúdo.
    """
    texto = "# Título\n```"
    result = utils.clean_markdown_report(texto)
    assert "```" not in result


def test_parse_json_strict_apenas_inicio_com_cercas():
    """
     Garante a cobertura do caso em que o JSON contém apenas
    a abertura das cercas (` ```json `) mas sem o fechamento final.
    O conteúdo interno ainda deve ser interpretado corretamente.
    """
    texto = '```json\n{"a": 1}'
    result = utils.parse_json_strict(texto)
    assert result == {"a": 1}


def test_parse_json_strict_apenas_fim_com_cercas():
    """
     Garante a cobertura do caso inverso: o JSON termina com as cercas
    de fechamento ``` mas não tem abertura. A função deve conseguir
    decodificar normalmente o conteúdo.
    """
    texto = '{"b": 2}\n```'
    result = utils.parse_json_strict(texto)
    assert result == {"b": 2}


def test_gerar_csv_azure_locale_invalido(monkeypatch):
    """
     Força uma exceção na detecção do locale para garantir que
    a função `gerar_csv_azure_from_df` utilize o fallback padrão.
    Mesmo sem locale válido, o CSV deve ser gerado corretamente.
    """
    df = pd.DataFrame([{"titulo": "CT", "cenario": "Quando faço algo"}])

    # Simula falha no locale.getlocale()
    monkeypatch.setattr("locale.getlocale", lambda: (None, None))

    csv_bytes = utils.gerar_csv_azure_from_df(df, "Area", "QA")

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
        utils.to_excel(df, "Sheet1")


def test_clean_markdown_report_final_com_cercas():
    """
     Cobre o uso do `re.sub` interno que remove as cercas finais.
    O conteúdo deve permanecer limpo e sem marcas de ``` no final.
    """
    texto = "# Título\n```"
    result = utils.clean_markdown_report(texto)
    assert "```" not in result
    assert "# Título" in result


def test_gerar_csv_azure_quando_sem_entao():
    """
     Cobre o cenário em que existe um passo 'Quando' mas não há
    passo 'Então'. O CSV ainda deve ser gerado e conter o passo único.
    """
    df = pd.DataFrame(
        [{"titulo": "CT incompleto", "cenario": ["Quando clico no botão"]}]
    )

    csv_bytes = utils.gerar_csv_azure_from_df(df, "Area", "QA")
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

    result = utils.preparar_df_para_zephyr_xlsx(df, "High", "QA", "Desc")

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

    csv_bytes = utils.gerar_csv_azure_from_df(df, "Area/Teste", "QA")
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

    csv_bytes = utils.gerar_csv_azure_from_df(df, "Area/Teste", "QA")
    text = csv_bytes.decode("utf-8-sig")

    #  Ambos os passos com 'E' devem estar presentes
    assert "E vê a tela inicial" in text
    assert "E outro passo" in text
