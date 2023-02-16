from dash import html, callback, Output, Input, State, register_page, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash_ag_grid as dag

register_page(__name__, path="/run-review/view-results/")

fig = go.Figure()
halfstyle = {'width': '50%', 'display': 'inline-block',
             'vertical-align': 'middle', 'horizontal-align': 'left'}
onethirdstyle = {'width': '33%', 'display': 'inline-block',
                 'vertical-align': 'middle', 'horizontal-align': 'center'}
quarterstyle = {'width': '35%', 'display': 'inline-block',
                'vertical-align': 'middle', 'horizontal-align': 'left'}
threequarterstyle = {'width': '65%', 'display': 'inline-block',
                     'vertical-align': 'middle', 'horizontal-align': 'right'}
remediation_actions = [{'label': 'Increase Jack Pressure', 'value': 1},
                       {'label': 'Reflange Fluid Line', 'value': 2},
                       {'label': 'Perform Optics Calibration', 'value': 3},
                       {'label': 'Repeat Testing As Is', 'value': 4}]

run_review_description = html.H1(id='run-review-description')

run_review_channel_selector_label = html.P(
    "Choose Channel", style=quarterstyle)
run_review_channel_selector = dcc.Dropdown(
    id='run-review-channel-selector', style=threequarterstyle)

run_review_xpcrmodule_selector_label = html.P(
    "Choose XPCR Module", style=quarterstyle)
run_review_xpcrmodule_selector = dcc.Dropdown(
    id='run-review-xpcrmodule-selector', style=threequarterstyle)


run_review_run_selector_label = html.P(
    "Filter for specific runs", style=quarterstyle)
run_review_run_selector = dcc.Dropdown(
    id='run-review-run-selector', style=threequarterstyle)
run_review_lane_selector_label = html.P(
    "Filter for specific lanes", style=quarterstyle)
run_review_lane_selector = dcc.Dropdown(
    id='run-review-lane-selector', style=threequarterstyle)
run_review_color_selector_label = html.P(
    "Choose Color Attribute", style=quarterstyle)
run_review_color_selector = dcc.Dropdown(options=['XPCR Module Lane', 'Run'], value='XPCR Module Lane',
                                         id='run-review-color-selector', style=threequarterstyle)
run_review_process_step_selector_label = html.P(
    "Choose Process Step", style=quarterstyle)
run_review_process_step_selector = dcc.Dropdown(
    ['Normalized', 'Raw', '2nd'], value='Normalized', id='run-review-process-step-selector', style=threequarterstyle)
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
            html.Div([html.P("What XPCR Module is Affected?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='module-issue-module-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("What type of issue is this?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='module-issue-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("What optics channel is this issue observed on?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='module-issue-channel-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("How severe is this issue?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='module-issue-severity-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            dbc.Button('Submit Module Issue', id='submit-module-issue')
        ]
    ),
    className="mt-3",
)


run_issue_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div([html.P("What XPCR Module is Affected?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='run-issue-module-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("Which run was issue observed in?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='run-issue-run-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("What type of issue is this?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='run-issue-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("What optics channel is this issue observed on?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='run-issue-channel-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("How severe is this issue?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='run-issue-severity-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            dbc.Button('Submit Run Issue', id='submit-run-issue')
        ]
    )
)

module_lane_issue_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div([html.P("What XPCR Module is Affected?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='lane-issue-module-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("What lane is affected by issue?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='lane-issue-lane-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("What type of issue is this?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='lane-issue-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("What optics channel is this issue observed on?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='lane-issue-channel-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            html.Div([html.P("How severe is this issue?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='lane-issue-severity-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
            dbc.Button('Submit Lane Issue', id='submit-lane-issue')
        ]
    ),
    className="mt-3",
)

sample_issue_content = dbc.Card(
    dbc.CardBody(
        [
            html.Div([html.P("What XPCR Module is Affected?", className="card-text", style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle'}),
                      dcc.Dropdown(id='sample-issue-module-options', style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'middle'})]),
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
            dag.AgGrid(
                enableEnterpriseModules=True,
                # licenseKey=os.environ['AGGRID_ENTERPRISE'],
                # columnDefs=initial_columnDefs,
                # rowData=intial_data,
                columnSize="sizeToFit",
                defaultColDef=dict(
                    resizable=True,
                ),
                rowSelection='single',
                # setRowId="id",
                id='issues-table'
            )
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
    children=[
        dbc.Tab(line_data_content, label="View Line Data",
                tab_id='run-review-line-data'),
        dbc.Tab(module_issue_content, label="Note Module Issue",
                tab_id='run-review-module-issues'),
        dbc.Tab(run_issue_content, label="Note Run Issue",
                tab_id='run-review-run-issues'),
        dbc.Tab(module_lane_issue_content, label="Note Lane Issue",
                tab_id='run-review-module-lane-issues'),
        dbc.Tab(sample_issue_content, label="Note Sample Issue",
                tab_id='run-review-sample-issues'),
        dbc.Tab(active_issues_content, label='View Active Issues',
                tab_id='run-review-active-issues'),
        dbc.Tab(remediation_action_content, label='Assign Remediation Action',
                tab_id='run-review-remediation-actions')
    ], id='review-tabs'
)


issue_post_response = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Issue Creation Result")),
    dbc.ModalBody("Issue was added successfully")
],
    id="issue-post-response",
    is_open=False)

run_review_update_response = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Run Review Status Updated Successfully")),
    dbc.ModalBody("Run Review Status Changed to Completed.")
],
    id="run-review-status-update-post-response",
    is_open=False)

run_review_status_update_button = dbc.Button("Mark Review Completed",
                                             id='run-review-completed-button')
run_review_acceptance_label = html.P(
    "Is Data Acceptable?", style=quarterstyle)
run_review_acceptance = dcc.Dropdown(
    options={True: "Yes", False: "No"}, id='run-review-acceptance', style=threequarterstyle)
layout = [
    run_review_description,
    issue_post_response,
    run_review_update_response,

    html.Div([html.Div([run_review_channel_selector_label, run_review_channel_selector], style=halfstyle),
              html.Div([run_review_xpcrmodule_selector_label, run_review_xpcrmodule_selector], style=halfstyle)]),
    html.Div([html.Div([run_review_process_step_selector_label, run_review_process_step_selector], style=halfstyle),
              html.Div([run_review_color_selector_label, run_review_color_selector], style=halfstyle)]),
    html.Div([html.Div([run_review_run_selector_label, run_review_run_selector], style=halfstyle),
              html.Div([run_review_lane_selector_label, run_review_lane_selector], style=halfstyle)]),

    html.Div([html.Div([run_review_acceptance_label, run_review_acceptance], style=halfstyle),
              html.Div([run_review_status_update_button], style=halfstyle)]),


    dcc.Loading(id='run-review-loading', type='graph',
                children=[run_review_curves]),
    tabs]  # , run_review_channel_selector,
