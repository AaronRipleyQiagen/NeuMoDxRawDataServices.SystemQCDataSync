from .dependencies import *



runset_reviews_table = dag.AgGrid(
    enableEnterpriseModules=True,
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
