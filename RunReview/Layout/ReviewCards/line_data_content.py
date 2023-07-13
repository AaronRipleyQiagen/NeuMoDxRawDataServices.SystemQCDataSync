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

add_sample_exclusion_button = AddSampleExclusionButton(
    aio_id="run-review-add-sample-exclusion-button"
)

line_data_content = dbc.Card(
    dbc.CardBody([run_review_line_data, html.Br(), add_sample_exclusion_button]),
    className="mt-3",
)
