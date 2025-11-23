import csv
import io
import locale
import pandas as pd

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

    Transforma o DataFrame interno de cenários em uma estrutura compatível com
    a importação via Excel do Zephyr. Cada passo do cenário gera uma linha.

    Args:
        df_original: DataFrame contendo os cenários gerados.
        priority: Prioridade a ser atribuída a todos os casos (ex: "High").
        labels: Etiquetas (labels) para os casos de teste.
        description: Descrição geral para os casos de teste.

    Returns:
        DataFrame formatado com colunas específicas do Zephyr (Issue Type, Summary, etc.).
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
        summary = row.get("titulo", f"Caso de Teste {int(index)+1}")  # type: ignore
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
        title = row.get("titulo", f"Caso de Teste {int(index)+1}")  # type: ignore
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
#  EXPORTAÇÃO PARA XRAY (JIRA XRAY) - CSV
# ==========================================================


def gerar_csv_xray_from_df(
    df_original: pd.DataFrame,
    test_repository_folder: str,
    custom_fields: dict | None = None,
) -> bytes:
    """
    Gera um CSV 100% compatível com Xray (Jira Test Management).

    Cria um arquivo CSV formatado para importação de testes manuais (Cucumber) no Xray.
    Inclui suporte a campos personalizados e estrutura Gherkin.

    Args:
        df_original: DataFrame contendo os cenários de teste.
        test_repository_folder: Caminho da pasta no repositório de testes do Xray.
        custom_fields: Dicionário opcional de campos personalizados (chave=nome, valor=valor).

    Returns:
        Bytes do arquivo CSV codificado em UTF-8.
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
        summary = row.get("titulo", f"Caso de Teste {int(index)+1}")  # type: ignore

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

    Formata os cenários de teste para o layout de importação CSV do TestRail,
    separando passos e resultados esperados.

    Args:
        df_original: DataFrame contendo os cenários.
        section: Seção (pasta) onde os casos serão criados no TestRail.
        priority: Prioridade dos casos (ex: "Medium", "High").
        template: Modelo de caso de teste (ex: "Test Case (Steps)").
        references: Referências externas (ex: IDs de tickets Jira).

    Returns:
        Bytes do arquivo CSV codificado em UTF-8.
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
        title = row.get("titulo", f"Caso de Teste {int(index)+1}")  # type: ignore

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


# ==========================================================
#  GERAÇÃO DE RELATÓRIOS (MARKDOWN)
# ==========================================================


def gerar_relatorio_md_completo(
    user_story: str, analysis_report: str, test_plan_report: str
) -> str:
    """
    Gera um relatório Markdown completo consolidando todas as etapas.

    Args:
        user_story: Texto original da User Story.
        analysis_report: Relatório da análise de requisitos.
        test_plan_report: Relatório do plano de testes.

    Returns:
        String contendo o relatório completo formatado em Markdown.
    """
    return f"""# 🔮 Relatório Completo - QA Oráculo

## 📋 User Story Original
{user_story}

---

## 🔍 Análise de Requisitos
{analysis_report}

---

## 🧪 Plano de Testes
{test_plan_report}
"""
