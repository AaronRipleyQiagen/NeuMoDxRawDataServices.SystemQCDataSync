from dash import html, callback, Output, Input, State, register_page, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash_ag_grid as dag
import os
from azure.storage.blob import BlobServiceClient
import base64

register_page(__name__, path="/run-review/view-results/")

fig = go.Figure()

halfstyle = {
    "width": "50%",
    "display": "inline-block",
    "vertical-align": "middle",
    "horizontal-align": "left",
    "padding-bottom": 5,
}

onethirdstyle = {
    "width": "33%",
    "display": "inline-block",
    "vertical-align": "middle",
    "horizontal-align": "center",
    "padding-bottom": 5,
}

quarterstyle = {
    "width": "35%",
    "display": "inline-block",
    "vertical-align": "middle",
    "horizontal-align": "right",
    "padding-bottom": 5,
}

threequarterstyle = {
    "width": "65%",
    "display": "inline-block",
    "vertical-align": "middle",
    "horizontal-align": "right",
    "padding-bottom": 5,
}

remediation_actions = [
    {"label": "Increase Jack Pressure", "value": 1},
    {"label": "Reflange Fluid Line", "value": 2},
    {"label": "Perform Optics Calibration", "value": 3},
    {"label": "Repeat Testing As Is", "value": 4},
]

run_review_description = html.H1(id="runset-description")

run_review_channel_selector_label = html.P(
    "Choose Channel", style=quarterstyle)

run_review_channel_selector = dcc.Dropdown(
    id="run-review-channel-selector", style=threequarterstyle
)

run_review_xpcrmodule_selector_label = html.P(
    "Choose XPCR Module", style=quarterstyle)

run_review_xpcrmodule_selector = dcc.Dropdown(
    id="run-review-xpcrmodule-selector", style=threequarterstyle
)

run_review_download_data = dbc.Button(
    "Download Data", style={"margin": "auto"}, id="run-review-download-data"
)

run_review_run_selector_label = html.P(
    "Filter for specific runs", style=quarterstyle)

run_review_run_selector = dcc.Dropdown(
    id="run-review-run-selector", style=threequarterstyle
)

run_review_lane_selector_label = html.P(
    "Filter for specific lanes", style=quarterstyle)

run_review_lane_selector = dcc.Dropdown(
    id="run-review-lane-selector", style=threequarterstyle
)

run_review_color_selector_label = html.P(
    "Choose Color Attribute", style=quarterstyle)

run_review_color_selector = dcc.Dropdown(
    options=["XPCR Module Lane", "Run", "XPCR Module Side"],
    value="XPCR Module Lane",
    id="run-review-color-selector",
    style=threequarterstyle,
)

run_review_process_step_selector_label = html.P(
    "Choose Process Step", style=quarterstyle
)

run_review_process_step_selector = dcc.Dropdown(
    ["Normalized", "Raw", "2nd"],
    value="Normalized",
    id="run-review-process-step-selector",
    style=threequarterstyle,
)

run_review_curves = dcc.Graph(id="run-review-curves", figure=fig)

run_review_line_data = dag.AgGrid(
    enableEnterpriseModules=True,
    # licenseKey=os.environ['AGGRID_ENTERPRISE'],
    # columnDefs=initial_columnDefs,
    rowData=[],
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection="single",
    id="runset-sample-results",
)

line_data_content = dbc.Card(
    dbc.CardBody([run_review_line_data]),
    className="mt-3",
)

run_summary_table = dag.AgGrid(
    enableEnterpriseModules=True,
    # licenseKey=os.environ['AGGRID_ENTERPRISE'],
    # columnDefs=initial_columnDefs,
    rowData=[],
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection="single",
    id="run-summary-table",
)

run_summary_channel_label = html.Label(
    "Choose Optics Channel to Summarize:", style=quarterstyle
)

run_summary_channel_selector = dcc.Dropdown(
    id="run-summary-channel-selector", style=halfstyle
)

run_summary_content = dbc.Card(
    dbc.CardBody(
        [run_summary_channel_label, run_summary_channel_selector, run_summary_table]
    ),
    className="mt-3",
)

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

