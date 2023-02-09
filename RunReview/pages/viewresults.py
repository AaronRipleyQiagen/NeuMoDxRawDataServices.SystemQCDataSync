from dash import html, callback, Output, Input, State, register_page, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go

register_page(__name__, path="/run-review/view-results/")

fig = go.Figure()

module_issues = [{'label': 'EP Variance is too high', 'value': 1},
                 {'label': 'Ct Variance is too high', 'value': 2},
                 {'label': 'Optics Baseline Left / Right Split', 'value': 3},
                 {'label': 'Weak Overall Module Performance', 'value': 4}]

lane_issues = [{'label': 'Inhibited Lane Performance', 'value': 1},
               {'label': 'Step Noise Observed', 'value': 2},
               {'label': 'Optics Noise Observed', 'value': 3},
               {'label': 'Elevated Baseline', 'value': 4}
               ]

remediation_actions = [{'label': 'Increase Jack Pressure', 'value': 1},
                       {'label': 'Reflange Fluid Line', 'value': 2},
                       {'label': 'Perform Optics Calibration', 'value': 3},
                       {'label': 'Repeat Testing As Is', 'value': 4}]

run_review_description = html.H1(id='run-review-description')
run_review_channel_selector = dcc.Dropdown(
    ['Yellow', 'Green', 'Orange', 'Red', 'Far Red'], value='Yellow', id='run-review-channel-selector')
run_review_process_step_selector = dcc.Dropdown(
    ['Normalized', 'Raw', '2nd'], value='Normalized', id='run-review-process-step-selector')
run_review_curves = dcc.Graph(id="run-review-curves", figure=fig)
run_review_line_data = dash_table.DataTable(
    id='runset-sample-results', row_selectable='Multi', sort_action='native')


tab1_content = dbc.Card(
    dbc.CardBody(
        [
            run_review_line_data
        ]
    ),
    className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Please Select Issue", className="card-text"),
            dcc.Dropdown(id='module-issue-options', options=module_issues),
            dbc.Button("Submit Module Issue", id='module-issue-submit')
        ]
    ),
    className="mt-3",
)

tab3_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Please Select Issue", className="card-text"),
            dcc.Dropdown(id='lane-issue-options', options=lane_issues),
            dbc.Button("Submit Lane Issue", id='lane-issue-submit')
        ]
    ),
    className="mt-3",
)

tab4_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Coming Soon", className="card-text"),
        ]
    ),
    className="mt-3",
)

tab5_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Please Choose a Remediation Action", className="card-text"),
            dcc.Dropdown(id='remediation-action-options',
                         options=remediation_actions),
            dbc.Button("Submit Action", id='remediation-action-submit')
        ]
    ),
    className="mt-3",
)

tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="View Line Data"),
        dbc.Tab(tab2_content, label="Note Module Issue"),
        dbc.Tab(tab3_content, label="Note Lane Issue"),
        dbc.Tab(tab4_content, label='View Active Issues'),
        dbc.Tab(tab5_content, label='Assign Remediation Action')
    ]
)
layout = [dcc.Loading(id='run-review-loading', type='graph', children=[
                      run_review_description, run_review_channel_selector, run_review_process_step_selector, run_review_curves, tabs])]  # , run_review_channel_selector,
# run_review_process_step_selector, run_review_curves, run_review_line_data, run_review_submit_button]
