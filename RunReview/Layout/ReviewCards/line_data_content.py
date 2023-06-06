from .dependencies import *

run_review_line_data = dag.AgGrid(
    enableEnterpriseModules=True,
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
