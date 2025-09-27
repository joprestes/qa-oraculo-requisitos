# utils.py 
# utils.py 
import unicodedata
import re
import datetime
import io
import pandas as pd
import json

def normalizar_string(texto: str) -> str:
    """Remove acentos e caracteres especiais de uma string."""
    nfkd_form = unicodedata.normalize('NFD', texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def gerar_nome_arquivo_seguro(user_story: str, extension: str) -> str:
    """Gera nome de arquivo seguro e único, baseado na user story e timestamp."""
    if not user_story:
        return f"relatorio_qa_oraculo.{extension}"
    primeira_linha_us = user_story.split('\n')[0].lower()
    nome_sem_acentos = normalizar_string(primeira_linha_us)
    nome_base = re.sub(r'[^\w\s-]', '', nome_sem_acentos).strip()
    nome_base = re.sub(r'[-_\s]+', '-', nome_base)[:50]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{nome_base}_{timestamp}.{extension}"

def to_excel(df: pd.DataFrame, sheet_name: str) -> bytes:
    """Converte um DataFrame em um arquivo Excel em memória (bytes)."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl', mode="w") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

def preparar_df_para_azure_xlsx(df_original: pd.DataFrame, area_path: str, assigned_to: str) -> pd.DataFrame:
    """
    Converte cenários Gherkin para o formato esperado pelo Azure Test Plans.
    - Linha 1: abertura do Test Case (step em branco obrigatório).
    - Demais linhas seguem as regras de mapeamento Gherkin:
      Dado → Step Action
      Quando + Então → mesma linha (Action/Expected)
      E → depende do contexto (Action se entre Quando/Então, Expected se após Então/Dado).
    """
    azure_rows = []
    header = ["Work Item Type", "Title", "Test Step", "Step Action", "Step Expected",
              "Priority", "Area Path", "Assigned To", "State"]
    priority_map = {"alta": "1", "média": "2", "baixa": "3"}

    for index, row in df_original.iterrows():
        title = row.get("titulo", f"Caso de Teste {index+1}")
        priority = priority_map.get(str(row.get("prioridade", "2")).lower(), "2")

        cenario_steps = row.get("cenario", [])
        if isinstance(cenario_steps, str):
            cenario_steps = [step.strip() for step in cenario_steps.split('\n') if step.strip()]

        # Step 1 - linha de abertura com campos completos e Step Action/Expected em branco
        azure_rows.append({
            "Work Item Type": "Test Case",
            "Title": title,
            "Test Step": 1,
            "Step Action": "",
            "Step Expected": "",
            "Priority": priority,
            "Area Path": area_path,
            "Assigned To": assigned_to,
            "State": "Design"
        })

        step_counter = 2
        pending_quando = None  # armazena o "Quando" até encontrar o "Então"

        for step in cenario_steps:
            if step.lower().startswith("dado"):
                azure_rows.append({
                    "Work Item Type": "",
                    "Title": "",
                    "Test Step": step_counter,
                    "Step Action": step,
                    "Step Expected": "",
                    "Priority": "",
                    "Area Path": "",
                    "Assigned To": "",
                    "State": ""
                })
                step_counter += 1

            elif step.lower().startswith("quando"):
                pending_quando = step  # aguarda o Então

            elif step.lower().startswith("então"):
                if pending_quando:
                    azure_rows.append({
                        "Work Item Type": "",
                        "Title": "",
                        "Test Step": step_counter,
                        "Step Action": pending_quando,
                        "Step Expected": step,
                        "Priority": "",
                        "Area Path": "",
                        "Assigned To": "",
                        "State": ""
                    })
                    pending_quando = None
                else:
                    azure_rows.append({
                        "Work Item Type": "",
                        "Title": "",
                        "Test Step": step_counter,
                        "Step Action": "",
                        "Step Expected": step,
                        "Priority": "",
                        "Area Path": "",
                        "Assigned To": "",
                        "State": ""
                    })
                step_counter += 1

            elif step.lower().startswith("e "):
                if pending_quando:
                    # É um "E" entre Quando e Então → Step Action
                    azure_rows.append({
                        "Work Item Type": "",
                        "Title": "",
                        "Test Step": step_counter,
                        "Step Action": step,
                        "Step Expected": "",
                        "Priority": "",
                        "Area Path": "",
                        "Assigned To": "",
                        "State": ""
                    })
                else:
                    # É um "E" depois do Dado ou do Então → Step Expected
                    azure_rows.append({
                        "Work Item Type": "",
                        "Title": "",
                        "Test Step": step_counter,
                        "Step Action": "",
                        "Step Expected": step,
                        "Priority": "",
                        "Area Path": "",
                        "Assigned To": "",
                        "State": ""
                    })
                step_counter += 1

            else:
                # fallback: joga como Step Action simples
                azure_rows.append({
                    "Work Item Type": "",
                    "Title": "",
                    "Test Step": step_counter,
                    "Step Action": step,
                    "Step Expected": "",
                    "Priority": "",
                    "Area Path": "",
                    "Assigned To": "",
                    "State": ""
                })
                step_counter += 1

        # se terminou sem "Então" após um "Quando", joga só o Quando como Step Action
        if pending_quando:
            azure_rows.append({
                "Work Item Type": "",
                "Title": "",
                "Test Step": step_counter,
                "Step Action": pending_quando,
                "Step Expected": "",
                "Priority": "",
                "Area Path": "",
                "Assigned To": "",
                "State": ""
            })
            step_counter += 1
            pending_quando = None

    return pd.DataFrame(azure_rows, columns=header)

def preparar_df_para_zephyr_xlsx(df_original: pd.DataFrame, priority: str, labels: str, description: str) -> pd.DataFrame:
    """
    Converte cenários de teste em DataFrame no formato Zephyr (Jira).
    - Issue Type sempre = Test
    - Summary = título ou padrão
    - Test Step = cada linha do cenário
    """
    zephyr_rows = []
    header = ["Issue Type", "Summary", "Priority", "Labels", "Description", "Test Step", "Expected Result"]

    for index, row in df_original.iterrows():
        summary = row.get("titulo", f"Caso de Teste {index+1}")

        cenario_steps = row.get("cenario", [])
        if isinstance(cenario_steps, str):
            cenario_steps = [step.strip() for step in cenario_steps.split('\n') if step.strip()]

        if not cenario_steps:
           continue
        else:
            for i, step in enumerate(cenario_steps):
                zephyr_rows.append({
                    "Issue Type": "Test",
                    "Summary": summary,
                    "Priority": priority,
                    "Labels": labels,
                    "Description": description if i == 0 else "",
                    "Test Step": step,
                    "Expected Result": ""
                })

    return pd.DataFrame(zephyr_rows, columns=header)

def get_flexible(data_dict: dict, keys: list, default_value):
    """Procura por múltiplas chaves possíveis em um dicionário."""
    if not isinstance(data_dict, dict):
        return default_value
    for key in keys:
        if key in data_dict:
            return data_dict[key]
    return default_value

def clean_markdown_report(report_text: str) -> str:
    """
    Limpa a string de um relatório para remover blocos de código Markdown
    que podem ser adicionados pela IA.
    Ex: Converte '```markdown\n# Título\n```' para '# Título'.
    """
    if not isinstance(report_text, str):
        return ""
    text = re.sub(r"^```[a-zA-Z]*\n", "", report_text.strip())
    text = re.sub(r"\n```$", "", text)
    return text.strip()

def parse_json_strict(s: str):
    """
    Faz parsing seguro de JSONs retornados pela IA, removendo cercas de código se existirem.
    Lança ValueError se não for um JSON válido.
    """
    s = s.strip()
    if s.startswith("```"):
        s = s.lstrip("`")
        s = s[s.find("{"):]
    if s.endswith("```"):
        s = s.rstrip("`")
        s = s[:s.rfind("}")+1]

    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        raise ValueError(f"Falha ao decodificar JSON: {e}")
