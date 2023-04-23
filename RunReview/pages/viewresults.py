from dash import html, callback, Output, Input, State, register_page, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash_ag_grid as dag
import os
from azure.storage.blob import BlobServiceClient
import base64

register_page(__name__, path="/run-review/view-results/")

fig = go.Figure()

halfstyle = {'width': '50%', 'display': 'inline-block',
             'vertical-align': 'middle', 'horizontal-align': 'left', 'padding-bottom': 5}

onethirdstyle = {'width': '33%', 'display': 'inline-block',
                 'vertical-align': 'middle', 'horizontal-align': 'center', 'padding-bottom': 5}

quarterstyle = {'width': '35%', 'display': 'inline-block',
                'vertical-align': 'middle', 'horizontal-align': 'right', 'padding-bottom': 5}

threequarterstyle = {'width': '65%', 'display': 'inline-block',
                     'vertical-align': 'middle', 'horizontal-align': 'right', 'padding-bottom': 5}

remediation_actions = [{'label': 'Increase Jack Pressure', 'value': 1},
                       {'label': 'Reflange Fluid Line', 'value': 2},
                       {'label': 'Perform Optics Calibration', 'value': 3},
                       {'label': 'Repeat Testing As Is', 'value': 4}]

run_review_description = html.H1(id='runset-description')

run_review_channel_selector_label = html.P(
    "Choose Channel", style=quarterstyle)

run_review_channel_selector = dcc.Dropdown(
    id='run-review-channel-selector', style=threequarterstyle)

run_review_xpcrmodule_selector_label = html.P(
    "Choose XPCR Module", style=quarterstyle)

run_review_xpcrmodule_selector = dcc.Dropdown(
    id='run-review-xpcrmodule-selector', style=threequarterstyle)

run_review_download_data = dbc.Button(
    "Download Data", style={'margin': 'auto'}, id='run-review-download-data')

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

run_review_line_data = dag.AgGrid(
    enableEnterpriseModules=True,
    # licenseKey=os.environ['AGGRID_ENTERPRISE'],
    # columnDefs=initial_columnDefs,
    rowData=[],
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection='single',
    id='runset-sample-results'
)

line_data_content = dbc.Card(
    dbc.CardBody(
        [
            run_review_line_data
        ]
    ),
    className="mt-3",
)

run_summary_table = dag.AgGrid(
    enableEnterpriseModules=True,
    # licenseKey=os.environ['AGGRID_ENTERPRISE'],
    # columnDefs=initial_columnDefs,
    rowData=[],
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection='single',
    id='run-summary-table',

)

run_summary_channel_label = html.Label(
    "Choose Optics Channel to Summarize:", style=quarterstyle)

run_summary_channel_selector = dcc.Dropdown(
    id='run-summary-channel-selector', style=halfstyle)

run_summary_content = dbc.Card(
    dbc.CardBody(
        [
            run_summary_channel_label,
            run_summary_channel_selector,
            run_summary_table
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
            ),
            html.Div([
                dbc.Button("Grade Issue Resolution",
                           id='issue-remediation-grade-button', disabled=True, style={'width': '35%', 'margin-left': '10%'}),
                dbc.Button("Delete Issue",
                           id='issue-delete-button', disabled=True, style={'width': '35%', 'margin-left': '10%'})])
        ]
    ),
    className="mt-3",
)

remediation_action_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Please Choose a Remediation Action", className="card-text"),
            html.Div([dcc.Dropdown(id='remediation-action-options', style=halfstyle),
                      dbc.Button("Submit Action", id='remediation-action-submit', style=halfstyle)]),
            dag.AgGrid(
                enableEnterpriseModules=True,
                # licenseKey=os.environ['AGGRID_ENTERPRISE'],
                # columnDefs=initial_columnDefs,
                # rowData={},
                columnSize="sizeToFit",
                defaultColDef=dict(
                    resizable=True,
                ),
                rowSelection='single',
                # setRowId="id",
                id='remediation-action-table'
            ),

            dbc.Button("Complete Remediation Action",
                       id='remediation-action-resolution', style={'width': '35%', 'margin-left': '10%'}),
            dbc.Button("Delete Remediation Action", id='remediation-action-delete-button',
                       style={'width': '35%', 'margin-left': '10%'})


        ]
    ),
    className="mt-3",
)

cartridge_pictures_content = dbc.Card(

    dbc.CardBody(
        [
            dcc.Upload(
                id='upload-cartridge-pictures',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '50%',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin-left': '25%',
                },
                # Allow multiple files to be uploaded
                multiple=True,
            ),

            html.Div(id='upload-cartridge-message'),

            dcc.Loading(id='cartridge-pictures-loading', type='dot', children=[dbc.Carousel(
                items=[],
                id="cartridge-images",
                className="carousel-fade",
            )])
        ]
    )


)