module_lane_issue_content = dbc.Card(
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
                        id="lane-issue-module-options",
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
                        id="lane-issue-lane-options",
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
                        id="lane-issue-options",
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
                        id="lane-issue-channel-options",
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
                        id="lane-issue-severity-options",
                        style={
                            "width": "70%",
                            "display": "inline-block",
                            "vertical-align": "middle",
                        },
                    ),
                ]
            ),
            dbc.Button("Submit Lane Issue", id="submit-lane-issue"),
        ]
    ),
    className="mt-3",
)

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

active_issues_content = dbc.Card(
    dbc.CardBody(
        [
            dag.AgGrid(
                enableEnterpriseModules=True,
                # licenseKey=os.environ['AGGRID_ENTERPRISE'],
                # columnDefs=initial_columnDefs,
                # rowData=intial_data,
                columnSize="sizeToFit",
                defaultColDef=dict(
                    resizable=True,
                ),
                rowSelection="single",
                # setRowId="id",
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
                # licenseKey=os.environ['AGGRID_ENTERPRISE'],
                # columnDefs=initial_columnDefs,
                # rowData={},
                columnSize="sizeToFit",
                defaultColDef=dict(
                    resizable=True,
                ),
                rowSelection="single",
                # setRowId="id",
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

cartridge_pictures_table = dag.AgGrid(
    enableEnterpriseModules=True,
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection="single",
    id="cartridge-pictures-table",
    style={"height": 300, "width": "100%"},
)

delete_cartridge_button = dbc.Button(
    "Delete Selected Picture",
    id="delete-cartridge-picture-button",
    style={
        "width": "35%",
        "margin-left": "10%",
        "display": "inline-block",
    },
)

update_cartridge_run_button = dbc.Button(
    "Update Cartridge Run",
    id="update-cartridge-run-button",
    style={
        "width": "35%",
        "margin-left": "10%",
        "display": "inline-block",
    },
)

update_cartridge_run_selection = dbc.Modal(
    [
        dbc.ModalHeader("Update Cartridge Run Selection"),
        dbc.ModalBody(
            [
                html.P(
                    "Please Select Which Run this Cartridge Picture is associated with."
                ),
                html.Br(),
                dcc.Dropdown(id="update-cartridge-run-options"),
                html.Br(),
                html.Div(
                    [
                        dbc.Button(
                            "Submit",
                            id="update-cartridge-run-submit",
                            style={
                                "width": "35%",
                                "margin-left": "10%",
                                "display": "inline-block",
                            },
                        ),
                        dbc.Button(
                            "Cancel",
                            id="update-cartridge-run-cancel",
                            style={
                                "width": "35%",
                                "margin-left": "10%",
                                "display": "inline-block",
                            },
                        ),
                    ]
                ),
            ]
        ),
        dbc.ModalFooter(),
    ],
    is_open=False,
    id="update-cartridge-run-selection",
)

update_cartridge_run_confirmation = dbc.Modal(
    [
        dbc.ModalHeader("Update Cartridge Run Confirmation"),
        dbc.ModalBody([html.P(id="update-cartridge-run-message")]),
        dbc.ModalFooter(),
    ],
    is_open=False,
    id="update-cartridge-run-confirmation",
)

upload_cartridge_response = dbc.Modal(
    [
        dbc.ModalHeader("Cartridge Upload Status"),
        dbc.ModalBody(
            [
                html.Div(
                    [
                        html.P(
                            "The following files have been successfully uploaded:"),
                        html.Ul(id="upload-cartridge-message"),
                    ]
                )
            ]
        ),
    ],
    is_open=False,
    id="upload-cartridge-response",
)

delete_cartridge_picture_confirmation = dbc.Modal(
    [
        dbc.ModalHeader("Delete Cartridge Picture Confirmation"),
        dbc.ModalBody(
            [
                html.P("Are you sure you would like to delete this picture?"),
                html.Br(),
                html.Div(
                    [
                        dbc.Button(
                            "Confirm",
                            id="delete-cartridge-picture-confirm",
                            style={
                                "width": "35%",
                                "margin-left": "10%",
                                "display": "inline-block",
                            },
                        ),
                        dbc.Button(
                            "Cancel",
                            id="delete-cartridge-picture-cancel",
                            style={
                                "width": "35%",
                                "margin-left": "10%",
                                "display": "inline-block",
                            },
                        ),
                    ]
                ),
            ]
        ),
        dbc.ModalFooter(),
    ],
    is_open=False,
    id="delete-cartridge-picture-confirmation",
)

delete_cartridge_picture_response = dbc.Modal(
    [
        dbc.ModalHeader("Delete Cartridge Picture Result"),
        dbc.ModalBody("Cartridge Picture Successfully Deleted."),
        dbc.ModalFooter(),
    ],
    is_open=False,
    id="delete-cartridge-picture-response",
)

cartridge_pictures_content = dbc.Card(
    dbc.CardBody(
        [
            upload_cartridge_response,
            delete_cartridge_picture_confirmation,
            update_cartridge_run_selection,
            update_cartridge_run_confirmation,
            delete_cartridge_picture_response,
            dcc.Upload(
                id="upload-cartridge-pictures",
                children=html.Div(
                    ["Drag and Drop or ", html.A("Select Files")]),
                style={
                    "width": "50%",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin-left": "25%",
                },
                multiple=True,
            ),
            dcc.Loading(
                id="cartridge-pictures-loading",
                type="dot",
                children=[
                    html.Br(),
                    html.Div(
                        children=[delete_cartridge_button,
                                  update_cartridge_run_button]
                    ),
                    html.Br(),
                    cartridge_pictures_table,
                    dbc.Carousel(items=[], id="cartridge-images",
                                 controls=False),
                ],
            ),
        ]
    )
)

tadm_pictures_table = dag.AgGrid(
    enableEnterpriseModules=True,
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection="single",
    id="tadm-pictures-table",
    style={"height": 300, "width": "100%"},
)

delete_tadm_button = dbc.Button(
    "Delete Selected Picture",
    id="delete-tadm-picture-button",
    style={
        "width": "35%",
        "margin-left": "10%",
        "display": "inline-block",
    },
)

update_tadm_run_button = dbc.Button(
    "Update TADM Run",
    id="update-tadm-run-button",
    style={
        "width": "35%",
        "margin-left": "10%",
        "display": "inline-block",
    },
)

update_tadm_run_selection = dbc.Modal(
    [
        dbc.ModalHeader("Update TADM Run Selection"),
        dbc.ModalBody(
            [
                html.P(
                    "Please Select Which Run this TADM Picture is associated with."
                ),
                html.Br(),
                dcc.Dropdown(id="update-tadm-run-options"),
                html.Br(),
                html.Div(
                    [
                        dbc.Button(
                            "Submit",
                            id="update-tadm-run-submit",
                            style={
                                "width": "35%",
                                "margin-left": "10%",
                                "display": "inline-block",
                            },
                        ),
                        dbc.Button(
                            "Cancel",
                            id="update-tadm-run-cancel",
                            style={
                                "width": "35%",
                                "margin-left": "10%",
                                "display": "inline-block",
                            },
                        ),
                    ]
                ),
            ]
        ),
        dbc.ModalFooter(),
    ],
    is_open=False,
    id="update-tadm-run-selection",
)

update_tadm_run_confirmation = dbc.Modal(
    [
        dbc.ModalHeader("Update TADM Run Confirmation"),
        dbc.ModalBody([html.P(id="update-tadm-run-message")]),
        dbc.ModalFooter(),
    ],
    is_open=False,
    id="update-tadm-run-confirmation",
)

upload_tadm_response = dbc.Modal(
    [
        dbc.ModalHeader("TADM Upload Status"),
        dbc.ModalBody(
            [
                html.Div(
                    [
                        html.P(
                            "The following files have been successfully uploaded:"),
                        html.Ul(id="upload-tadm-message"),
                    ]
                )
            ]
        ),
    ],
    is_open=False,
    id="upload-tadm-response",
)

delete_tadm_picture_confirmation = dbc.Modal(
    [
        dbc.ModalHeader("Delete TADM Picture Confirmation"),
        dbc.ModalBody(
            [
                html.P("Are you sure you would like to delete this picture?"),
                html.Br(),
                html.Div(
                    [
                        dbc.Button(
                            "Confirm",
                            id="delete-tadm-picture-confirm",
                            style={
                                "width": "35%",
                                "margin-left": "10%",
                                "display": "inline-block",
                            },
                        ),
                        dbc.Button(
                            "Cancel",
                            id="delete-tadm-picture-cancel",
                            style={
                                "width": "35%",
                                "margin-left": "10%",
                                "display": "inline-block",
                            },
                        ),
                    ]
                ),
            ]
        ),
        dbc.ModalFooter(),
    ],
    is_open=False,
    id="delete-tadm-picture-confirmation",
)

delete_tadm_picture_response = dbc.Modal(
    [
        dbc.ModalHeader("Delete TADM Picture Result"),
        dbc.ModalBody("TADM Picture Successfully Deleted."),
        dbc.ModalFooter(),
    ],
    is_open=False,
    id="delete-tadm-picture-response",
)

tadm_pictures_content = dbc.Card(
    dbc.CardBody(
        [
            upload_tadm_response,
            delete_tadm_picture_confirmation,
            update_tadm_run_selection,
            update_tadm_run_confirmation,
            delete_tadm_picture_response,
            dcc.Upload(
                id="upload-tadm-pictures",
                children=html.Div(
                    ["Drag and Drop or ", html.A("Select Files")]),
                style={
                    "width": "50%",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin-left": "25%",
                },
                multiple=True,
            ),
            dcc.Loading(
                id="tadm-pictures-loading",
                type="dot",
                children=[
                    html.Br(),
                    html.Div(
                        children=[delete_tadm_button, update_tadm_run_button]
                    ),
                    html.Br(),
                    tadm_pictures_table,
                    dbc.Carousel(items=[], id="tadm-images", controls=False),
                ],
            ),
        ]
    )
)

comments_table = dag.AgGrid(
    enableEnterpriseModules=True,
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection="single",
    id="comments-table",
)

comments_text = (
    dcc.Textarea(
        id="comments-text",
        value="Enter Comment Here",
        style={"width": "100%", "height": 300},
    ),
)

create_comment_button = dbc.Button(
    "Create Comment",
    id="create-comment-button",
    style={"width": "20%", "margin-left": "10%", "display": "inline-block"},
)

delete_comment_button = dbc.Button(
    "Delete Comment",
    id="delete-comment-button",
    style={"width": "20%", "margin-left": "10%", "display": "inline-block"},
)

view_comment_button = dbc.Button(
    "View Comment",
    id="view-comment-button",
    style={"width": "20%", "margin-left": "10%", "display": "inline-block"},
)

add_comment_button = dbc.Button(
    "Add Comment",
    id="add-comment-button",
    style={"width": "35%", "margin-left": "10%", "display": "inline-block"},
)

cancel_comment_button = dbc.Button(
    "Cancel",
    id="cancel-comment-button",
    style={"width": "35%", "margin-left": "10%", "display": "inline-block"},
)

comments_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Add Comment to Runset")),
        dbc.ModalBody(comments_text),
        html.Div([add_comment_button, cancel_comment_button]),
    ],
    id="comments-modal",
    is_open=False,
)

comments_view_text = html.P(id="comments-view-text")

comments_view_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Comment Text")),
        dbc.ModalBody(comments_view_text),
    ],
    id="comments-view-modal",
    is_open=False,
)

