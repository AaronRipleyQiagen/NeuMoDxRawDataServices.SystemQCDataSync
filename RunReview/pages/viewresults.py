from dash import html, callback, Output, Input, State, register_page, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go

register_page(__name__, path="/run-review/view-results/")

fig = go.Figure()

remediation_actions = [{'label': 'Increase Jack Pressure', 'value': 1},
                       {'label': 'Reflange Fluid Line', 'value': 2},
                       {'label': 'Perform Optics Calibration', 'value': 3},
                       {'label': 'Repeat Testing As Is', 'value': 4}]

run_review_description = html.H1(id='run-review-description')
run_review_channel_selector = dcc.Dropdown(id='run-review-channel-selector')
run_review_process_step_selector = dcc.Dropdown(
    ['Normalized', 'Raw', '2nd'], value='Normalized', id='run-review-process-step-selector')
run_review_curves = dcc.Graph(id="run-review-curves", figure=fig)
run_review_line_data = dash_table.DataTable(
    id='runset-sample-results', row_selectable='Multi', sort_action='native')


line_data_content = dbc.Card(
    dbc.CardBody(
        [
            run_review_line_data
        ]
    ),
    className="mt-3",
)

module_issue_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div([html.P("What type of issue is this?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='module-issue-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("What optics channel is this issue observed on?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='module-issue-channel-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("How severe is this issue?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='module-issue-severity-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            dbc.Button('Submit Module Issue', id='submit-sample-issue')
        ]
    ),
    className="mt-3",
)


run_issue_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div([html.P("Which run was issue observed in?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='run-issue-run-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("What type of issue is this?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='run-issue-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("What optics channel is this issue observed on?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='run-issue-channel-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("How severe is this issue?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='run-issue-severity-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            dbc.Button('Submit Run Issue', id='submit-sample-issue')
        ]
    )
)

module_lane_issue_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div([html.P("What lane is affected by issue?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='lane-issue-lane-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("What type of issue is this?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='lane-issue-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("What optics channel is this issue observed on?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='lane-issue-channel-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("How severe is this issue?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='lane-issue-severity-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            dbc.Button('Submit Lane Issue', id='submit-sample-issue')
        ]
    ),
    className="mt-3",
)

sample_issue_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div([html.P("Which run was issue observed in?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='sample-issue-run-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("What lane is affected by issue?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='sample-issue-lane-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("What type of issue is this?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='sample-issue-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("What optics channel is this issue observed on?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='sample-issue-channel-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("How severe is this issue?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='sample-issue-severity-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            dbc.Button('Submit Sample Issue', id='submit-sample-issue')
        ]
    )
)

active_issues_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Coming Soon", className="card-text"),
        ]
    ),
    className="mt-3",
)

remediation_action_content = dbc.Card(
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
        dbc.Tab(line_data_content, label="View Line Data"),
        dbc.Tab(module_issue_content, label="Note Module Issue"),
        dbc.Tab(run_issue_content, label="Note Run Issue"),
        dbc.Tab(module_lane_issue_content, label="Note Lane Issue"),
        dbc.Tab(sample_issue_content, label="Note Sample Issue"),
        dbc.Tab(active_issues_content, label='View Active Issues'),
        dbc.Tab(remediation_action_content, label='Assign Remediation Action')
    ]
)
layout = [dcc.Loading(id='run-review-loading', type='graph', children=[
                      run_review_description, run_review_channel_selector, run_review_process_step_selector, run_review_curves, tabs])]  # , run_review_channel_selector,
# run_review_process_step_selector, run_review_curves, run_review_line_data, run_review_submit_button]
