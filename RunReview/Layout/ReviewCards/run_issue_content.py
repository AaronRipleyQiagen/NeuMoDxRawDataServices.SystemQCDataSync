from .dependencies import *

run_issue_content = dbc.Card(
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
                        id="run-issue-module-options",
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
                        "Which run was issue observed in?",
                        className="card-text",
                        style={
                            "width": "30%",
                            "display": "inline-block",
                            "vertical-align": "middle",
                        },
                    ),
                    dcc.Dropdown(
                        id="run-issue-run-options",
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
                        id="run-issue-options",
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
                        "What optics channel is this issue observed on?",
                        className="card-text",
                        style={
                            "width": "30%",
                            "display": "inline-block",
                            "vertical-align": "middle",
                        },
                    ),
                    dcc.Dropdown(
                        id="run-issue-channel-options",
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
                        id="run-issue-severity-options",
                        style={
                            "width": "70%",
                            "display": "inline-block",
                            "vertical-align": "middle",
                        },
                    ),
                ]
            ),
            dbc.Button("Submit Run Issue", id="submit-run-issue"),
        ]
    )
)
