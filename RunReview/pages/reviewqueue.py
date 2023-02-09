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
# api_url = "https://localhost:7191/api/"


def populate_review_queue():
    runsets_url = api_url + "RunSets"

    runsets = requests.get(url=runsets_url, verify=False).json()

    df = pd.DataFrame.from_dict(runsets)
    df['Status'] = [x[0]['runSetStatus']['name']
                    for x in df['runSetRunSetStatuses']]

    df['XPCR Module'] = [x[0]['xpcrModule']
                          ['xpcrModuleSerial'] for x in df['runSetXPCRModules']]

    columns = ['id', 'Status', 'XPCR Module', 'name', 'number', 'runSetStartDate',
               'sampleCount']

    groupable_columns = ['Status', 'XPCR Module']

    column_names = {'name': 'Description', 'number': 'Number',
                    'runSetStartDate': 'Start Date', 'sampleCount': 'Sample Count'}
    df = df[columns].rename(column_names, axis=1)

    df_columnDefs = []
    for column in df.columns:
        if 'Date' in column:
            df[column] = df[column].astype(
                'datetime64').dt.strftime("%d %B %Y %H:%M:%S")
        if column in groupable_columns:
            df_columnDefs.append(
                {"headerName": column, "field": column, "rowGroup": True, "filter": True})
        else:
            if column != 'id':
                df_columnDefs.append(
                    {"headerName": column, "field": column, "filter": True})
    return df.to_dict('records'), df_columnDefs


intial_data, initial_columnDefs = populate_review_queue()

review_queue = dag.AgGrid(
    enableEnterpriseModules=True,
    # licenseKey=os.environ['AGGRID_ENTERPRISE'],
    columnDefs=initial_columnDefs,
    rowData=intial_data,
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection='single',
    setRowId="id",
    id='review-queue-table'
)

refresh_button = dbc.Button("Refresh Data", id='refresh-review-queue')
load_review_queue = html.Div(id='review_queue_loading')
get_runset_data = dbc.Button('Review Data', id='get-runset-data')
layout = [review_queue, html.Div([refresh_button]), get_runset_data]
