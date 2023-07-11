from .dependencies import *
from Shared.Components import SampleExclusionControls

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

sample_exclusion_controls = SampleExclusionControls(aio_id="run-review")

line_data_content = dbc.Card(
    dbc.CardBody([run_review_line_data, html.Br(), sample_exclusion_controls]),
    className="mt-3",
)
