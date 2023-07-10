from flask import session
from dash import Input, Output, dcc, html, no_update, ctx
import dash_bootstrap_components as dbc
from dash import Dash
from dash import (
    html,
    callback,
    Output,
    Input,
    State,
    register_page,
    dcc,
    dash_table,
)
import os
import requests
import json
import pandas as pd
import numpy as np
import warnings
import plotly.graph_objects as go
import aiohttp
import asyncio
import base64
import uuid
import logging
from flask_mail import Mail, Message
import app_config
import msal
from Shared.appbuildhelpers import *
from flask import redirect, url_for
from dash import (
    Dash,
    dcc,
    html,
    Input,
    Output,
    State,
    dash_table,
    callback,
    register_page,
)
import dash_bootstrap_components as dbc
import pandas as pd
import dash_ag_grid as dag
import os
import requests
from .functions import *

warnings.filterwarnings("ignore")

url_base = "/dashboard/run-review-queue/"

CONTENT_STYLE = {
    "margin-left": "2.5%",
    "margin-right": "2.5%",
    "margin-top": "2.5%",
}

review_loader = html.Div(id="run-reviewer-loader")

review_queue = dcc.Loading(
    id="review_queue_loading",
    children=[
        dag.AgGrid(
            enableEnterpriseModules=True,
            columnSize="sizeToFit",
            defaultColDef=dict(
                resizable=True,
            ),
            rowSelection="single",
            id="review-queue-table",
            style={"height": 600},
        )
    ],
    type="circle",
)

runset_status_selection_label = html.Label(
    "Filter By Runset Status:",
    style={
        "width": "50%",
        "display": "inline-block",
        "vertical-align": "middle",
        "horizontal-align": "left",
    },
)

runset_status_selections = dcc.Dropdown(
    id="runset-status-selections",
    options={
        "Queue": "Queue",
        "Reviewing": "Reviewing",
        "Approved": "Approved",
        "Rejected": "Rejected",
    },
    multi=True,
    value=["Queue", "Reviewing", "Rejected"],
    style={
        "display": "inline-block",
        "vertical-align": "middle",
        "horizontal-align": "left",
        "width": "100%",
    },
)

review_group_completed_filter = dcc.Checklist(
    options=[
        {"label": "Filter Out Runsets My Group Has Completed?", "value": True},
    ],
    value=[True],
    inline=True,
    id="review-group-completed-filter",
)

my_runsets_filter = dcc.Checklist(
    options=[
        {"label": "Filter To Only Runsets Created By Me?", "value": True},
    ],
    value=[False],
    inline=True,
    id="my-runsets-filter",
)

review_assignment_label = html.Label(
    "Filter by Review Assignment",
    style={
        "width": "50%",
        "display": "inline-block",
        "vertical-align": "middle",
        "horizontal-align": "left",
    },
)

review_assignment_selections = dcc.Dropdown(
    id="review-assignment-selections",
    multi=True,
    style={
        "display": "inline-block",
        "vertical-align": "middle",
        "horizontal-align": "left",
        "width": "100%",
    },
)

runset_status_group = html.Div(
    children=[runset_status_selection_label, runset_status_selections],
    style={
        "width": "100%",
        "display": "inline-block",
        "vertical-align": "middle",
        "horizontal-align": "left",
    },
)

review_assignment_group = html.Div(
    children=[
        review_assignment_label,
        review_assignment_selections,
        review_group_completed_filter,
        my_runsets_filter,
    ],
    style={
        "width": "100%",
        "display": "inline-block",
        "vertical-align": "middle",
        "horizontal-align": "left",
    },
)

refresh_button = dbc.Button(
    "Refresh Data",
    id="refresh-review-queue",
    style={"width": "30%", "margin-left": "2.5%", "display": "inline-block"},
)

get_runset_data = dbc.Button(
    "View Runset",
    id="get-runset-data",
    n_clicks=0,
    style={"width": "30%", "margin-left": "2.5%", "display": "inline-block"},
)

delete_runset_button = dbc.Button(
    "Delete Runset",
    id="delete-runset-button",
    style={"width": "30%", "margin-left": "2.5%", "display": "inline-block"},
)

