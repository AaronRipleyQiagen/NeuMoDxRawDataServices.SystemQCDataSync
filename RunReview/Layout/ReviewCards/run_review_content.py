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


run_review_content = dbc.Card(
    dbc.CardBody(
        [
            runset_reviews_table,
        ]
    ),
    className="mt-3",
)