comments_post_response = dbc.Modal(
    [dbc.ModalHeader(dbc.ModalTitle("Comment Added to Runset"))],
    id="comments-post-response",
    is_open=False,
)

confirm_comment_delete_button = dbc.Button(
    "Yes",
    id="confirm-comment-delete-button",
    style={"width": "35%", "margin-left": "10%", "display": "inline-block"},
)

cancel_comment_delete_button = dbc.Button(
    "No",
    id="cancel-comment-delete-button",
    style={"width": "35%", "margin-left": "10%", "display": "inline-block"},
)

comments_delete_confirmation = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Confirm Comment Deletion")),
        dbc.ModalBody("Are You Sure you want to delete this comment?"),
        html.Div([confirm_comment_delete_button,
                 cancel_comment_delete_button]),
    ],
    id="comments-delete-confirmation",
    is_open=False,
)

comments_delete_response = dbc.Modal(
    [dbc.ModalHeader(dbc.ModalTitle("Comment Removed from Runset"))],
    id="comments-delete-response",
    is_open=False,
)

comments_content = dbc.Card(
    dbc.CardBody(
        [
            comments_table,
            html.Div(
                children=[
                    create_comment_button,
                    delete_comment_button,
                    view_comment_button,
                ]
            ),
        ]
    ),
    className="mt-3",
)

