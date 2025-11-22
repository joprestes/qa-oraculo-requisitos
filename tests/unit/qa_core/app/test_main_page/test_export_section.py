from unittest.mock import MagicMock, patch

import pandas as pd

from qa_core import app


@patch("qa_core.app._render_export_previews")
def test_render_export_section_com_campos_xray_e_testrail(mock_preview, mocked_st):
    df = pd.DataFrame(
        [
            {
                "titulo": "Caso completo",
                "prioridade": "Alta",
                "cenario": ["Dado algo", "Então resultado"],
            }
        ]
    )
    mocked_st.session_state.update(
        {
            "test_plan_df": df,
            "xray_test_folder": "QA/FOLDER",
            "xray_labels": "Regression",
            "xray_priority": "High",
            "xray_component": "Core",
            "xray_fix_version": "1.0.0",
            "xray_assignee": "qa.user",
            "xray_test_set": "Sprint 42",
            "xray_custom_fields": "Epic Link=PROJ-1\nTeam=QA Core",
            "testrail_section": "Backoffice",
            "testrail_priority": "Medium",
            "testrail_references": "PROJ-1",
        }
    )

    col_azure = MagicMock()
    col_zephyr = MagicMock()
    col_xray = MagicMock()

    with (
        patch(
            "qa_core.app._render_basic_exports",
            return_value=(col_azure, col_zephyr, col_xray),
        ),
        patch("qa_core.app.gerar_csv_xray_from_df", return_value=b"xray") as mock_xray,
        patch(
            "qa_core.app.gerar_csv_testrail_from_df", return_value=b"testrail"
        ) as mock_testrail,
    ):
        app._render_export_section()

    custom_fields = mock_xray.call_args.kwargs["custom_fields"]
    assert custom_fields == {
        "Labels": "Regression",
        "Priority": "High",
        "Component": "Core",
        "Fix Version": "1.0.0",
        "Assignee": "qa.user",
        "Test Set": "Sprint 42",
        "Epic Link": "PROJ-1",
        "Team": "QA Core",
    }
    mock_testrail.assert_called_once()
    col_xray.download_button.assert_called_once()
    label, payload = col_zephyr.download_button.call_args[0][:2]
    kwargs = col_zephyr.download_button.call_args[1]
    assert label == "🧪 TestRail (.csv)"
    assert payload == b"testrail"
    assert kwargs["mime"] == "text/csv"
    assert kwargs["use_container_width"] is True
    assert kwargs["file_name"].endswith("testrail.csv")
