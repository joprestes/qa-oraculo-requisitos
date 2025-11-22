# ==========================================================
# exporters.py — Exportadores Avançados
# ==========================================================
"""
Utilitários para exportação em formatos avançados:
- Cucumber Studio (ZIP de arquivos .feature)
- Postman Collections (JSON)
- Batch Export (ZIP de múltiplas análises)
"""
import io
import json
import zipfile
from datetime import datetime

import pandas as pd


def export_to_cucumber_zip(df: pd.DataFrame) -> bytes:
    """
    Gera um arquivo ZIP contendo arquivos .feature para Cucumber Studio.

    Args:
        df: DataFrame com os cenários de teste (deve ter colunas: titulo, cenario, dado, quando, entao)

    Returns:
        Bytes do arquivo ZIP.
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for idx, row in df.iterrows():
            # Gera o conteúdo do arquivo .feature
            feature_content = _generate_feature_file(row)

            # Nome do arquivo baseado no título do cenário
            filename = _sanitize_filename(row.get("titulo", f"cenario_{idx}"))
            feature_filename = f"{filename}.feature"

            # Adiciona ao ZIP
            zip_file.writestr(feature_filename, feature_content)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def _generate_feature_file(row: pd.Series) -> str:
    """Gera o conteúdo de um arquivo .feature a partir de uma linha do DataFrame."""
    titulo = row.get("titulo", "Cenário sem título")
    cenario = row.get("cenario", "")

    # Extrai os steps
    dado = row.get("dado", "")
    quando = row.get("quando", "")
    entao = row.get("entao", "")

    # Monta o conteúdo do .feature
    content = f"""# language: pt
Funcionalidade: {titulo}

  Cenário: {cenario or titulo}
"""

    # Adiciona os steps
    if dado:
        for line in str(dado).split("\n"):
            if line.strip():
                content += f"    Dado {line.strip()}\n"

    if quando:
        for line in str(quando).split("\n"):
            if line.strip():
                content += f"    Quando {line.strip()}\n"

    if entao:
        for line in str(entao).split("\n"):
            if line.strip():
                content += f"    Então {line.strip()}\n"

    return content


def export_to_postman_collection(df: pd.DataFrame, user_story: str = "") -> str:
    """
    Gera uma Postman Collection (JSON) a partir dos cenários de teste.

    Args:
        df: DataFrame com os cenários de teste.
        user_story: User Story original (para incluir na descrição).

    Returns:
        String JSON da Postman Collection.
    """
    collection = {
        "info": {
            "name": "QA Oráculo - Test Scenarios",
            "description": f"Cenários de teste gerados automaticamente.\n\nUser Story:\n{user_story}",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [],
    }

    for idx, row in df.iterrows():
        titulo = row.get("titulo", f"Cenário {idx + 1}")
        cenario = row.get("cenario", "")
        dado = row.get("dado", "")
        quando = row.get("quando", "")
        entao = row.get("entao", "")

        # Cria um item de request para cada cenário
        # Nota: Como não temos endpoints reais, criamos requests de exemplo
        request_item = {
            "name": titulo,
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(
                        {
                            "cenario": cenario,
                            "dado": dado,
                            "quando": quando,
                            "entao": entao,
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                },
                "url": {
                    "raw": "{{base_url}}/api/test-scenario",
                    "host": ["{{base_url}}"],
                    "path": ["api", "test-scenario"],
                },
                "description": f"**Cenário:** {cenario}\n\n**Dado:** {dado}\n\n**Quando:** {quando}\n\n**Então:** {entao}",
            },
            "response": [],
        }

        collection["item"].append(request_item)

    return json.dumps(collection, ensure_ascii=False, indent=2)


def export_batch_zip(analysis_ids: list[int]) -> bytes:
    """
    Gera um arquivo ZIP contendo exportações de múltiplas análises.

    Args:
        analysis_ids: Lista de IDs de análises para exportar.

    Returns:
        Bytes do arquivo ZIP.
    """
    from ..database import get_analysis_by_id
    from ..exporters import gerar_relatorio_md_completo
    from ..pdf_generator import generate_pdf_report

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for analysis_id in analysis_ids:
            analysis = get_analysis_by_id(analysis_id)

            if not analysis:
                continue

            # Converte para dict se necessário
            if not isinstance(analysis, dict):
                analysis = dict(analysis)

            # Extrai dados
            user_story = analysis.get("user_story", "")
            analysis_report = analysis.get("analysis_report", "")
            test_plan_report = analysis.get("test_plan_report", "")
            test_plan_df_json = analysis.get("test_plan_df_json")

            # Cria um prefixo para os arquivos desta análise
            timestamp = analysis.get("created_at", datetime.now())
            if isinstance(timestamp, str):
                prefix = timestamp.split()[0].replace("-", "")
            elif hasattr(timestamp, "strftime"):
                prefix = timestamp.strftime("%Y%m%d")
            else:
                prefix = f"analysis_{analysis_id}"

            # 1. Exporta Markdown completo
            md_content = gerar_relatorio_md_completo(
                user_story, analysis_report, test_plan_report
            )
            zip_file.writestr(f"{prefix}_analise_{analysis_id}.md", md_content)

            # 2. Exporta PDF (se houver DataFrame)
            if test_plan_df_json:
                try:
                    records = json.loads(test_plan_df_json)
                    df = pd.DataFrame(records)
                    pdf_bytes = generate_pdf_report(analysis_report, df)
                    zip_file.writestr(f"{prefix}_analise_{analysis_id}.pdf", pdf_bytes)
                except Exception:
                    pass  # Se falhar, apenas não inclui o PDF

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def _sanitize_filename(name: str) -> str:
    """Remove caracteres inválidos de nomes de arquivo."""
    import re

    # Remove caracteres especiais, mantém apenas letras, números, espaços e underscores
    sanitized = re.sub(r"[^\w\s-]", "", name)
    # Substitui espaços por underscores
    sanitized = re.sub(r"\s+", "_", sanitized)
    # Limita o tamanho
    return sanitized[:50]