delete_runset_confirmation_modal = dbc.Modal(
    [
        dbc.ModalHeader("Delete Runset Confirmation"),
        dbc.ModalBody(
            [
                html.P("Are you sure you would like to delete this Runset?"),
                html.Div(
                    [
                        dbc.Button(
                            "Confirm",
                            id="delete-runset-confirm-button",
                            style={
                                "width": "35%",
                                "margin-left": "10%",
                                "display": "inline-block",
                            },
                        ),
                        dbc.Button(
                            "Cancel",
                            id="delete-runset-cancel-button",
                            style={
                                "width": "35%",
                                "margin-left": "10%",
                                "display": "inline-block",
                            },
                        ),
                    ]
                ),
            ]
        ),
        dbc.ModalFooter(),
    ],
    id="delete-runset-confirmation",
)

delete_runset_response = dbc.Modal(
    [
        dbc.ModalHeader("Delete Runset Result"),
        dbc.ModalBody(html.P(id="delete-runset-result-message")),
        dbc.ModalFooter(),
    ],
    is_open=False,
    id="delete-runset-response",
)

buttons = html.Div(
    [refresh_button, get_runset_data, delete_runset_button], style={"padding": "10px"}
)

runset_id_selected = dcc.Store(id="runset-id-selected", storage_type="session")

page_container = [
    html.Div(
        [runset_status_group, review_assignment_group], style={"padding-bottom": "2.5%"}
    ),
    review_queue,
    buttons,
    delete_runset_confirmation_modal,
    delete_runset_response,
    runset_id_selected,
]

content = html.Div(
    id="run-reviewer-page-content", style=CONTENT_STYLE, children=page_container
)

layout = html.Div(
    [
        review_loader,
        dcc.Loading(
            id="run-review-href-loader",
            fullscreen=True,
            type="dot",
            children=[dcc.Location(id="run-review-url")],
        ),
        content,
        html.Div(id="external-link-output"),
    ]
)