misc_files_table = dag.AgGrid(
    enableEnterpriseModules=True,
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection="single",
    id="misc-files-table",
)

misc_file_download_button = dbc.Button(
    "Download File",
    id="misc-file-download-button",
    style={
        "width": "35%",
        "margin-left": "10%",
        "display": "inline-block",
    },
)

misc_file_download = dcc.Download(id="misc-file-download")

misc_file_upload_button = dcc.Upload(
    id="misc-file-upload-button",
    children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
    style={
        "width": "100%",
        "borderWidth": "1px",
        "borderStyle": "dashed",
        "borderRadius": "5px",
        "textAlign": "center",
        "margin-left": "0%",
        "padding": "10px",
    },
    # Allow multiple files to be uploaded
    multiple=True,
)

delete_misc_file_button = dbc.Button(
    "Delete Selected File",
    id="delete-misc-file-button",
    style={
        "width": "35%",
        "margin-left": "10%",
        "display": "inline-block",
    },
)

delete_misc_file_picture_confirmation = dbc.Modal(
    [
        dbc.ModalHeader("Delete Miscellaneous File Confirmation"),
        dbc.ModalBody(
            [
                html.P("Are you sure you would like to delete this file?"),
                html.Div(
                    [
                        dbc.Button(
                            "Confirm",
                            id="delete-misc-file-confirm",
                            style={
                                "width": "35%",
                                "margin-left": "10%",
                                "display": "inline-block",
                            },
                        ),
                        dbc.Button(
                            "Cancel",
                            id="delete-misc-file-cancel",
                            style={
                                "width": "35%",
                                "margin-left": "10%",
                                "display": "inline-block",
                            },
                        ),
                    ]
                ),
            ]
        ),
        dbc.ModalFooter(),
    ],
    is_open=False,
    id="delete-misc-file-confirmation",
)

