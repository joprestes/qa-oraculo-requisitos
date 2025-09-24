import unittest
import pandas as pd
import datetime
import io
from unittest.mock import patch

from utils import (
    gerar_nome_arquivo_seguro,
    preparar_df_para_azure_xlsx,
    preparar_df_para_zephyr_xlsx,
    normalizar_string,
    to_excel,
    get_flexible
)

class TestUtilsFunctions(unittest.TestCase):
    def setUp(self):
        print("\n--- Configurando dados de teste para utils ---")
        self.sample_df = pd.DataFrame([
            {"titulo": "Caminho Feliz", "prioridade": "alta", "cenario": "Passo 1\nPasso 2"},
            {"titulo": "Caminho Infeliz", "prioridade": "média", "cenario": "Passo A"}
        ])

    def test_normalizar_string(self):
        print("--- Testando a normalização de strings ---")
        self.assertEqual(normalizar_string("usuário e relatório com ç e ã"), "usuario e relatorio com c e a")

    def test_get_flexible(self):
        print("--- Testando a busca flexível de chaves ---")
        data = {"avaliacao_geral": "Bom", "riscos": ["Risco 1"]}

        # Caso 1: Encontra a chave primária
        self.assertEqual(get_flexible(data, ["avaliacao_geral", "avaliacao"], "Padrão"), "Bom")
        
        # Caso 2: Encontra a chave alternativa
        self.assertEqual(get_flexible(data, ["riscos_e_dependencias", "riscos"], []), ["Risco 1"])

        # Caso 3: Nenhuma chave encontrada, retorna o padrão
        self.assertEqual(get_flexible(data, ["pontos_ambiguos", "ambiguidades"], []), [])

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

    @patch('utils.datetime')
    def test_gerar_nome_arquivo_seguro(self, mock_datetime):
        print("--- Testando a geração de nome de arquivo seguro ---")
        mock_now = datetime.datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.datetime.now.return_value = mock_now
        self.assertEqual(gerar_nome_arquivo_seguro("usuário", "txt"), "usuario_20240101_120000.txt")
        self.assertEqual(gerar_nome_arquivo_seguro("", "md"), "relatorio_qa_oraculo.md")

    def test_preparar_df_azure_com_cenario_vazio(self):
        print("--- Testando Azure com cenário vazio ---")
        df = pd.DataFrame([{"titulo": "CT Vazio", "cenario": ""}])
        self.assertEqual(len(preparar_df_para_azure_xlsx(df, "P", "A")), 1)

    def test_preparar_df_zephyr_com_cenario_vazio(self):
        print("--- Testando Zephyr com cenário vazio ---")
        df = pd.DataFrame([{"titulo": "CT Vazio", "cenario": ""}])
        self.assertTrue(preparar_df_para_zephyr_xlsx(df, "L", "b", "D").empty)

    def test_preparar_df_azure_com_cenario_em_lista(self):
        print("--- Testando Azure com cenário em lista ---")
        df = pd.DataFrame([{"cenario": ["Passo 1", "Passo 2"]}])
        self.assertEqual(len(preparar_df_para_azure_xlsx(df, "P", "A")), 3)

    def test_preparar_df_azure_com_dados_ausentes(self):
        print("--- Testando Azure com dados ausentes ---")
        df = pd.DataFrame([{"cenario": "Passo"}])
        df_azure = preparar_df_para_azure_xlsx(df, "P", "A")
        self.assertEqual(df_azure.iloc[0]["Title"], "Caso de Teste 1")
        self.assertEqual(df_azure.iloc[0]["Priority"], "2")
        df_inv = pd.DataFrame([{"prioridade": "urgente", "cenario": "Passo"}])
        self.assertEqual(preparar_df_para_azure_xlsx(df_inv, "P", "A").iloc[0]["Priority"], "2")

    def test_preparar_df_zephyr_com_dados_ausentes(self):
        print("--- Testando Zephyr com dados ausentes ---")
        df = pd.DataFrame([{"cenario": "Passo"}])
        self.assertEqual(preparar_df_para_zephyr_xlsx(df, "L", "b", "D").iloc[0]["Summary"], "Caso de Teste 1")

    def test_to_excel_conversion(self):
        print("--- Testando a conversão para Excel em memória ---")
        source_df = pd.DataFrame({'ID': [1, 2], 'Nome': ['Teste A', 'Teste B']})
        sheet_name = "MinhaPlanilha"
        excel_bytes = to_excel(source_df, sheet_name)
        self.assertIsInstance(excel_bytes, bytes)
        self.assertTrue(len(excel_bytes) > 0)
        result_df = pd.read_excel(io.BytesIO(excel_bytes), sheet_name=sheet_name)
        pd.testing.assert_frame_equal(source_df, result_df)

if __name__ == '__main__':
    unittest.main()