tadm_pictures_content = dbc.Card(

    dbc.CardBody(
        [
            dcc.Upload(
                id='upload-tadm-pictures',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '50%',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin-left': '25%',
                },
                # Allow multiple files to be uploaded
                multiple=True,
            ),
            html.Div(id='upload-tadm-message'),
            dcc.Loading(id='tadm-pictures-loading', type='dot', children=[dbc.Carousel(
                items=[],
                id="tadm-images",
                className="carousel-fade",
            )])
        ]
    )
)

comments_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Coming Soon :)", className="card-text")
        ]
    ),
    className="mt-3",
)

misc_files_table = dag.AgGrid(
    enableEnterpriseModules=True,
    # licenseKey=os.environ['AGGRID_ENTERPRISE'],
    # columnDefs=initial_columnDefs,
    # rowData=[],
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection='single',
    id='misc-files-table'
)

misc_file_download_button = dbc.Button(
    "Download File", id='misc-file-download-button')

misc_file_upload_button = dcc.Upload(
    id='misc-file-upload-button',
    children=html.Div([
        'Drag and Drop or ',
        html.A('Select Files')
    ]),
    style={
        'width': '100%',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin-left': '0%',
        'padding': '10px'
    },
    # Allow multiple files to be uploaded
    multiple=True,
)

misc_files_content = dbc.Card(
    dbc.CardBody(
        [
            misc_file_upload_button,
            misc_files_table,
            misc_file_download_button
        ]
    ),
    className="mt-3",
)

file_upload_response = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("File Upload Status")),
    dbc.ModalBody("File was uploaded successfully"),
    dbc.ModalFooter(children=[dbc.Button(
        "Close", id='file-upload-response-close-button')])
],
    id="file-upload-response",
    is_open=False)

runset_reviews_table = dag.AgGrid(
    enableEnterpriseModules=True,
    # licenseKey=os.environ['AGGRID_ENTERPRISE'],
    # columnDefs=initial_columnDefs,
    # rowData=[],
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection='single',
    id='runset-reviews-table'
)

run_review_content = dbc.Card(
    dbc.CardBody(
        [
            runset_reviews_table
        ]
    ),
    className="mt-3"
)

review_tabs = dbc.Tabs(
    children=[
        dbc.Tab(line_data_content, label="View Line Data",
                tab_id='run-review-line-data'),
        dbc.Tab(run_summary_content, label="View Run Stats",
                tab_id='run-summary-data'),
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
        dbc.Tab(remediation_action_content, label='Manage Remediation Actions',
                tab_id='run-review-remediation-actions'),
        dbc.Tab(cartridge_pictures_content,
                label='Cartridge Pictures', tab_id='cartidge-pictures'),
        dbc.Tab(tadm_pictures_content,
                label='TADM Pictures', tab_id='tadm-pictures'),
        dbc.Tab(misc_files_content, label='Miscellaneous Files',
                tab_id='misc-files'),
        dbc.Tab(run_review_content, label='Runset Reviews',
                tab_id='runset-reviews')
    ], id='review-tabs'
)

issue_post_response = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Issue Creation Result")),
    dbc.ModalBody("Issue was added successfully")
],
    id="issue-post-response",
    is_open=False)

issue_delete_confirmation = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Issue Deletion Confirmation")),
    dbc.ModalBody("Are you sure you want to delete this issue?"),
    html.Div([dbc.Button("Yes", id='issue-delete-confirmed-button',
                         style={'width': '35%', 'margin-left': '10%', 'display': 'inline-block'}),
              dbc.Button("No", id='issue-delete-canceled-button',
                         style={'width': '35%', 'margin-left': '10%', 'display': 'inline-block'})]
             )

],
    id="issue-delete-confirmation",
    is_open=False)

issue_delete_response = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle(
                    "Issue Deletion Result")),
    dbc.ModalBody("Issue was deleted successfully")
],
    id="issue-delete-response",
    is_open=False)

remediation_action_post_response = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Remediation Action Creation Result")),
    dbc.ModalBody("Remediation Action was added successfully")
],
    id="remediation-action-post-response",
    is_open=False)

remediation_action_update_response = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle(
                    "Remediation Action Update Result")),
    dbc.ModalBody("Remediation Action was updated successfully")
],
    id="remediation-action-update-response",
    is_open=False)

