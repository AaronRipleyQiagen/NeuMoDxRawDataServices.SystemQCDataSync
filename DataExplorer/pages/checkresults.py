from dash import (
    html,
    callback,
    clientside_callback,
    Output,
    Input,
    State,
    register_page,
    dcc,
    dash_table,
    ctx,
    no_update,
)
import dash_bootstrap_components as dbc
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import requests

import dash_ag_grid as dag
from Shared.neumodx_objects import SampleJSONReader, getSampleDataAsync
from Shared.styles import *
from Shared.Components import *

fig = go.Figure()

colorDict = {
    1: "#FF0000",  # Red 1
    2: "#00B050",  # Green 2
    3: "#0070C0",  # Blue 3
    4: "#7030A0",  # Purple 4
    5: "#808080",  # Light Grey 5
    6: "#FF6600",  # Orange 6
    7: "#FFCC00",  # Yellow 7
    8: "#9999FF",  # Light Purple 8
    9: "#333333",  # Black 9
    10: "#808000",  # Goldish 10
    11: "#FF99CC",  # Hot Pink 11
    12: "#003300",  # Dark Green 12
}

register_page(__name__, path="/results/")


"""
Layout Components
"""
data_explorer_external_link_redirect = html.Div(
    id="data-explorer-external-link-redirect"
)
created_runset_id = dcc.Store(id="created-runset-id", storage_type="session")
sample_results_table = dag.AgGrid(
    enableEnterpriseModules=True,
    rowData=[],
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection="single",
    id="sample-results-table",
)
reviewgroup_selector_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Add Runset Review Assignemnts")),
        dbc.ModalBody(
            children=[
                html.Label("Select Groups required to review this runset."),
                dbc.Checklist(id="review-group-options", switch=True),
            ]
        ),
        dbc.ModalFooter(
            [
                dbc.Button(
                    "Submit",
                    id="submit-reviewgroup-selection-button",
                    className="ms-auto",
                    n_clicks=0,
                ),
                dbc.Button(
                    "Cancel",
                    id="cancel-reviewgroup-selection-button",
                    className="ms-auto",
                    n_clicks=0,
                ),
            ]
        ),
    ],
    id="reviewgroup-selector-modal-data-explorer",
    is_open=False,
)
post_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Runset Creation Result")),
        dbc.ModalBody(
            children=[
                html.P("Runset was successfully created."),
                dbc.Button("View Runset", id="view-runset-button"),
            ]
        ),
        dbc.ModalFooter(),
    ],
    id="post-response",
    is_open=False,
)
runset_selector_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Run Type Selector")),
        dbc.ModalBody("Please Make A Run Type Selection"),
        dcc.Dropdown(id="runset-type-options"),
        dbc.ModalFooter(
            [
                dbc.Button(
                    "Submit", id="submit-button", className="ms-auto", n_clicks=0
                ),
                dbc.Button(
                    "Cancel", id="cancel-button", className="ms-auto", n_clicks=0
                ),
            ]
        ),
    ],
    id="runset-selector-modal",
    is_open=False,
)


runset_attempt_prompt = UserInputModal(
    aio_id="data-explorer",
    modal_body=RunSetAttemptModalBody(aio_id="data-explorer"),
)

channel_selector = dcc.Dropdown(
    ["Yellow", "Green", "Orange", "Red", "Far Red"],
    value="Yellow",
    id="channel-selector",
)
process_step_selector = dcc.Dropdown(
    ["Normalized", "Raw", "2nd"], value="Raw", id="process-step-selector"
)
create_run_review_button = dbc.Button(
    "Create Run Review from Dataset", id="create-run-review-button"
)
run_review_confirmation = html.H1(id="run-review-confirmation")
fig = dcc.Graph(id="curves", figure=fig)
layout = html.Div(
    children=[
        created_runset_id,
        html.H1(id="h1_1", children="Results Viewer"),
        dcc.Loading(
            id="samples-loading",
            type="graph",
            fullscreen=True,
            children=[
                channel_selector,
                process_step_selector,
                fig,
                sample_results_table,
                create_run_review_button,
                run_review_confirmation,
            ],
        ),
        dcc.Loading(
            id="pending-post",
            type="cube",
            fullscreen="true",
            children=[reviewgroup_selector_modal, post_response, runset_selector_modal],
        ),
        data_explorer_external_link_redirect,
    ]
)


@callback(
    Output("channel-selector", "value"),
    Output("process-step-selector", "value"),
    Output("sample-info", "data"),
    Output("runset-type-options", "options"),
    Input("url", "href"),
    State("selected-cartridge-sample-ids", "data"),
)
def get_sample_ids_from_dcc_store(href, selected_cartridge_sample_ids):
    print("Getting Data from DCC Store")
    selected_sample_ids = []
    sample_id_container = []
    for cartridge_id in selected_cartridge_sample_ids:
        for sample_id in selected_cartridge_sample_ids[cartridge_id]:
            selected_sample_ids.append(sample_id)
    sample_data = getSampleDataAsync(selected_sample_ids)
    jsonReader = SampleJSONReader(json.dumps(sample_data))
    jsonReader.standardDecode()
    dataframe = jsonReader.DataFrame
    dataframe["RawDataDatabaseId"] = dataframe.reset_index()["id"].values
    dataframe["Channel"] = dataframe["Channel"].replace("Far_Red", "Far Red")

    """
    Get SPC2 Channel Based on Result Code Id
    """
    if dataframe["Result Code"][0] in ["QUAL", "HCV", "CTNG"]:
        SPC2_channel = "Yellow"
    else:
        SPC2_channel = "Red"

    """
    Get Run Set Type Options based on Result Codes contained in DataFrame
    """

    runsettypeoptions = {}
    for resultcode in dataframe["Result Code"].unique():
        request_url = os.environ[
            "RUN_REVIEW_API_BASE"
        ] + "QualificationAssays/{}".format(resultcode)
        print(request_url)
        try:
            resp = requests.get(request_url, verify=False).json()

            for runsettype in resp["runSetTypes"]:
                runsettypeoptions[runsettype["id"]] = runsettype["description"]
        except:
            pass

    return (
        SPC2_channel,
        "Normalized",
        dataframe.to_dict(orient="records"),
        runsettypeoptions,
    )


