from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from Shared.styles import *


module_runs = dag.AgGrid(
    enableEnterpriseModules=True,
    columnSize="sizeToFit",
    rowData=[],
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection="multiple",
    id="module-runs-table",
    style={"height": 600},
)


data_finder_layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Div(id="load-interval"),
        html.Div(id="data-finder-external-redirect"),
        dcc.Store(id="xpcrmodule-runset-data", storage_type="local"),
        dcc.Store(id="cartridge-ids-selected", storage_type="session"),
        dcc.Store(id="xpcrmodule-id-selected", storage_type="local"),
        html.Div(
            [
                dcc.Loading(
                    children=[
                        html.Div(
                            [
                                html.P([html.H2(["Choose Run(s) of Interest"])]),
                                html.H2(
                                    ["Select Module of Interest:"], style=halfstyle
                                ),
                                dcc.Dropdown(id="xpcr-module-options", style=halfstyle),
                            ]
                        )
                    ],
                    type="default",
                    fullscreen=True,
                )
            ]
        ),
        html.Div(
            [
                dcc.Loading(
                    id="samples-loading",
                    type="default",
                    fullscreen=True,
                    children=[module_runs],
                ),
            ]
        ),
        html.Br(),
        html.Div(
            [
                dbc.Button("Get Data", id="get-data", style=quarterstyle),
            ]
        ),
    ]
)
