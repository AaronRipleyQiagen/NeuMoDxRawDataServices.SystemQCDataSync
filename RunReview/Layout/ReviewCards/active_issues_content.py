from .dependencies import *

active_issues_content = dbc.Card(
    dbc.CardBody(
        [
            dag.AgGrid(
                enableEnterpriseModules=True,
                columnSize="sizeToFit",
                defaultColDef=dict(
                    resizable=True,
                ),
                rowSelection="single",
                id="issues-table",
            ),
            html.Div(
                [
                    dbc.Button(
                        "Grade Issue Resolution",
                        id="issue-remediation-grade-button",
                        disabled=True,
                        style={"width": "35%", "margin-left": "10%"},
                    ),
                    dbc.Button(
                        "Delete Issue",
                        id="issue-delete-button",
                        disabled=True,
                        style={"width": "35%", "margin-left": "10%"},
                    ),
                ]
            ),
        ]
    ),
    className="mt-3",
)