@callback(
    [
        Output("curves", "figure"),
        Output("sample-results-table", "rowData"),
        Output("sample-results-table", "columnDefs"),
    ],
    [
        Input("channel-selector", "value"),
        Input("process-step-selector", "value"),
        Input("sample-info", "data"),
    ],
    prevent_initial_call=True,
)
def update_pcr_curves(channel, process_step, data):
    dataframe = pd.DataFrame.from_dict(data)
    dataframe["Channel"] = dataframe["Channel"].replace("Far_Red", "Far Red")
    # Start making graph...
    fig = go.Figure()
    df = dataframe.reset_index().set_index(
        ["Channel", "Processing Step", "XPCR Module Serial"]
    )
    try:
        df_Channel = df.loc[channel]
    except KeyError:
        channel = df.index.unique(0)[0]
        df_Channel = df.loc[channel]

    df_Channel_Step = df_Channel.loc[process_step].reset_index()
    df_Channel_Step.sort_values("XPCR Module Lane", inplace=True)

    readings_columns = df_Channel_Step[
        [
            x
            for x in df_Channel_Step.columns
            if "Reading " in x
            and "Blank" not in x
            and "Dark" not in x
            and "Id" not in x
        ]
    ]
    cycles = np.arange(1, len(readings_columns.columns) + 1)
    df_Channel_Step["Readings Array"] = [
        np.column_stack(zip(cycles, x)) for x in readings_columns.values
    ]

    for idx in df_Channel_Step.index:
        X = np.array([read for read in df_Channel_Step.loc[idx, "Readings Array"]][0])
        Y = np.array([read for read in df_Channel_Step.loc[idx, "Readings Array"]][1])
        _name = str(df_Channel_Step.loc[idx, "XPCR Module Lane"])
        fig.add_trace(
            go.Scatter(
                x=X,
                y=Y,
                mode="lines",
                name=_name,
                line=dict(
                    color=colorDict[df_Channel_Step.loc[idx, "XPCR Module Lane"]]
                ),
            )
        )
    output_frame = df_Channel_Step  # .to_dict('records'

    inital_selection = [
        "XPCR Module Serial",
        "XPCR Module Lane",
        "Sample ID",
        "Target Name",
        "Localized Result",
        "Overall Result",
        "Ct",
        "End Point Fluorescence",
        "Max Peak Height",
        "EPR",
    ]
    column_definitions = []
    aggregates = ["Ct", "EPR", "End Point Fluorescence", "Max Peak Height"] + [
        x for x in output_frame.columns if "Baseline" in x or "Reading" in x
    ]
    groupables = ["XPCR Module Serial"] + [
        x for x in output_frame.columns if "Lot" in x or "Serial" in x or "Barcode" in x
    ]
    floats = ["Ct", "EPR"]
    ints = ["End Point Fluorescence", "Max Peak Height"]
    for column in output_frame.columns:
        column_definition = {"headerName": column, "field": column, "filter": True}
        if column not in inital_selection:
            column_definition["hide"] = True
        if column in aggregates:
            column_definition["enableValue"] = True
        if column in groupables:
            column_definition["enableRowGroup"] = True
        # if column in ints:
        #     column_definition['valueFormatter'] = {
        #         "function": "'$' + (params.value)"}
        column_definitions.append(column_definition)
    return fig, output_frame.to_dict("records"), column_definitions


@callback(
    Output("runset-selector-modal", "is_open"),
    [
        Input("create-run-review-button", "n_clicks"),
        Input("submit-button", "n_clicks"),
        Input("cancel-button", "n_clicks"),
    ],
    [State("runset-selector-modal", "is_open")],
    prevent_initial_call=True,
)
def switch_runset_selector(create_clicks, submit_clicks, cancel_clicks, is_open):
    if create_clicks or cancel_clicks or submit_clicks:
        return not is_open

    return is_open


@callback(
    Output("reviewgroup-selector-modal-data-explorer", "is_open"),
    Input("review-group-options", "options"),
    Input("submit-reviewgroup-selection-button", "n_clicks"),
    Input("cancel-reviewgroup-selection-button", "n_clicks"),
    State("reviewgroup-selector-modal-data-explorer", "is_open"),
    prevent_initial_call=True,
)
def switch_runset_selector(
    options, submit_button, cancel_button, reviewgroup_selector_modal_is_open
):
    return not reviewgroup_selector_modal_is_open


"""
Following Javascript function allows for users to redirect the user to a specific run-review page.
Note that because the way this is used (Dash App embedded inside of Flask App), it is necessary to 
use javascript to do this redirect.
"""

clientside_callback(
    """
        function goToRunSetPage(n_clicks, runset_id) {
            if (n_clicks && n_clicks > 0) {
                var currentHref = window.top.location.href;
                var splitString = '/data-explorer/';
                var hrefParts = currentHref.split(splitString);
                if (hrefParts.length > 1) {
                    var newHref = hrefParts[0] + '/run-review/' + runset_id;
                    window.top.location.href = newHref;
                }
            }
        }
        """,
    Output("data-explorer-external-link-redirect", "children"),
    Input("view-runset-button", "n_clicks"),
    State("created-runset-id", "data"),
)
