from .dependencies import *

module_issue_content = dbc.Card(
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
                        id="module-issue-module-options",
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
                        id="module-issue-options",
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
                        id="module-issue-channel-options",
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
                        id="module-issue-severity-options",
                        style={
                            "width": "70%",
                            "display": "inline-block",
                            "vertical-align": "middle",
                        },
                    ),
                ]
            ),
            dbc.Button("Submit Module Issue", id="submit-module-issue"),
        ]
    ),
    className="mt-3",
)
