# ==========================================================
# test_xray_export.py — Testes para exportação Xray CSV
# ==========================================================
# Valida a geração de CSV compatível com Xray (Jira Test Management)
# ==========================================================

import pandas as pd

from qa_core.utils import gerar_csv_xray_from_df


def test_gerar_csv_xray_estrutura_basica():
    """
    Testa se o CSV gerado contém o cabeçalho correto no formato Xray.
    """
    df = pd.DataFrame(
        [
            {
                "titulo": "Teste de Login",
                "cenario": "Given que o usuário está na tela de login\nWhen ele insere credenciais válidas\nThen ele deve ser autenticado",
                "criterio_de_aceitacao_relacionado": "Sistema deve autenticar usuário",
                "justificativa_acessibilidade": "Teclado navegável",
            }
        ]
    )

    csv_bytes = gerar_csv_xray_from_df(df, "Login")
    csv_text = csv_bytes.decode("utf-8")

    # Verifica cabeçalho
    assert "Summary" in csv_text
    assert "Description" in csv_text
    assert "Test_Repository_Folder" in csv_text
    assert "Test_Type" in csv_text
    assert "Gherkin_Definition" in csv_text


def test_gerar_csv_xray_conteudo_cenario():
    """
    Testa se o conteúdo do cenário Gherkin é preservado corretamente.
    """
    cenario_gherkin = """Given que o usuário está na tela de pagamento
When ele seleciona a opção TED
Then o sistema deve exibir o formulário de TED"""

    df = pd.DataFrame(
        [
            {
                "titulo": "Solicitar TED",
                "cenario": cenario_gherkin,
                "criterio_de_aceitacao_relacionado": "Exibir formulário TED",
                "justificativa_acessibilidade": "Compatível com leitores de tela",
            }
        ]
    )

    csv_bytes = gerar_csv_xray_from_df(df, "TED")
    csv_text = csv_bytes.decode("utf-8")

    # Verifica se o cenário está presente
    assert "Solicitar TED" in csv_text
    assert "Given que o usuário está na tela de pagamento" in csv_text
    assert "When ele seleciona a opção TED" in csv_text
    assert "Then o sistema deve exibir o formulário de TED" in csv_text
    assert "TED" in csv_text  # Test_Repository_Folder
    assert "Cucumber" in csv_text  # Test_Type


def test_gerar_csv_xray_test_type_sempre_cucumber():
    """
    Testa se o Test_Type é sempre 'Cucumber' conforme especificação Xray.
    """
    df = pd.DataFrame(
        [
            {
                "titulo": "Teste API",
                "cenario": "Given uma API ativa\nWhen faço requisição\nThen recebo resposta",
            }
        ]
    )

    csv_bytes = gerar_csv_xray_from_df(df, "API")
    csv_text = csv_bytes.decode("utf-8")

    assert "Cucumber" in csv_text
    assert csv_text.count("Cucumber") == 1  # Apenas uma vez (no cenário)


def test_gerar_csv_xray_multiplos_cenarios():
    """
    Testa geração de CSV com múltiplos cenários de teste.
    """
    df = pd.DataFrame(
        [
            {
                "titulo": "Teste 1",
                "cenario": "Given cenário 1\nWhen ação 1\nThen resultado 1",
                "criterio_de_aceitacao_relacionado": "Critério 1",
            },
            {
                "titulo": "Teste 2",
                "cenario": "Given cenário 2\nWhen ação 2\nThen resultado 2",
                "criterio_de_aceitacao_relacionado": "Critério 2",
            },
        ]
    )

    csv_bytes = gerar_csv_xray_from_df(df, "Testes")
    csv_text = csv_bytes.decode("utf-8")

    # Verifica que ambos os testes estão presentes
    assert "Teste 1" in csv_text
    assert "Teste 2" in csv_text
    assert "cenário 1" in csv_text
    assert "cenário 2" in csv_text


def test_gerar_csv_xray_dataframe_vazio():
    """
    Testa comportamento com DataFrame vazio.
    """
    df = pd.DataFrame()
    csv_bytes = gerar_csv_xray_from_df(df, "Vazio")
    csv_text = csv_bytes.decode("utf-8")

    # Deve conter apenas o cabeçalho
    assert "Summary" in csv_text
    assert "Test_Type" in csv_text
    # Não deve ter linhas de dados
    lines = csv_text.strip().split("\n")
    assert len(lines) == 1  # Apenas cabeçalho


def test_gerar_csv_xray_test_repository_folder():
    """
    Testa se o Test_Repository_Folder é aplicado corretamente.
    """
    df = pd.DataFrame(
        [
            {
                "titulo": "Teste Pagamento",
                "cenario": "Given usuário tem saldo\nWhen solicita pagamento\nThen pagamento é processado",
            }
        ]
    )

    folder_name = "Pagamentos/PIX"
    csv_bytes = gerar_csv_xray_from_df(df, folder_name)
    csv_text = csv_bytes.decode("utf-8")

    assert folder_name in csv_text


def test_gerar_csv_xray_descricao_completa():
    """
    Testa se a descrição combina critério de aceitação e justificativa.
    """
    df = pd.DataFrame(
        [
            {
                "titulo": "Teste Completo",
                "cenario": "Given teste\nWhen ação\nThen resultado",
                "criterio_de_aceitacao_relacionado": "Deve funcionar corretamente",
                "justificativa_acessibilidade": "Suporte a WCAG 2.1",
            }
        ]
    )

    csv_bytes = gerar_csv_xray_from_df(df, "Testes")
    csv_text = csv_bytes.decode("utf-8")

    # Verifica que ambas as informações estão na descrição
    assert "Deve funcionar corretamente" in csv_text
    assert "Suporte a WCAG 2.1" in csv_text


