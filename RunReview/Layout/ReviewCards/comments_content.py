from .dependencies import *

comments_table = dag.AgGrid(
    enableEnterpriseModules=True,
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection="single",
    id="comments-table",
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