remediation_action_delete_confirmation = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle(
                    "Remediation Action Deletion Confirmation")),
    dbc.ModalBody("Are you sure you want to delete this remediation action?"),
    html.Div([dbc.Button("Yes", id='remediation-action-delete-confirmed-button',
                         style={'width': '35%', 'margin-left': '10%', 'display': 'inline-block'}),
              dbc.Button("No", id='remediation-action-delete-canceled-button',
                         style={'width': '35%', 'margin-left': '10%', 'display': 'inline-block'})])
],
    id="remediation-action-delete-confirmation",
    is_open=False)

remediation_action_delete_response = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle(
                    "Remediation Action Deletion Result")),
    dbc.ModalBody("Remediation Action was deleted successfully")
],
    id="remediation-action-delete-response",
    is_open=False)

issue_resolution_remediation_action_selection = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Remediation Action Selection")),
    dbc.ModalBody([
        html.P("Please select the remediation action intended to address this issue."),
        dcc.Dropdown(id='issue-resolution-remediation-action-options'),
        html.P("Did it work?"),
        dcc.Dropdown(id='issue-resolution-remediation-success',
                     options={1: 'Yes', 0: 'No'}),
        dbc.Button("Submit", id='issue-resolution-submit')]
    )],
    id="issue-resolution-remediation-action-selection-prompt",
    is_open=False)

issue_resolution_remediation_action_response = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Issue Resolution Status")),
    dbc.ModalBody("Remediation Attempt was recorded successfully")
],
    id="issue-remediation-attempt-submission-response",
    is_open=False)

run_review_update_response = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Run Review Status Updated Successfully")),
    dbc.ModalBody("Run Review Status Changed to Completed.")
],
    id="run-review-status-update-post-response",
    is_open=False)

run_review_status_update_button = dbc.Button("Submit Review",
                                             id='run-review-completed-button', style=quarterstyle)

run_review_acceptance_label = html.P(
    "Is Data Acceptable?", style=quarterstyle)

run_review_acceptance = dcc.Dropdown(
    options={True: "Yes", False: "No"}, id='run-review-acceptance', style=threequarterstyle)

reviewgroup_selector_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Add Runset Review Assignemnts")),
        dbc.ModalBody(children=[html.Label("Select Groups required to review this runset."),
                                dbc.Checklist(id="review-group-options",
                                              switch=True
                                              ),
                                ]),

        dbc.ModalFooter(
            [dbc.Button(
                "Submit", id="submit-reviewgroup-selection-button", className="ms-auto", n_clicks=0
            ),


                dbc.Button(
                "Cancel", id="cancel-reviewgroup-selection-button", className="ms-auto", n_clicks=0
            )]
        ),

    ],
    id="reviewgroup-selector-modal",
    is_open=False,
)

add_review_assignment_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Run Review Assignment result")),
        dbc.ModalBody("Run Review Assignment was added successfully")
    ],
    id="add-review-assignment-response",
    is_open=False,
)

add_review_group_button = dbc.Button("Add Reviewer for Dataset",
                                     id='add-review-group-button')

layout = [
    run_review_description,
    issue_post_response,
    run_review_update_response,
    remediation_action_post_response,
    remediation_action_update_response,
    remediation_action_delete_confirmation,
    remediation_action_delete_response,
    issue_delete_confirmation,
    issue_delete_response,
    issue_resolution_remediation_action_selection,
    issue_resolution_remediation_action_response,
    reviewgroup_selector_modal,
    add_review_assignment_response,
    file_upload_response,

    html.Div([html.Div([run_review_channel_selector_label, run_review_channel_selector], style=halfstyle),
              html.Div([run_review_xpcrmodule_selector_label, run_review_xpcrmodule_selector], style=halfstyle)]),
    html.Div([html.Div([run_review_process_step_selector_label, run_review_process_step_selector], style=halfstyle),
              html.Div([run_review_color_selector_label, run_review_color_selector], style=halfstyle)]),
    html.Div([html.Div([run_review_run_selector_label, run_review_run_selector], style=halfstyle),
              html.Div([run_review_lane_selector_label, run_review_lane_selector], style=halfstyle)]),

    html.Div([html.Div([run_review_acceptance_label, run_review_acceptance], style=halfstyle),
              html.Div([run_review_status_update_button], style=halfstyle)]),

    html.Div([html.Div([run_review_download_data], style=halfstyle),
              html.Div([add_review_group_button], style=halfstyle)]),

    dcc.Loading(id='run-review-loading', type='graph',
                children=[run_review_curves]),
    review_tabs]  # , run_review_channel_selector,
