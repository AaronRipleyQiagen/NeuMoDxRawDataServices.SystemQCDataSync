from .dependencies import *

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
