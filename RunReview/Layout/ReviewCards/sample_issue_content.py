from .dependencies import *

sample_issue_content = dbc.Card(
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
                        id="sample-issue-module-options",
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
                        id="sample-issue-run-options",
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
                        "What lane is affected by issue?",
                        className="card-text",
                        style={
                            "width": "30%",
                            "display": "inline-block",
                            "vertical-align": "middle",
                        },
                    ),
                    dcc.Dropdown(
                        id="sample-issue-lane-options",
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
                        id="sample-issue-options",
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
                        id="sample-issue-channel-options",
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
                        id="sample-issue-severity-options",
                        style={
                            "width": "70%",
                            "display": "inline-block",
                            "vertical-align": "middle",
                        },
                    ),
                ]
            ),
            dbc.Button("Submit Sample Issue", id="submit-sample-issue"),
        ]
    )
)
