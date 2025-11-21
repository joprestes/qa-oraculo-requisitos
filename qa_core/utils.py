# ==========================================================
# utils.py — Funções utilitárias do QA Oráculo (versão final)
# ==========================================================
# Este módulo reúne todas as funções de suporte do projeto:
#   - Normalização de strings e nomes de arquivos
#   - Exportação para Excel (XLSX) e CSV (Azure, Zephyr)
#   - Limpeza de relatórios e parsing seguro de JSON
#   - Geração de CSV para Azure Test Plans com autodetecção
#
# Tudo foi projetado para ser compreensível e útil ao QA:
#   🔹 Código limpo e documentado
#   🔹 Comentários explicando a lógica de cada regra
#   🔹 Compatibilidade garantida com Excel PT-BR e EN-US
# ==========================================================

import csv
import datetime
import io
import json
import locale
import re
import unicodedata

import pandas as pd

# ==========================================================
# NORMALIZAÇÃO E NOMES DE ARQUIVOS
# ==========================================================


def normalizar_string(texto: str) -> str:
    """Remove acentos e caracteres especiais de uma string.
    
    Normaliza uma string removendo acentuação e diacríticos, mantendo
    apenas caracteres ASCII básicos. Útil para geração de nomes de arquivos
    seguros e comparações de texto.
    
    Args:
        texto: String a ser normalizada.
    
    Returns:
        String normalizada sem acentos e caracteres especiais.
        
    Examples:
        >>> normalizar_string("Criação de usuário")
        'Criacao de usuario'
        >>> normalizar_string("Éção")
        'Ecao'
    """
    nfkd_form = unicodedata.normalize("NFD", texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def gerar_nome_arquivo_seguro(user_story: str, extension: str) -> str:
    """Gera nome de arquivo limpo, seguro e único baseado na User Story.
    
    Cria um nome de arquivo válido a partir do texto da User Story,
    removendo caracteres especiais, limitando o tamanho e adicionando
    timestamp para garantir unicidade.
    
    Args:
        user_story: Texto da User Story para gerar o nome do arquivo.
        extension: Extensão do arquivo (sem ponto), ex: 'pdf', 'csv', 'md'.
    
    Returns:
        Nome de arquivo seguro no formato: 'nome-base_YYYYMMDD_HHMMSS.extension'
        Se user_story estiver vazia, retorna 'relatorio_qa_oraculo.extension'.
        
    Examples:
        >>> gerar_nome_arquivo_seguro("Como usuário, quero fazer login", "pdf")
        'como-usuario-quero-fazer-login_20251120_215500.pdf'
        >>> gerar_nome_arquivo_seguro("", "csv")
        'relatorio_qa_oraculo.csv'
        
    Note:
        - Usa apenas a primeira linha da User Story
        - Limita o nome base a 50 caracteres
        - Remove acentos e caracteres especiais
        - Substitui espaços e underscores por hífens
    """
    if not user_story:
        return f"relatorio_qa_oraculo.{extension}"

    primeira_linha_us = user_story.split("\n")[0].lower()
    nome_sem_acentos = normalizar_string(primeira_linha_us)
    nome_base = re.sub(r"[^\w\s-]", "", nome_sem_acentos).strip()
    nome_base = re.sub(r"[-_\s]+", "-", nome_base)[:50]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{nome_base}_{timestamp}.{extension}"


# ==========================================================
#  EXPORTAÇÃO PARA EXCEL
# ==========================================================


def to_excel(df: pd.DataFrame, sheet_name: str) -> bytes:
    """Converte um DataFrame Pandas em bytes de arquivo Excel.
    
    Gera um arquivo Excel (.xlsx) em memória a partir de um DataFrame,
    retornando os bytes prontos para download ou salvamento.
    
    Args:
        df: DataFrame Pandas contendo os dados a serem exportados.
        sheet_name: Nome da planilha (aba) no arquivo Excel.
    
    Returns:
        Bytes do arquivo Excel (.xlsx) pronto para download.
        
    Examples:
        >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        >>> excel_bytes = to_excel(df, "Dados")
        >>> len(excel_bytes) > 0
        True
        
    Note:
        Utiliza o engine 'openpyxl' para geração do arquivo Excel.
        O índice do DataFrame não é incluído na exportação.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl", mode="w") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()


# ==========================================================
#  EXPORTAÇÃO PARA JIRA ZEPHYR
# ==========================================================


def preparar_df_para_zephyr_xlsx(
    df_original: pd.DataFrame, priority: str, labels: str, description: str
) -> pd.DataFrame:
    """
    Converte cenários de teste em DataFrame no formato aceito pelo Zephyr (Jira).
    Cada linha do DataFrame representa um passo do caso de teste.
    """
    zephyr_rows = []
    header = [
        "Issue Type",
        "Summary",
        "Priority",
        "Labels",
        "Description",
        "Test Step",
        "Expected Result",
    ]

    for index, row in df_original.iterrows():
        summary = row.get("titulo", f"Caso de Teste {index+1}")
        cenario_steps = row.get("cenario", [])

        if isinstance(cenario_steps, str):
            cenario_steps = [s.strip() for s in cenario_steps.split("\n") if s.strip()]
        if not cenario_steps:
            continue

        for i, step in enumerate(cenario_steps):
            zephyr_rows.append(
                {
                    "Issue Type": "Test",
                    "Summary": summary,
                    "Priority": priority,
                    "Labels": labels,
                    "Description": description if i == 0 else "",
                    "Test Step": step,
                    "Expected Result": "",
                }
            )

    return pd.DataFrame(zephyr_rows, columns=header)


# ==========================================================
#  FUNÇÕES DE SUPORTE E LIMPEZA
# ==========================================================


def get_flexible(data_dict: dict, keys: list, default_value):
    """Busca flexível de valores por múltiplas chaves possíveis."""
    if not isinstance(data_dict, dict):
        return default_value
    for key in keys:
        if key in data_dict:
            return data_dict[key]
    return default_value


def clean_markdown_report(report_text: str) -> str:
    """Remove blocos de código Markdown do texto."""
    if not isinstance(report_text, str):
        return ""
    text = re.sub(r"^```[a-zA-Z]*\n", "", report_text.strip())
    text = re.sub(r"\n```$", "", text)
    return text.strip()


def parse_json_strict(s: str):
    """Faz parsing seguro de JSON retornado pela IA."""
    s = s.strip()
    if s.startswith("```"):
        s = s.lstrip("`")
        s = s[s.find("{") :]
    if s.endswith("```"):
        s = s.rstrip("`")
        s = s[: s.rfind("}") + 1]

    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        raise ValueError(f"Falha ao decodificar JSON: {e}") from e


# ==========================================================
#  EXPORTAÇÃO PARA AZURE TEST PLANS (CSV)
# ==========================================================


def gerar_csv_azure_from_df(  # noqa: C901
    df_original: pd.DataFrame,
    area_path: str,
    assigned_to: str,
    default_priority: str = "2",
    default_state: str = "Design",
) -> bytes:
    """
    Gera um CSV 100% compatível com Azure Test Plans.

    - A 1ª coluna "ID" é obrigatória (vazia) — Azure gera automaticamente.
    - Cada linha do DataFrame é um Test Case.
    - Step 1 é sempre o cabeçalho (sem ação).
    - 'Dado', 'Quando', 'Então', 'E' são mapeados conforme o formato Gherkin.
    - O delimitador é detectado automaticamente com base no idioma do sistema:
        PT-BR → usa ';'
        EN-US → usa ','
    - Codificação UTF-8 com BOM → compatível com Excel e Azure.
    """

    # 📌 Autodetecção de localidade do sistema (para decidir delimitador)
    loc = locale.getlocale()[0] or ""
    sep = ";" if "pt" in loc.lower() else ","

    header = [
        "ID",  # Coluna obrigatória, mesmo vazia
        "Work Item Type",
        "Title",
        "Test Step",
        "Step Action",
        "Step Expected",
        "Priority",
        "Area Path",
        "Assigned To",
        "State",
    ]

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=sep, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)

    if df_original.empty:
        return buffer.getvalue().encode("utf-8-sig")

    area_path = (area_path or "").strip()
    assigned_to = (assigned_to or "").strip()

    # Mapeia texto de prioridade → valor numérico
    priority_map = {
        "alta": "1",
        "high": "1",
        "média": "2",
        "media": "2",
        "medium": "2",
        "baixa": "3",
        "low": "3",
    }

    # Cada linha do DF é um caso de teste
    for index, row in df_original.iterrows():
        title = row.get("titulo", f"Caso de Teste {index+1}")
        priority_raw = str(row.get("prioridade", default_priority)).lower().strip()
        priority_value = priority_map.get(priority_raw, default_priority)

        cenario_steps = row.get("cenario", [])
        if isinstance(cenario_steps, str):
            cenario_steps = [x.strip() for x in cenario_steps.split("\n") if x.strip()]
        if not isinstance(cenario_steps, list):
            cenario_steps = []

        # 1️Cabeçalho do Test Case
        writer.writerow(
            [
                "",  # ID vazio
                "Test Case",
                title,
                "1",
                "",
                "",
                priority_value,
                area_path,
                assigned_to,
                default_state,
            ]
        )

        step_counter = 2
        pending_quando = None

        # 2️ Passos Gherkin
        for step in cenario_steps:
            step_lower = step.lower().strip()

            if step_lower.startswith("dado"):
                writer.writerow(
                    ["", "", "", str(step_counter), step, "", "", "", "", ""]
                )
                step_counter += 1

            elif step_lower.startswith("quando"):
                pending_quando = step

            elif step_lower.startswith(("então", "entao")):
                writer.writerow(
                    [
                        "",
                        "",
                        "",
                        str(step_counter),
                        pending_quando or "",
                        step,
                        "",
                        "",
                        "",
                        "",
                    ]
                )
                pending_quando = None
                step_counter += 1

            elif step_lower.startswith("e "):
                if pending_quando:
                    writer.writerow(
                        ["", "", "", str(step_counter), step, "", "", "", "", ""]
                    )
                else:
                    writer.writerow(
                        ["", "", "", str(step_counter), "", step, "", "", "", ""]
                    )
                step_counter += 1

        # 3️Caso tenha um 'Quando' sem 'Então'
        if pending_quando:
            writer.writerow(
                ["", "", "", str(step_counter), pending_quando, "", "", "", "", ""]
            )
            step_counter += 1

        # 4️ Linha em branco para separar Test Cases
        writer.writerow([])

    csv_bytes = buffer.getvalue().encode("utf-8-sig")
    buffer.close()
    return csv_bytes


# ==========================================================
#  Salva Gherkin após edição do usuário
# ==========================================================


def gerar_relatorio_md_dos_cenarios(df):
    """
    Gera texto Markdown consolidado com os cenários Gherkin atuais.
    Cada linha do DataFrame vira um bloco Markdown formatado.
    """
    if df is None or df.empty:
        return "⚠️ Nenhum cenário disponível para gerar relatório."

    blocos = []
    for _, row in df.iterrows():
        titulo = row.get("titulo", "Sem título")
        prioridade = row.get("prioridade", "-")
        criterio = row.get("criterio_de_aceitacao_relacionado", "")
        cenario = row.get("cenario", "")

        bloco = f"""### 🧩 {titulo}
**Prioridade:** {prioridade}  
**Critério de Aceitação:** {criterio}

```gherkin
{cenario.strip()}
```
"""
        blocos.append(bloco)
    return "\n".join(blocos)


# ==========================================================
#  EXPORTAÇÃO PARA XRAY (JIRA XRAY) - CSV
# ==========================================================


def gerar_csv_xray_from_df(
    df_original: pd.DataFrame,
    test_repository_folder: str,
    custom_fields: dict | None = None,
) -> bytes:
    """
    Gera um CSV 100% compatível com Xray (Jira Test Management).

    Formato requerido pelo Xray:
    - Summary: nome da atividade de teste
    - Description: descrição do teste
    - Test_Repository_Folder: diretório onde o teste será salvo (deve existir no Xray)
    - Test_Type: tipo de teste (sempre "Cucumber" para cenários Gherkin)
    - Gherkin_Definition: cenário de teste completo em formato Gherkin

    Campos opcionais/personalizados suportados:
    - Labels: etiquetas para categorização
    - Priority: prioridade do teste (High, Medium, Low)
    - Component: componente do sistema relacionado
    - Assignee: responsável pelo teste
    - Qualquer outro campo customizado do Jira

    Args:
        df_original: DataFrame com os cenários de teste
        test_repository_folder: Diretório no Xray onde os testes serão salvos
        custom_fields: Dicionário com campos personalizados (ex: {"Labels": "QA,Automation", "Priority": "High"})

    Requisitos:
    - Separação por vírgulas
    - Codificação UTF-8
    - Quebras de linha preservadas no campo Gherkin_Definition
    """

    # Campos obrigatórios do Xray
    header = [
        "Summary",
        "Description",
        "Test_Repository_Folder",
        "Test_Type",
        "Gherkin_Definition",
    ]

    # Adiciona campos personalizados ao cabeçalho
    custom_fields = custom_fields or {}
    if custom_fields:
        header.extend(custom_fields.keys())

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=",", quoting=csv.QUOTE_ALL)
    writer.writerow(header)

    if df_original.empty:
        return buffer.getvalue().encode("utf-8")

    test_repository_folder = (test_repository_folder or "").strip()

    # Cada linha do DataFrame é um caso de teste
    for index, row in df_original.iterrows():
        # Summary: usa o título do caso de teste
        summary = row.get("titulo", f"Caso de Teste {index+1}")

        # Description: combina critério de aceitação e justificativa de acessibilidade
        criterio = row.get("criterio_de_aceitacao_relacionado", "")
        justificativa = row.get("justificativa_acessibilidade", "")

        description_parts = []
        if criterio:
            description_parts.append(f"Critério de Aceitação: {criterio}")
        if justificativa:
            description_parts.append(
                f"Justificativa de Acessibilidade: {justificativa}"
            )

        description = (
            " | ".join(description_parts)
            if description_parts
            else "Teste gerado pelo QA Oráculo"
        )

        # Test_Type: sempre "Cucumber"
        test_type = "Cucumber"

        # Gherkin_Definition: cenário completo preservando quebras de linha
        cenario = row.get("cenario", "")
        if isinstance(cenario, list):
            gherkin_definition = "\n".join(cenario)
        else:
            gherkin_definition = str(cenario).strip()

        # Monta a linha com campos obrigatórios
        row_data = [
            summary,
            description,
            test_repository_folder,
            test_type,
            gherkin_definition,
        ]

        # Adiciona valores dos campos personalizados
        if custom_fields:
            row_data.extend(custom_fields.values())

        # Escreve a linha no CSV
        writer.writerow(row_data)

    csv_bytes = buffer.getvalue().encode("utf-8")
    buffer.close()
    return csv_bytes


# ==========================================================
#  EXPORTAÇÃO PARA TESTRAIL (CSV)
# ==========================================================


def gerar_csv_testrail_from_df(
    df_original: pd.DataFrame,
    section: str = "",
    priority: str = "Medium",
    template: str = "Test Case (Steps)",
    references: str = "",
) -> bytes:
    """
    Gera um CSV compatível com importação de casos no TestRail.

    Colunas comuns aceitas pelo TestRail Import (CSV):
    - Title (obrigatório)
    - Section (opcional)
    - Template (ex.: "Test Case (Steps)")
    - Type (ex.: "Functional")
    - Priority (ex.: "High", "Medium", "Low")
    - Estimate (opcional)
    - References (opcional)
    - Steps (texto com quebras de linha para cada passo)
    - Expected Result (texto com quebras de linha, alinhadas aos passos)

    Observação: utilizamos um formato simples com Steps/Expected Result multiline.
    """

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

    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=",", quoting=csv.QUOTE_ALL)
    writer.writerow(header)

    if df_original is None or df_original.empty:
        return buffer.getvalue().encode("utf-8")

    # Normaliza campos padrões
    section = (section or "").strip()
    priority = (priority or "").strip() or "Medium"
    template = (template or "").strip() or "Test Case (Steps)"
    references = (references or "").strip()

    for index, row in df_original.iterrows():
        title = row.get("titulo", f"Caso de Teste {index+1}")

        steps_raw = row.get("cenario", [])
        if isinstance(steps_raw, str):
            steps_list = [s.strip() for s in steps_raw.split("\n") if s.strip()]
        elif isinstance(steps_raw, list):
            steps_list = [str(s).strip() for s in steps_raw if str(s).strip()]
        else:
            steps_list = []

        # Para manter compatibilidade simples, não geramos expected separado por passo.
        # O campo "Expected Result" será preenchido com linhas vazias correspondentes,
        # ou, se houver "então" explícitos, tenta mapear de forma básica.
        expected_list = []
        for s in steps_list:
            lower = s.lower()
            if lower.startswith("quando"):
                expected_list.append("")
            elif lower.startswith(("então", "entao")):
                # Usa o próprio passo como expected para parear com o último 'Quando' se existir
                if expected_list:
                    expected_list[-1] = s
                else:
                    expected_list.append(s)
            else:
                expected_list.append("")

        steps_text = "\n".join(steps_list)
        expected_text = "\n".join(expected_list) if expected_list else ""

        writer.writerow(
            [
                title,
                section,
                template,
                "Functional",
                priority,
                "",
                references,
                steps_text,
                expected_text,
            ]
        )

    csv_bytes = buffer.getvalue().encode("utf-8")
    buffer.close()
    return csv_bytes
