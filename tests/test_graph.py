import unittest
import json
from unittest.mock import patch, MagicMock

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

class TestHelperFunctions(unittest.TestCase):
    """Testes para as funções auxiliares do grafo."""

    def test_extrair_json_com_variacoes_markdown(self):
        print("\n--- Testando extrair_json com variações de markdown ---")
        casos = {
            "com tag json": "```json\n{\"key\": \"value\"}\n```",
            "sem tag json": "```\n{\"key\": \"value\"}\n```",
            "com espacos": "  ```json\n  {\"key\": \"value\"}  \n```  "
        }
        for nome, texto in casos.items():
            with self.subTest(nome):
                self.assertEqual(json.loads(extrair_json_da_resposta(texto)), {"key": "value"})

    def test_extrair_json_sem_markdown(self):
        print("--- Testando extrair_json sem markdown ---")
        texto = "{\"key\": \"value\"}"
        self.assertEqual(json.loads(extrair_json_da_resposta(texto)), {"key": "value"})

    def test_extrair_json_falha_graciosamente(self):
        print("--- Testando falha graciosa de extrair_json ---")
        self.assertIsNone(extrair_json_da_resposta("Apenas texto."))

    @patch('graph.time.sleep', return_value=None)
    @patch('graph.genai.GenerativeModel')
    def test_chamar_modelo_com_sucesso_imediato(self, mock_gen_model, mock_sleep):
        print("--- Testando chamar_modelo com sucesso imediato ---")
        mock_model_instance = mock_gen_model.return_value
        mock_model_instance.generate_content.return_value = "Sucesso"
        
        resultado = chamar_modelo_com_retry(mock_model_instance, "prompt")
        
        self.assertEqual(resultado, "Sucesso")
        mock_model_instance.generate_content.assert_called_once()
        mock_sleep.assert_not_called()

    @patch('graph.time.sleep', return_value=None)
    @patch('graph.genai.GenerativeModel')
    def test_chamar_modelo_com_retry_e_sucesso(self, mock_gen_model, mock_sleep):
        print("--- Testando chamar_modelo com retry e sucesso ---")
        mock_model_instance = mock_gen_model.return_value
        mock_model_instance.generate_content.side_effect = [ResourceExhausted("Cota esgotada"), "Sucesso"]
        
        resultado = chamar_modelo_com_retry(mock_model_instance, "prompt", tentativas=2)
        
        self.assertEqual(resultado, "Sucesso")
        self.assertEqual(mock_model_instance.generate_content.call_count, 2)
        mock_sleep.assert_called_once_with(60)

    @patch('graph.time.sleep', return_value=None)
    @patch('graph.genai.GenerativeModel')
    def test_chamar_modelo_com_falha_total_de_cota(self, mock_gen_model, mock_sleep):
        print("--- Testando chamar_modelo com falha total de cota ---")
        mock_model_instance = mock_gen_model.return_value
        mock_model_instance.generate_content.side_effect = ResourceExhausted("Cota esgotada")
        
        resultado = chamar_modelo_com_retry(mock_model_instance, "prompt", tentativas=3)

        self.assertIsNone(resultado)
        self.assertEqual(mock_model_instance.generate_content.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch('builtins.print')
    @patch('graph.time.sleep', return_value=None)
    @patch('graph.genai.GenerativeModel')
    def test_chamar_modelo_com_erro_inesperado(self, mock_gen_model, mock_sleep, mock_print):
        print("--- Testando chamar_modelo com erro inesperado ---")
        mock_model_instance = mock_gen_model.return_value
        erro_generico = ValueError("Erro genérico")
        mock_model_instance.generate_content.side_effect = erro_generico
        
        resultado = chamar_modelo_com_retry(mock_model_instance, "prompt")
        
        self.assertIsNone(resultado)
        mock_model_instance.generate_content.assert_called_once()
        mock_sleep.assert_not_called()
        mock_print.assert_called_with(f"❌ Erro inesperado na comunicação: {erro_generico}")

class TestGraphNodes(unittest.TestCase):
    """Testes para a resiliência dos nós individuais do grafo."""

    def setUp(self):
        self.estado_inicial_mock = {"user_story": "Uma US"}

    @patch('graph.chamar_modelo_com_retry')
    def test_node_analisar_historia_resiliencia(self, mock_chamar_modelo):
        print("--- Testando resiliência do node_analisar_historia ---")
        casos = {
            "json_invalido": ('```json\n{"key": "value",}\n```', "Falha ao decodificar a resposta da análise."),
            "sem_json": ("Apenas texto.", "Nenhum dado estruturado encontrado na resposta."),
            "falha_api": (None, "Falha na comunicação com o serviço de análise.")
        }
        for nome, (texto_resposta, msg_erro) in casos.items():
            with self.subTest(nome):
                mock_resposta = MagicMock()
                mock_resposta.text = texto_resposta
                mock_chamar_modelo.return_value = mock_resposta if texto_resposta is not None else None
                
                resultado = node_analisar_historia(self.estado_inicial_mock)
                self.assertIn("erro", resultado["analise_da_us"])
                self.assertIn(msg_erro, resultado["analise_da_us"]["erro"])

    @patch('graph.chamar_modelo_com_retry')
    def test_node_criar_plano_e_casos_de_teste_resiliencia(self, mock_chamar_modelo):
        print("--- Testando resiliência do node_criar_plano_e_casos_de_teste ---")
        estado_com_analise = {**self.estado_inicial_mock, "analise_da_us": {"analise_ambiguidade": {}}}
        casos = {
            "json_invalido": ('```json\n{"key": "value",}\n```', "Falha ao decodificar a resposta do plano."),
            "sem_json": ("Apenas texto.", "Nenhum dado estruturado encontrado na resposta."),
            "falha_api": (None, "Falha na comunicação com o serviço de planejamento.")
        }
        for nome, (texto_resposta, msg_erro) in casos.items():
            with self.subTest(nome):
                mock_resposta = MagicMock()
                mock_resposta.text = texto_resposta
                mock_chamar_modelo.return_value = mock_resposta if texto_resposta is not None else None
                
                resultado = node_criar_plano_e_casos_de_teste(estado_com_analise)
                self.assertIn("erro", resultado["plano_e_casos_de_teste"])
                self.assertIn(msg_erro, resultado["plano_e_casos_de_teste"]["erro"])

    @patch('graph.chamar_modelo_com_retry', return_value=None)
    def test_nodes_de_relatorio_lidam_com_falha_api(self, mock_chamar_modelo):
        print("--- Testando resiliência dos nós de geração de relatório ---")
        nodes_de_relatorio = {
            "analise": node_gerar_relatorio_analise,
            "plano_de_testes": node_gerar_relatorio_plano_de_testes
        }
        estados_de_entrada = {
            "analise": {**self.estado_inicial_mock, "analise_da_us": {}},
            "plano_de_testes": {**self.estado_inicial_mock, "plano_e_casos_de_teste": {}}
        }
        chaves_de_saida = {
            "analise": "relatorio_analise_inicial",
            "plano_de_testes": "relatorio_plano_de_testes"
        }

        for nome, node_func in nodes_de_relatorio.items():
            with self.subTest(f"Nó de relatório: {nome}"):
                resultado = node_func(estados_de_entrada[nome])
                self.assertIn("Erro", resultado[chaves_de_saida[nome]])

class TestGraphFlows(unittest.TestCase):
    """Testes de ponta a ponta para os fluxos compilados do grafo."""

    @patch('graph.chamar_modelo_com_retry')
    def test_fluxo_completo_grafo_analise(self, mock_chamar_modelo):
        print("--- Testando fluxo de ponta a ponta do grafo_analise ---")
        mock_chamar_modelo.return_value = MagicMock(text='{"key": "value"}')
        
        resultado = grafo_analise.invoke({"user_story": "US de teste"})
        
        self.assertIn("relatorio_analise_inicial", resultado)
        self.assertNotIn("erro", resultado.get("analise_da_us", {}))

    @patch('graph.chamar_modelo_com_retry')
    def test_fluxo_completo_grafo_plano_testes(self, mock_chamar_modelo):
        print("--- Testando fluxo de ponta a ponta do grafo_plano_testes ---")
        mock_chamar_modelo.return_value = MagicMock(text='{"key": "value"}')
        
        estado_mock = {"user_story": "US de teste", "analise_da_us": {}}
        resultado = grafo_plano_testes.invoke(estado_mock)
        
        self.assertIn("relatorio_plano_de_testes", resultado)
        self.assertNotIn("erro", resultado.get("plano_e_casos_de_teste", {}))

if __name__ == '__main__':
    unittest.main()