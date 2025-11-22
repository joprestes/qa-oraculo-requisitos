import io
import json
import zipfile

import pandas as pd

from qa_core.utils.exporters import (
    export_to_cucumber_zip,
    export_to_postman_collection,
    _generate_feature_file,
    _sanitize_filename,
)


def test_sanitize_filename():
    assert _sanitize_filename("Test Scenario #1") == "Test_Scenario_1"
    # O sanitizador mantém caracteres unicode válidos
    assert _sanitize_filename("Cenário com acentuação") == "Cenário_com_acentuação"
    assert len(_sanitize_filename("a" * 100)) <= 50


def test_generate_feature_file():
    row = pd.Series(
        {
            "titulo": "Login de usuário",
            "cenario": "Login com credenciais válidas",
            "dado": "que o usuário está na página de login",
            "quando": "ele insere credenciais válidas",
            "entao": "ele deve ser redirecionado para o dashboard",
        }
    )

    feature_content = _generate_feature_file(row)

    assert "# language: pt" in feature_content
    assert "Funcionalidade: Login de usuário" in feature_content
    assert "Cenário: Login com credenciais válidas" in feature_content
    assert "Dado que o usuário está na página de login" in feature_content
    assert "Quando ele insere credenciais válidas" in feature_content
    assert "Então ele deve ser redirecionado para o dashboard" in feature_content


def test_export_to_cucumber_zip():
    df = pd.DataFrame(
        [
            {
                "titulo": "Cenário 1",
                "cenario": "Teste 1",
                "dado": "contexto 1",
                "quando": "ação 1",
                "entao": "resultado 1",
            },
            {
                "titulo": "Cenário 2",
                "cenario": "Teste 2",
                "dado": "contexto 2",
                "quando": "ação 2",
                "entao": "resultado 2",
            },
        ]
    )

    zip_bytes = export_to_cucumber_zip(df)

    assert isinstance(zip_bytes, bytes)
    assert len(zip_bytes) > 0

    # Verifica o conteúdo do ZIP
    with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zip_file:
        files = zip_file.namelist()
        assert len(files) == 2
        # Os nomes de arquivo mantêm acentuação
        assert any("Cenário_1.feature" in f for f in files)
        assert any("Cenário_2.feature" in f for f in files)


def test_export_to_postman_collection():
    df = pd.DataFrame(
        [
            {
                "titulo": "Teste API",
                "cenario": "POST /users",
                "dado": "dados válidos",
                "quando": "envio requisição",
                "entao": "recebo 201",
            }
        ]
    )

    collection_json = export_to_postman_collection(
        df, "Como usuário, quero criar conta"
    )

    assert isinstance(collection_json, str)
    collection = json.loads(collection_json)

    assert "info" in collection
    assert collection["info"]["name"] == "QA Oráculo - Test Scenarios"
    assert "Como usuário" in collection["info"]["description"]
    assert "item" in collection
    assert len(collection["item"]) == 1
    assert collection["item"][0]["name"] == "Teste API"


def test_export_to_postman_collection_empty_df():
    df = pd.DataFrame()
    collection_json = export_to_postman_collection(df)
    collection = json.loads(collection_json)

    assert collection["item"] == []
