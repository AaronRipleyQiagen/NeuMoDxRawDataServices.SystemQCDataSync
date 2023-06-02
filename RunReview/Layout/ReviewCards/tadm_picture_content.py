from .dependencies import *

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
