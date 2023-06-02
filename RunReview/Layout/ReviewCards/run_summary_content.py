from .dependencies import *

run_summary_table = dag.AgGrid(
    enableEnterpriseModules=True,
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