delete_misc_file_picture_response = dbc.Modal(
    [
        dbc.ModalHeader("Delete Miscellaneous File Result"),
        dbc.ModalBody("Miscellaneous Picture Successfully Deleted."),
        dbc.ModalFooter(),
    ],
    is_open=False,
    id="delete-misc-file-response",
)

misc_files_content = dbc.Card(
    dbc.CardBody(
        [
            delete_misc_file_picture_confirmation,
            delete_misc_file_picture_response,
            misc_file_upload_button,
            misc_files_table,
            misc_file_download,
            html.Div([misc_file_download_button, delete_misc_file_button]),
        ]
    ),
    className="mt-3",
)

file_upload_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("File Upload Status")),
        dbc.ModalBody("File was uploaded successfully"),
        dbc.ModalFooter(
            children=[dbc.Button(
                "Close", id="file-upload-response-close-button")]
        ),
    ],
    id="file-upload-response",
    is_open=False,
)

runset_reviews_table = dag.AgGrid(
    enableEnterpriseModules=True,
    # licenseKey=os.environ['AGGRID_ENTERPRISE'],
    # columnDefs=initial_columnDefs,
    # rowData=[],
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection="single",
    id="runset-reviews-table",
)

runset_info = html.Div(children=[html.P(id="runset-creator-name")])

run_review_content = dbc.Card(
    dbc.CardBody(
        [
            runset_info,
            runset_reviews_table,
        ]
    ),
    className="mt-3",
)