def Add_Dash(app):
    app = Dash(
        __name__,
        server=app,
        url_base_pathname=url_base,
        use_pages=False,
        external_stylesheets=[dbc.themes.COSMO],
    )

    apply_layout_with_auth(app, layout)

    """
    Following Javascript function allows for users to redirect the user to a specific run-review page.
    Note that because the way this is used (Dash App embedded inside of Flask App), it is necessary to 
    use javascript to do this redirect.
    """

    app.clientside_callback(
        """
        function navigateToGoogle(n_clicks, runset_id) {
            if (n_clicks && n_clicks > 0) {
                var currentHref = window.top.location.href;
                var splitString = '/run-review-queue/';
                var hrefParts = currentHref.split(splitString);
                if (hrefParts.length > 1) {
                    var newHref = hrefParts[0] + '/run-review/' + runset_id;
                    window.top.location.href = newHref;
                }
            }
        }
        """,
        Output("external-link-output", "children"),
        Input("get-runset-data", "n_clicks"),
        State("runset-id-selected", "data"),
    )

    @app.callback(
        Output("runset-id-selected", "data"),
        Input("review-queue-table", "selectionChanged"),
    )
    def get_runset_selected(selection):
        if ctx.triggered_id:
            return selection[0]["Id"]
        else:
            return no_update

    @app.callback(
        Output("review-assignment-selections", "options"),
        Output("review-assignment-selections", "value"),
        Input("refresh-review-queue", "n_clicks"),
    )
    def get_review_group_options(n):
        review_groups_url = os.environ["RUN_REVIEW_API_BASE"] + "ReviewGroups"
        review_groups = requests.get(review_groups_url, verify=False).json()
        review_group_options = {}
        for review_group in review_groups:
            review_group_options[review_group["id"]] = review_group["description"]
        return review_group_options, session["user"].group_id

    @app.callback(
        Output("review-queue-table", "rowData"),
        Output("review-queue-table", "columnDefs"),
        Input("refresh-review-queue", "n_clicks"),
        Input("runset-status-selections", "value"),
        Input("review-assignment-selections", "value"),
        Input("review-group-completed-filter", "value"),
        Input("my-runsets-filter", "value"),
        Input("delete-runset-response", "is_open"),
    )
    def refresh_review_queue(
        n,
        runset_status_selections,
        review_assignment_selections,
        review_group_completed_filter,
        my_runsets_filter,
        delete_response_is_open,
    ):
        """
        Convert Runset Status Selections & review assisgnment selections to list in the event only one selection is made.
        """
        if ctx.triggered_id != "delete-runset-response" or (
            ctx.triggered_id == "delete-runset-response" and not delete_response_is_open
        ):
            initial_columnDefs = [
                {
                    "headerName": "Status",
                    "field": "Status",
                    "rowGroup": True,
                    "filter": True,
                },
                {"headerName": "XPCR Module", "field": "XPCR Module", "filter": True},
                {"headerName": "Description", "field": "Description", "filter": True},
                {"headerName": "Start Date", "field": "Start Date", "filter": True},
                {"headerName": "Sample Count", "field": "Sample Count", "filter": True},
                {"headerName": "Id", "field": "Id", "filter": True, "hide": True},
                {
                    "headerName": "UserId",
                    "field": "UserId",
                    "filter": True,
                    "hide": True,
                },
            ]

            if isinstance(runset_status_selections, str):
                runset_status_selections = [runset_status_selections]

            if isinstance(review_assignment_selections, str):
                review_assignment_selections = [review_assignment_selections]

            user_group_id = (
                session["user"].group_id
                if True in review_group_completed_filter
                else None,
            )

            if True in my_runsets_filter:
                my_runset_filter_value = True
            else:
                my_runset_filter_value = False
            rowData, columnDefs = populate_review_queue(
                session["user"].id,
                user_group_id=user_group_id,
                review_group_ids=review_assignment_selections,
                runset_status_ids=runset_status_selections,
                my_runsets_filter=my_runset_filter_value,
            )

            if rowData:
                return rowData, columnDefs
            else:
                return [], initial_columnDefs

    @app.callback(
        Output("delete-runset-button", "disabled"),
        Input("review-queue-table", "selectionChanged"),
    )
    def check_cartridge_delete_validity(selection):
        if ctx.triggered_id == "review-queue-table":
            if selection[0]["UserId"] == session["user"].id:
                return False
        return True

    @app.callback(
        Output("delete-runset-confirmation", "is_open"),
        Input("delete-runset-button", "n_clicks"),
        Input("delete-runset-confirm-button", "n_clicks"),
        Input("delete-runset-cancel-button", "n_clicks"),
        State("delete-runset-confirmation", "is_open"),
        prevent_intitial_call=True,
    )
    def control_delete_cartridge_picture_popup(
        delete_click, confirm_click, cancel_click, is_open
    ):
        if ctx.triggered_id and "delete" in ctx.triggered_id:
            return not is_open
        return is_open

    @app.callback(
        Output("delete-runset-response", "is_open"),
        Output("delete-runset-result-message", "children"),
        Input("delete-runset-confirm-button", "n_clicks"),
        State("review-queue-table", "selectionChanged"),
        State("delete-runset-response", "is_open"),
    )
    def delete_runset(confirm_click, selection, is_open):
        if ctx.triggered_id == "delete-runset-confirm-button":
            delete_cartridge_picture_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "Runsets/{}".format(selection[0]["Id"])
            print(delete_cartridge_picture_url)
            response = requests.delete(url=delete_cartridge_picture_url, verify=False)
            print("Runset Delete Status Code: ", response.status_code)
            if response.status_code == 200:
                message = "Runset was deleted successfully"
            else:
                message = "Runset was not deleted successfully"
            return not is_open, message
        else:
            return no_update

    return app.server


if __name__ == "__main__":
    app = Dash(
        name="dashboard-run-review-queue",
        use_pages=True,
        pages_folder="run-review-queue-pages",
        url_base_pathname=url_base,
        external_stylesheets=[dbc.themes.COSMO],
    )
    app.layout = html.Div(
        [review_loader, dcc.Location(id="run-review-url"), sidebar, content]
    )
    app.run_server(debug=True)
