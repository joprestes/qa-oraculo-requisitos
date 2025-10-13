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
# 🔤 NORMALIZAÇÃO E NOMES DE ARQUIVOS
# ==========================================================


def normalizar_string(texto: str) -> str:
    """Remove acentos e caracteres especiais de uma string."""
    nfkd_form = unicodedata.normalize("NFD", texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def gerar_nome_arquivo_seguro(user_story: str, extension: str) -> str:
    """
    Gera nome de arquivo limpo, seguro e único, baseado na User Story.
    Inclui timestamp para evitar sobrescrita.
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
# 📊 EXPORTAÇÃO PARA EXCEL
# ==========================================================


def to_excel(df: pd.DataFrame, sheet_name: str) -> bytes:
    """Converte um DataFrame Pandas em bytes de arquivo Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl", mode="w") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()


# ==========================================================
# 🧩 EXPORTAÇÃO PARA JIRA ZEPHYR
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
# 🔍 FUNÇÕES DE SUPORTE E LIMPEZA
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
# 🚀 EXPORTAÇÃO PARA AZURE TEST PLANS (CSV)
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

        # 1️⃣ Cabeçalho do Test Case
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

        # 2️⃣ Passos Gherkin
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

        # 3️⃣ Caso tenha um 'Quando' sem 'Então'
        if pending_quando:
            writer.writerow(
                ["", "", "", str(step_counter), pending_quando, "", "", "", "", ""]
            )
            step_counter += 1

        # 4️⃣ Linha em branco para separar Test Cases
        writer.writerow([])

    csv_bytes = buffer.getvalue().encode("utf-8-sig")
    buffer.close()
    return csv_bytes
