from dash import html, callback, Output, Input, State, register_page, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go

register_page(__name__, path="/run-review/view-results/")

fig = go.Figure()


run_review_description = html.H1(id='run-review-description', children=["yes"])
run_review_channel_selector = dcc.Dropdown(
    ['Yellow', 'Green', 'Orange', 'Red', 'Far Red'], value='Yellow', id='run-review-channel-selector')
run_review_process_step_selector = dcc.Dropdown(
    ['Normalized', 'Raw', '2nd'], value='Normalized', id='run-review-process-step-selector')
run_review_curves = dcc.Graph(id="run-review-curves", figure=fig)
run_review_line_data = dash_table.DataTable(
    id='runset-sample-results', row_selectable='Multi', sort_action='native')
# run_review_submit_button = dbc.Button("Submit Run Review",
#                                       id='submit-run-review-button')
layout = [dcc.Loading(id='run-review-loading', type='graph', children=[
                      run_review_description, run_review_channel_selector, run_review_process_step_selector, run_review_curves, run_review_line_data])]  # , run_review_channel_selector,
# run_review_process_step_selector, run_review_curves, run_review_line_data, run_review_submit_button]
