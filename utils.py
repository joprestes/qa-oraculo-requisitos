import pandas as pd
import datetime
import re
import io

def gerar_nome_arquivo_seguro(user_story: str, extension: str) -> str: 
    """Gera um nome de arquivo seguro a partir da User Story."""
    if not user_story: return f"relatorio_qa_oraculo.{extension}"
    primeira_linha_us = user_story.split('\n')[0].lower()
    nome_base = re.sub(r'[^\w\s-]', '', primeira_linha_us).strip()
    nome_base = re.sub(r'[-\s]+', '-', nome_base)[:50]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{nome_base}_{timestamp}.{extension}"

def to_excel(df: pd.DataFrame, sheet_name: str) -> bytes:
    """Converte um DataFrame para um objeto Excel em memória (bytes)."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

def preparar_df_para_azure_xlsx(df_original: pd.DataFrame, area_path: str, assigned_to: str) -> pd.DataFrame:
    """Prepara o DataFrame para o formato de importação do Azure DevOps."""
    azure_rows = []
    header = ["Work Item Type", "Title", "Test Step", "Step Action", "Step Expected", "Priority", "Area Path", "Assigned To", "State"]
    priority_map = {"alta": "1", "média": "2", "baixa": "3"}

    for index, row in df_original.iterrows():
        title = row.get("titulo", f"Caso de Teste {index+1}")
        priority = priority_map.get(str(row.get("prioridade", "2")).lower(), "2")
        
        azure_rows.append({
            "Work Item Type": "Test Case", "Title": title, "Test Step": 1, "Step Action": "", "Step Expected": "",
            "Priority": priority, "Area Path": area_path, "Assigned To": assigned_to, "State": "Design"
        })

        cenario_steps = row.get("cenario", [])
        if isinstance(cenario_steps, str):
            cenario_steps = [step for step in cenario_steps.split('\n') if step.strip()]

        step_counter = 2
        for step in cenario_steps:
            azure_rows.append({"Test Step": step_counter, "Step Action": step, "Step Expected": ""})
            step_counter += 1

    return pd.DataFrame(azure_rows, columns=header)

def preparar_df_para_zephyr_xlsx(df_original: pd.DataFrame, priority: str, labels: str, description: str) -> pd.DataFrame:
    """Transforma o DataFrame no formato de importação do Jira Zephyr."""
    zephyr_rows = []
    header = ["Issue Type", "Summary", "Priority", "Labels", "Description", "Test Step", "Expected Result"]
    
    for index, row in df_original.iterrows():
        summary = row.get("titulo", f"Caso de Teste {index+1}")
        cenario_steps = row.get("cenario", [])
        if isinstance(cenario_steps, str):
            cenario_steps = [step for step in cenario_steps.split('\n') if step.strip()]

        if not cenario_steps: continue

        zephyr_rows.append({
            "Issue Type": "Test", "Summary": summary, "Priority": priority, "Labels": labels,
            "Description": description, "Test Step": cenario_steps[0], "Expected Result": ""
        })

        for i in range(1, len(cenario_steps)):
            zephyr_rows.append({"Test Step": cenario_steps[i]})

    return pd.DataFrame(zephyr_rows, columns=header)