from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from .styles import *
from plotly import graph_objects as go

run_review_description = html.H1(id="runset-description")
runset_info = html.Div(
    children=[
        html.H2(id="runset-creator-name", style=halfstyle),
        html.H2(id="runset-system-description", style=halfstyle),
    ]
)

run_review_channel_selector_label = html.P("Choose Channel", style=quarterstyle)

run_review_channel_selector = dcc.Dropdown(
    id="run-review-channel-selector", style=threequarterstyle
)

run_review_xpcrmodule_selector_label = html.P("Choose XPCR Module", style=quarterstyle)

run_review_xpcrmodule_selector = dcc.Dropdown(
    id="run-review-xpcrmodule-selector", style=threequarterstyle
)

run_review_download_data = dbc.Button(
    "Download Data", style={"margin": "auto"}, id="run-review-download-data"
)

run_review_run_selector_label = html.P("Filter for specific runs", style=quarterstyle)

run_review_run_selector = dcc.Dropdown(
    id="run-review-run-selector", style=threequarterstyle
)

run_review_lane_selector_label = html.P("Filter for specific lanes", style=quarterstyle)

run_review_lane_selector = dcc.Dropdown(
    id="run-review-lane-selector", style=threequarterstyle
)

run_review_color_selector_label = html.P("Choose Color Attribute", style=quarterstyle)

run_review_color_selector = dcc.Dropdown(
    options=["XPCR Module Lane", "Run", "XPCR Module Side"],
    value="XPCR Module Lane",
    id="run-review-color-selector",
    style=threequarterstyle,
)

run_review_process_step_selector_label = html.P(
    "Choose Process Step", style=quarterstyle
)

run_review_process_step_selector = dcc.Dropdown(
    ["Normalized", "Raw", "2nd"],
    value="Normalized",
    id="run-review-process-step-selector",
    style=threequarterstyle,
)

add_review_group_button = html.Div(
    [
        dbc.Button(
            "Add Reviewer for Dataset", id="add-review-group-button", style=quarterstyle
        )
    ]
)

run_review_status_update_button = dbc.Button(
    "Submit Review", id="run-review-completed-button", style=quarterstyle
)

run_review_acceptance_label = html.P("Is Data Acceptable?", style=quarterstyle)

run_review_acceptance = dcc.Dropdown(
    options={True: "Yes", False: "No"},
    id="run-review-acceptance",
    style=threequarterstyle,
)

fig = go.Figure()

run_review_curves = dcc.Graph(id="run-review-curves", figure=fig)

filter_option_objects = html.Div(
    [
        run_review_description,
        runset_info,
        html.Div(
            [
                html.Div(
                    [run_review_channel_selector_label, run_review_channel_selector],
                    style=halfstyle,
                ),
                html.Div(
                    [
                        run_review_xpcrmodule_selector_label,
                        run_review_xpcrmodule_selector,
                    ],
                    style=halfstyle,
                ),
            ]
        ),
        html.Div(
            [
                html.Div(
                    [
                        run_review_process_step_selector_label,
                        run_review_process_step_selector,
                    ],
                    style=halfstyle,
                ),
                html.Div(
                    [run_review_color_selector_label, run_review_color_selector],
                    style=halfstyle,
                ),
            ]
        ),
        html.Div(
            [
                html.Div(
                    [run_review_run_selector_label, run_review_run_selector],
                    style=halfstyle,
                ),
                html.Div(
                    [run_review_lane_selector_label, run_review_lane_selector],
                    style=halfstyle,
                ),
            ]
        ),
        html.Div(
            [
                html.Div(
                    [run_review_acceptance_label, run_review_acceptance],
                    style=halfstyle,
                ),
                html.Div([run_review_status_update_button], style=halfstyle),
            ]
        ),
        html.Div(
            [
                html.Div([run_review_download_data], style=halfstyle),
                html.Div([add_review_group_button], style=halfstyle),
            ]
        ),
    ]
)

graph_objects = html.Div(
    [dcc.Loading(id="run-review-loading", type="graph", children=[run_review_curves])]
)
