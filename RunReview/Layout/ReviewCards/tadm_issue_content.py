from .dependencies import *

tadm_issue_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div(
                [
                    html.P(
                        "What XPCR Module is Affected?",
                        className="card-text",
                        style={
                            "width": "30%",
                            "display": "inline-block",
                            "vertical-align": "middle",
                        },
                    ),
                    dcc.Dropdown(
                        id="tadm-issue-module-options",
                        style={
                            "width": "70%",
                            "display": "inline-block",
                            "vertical-align": "middle",
                        },
                    ),
                ]
            ),
            html.Div(
                [
                    html.P(
                        "What type of issue is this?",
                        className="card-text",
                        style={
                            "width": "30%",
                            "display": "inline-block",
                            "vertical-align": "middle",
                        },
                    ),
                    dcc.Dropdown(
                        id="tadm-issue-options",
                        style={
                            "width": "70%",
                            "display": "inline-block",
                            "vertical-align": "middle",
                        },
                    ),
                ]
            ),
            html.Div(
                [
                    html.P(
                        "How severe is this issue?",
                        className="card-text",
                        style={
                            "width": "30%",
                            "display": "inline-block",
                            "vertical-align": "middle",
                        },
                    ),
                    dcc.Dropdown(
                        id="tadm-issue-severity-options",
                        style={
                            "width": "70%",
                            "display": "inline-block",
                            "vertical-align": "middle",
                        },
                    ),
                ]
            ),
            dbc.Button("Submit TADM Issue", id="submit-tadm-issue"),
        ]
    ),
    className="mt-3",
)
