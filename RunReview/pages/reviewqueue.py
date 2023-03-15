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

review_queue = dag.AgGrid(
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
    id='review-queue-table'
)

refresh_button = dbc.Button("Refresh Data", id='refresh-review-queue')
# load_review_queue = html.Div(id='review_queue_loading')
get_runset_data = dbc.Button(
    'Review Data', id='get-runset-data',  n_clicks=0)
layout = [review_queue, html.Div([refresh_button, get_runset_data])]