def test_gerar_csv_xray_encoding_utf8():
    """
    Testa se o CSV é gerado com encoding UTF-8 correto.
    """
    df = pd.DataFrame(
        [
            {
                "titulo": "Teste com Acentuação",
                "cenario": "Dado que há acentuação\nQuando é testado\nEntão não há problemas",
                "criterio_de_aceitacao_relacionado": "Critério com ç, ã, é",
            }
        ]
    )

    csv_bytes = gerar_csv_xray_from_df(df, "Testes")
    csv_text = csv_bytes.decode("utf-8")

    # Caracteres acentuados devem ser preservados
    assert "Acentuação" in csv_text
    assert "ç" in csv_text or "Critério" in csv_text
    assert "não" in csv_text


def test_gerar_csv_xray_cenario_como_lista():
    """
    Testa se cenários fornecidos como lista são convertidos corretamente.
    """
    df = pd.DataFrame(
        [
            {
                "titulo": "Teste Lista",
                "cenario": [
                    "Given passo 1",
                    "When passo 2",
                    "Then passo 3",
                ],
            }
        ]
    )

    csv_bytes = gerar_csv_xray_from_df(df, "Testes")
    csv_text = csv_bytes.decode("utf-8")

    # Deve converter lista em string com quebras de linha
    assert "passo 1" in csv_text
    assert "passo 2" in csv_text
    assert "passo 3" in csv_text


def test_gerar_csv_xray_campos_opcionais_ausentes():
    """
    Testa comportamento quando campos opcionais estão ausentes.
    """
    df = pd.DataFrame(
        [
            {
                "titulo": "Teste Mínimo",
                "cenario": "Given teste simples",
            }
        ]
    )

    csv_bytes = gerar_csv_xray_from_df(df, "Testes")
    csv_text = csv_bytes.decode("utf-8")

    # Deve usar descrição padrão quando campos opcionais estão ausentes
    assert "Teste Mínimo" in csv_text
    assert "teste simples" in csv_text


def test_gerar_csv_xray_com_campos_personalizados():
    """
    Testa adição de campos personalizados ao CSV.
    """
    df = pd.DataFrame(
        [
            {
                "titulo": "Teste com Campos Customizados",
                "cenario": "Given cenário\nWhen ação\nThen resultado",
            }
        ]
    )

    custom_fields = {"Labels": "QA,Automation", "Priority": "High", "Component": "API"}

    csv_bytes = gerar_csv_xray_from_df(df, "Testes", custom_fields=custom_fields)
    csv_text = csv_bytes.decode("utf-8")

    # Verifica cabeçalho com campos customizados
    assert "Labels" in csv_text
    assert "Priority" in csv_text
    assert "Component" in csv_text

    # Verifica valores dos campos
    assert "QA,Automation" in csv_text
    assert "High" in csv_text
    assert "API" in csv_text


def test_gerar_csv_xray_com_campos_personalizados_complexos():
    """
    Testa campos customizados com nomes compostos e valores complexos.
    """
    df = pd.DataFrame(
        [
            {
                "titulo": "Teste Complexo",
                "cenario": "Given teste",
            }
        ]
    )

    custom_fields = {
        "Epic Link": "PROJ-123",
        "Sprint": "Sprint 10",
        "Custom Field": "Valor com espaços",
    }

    csv_bytes = gerar_csv_xray_from_df(df, "Testes", custom_fields=custom_fields)
    csv_text = csv_bytes.decode("utf-8")

    # Verifica campos com nomes compostos
    assert "Epic Link" in csv_text
    assert "PROJ-123" in csv_text
    assert "Sprint" in csv_text
    assert "Sprint 10" in csv_text
    assert "Custom Field" in csv_text
    assert "Valor com espaços" in csv_text


def test_gerar_csv_xray_sem_campos_personalizados():
    """
    Testa que campos personalizados None ou vazio não quebram a função.
    """
    df = pd.DataFrame(
        [
            {
                "titulo": "Teste Sem Customização",
                "cenario": "Given teste básico",
            }
        ]
    )

    # Testa com None
    csv_bytes = gerar_csv_xray_from_df(df, "Testes", custom_fields=None)
    csv_text = csv_bytes.decode("utf-8")
    assert "Teste Sem Customização" in csv_text

    # Testa com dicionário vazio
    csv_bytes = gerar_csv_xray_from_df(df, "Testes", custom_fields={})
    csv_text = csv_bytes.decode("utf-8")
    assert "Teste Sem Customização" in csv_text


def test_gerar_csv_xray_ordem_campos_personalizados():
    """
    Testa se a ordem dos campos personalizados é preservada.
    """
    df = pd.DataFrame(
        [
            {
                "titulo": "Teste Ordem",
                "cenario": "Given teste",
            }
        ]
    )

    custom_fields = {"Campo1": "Valor1", "Campo2": "Valor2", "Campo3": "Valor3"}

    csv_bytes = gerar_csv_xray_from_df(df, "Testes", custom_fields=custom_fields)
    csv_text = csv_bytes.decode("utf-8")

    # Verifica que todos os campos estão presentes
    assert "Campo1" in csv_text
    assert "Campo2" in csv_text
    assert "Campo3" in csv_text
    assert "Valor1" in csv_text
    assert "Valor2" in csv_text
    assert "Valor3" in csv_text
