from .dependencies import *

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

misc_files_table = dag.AgGrid(
    enableEnterpriseModules=True,
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection="single",
    id="misc-files-table",
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

misc_files_content = dbc.Card(
    dbc.CardBody(
        [
            delete_misc_file_picture_confirmation,
            delete_misc_file_picture_response,
            misc_file_upload_button,
            misc_files_table,
            misc_file_download,
            file_upload_response,
            html.Div([misc_file_download_button, delete_misc_file_button]),
        ]
    ),
    className="mt-3",
)
