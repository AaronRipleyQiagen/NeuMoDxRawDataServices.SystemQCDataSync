from .dependencies import *

remediation_action_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Please Choose a Remediation Action", className="card-text"),
            html.Div(
                [
                    dcc.Dropdown(id="remediation-action-options",
                                 style=halfstyle),
                    dbc.Button(
                        "Submit Action", id="remediation-action-submit", style=halfstyle
                    ),
                ]
            ),
            dag.AgGrid(
                enableEnterpriseModules=True,
                columnSize="sizeToFit",
                defaultColDef=dict(
                    resizable=True,
                ),
                rowSelection="single",
                id="remediation-action-table",
            ),
            dbc.Button(
                "Complete Remediation Action",
                id="remediation-action-resolution",
                style={"width": "35%", "margin-left": "10%"},
            ),
            dbc.Button(
                "Delete Remediation Action",
                id="remediation-action-delete-button",
                style={"width": "35%", "margin-left": "10%"},
            ),
        ]
    ),
    className="mt-3",
)