review_tabs = dbc.Tabs(
    children=[
        dbc.Tab(
            line_data_content, label="View Line Data", tab_id="run-review-line-data"
        ),
        dbc.Tab(run_summary_content, label="View Run Stats",
                tab_id="run-summary-data"),
        dbc.Tab(
            module_issue_content,
            label="Note Module Issue",
            tab_id="run-review-module-issues",
        ),
        dbc.Tab(
            run_issue_content, label="Note Run Issue", tab_id="run-review-run-issues"
        ),
        dbc.Tab(
            module_lane_issue_content,
            label="Note Lane Issue",
            tab_id="run-review-module-lane-issues",
        ),
        dbc.Tab(
            sample_issue_content,
            label="Note Sample Issue",
            tab_id="run-review-sample-issues",
        ),
        dbc.Tab(
            tadm_issue_content, label="Note TADM Issue", tab_id="run-review-tadm-issues"
        ),
        dbc.Tab(
            active_issues_content,
            label="View Active Issues",
            tab_id="run-review-active-issues",
        ),
        dbc.Tab(
            remediation_action_content,
            label="Manage Remediation Actions",
            tab_id="run-review-remediation-actions",
        ),
        dbc.Tab(
            cartridge_pictures_content,
            label="Cartridge Pictures",
            tab_id="cartidge-pictures",
        ),
        dbc.Tab(tadm_pictures_content, label="TADM Pictures",
                tab_id="tadm-pictures"),
        dbc.Tab(misc_files_content, label="Miscellaneous Files",
                tab_id="misc-files"),
        dbc.Tab(run_review_content, label="Runset Reviews",
                tab_id="runset-reviews"),
        dbc.Tab(comments_content, label="Comments", tab_id="runset-comments"),
    ],
    id="review-tabs",
)

issue_post_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Issue Creation Result")),
        dbc.ModalBody(html.P(id="issue-post-response-message")),
    ],
    id="issue-post-response",
    is_open=False,
)

issue_delete_confirmation = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Issue Deletion Confirmation")),
        dbc.ModalBody("Are you sure you want to delete this issue?"),
        html.Div(
            [
                dbc.Button(
                    "Yes",
                    id="issue-delete-confirmed-button",
                    style={
                        "width": "35%",
                        "margin-left": "10%",
                        "display": "inline-block",
                    },
                ),
                dbc.Button(
                    "No",
                    id="issue-delete-canceled-button",
                    style={
                        "width": "35%",
                        "margin-left": "10%",
                        "display": "inline-block",
                    },
                ),
            ]
        ),
    ],
    id="issue-delete-confirmation",
    is_open=False,
)

issue_delete_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Issue Deletion Result")),
        dbc.ModalBody("Issue was deleted successfully"),
    ],
    id="issue-delete-response",
    is_open=False,
)

remediation_action_post_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Remediation Action Creation Result")),
        dbc.ModalBody("Remediation Action was added successfully"),
    ],
    id="remediation-action-post-response",
    is_open=False,
)

remediation_action_update_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Remediation Action Update Result")),
        dbc.ModalBody("Remediation Action was updated successfully"),
    ],
    id="remediation-action-update-response",
    is_open=False,
)

remediation_action_delete_confirmation = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle(
            "Remediation Action Deletion Confirmation")),
        dbc.ModalBody(
            "Are you sure you want to delete this remediation action?"),
        html.Div(
            [
                dbc.Button(
                    "Yes",
                    id="remediation-action-delete-confirmed-button",
                    style={
                        "width": "35%",
                        "margin-left": "10%",
                        "display": "inline-block",
                    },
                ),
                dbc.Button(
                    "No",
                    id="remediation-action-delete-canceled-button",
                    style={
                        "width": "35%",
                        "margin-left": "10%",
                        "display": "inline-block",
                    },
                ),
            ]
        ),
    ],
    id="remediation-action-delete-confirmation",
    is_open=False,
)

remediation_action_delete_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Remediation Action Deletion Result")),
        dbc.ModalBody("Remediation Action was deleted successfully"),
    ],
    id="remediation-action-delete-response",
    is_open=False,
)

