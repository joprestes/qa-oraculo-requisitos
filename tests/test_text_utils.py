import datetime
import unittest
from unittest.mock import patch

import pandas as pd
import pytest

from qa_core import text_utils
from qa_core.text_utils import (
    clean_markdown_report,
    gerar_nome_arquivo_seguro,
    gerar_relatorio_md_dos_cenarios,
    get_flexible,
    normalizar_string,
    parse_json_strict,
)

MAX_FILENAME_BASE = 50


class TestTextUtilsFunctions(unittest.TestCase):
    """Classe que testa as funções de manipulação de texto."""

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

    @patch("qa_core.text_utils.datetime")
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


class TestTextUtilsExtras(unittest.TestCase):
    """Testa funções auxiliares de limpeza e parsing."""

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


def test_parse_json_strict_com_cercas_incompletas():
    """
     Cobre o caso em que há apenas a abertura das cercas ```json,
    mas sem o fechamento final. A função deve conseguir parsear o conteúdo.
    """
    texto = '```json\n{"key": "value"}'
    assert text_utils.parse_json_strict(texto) == {"key": "value"}


def test_parse_json_strict_invalido_levanta():
    """
     Caso o conteúdo seja ilegível como JSON, o método
    deve lançar uma exceção ValueError, indicando falha no parsing.
    """
    with pytest.raises(ValueError):
        text_utils.parse_json_strict("não é json válido")


def test_gerar_nome_arquivo_seguro_caracteres_invalidos():
    """
     Garante que caracteres inválidos em nomes de arquivo
    (como /, :, *, ?) sejam removidos e que a extensão final seja mantida.
    """
    nome = gerar_nome_arquivo_seguro("História/Inválida:*?", "txt")
    assert nome.endswith(".txt")
    assert "/" not in nome and ":" not in nome


def test_parse_json_strict_lixo_ao_redor():
    """
    Garante que parse_json_strict consegue extrair JSON mesmo com lixo ao redor,
    graças à melhoria com extract_json_from_text.
    """
    texto = 'início```json\n{"ok": true}\n```fim'
    resultado = text_utils.parse_json_strict(texto)
    assert resultado == {"ok": True}


def test_clean_markdown_report_cercas_incompletas():
    texto = "```markdown\n# Título sem fechamento"
    result = text_utils.clean_markdown_report(texto)
    assert "# Título" in result


def test_clean_markdown_report_com_fechamento_de_cercas():
    """
     Verifica se a função `clean_markdown_report` remove corretamente
    o fechamento de cercas de código (```), mantendo apenas o conteúdo.
    """
    texto = "# Título\n```"
    result = text_utils.clean_markdown_report(texto)
    assert "```" not in result


def test_parse_json_strict_apenas_inicio_com_cercas():
    """
     Garante a cobertura do caso em que o JSON contém apenas
    a abertura das cercas (` ```json `) mas sem o fechamento final.
    O conteúdo interno ainda deve ser interpretado corretamente.
    """
    texto = '```json\n{"a": 1}'
    result = text_utils.parse_json_strict(texto)
    assert result == {"a": 1}


def test_parse_json_strict_apenas_fim_com_cercas():
    """
     Garante a cobertura do caso inverso: o JSON termina com as cercas
    de fechamento ``` mas não tem abertura. A função deve conseguir
    decodificar normalmente o conteúdo.
    """
    texto = '{"b": 2}\n```'
    result = text_utils.parse_json_strict(texto)
    assert result == {"b": 2}


def test_clean_markdown_report_final_com_cercas():
    """
     Cobre o uso do `re.sub` interno que remove as cercas finais.
    O conteúdo deve permanecer limpo e sem marcas de ``` no final.
    """
    texto = "# Título\n```"
    result = text_utils.clean_markdown_report(texto)
    assert "```" not in result
    assert "# Título" in result


def test_normalizar_string_vazia_ou_none():
    assert text_utils.normalizar_string("") == ""
    assert text_utils.normalizar_string("áéíóú") == "aeiou"
    # None deve levantar AttributeError (pois não é string)
    with pytest.raises(TypeError):
        text_utils.normalizar_string(None)


def test_gerar_nome_arquivo_seguro_truncamento():
    us = "História muito longa " * 10  # cria um nome >50 chars
    nome = text_utils.gerar_nome_arquivo_seguro(us, "csv")
    assert nome.endswith(".csv")
    # o nome base deve ter no máximo 50 caracteres antes do timestamp
    assert len(nome.split("_")[0]) <= MAX_FILENAME_BASE
