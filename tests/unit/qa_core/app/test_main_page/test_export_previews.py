from unittest.mock import MagicMock, patch
import pandas as pd
from qa_core import app


def test_render_export_previews_azure_success(mocked_st):
    # Setup
    df = pd.DataFrame([{"titulo": "Teste"}])
    mocked_st.session_state.update(
        {"test_plan_df": df, "area_path_input": "Area", "assigned_to_input": "User"}
    )

    # Mock tabs
    mock_tabs = [MagicMock() for _ in range(5)]
    mocked_st.tabs.return_value = mock_tabs

    with patch(
        "qa_core.app.gerar_csv_azure_from_df", return_value=b"ID,Title\n1,Teste"
    ) as mock_azure:
        app._render_export_previews()

        # Verify call
        mock_azure.assert_called_once()
        # Verify decoding and display
        mocked_st.code.assert_any_call("ID,Title\n1,Teste", language="csv")


def test_render_export_previews_testrail_success(mocked_st):
    # Setup
    df = pd.DataFrame([{"titulo": "Teste"}])
    mocked_st.session_state.update(
        {
            "test_plan_df": df,
            "testrail_section": "Section",
            "testrail_priority": "Medium",
        }
    )

    mock_tabs = [MagicMock() for _ in range(5)]
    mocked_st.tabs.return_value = mock_tabs

    with patch(
        "qa_core.app.gerar_csv_testrail_from_df",
        return_value=b"Title,Section\nTeste,Section",
    ) as mock_testrail:
        app._render_export_previews()

        mock_testrail.assert_called_once()
        mocked_st.code.assert_any_call("Title,Section\nTeste,Section", language="csv")


def test_render_export_previews_xray_success(mocked_st):
    # Setup
    df = pd.DataFrame([{"titulo": "Teste"}])
    mocked_st.session_state.update(
        {
            "test_plan_df": df,
            "xray_test_folder": "Folder",
            "xray_labels": "Label1",
            "xray_priority": "High",
            "xray_custom_fields": "Key=Value",
        }
    )

    mock_tabs = [MagicMock() for _ in range(5)]
    mocked_st.tabs.return_value = mock_tabs

    with patch(
        "qa_core.app.gerar_csv_xray_from_df",
        return_value=b"Summary,Folder\nTeste,Folder",
    ) as mock_xray:
        app._render_export_previews()

        # Verify arguments
        args, kwargs = mock_xray.call_args
        assert args[1] == "Folder"
        assert args[2] == {"Labels": "Label1", "Priority": "High", "Key": "Value"}

        mocked_st.code.assert_any_call("Summary,Folder\nTeste,Folder", language="csv")


def test_render_export_previews_error_handling(mocked_st):
    # Setup
    df = pd.DataFrame([{"titulo": "Teste"}])
    mocked_st.session_state.update({"test_plan_df": df})

    mock_tabs = [MagicMock() for _ in range(5)]
    mocked_st.tabs.return_value = mock_tabs

    with patch(
        "qa_core.app.gerar_csv_azure_from_df", side_effect=Exception("Erro simulado")
    ):
        app._render_export_previews()

        mocked_st.warning.assert_any_call(
            "⚠️ Não foi possível gerar o preview do Azure: Erro simulado"
        )
