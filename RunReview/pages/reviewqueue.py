from flask import redirect, url_for
from dash import Dash, dcc, html, Input, Output, State, dash_table, callback, register_page
import dash_bootstrap_components as dbc
import pandas as pd
import dash_ag_grid as dag
import os
import requests

register_page(__name__, path="/run-review/review-queue/")

"""
Access API Endpoint to retreieve runsets from database.
"""
api_url = os.environ['RUN_REVIEW_API_BASE']

review_queue = dcc.Loading(id='review_queue_loading', children=[dag.AgGrid(
    enableEnterpriseModules=True,
    # licenseKey=os.environ['AGGRID_ENTERPRISE'],
    # columnDefs=initial_columnDefs,
    # rowData=[],
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection='single',
    id='review-queue-table'
)], type='circle')

runset_status_selection_label = html.Label("Filter By Runset Status:",
                                           style={'width': '50%',
                                                  'display': 'inline-block',
                                                  'vertical-align': 'middle',
                                                  'horizontal-align': 'left'})

runset_status_selections = dcc.Dropdown(id='runset-status-selections',
                                        options={'Queue': 'Queue',
                                                 'Reviewing': 'Reviewing',
                                                 'Approved': 'Approved',
                                                 'Rejected': 'Rejected'},
                                        multi=True,
                                        value=['Queue', 'Reviewing'],
                                        style={'display': 'inline-block',
                                               'vertical-align': 'middle',
                                               'horizontal-align': 'left',
                                               'width': '100%'},
                                        )

review_group_completed_filter = dcc.Checklist(
    options=[
        {'label': 'Filter Out Runsets my Group has Completed?', 'value': True},
    ],
    value=[True],
    inline=True,
    id='review-group-completed-filter'
)

review_assignment_label = html.Label("Filter by Review Assignment",
                                     style={'width': '50%',
                                            'display': 'inline-block',
                                            'vertical-align': 'middle',
                                            'horizontal-align': 'left'})

review_assignment_selections = dcc.Dropdown(id='review-assignment-selections',
                                            multi=True,
                                            style={'display': 'inline-block',
                                                   'vertical-align': 'middle',
                                                   'horizontal-align': 'left',
                                                   'width': '100%'}
                                            )

runset_status_group = html.Div(
    children=[runset_status_selection_label,
              runset_status_selections],
    style={'width': '100%',
           'display': 'inline-block',
           'vertical-align': 'middle',
           'horizontal-align': 'left'})


review_assignment_group = html.Div(
    children=[review_assignment_label, review_assignment_selections,
              review_group_completed_filter],
    style={'width': '100%',
           'display': 'inline-block',
           'vertical-align': 'middle',
           'horizontal-align': 'left'})

refresh_button = dbc.Button("Refresh Data", id='refresh-review-queue')

get_runset_data = dbc.Button(
    'Review Data', id='get-runset-data',  n_clicks=0)

layout = [html.Div([runset_status_group, review_assignment_group], style={'padding-bottom': '2.5%'}), review_queue,
          html.Div([refresh_button, get_runset_data])]