issue_resolution_remediation_action_selection = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Remediation Action Selection")),
        dbc.ModalBody(
            [
                html.P(
                    "Please select the remediation action intended to address this issue."
                ),
                dcc.Dropdown(id="issue-resolution-remediation-action-options"),
                html.P("Did it work?"),
                dcc.Dropdown(
                    id="issue-resolution-remediation-success",
                    options={1: "Yes", 0: "No"},
                ),
                dbc.Button("Submit", id="issue-resolution-submit"),
            ]
        ),
    ],
    id="issue-resolution-remediation-action-selection-prompt",
    is_open=False,
)

issue_resolution_remediation_action_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Issue Resolution Status")),
        dbc.ModalBody("Remediation Attempt was recorded successfully"),
    ],
    id="issue-remediation-attempt-submission-response",
    is_open=False,
)

run_review_update_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle(
            "Run Review Status Updated Successfully")),
        dbc.ModalBody("Run Review Status Changed to Completed."),
    ],
    id="run-review-status-update-post-response",
    is_open=False,
)

run_review_status_update_button = dbc.Button(
    "Submit Review", id="run-review-completed-button", style=quarterstyle
)

run_review_acceptance_label = html.P("Is Data Acceptable?", style=quarterstyle)

run_review_acceptance = dcc.Dropdown(
    options={True: "Yes", False: "No"},
    id="run-review-acceptance",
    style=threequarterstyle,
)

reviewgroup_selector_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Add Runset Review Assignemnts")),
        dbc.ModalBody(
            children=[
                html.Label("Select Groups required to review this runset."),
                dbc.Checklist(id="review-group-options", switch=True),
            ]
        ),
        dbc.ModalFooter(
            [
                dbc.Button(
                    "Submit",
                    id="submit-reviewgroup-selection-button",
                    className="ms-auto",
                    n_clicks=0,
                ),
                dbc.Button(
                    "Cancel",
                    id="cancel-reviewgroup-selection-button",
                    className="ms-auto",
                    n_clicks=0,
                ),
            ]
        ),
    ],
    id="reviewgroup-selector-modal",
    is_open=False,
)

add_review_assignment_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Run Review Assignment result")),
        dbc.ModalBody("Run Review Assignment was added successfully"),
    ],
    id="add-review-assignment-response",
    is_open=False,
)

add_review_group_button = dbc.Button(
    "Add Reviewer for Dataset", id="add-review-group-button"
)

layout = [
    run_review_description,
    issue_post_response,
    run_review_update_response,
    remediation_action_post_response,
    remediation_action_update_response,
    remediation_action_delete_confirmation,
    remediation_action_delete_response,
    comments_modal,
    comments_post_response,
    comments_delete_response,
    comments_delete_confirmation,
    comments_view_modal,
    issue_delete_confirmation,
    issue_delete_response,
    issue_resolution_remediation_action_selection,
    issue_resolution_remediation_action_response,
    reviewgroup_selector_modal,
    add_review_assignment_response,
    file_upload_response,
    html.Div(
        [
            html.Div(
                [run_review_channel_selector_label, run_review_channel_selector],
                style=halfstyle,
            ),
            html.Div(
                [run_review_xpcrmodule_selector_label,
                    run_review_xpcrmodule_selector],
                style=halfstyle,
            ),
        ]
    ),
    html.Div(
        [
            html.Div(
                [
                    run_review_process_step_selector_label,
                    run_review_process_step_selector,
                ],
                style=halfstyle,
            ),
            html.Div(
                [run_review_color_selector_label, run_review_color_selector],
                style=halfstyle,
            ),
        ]
    ),
    html.Div(
        [
            html.Div(
                [run_review_run_selector_label, run_review_run_selector],
                style=halfstyle,
            ),
            html.Div(
                [run_review_lane_selector_label, run_review_lane_selector],
                style=halfstyle,
            ),
        ]
    ),
    html.Div(
        [
            html.Div(
                [run_review_acceptance_label, run_review_acceptance], style=halfstyle
            ),
            html.Div([run_review_status_update_button], style=halfstyle),
        ]
    ),
    html.Div(
        [
            html.Div([run_review_download_data], style=halfstyle),
            html.Div([add_review_group_button], style=halfstyle),
        ]
    ),
    dcc.Loading(id="run-review-loading", type="graph",
                children=[run_review_curves]),
    review_tabs,
]  # , run_review_channel_selector,
