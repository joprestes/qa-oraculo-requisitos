
import unittest
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from graph import extrair_json_da_resposta

class TestFuncoesAuxiliares(unittest.TestCase):
    """
    Suíte de testes para as funções auxiliares em main.py.
    """

    def test_extrair_json_com_markdown(self):
        """
        Testa se a função extrai corretamente o JSON de dentro de um bloco de código Markdown.
        """
        print("\nExecutando: test_extrair_json_com_markdown")
        texto_ia = 'Claro, aqui está:\n```json\n{"chave": "valor"}\n```'
        esperado = '{"chave": "valor"}'
        resultado = extrair_json_da_resposta(texto_ia)
        self.assertEqual(resultado, esperado)

    def test_extrair_json_sem_markdown(self):
        """
        Testa se a função retorna o JSON quando não há formatação Markdown.
        """
        print("Executando: test_extrair_json_sem_markdown")
        texto_ia = '{"chave": "valor"}'
        esperado = '{"chave": "valor"}'
        resultado = extrair_json_da_resposta(texto_ia)
        self.assertEqual(resultado, esperado)

    def test_extrair_json_com_texto_introdutorio(self):
        """
        Testa se a função ignora texto introdutório e extrai o JSON.
        """
        print("Executando: test_extrair_json_com_texto_introdutorio")
        texto_ia = 'Aqui está o JSON que você pediu: {"chave": "valor"}'
        esperado = '{"chave": "valor"}'
        resultado = extrair_json_da_resposta(texto_ia)
        self.assertEqual(resultado, esperado)

    def test_retornar_none_se_nao_houver_json(self):
        """
        Testa se a função retorna None quando não há nenhum JSON no texto.
        """
        print("Executando: test_retornar_none_se_nao_houver_json")
        texto_ia = "Desculpe, não consegui gerar um JSON válido."
        resultado = extrair_json_da_resposta(texto_ia)
        self.assertIsNone(resultado)

if __name__ == '__main__':
    unittest.main()