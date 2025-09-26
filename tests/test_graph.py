import unittest
import json
from unittest.mock import patch, MagicMock

# Importamos a função específica para controlar o cache
from langchain.globals import set_llm_cache

# Importando o que será testado
from graph import (
    extrair_json_da_resposta,
    chamar_modelo_com_retry,
    node_analisar_historia,
    node_gerar_relatorio_analise,
    node_criar_plano_e_casos_de_teste,
    node_gerar_relatorio_plano_de_testes,
    grafo_analise,
    grafo_plano_testes
)
from google.api_core.exceptions import ResourceExhausted

def mock_print(*args, **kwargs):
    pass

# --- CLASSE BASE PARA CONTROLAR O AMBIENTE DE TESTE ---
class BaseGraphTestCase(unittest.TestCase):
    """
    Uma classe base que garante que o cache do LangChain seja desativado
    antes de cada teste e reativado depois.
    """
    def setUp(self):
        """Desativa o cache ANTES de cada teste."""
        set_llm_cache(None)
        super().setUp()

    def tearDown(self):
        """Restaura o cache DEPOIS de cada teste (boa prática)."""
        set_llm_cache(None) # Garante que continue nulo.
        super().tearDown()



class TestHelperFunctions(BaseGraphTestCase):
    """Testes para as funções auxiliares do grafo."""
  
    
    def test_extrair_json_com_variacoes_markdown(self):
        casos = { "com tag json": "```json\n{\"key\": \"value\"}\n```", "sem tag json": "```\n{\"key\": \"value\"}\n```", "com espacos": "  ```json\n  {\"key\": \"value\"}  \n```  " }
        for nome, texto in casos.items():
            with self.subTest(nome):
                self.assertEqual(json.loads(extrair_json_da_resposta(texto)), {"key": "value"})

    def test_extrair_json_sem_markdown(self):
        texto = "{\"key\": \"value\"}"
        self.assertEqual(json.loads(extrair_json_da_resposta(texto)), {"key": "value"})

    def test_extrair_json_falha_graciosamente(self):
        self.assertIsNone(extrair_json_da_resposta("Apenas texto."))
    
    @patch('graph.time.sleep', return_value=None)
    def test_chamar_modelo_com_retry_e_sucesso(self, mock_sleep):
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = MagicMock(text="Sucesso")
        resultado = chamar_modelo_com_retry(mock_model_instance, "prompt", tentativas=2)
        self.assertEqual(resultado.text, "Sucesso")
        mock_model_instance.generate_content.assert_called_once()

    @patch('graph.time.sleep', return_value=None)
    def test_chamar_modelo_com_retry_e_falha_parcial(self, mock_sleep):
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = [ ResourceExhausted("Cota esgotada"), MagicMock(text="Sucesso") ]
        resultado = chamar_modelo_com_retry(mock_model_instance, "prompt", tentativas=2)
        self.assertEqual(resultado.text, "Sucesso")
        self.assertEqual(mock_model_instance.generate_content.call_count, 2)
        mock_sleep.assert_called_once_with(60)

    @patch('graph.time.sleep', return_value=None)
    def test_chamar_modelo_com_falha_total_de_cota(self, mock_sleep):
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = ResourceExhausted("Cota esgotada")
        resultado = chamar_modelo_com_retry(mock_model_instance, "prompt", tentativas=3)
        self.assertIsNone(resultado)
        self.assertEqual(mock_model_instance.generate_content.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch('builtins.print', new=mock_print)
    @patch('graph.time.sleep', return_value=None)
    def test_chamar_modelo_com_erro_inesperado(self, mock_sleep):
        mock_model_instance = MagicMock()
        erro_generico = ValueError("Erro genérico")
        mock_model_instance.generate_content.side_effect = erro_generico
        resultado = chamar_modelo_com_retry(mock_model_instance, "prompt")
        self.assertIsNone(resultado)
        mock_model_instance.generate_content.assert_called_once()
        mock_sleep.assert_not_called()

class TestGraphNodes(BaseGraphTestCase):
    """Testes para a resiliência dos nós individuais do grafo."""

    def setUp(self):
        super().setUp() # Chama o setUp da classe base primeiro
        self.estado_inicial_mock = {"user_story": "Uma US"}

    @patch('graph.chamar_modelo_com_retry')
    def test_node_analisar_historia_resiliencia(self, mock_chamar_modelo):
        casos = { "json_invalido": (MagicMock(text='```json\n{"key": "value",}\n```'), "Falha ao decodificar"), "sem_json": (MagicMock(text="Apenas texto."), "Nenhum dado estruturado"), "falha_api": (None, "Falha na comunicação") }
        for nome, (resposta_mock, msg_erro) in casos.items():
            with self.subTest(nome):
                mock_chamar_modelo.return_value = resposta_mock
                resultado = node_analisar_historia(self.estado_inicial_mock)
                self.assertIn("erro", resultado["analise_da_us"])
                self.assertIn(msg_erro, resultado["analise_da_us"]["erro"])

 
    @patch('graph.chamar_modelo_com_retry')
    def test_node_criar_plano_e_casos_de_teste_resiliencia(self, mock_chamar_modelo):
        estado_com_analise = {**self.estado_inicial_mock, "analise_da_us": {}}
        casos = { "json_invalido": (MagicMock(text='```json\n{"key": "value",}\n```'), "Falha ao decodificar"), "sem_json": (MagicMock(text="Apenas texto."), "Nenhum dado estruturado"), "falha_api": (None, "Falha na comunicação") }
        for nome, (resposta_mock, msg_erro) in casos.items():
            with self.subTest(nome):
                mock_chamar_modelo.return_value = resposta_mock
                resultado = node_criar_plano_e_casos_de_teste(estado_com_analise)
                self.assertIn("erro", resultado["plano_e_casos_de_teste"])
                self.assertIn(msg_erro, resultado["plano_e_casos_de_teste"]["erro"])

    @patch('graph.chamar_modelo_com_retry', return_value=None)
    def test_nodes_de_relatorio_lidam_com_falha_api(self, mock_chamar_modelo):
        nodes = { "analise": (node_gerar_relatorio_analise, {"analise_da_us": {}}, "relatorio_analise_inicial"), "plano_de_testes": (node_gerar_relatorio_plano_de_testes, {"plano_e_casos_de_teste": {}}, "relatorio_plano_de_testes") }
        for nome, (node_func, estado_extra, chave_saida) in nodes.items():
            with self.subTest(f"Nó de relatório: {nome}"):
                estado_de_entrada = {**self.estado_inicial_mock, **estado_extra}
                resultado = node_func(estado_de_entrada)
                self.assertIn("Erro", resultado[chave_saida])

class TestGraphFlows(BaseGraphTestCase):
    """Testes de ponta a ponta para os fluxos compilados do grafo."""

    @patch('graph.chamar_modelo_com_retry')
    def test_fluxo_completo_grafo_analise(self, mock_chamar_modelo):
        mock_chamar_modelo.return_value = MagicMock(text='{"key": "value"}')
        resultado = grafo_analise.invoke({"user_story": "US de teste"})
        self.assertIn("relatorio_analise_inicial", resultado)
        self.assertNotIn("erro", resultado.get("analise_da_us", {}))

    @patch('graph.chamar_modelo_com_retry')
    def test_fluxo_completo_grafo_plano_testes(self, mock_chamar_modelo):
        mock_chamar_modelo.return_value = MagicMock(text='{"key": "value"}')
        estado_mock = {"user_story": "US de teste", "analise_da_us": {}}
        resultado = grafo_plano_testes.invoke(estado_mock)
        self.assertIn("relatorio_plano_de_testes", resultado)
        self.assertNotIn("erro", resultado.get("plano_e_casos_de_teste", {}))

if __name__ == '__main__':
    unittest.main()