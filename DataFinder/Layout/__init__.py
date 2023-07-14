from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_ag_grid as dag


module_runs = dag.AgGrid(
    enableEnterpriseModules=True,
    rowData=[],
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection="multiple",
    id="module-runs-table",
)


data_finder_layout = html.Div(
    [
        html.Div(id="load-interval"),
        html.Div(id="data-finder-external-redirect"),
        dcc.Store(id="cartridge-ids-selected", storage_type="session"),
        html.Div(
            [
                html.Div(
                    [
                        html.H2(["Select Module of Interest:"]),
                        dcc.Dropdown(id="xpcr-module-options"),
                    ]
                ),
            ]
        ),
        html.Div(
            [
                html.P([html.H2(["Choose Run(s) of Interest"])]),
                dcc.Loading(
                    id="samples-loading",
                    type="default",
                    fullscreen=True,
                    children=[module_runs],
                ),
            ]
        ),
        html.Div(
            [
                dbc.Button("Get Data", id="get-data"),
            ]
        ),
    ]
)
