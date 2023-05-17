from flask import session
from dash import Input, Output, dcc, html, no_update, ctx
import dash_bootstrap_components as dbc
from dash import Dash
from .appbuildhelpers import apply_layout_with_auth
from dash import (
    html,
    callback,
    Output,
    Input,
    State,
    register_page,
    dcc,
    dash_table,
    page_container,
)
from .functions import *
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

warnings.filterwarnings("ignore")

system_qc_tech_IIs = {
    "Brian": "brian.colson1@contractor.qiagen.com",
    "Hunter": "hunter.rose1@contractor.qiagen.com",
    "Isaiah": "isaiah.thompson1@contractor.qiagen.com",
    "Keller": "keller.masing@contractor.qiagen.com",
    "Kyla": "kyla.tackett1@contractor.qiagen.com",
    "Nathan": "nathan.king1@contractor.qiagen.com",
    "Richie": "richard.wynn1@contractor.qiagen.com",
}
system_qc_reviewers = {
    "Leanna": "leanna.hoyer@qiagen.com",
    "Jeremias": "jeremias.lioi@qiagen.com",
}
system_integration_reviewers = {
    "Catherine": "catherine.couture@qiagen.com",
    "Aaron": "aaron.ripley@qiagen.com",
}
engineering_reviewers = {"Vik": "viktoriah.slusher@qiagen.com"}
admin_reviewers = {"David": "david.edwin@qiagen.com"}

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
    "Left": "#FF0000",  # Red Left
    "Right": "#00B050",  # Green Right
}

url_base = "/dashboard/"
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H3("Run Review Options", className="display-6"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/dashboard/run-review/",
                            active="exact"),
                dbc.NavLink(
                    "Run Review Queue",
                    href="/dashboard/run-review/review-queue",
                    active="exact",
                ),
                dbc.NavLink(
                    "View Module History",
                    href="/dashboard/run-review/module-history",
                    active="exact",
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

review_loader = html.Div(id="run-reviewer-loader")

content = html.Div(
    id="run-reviewer-page-content", style=CONTENT_STYLE, children=page_container
)

runset_selection = dcc.Store(
    id="runset-selection-data", storage_type="session", data=""
)

runset_sample_data = dcc.Store(id="runset-sample-data", storage_type="session")

runset_review = dcc.Store(id="runset-review", storage_type="session", data="")

runset_channel_options = dcc.Store(
    id="runset-channel-options", storage_type="session", data=""
)

channel_selected = dcc.Store(
    id="channel-selected", storage_type="session", data="")

spc_channel = dcc.Store(id="spc-channel", storage_type="session", data="")

runset_severity_options = dcc.Store(
    id="runset-severity-options", storage_type="session", data=""
)

severity_selected = dcc.Store(
    id="severity-selected", storage_type="session", data="")

runset_run_options = dcc.Store(
    id="runset-run-options", storage_type="session", data="")

run_option_selected = dcc.Store(
    id="run-option-selected", storage_type="session", data=""
)

runset_xpcrmodulelane_options = dcc.Store(
    id="runset-xpcrmodulelane-options", storage_type="session", data=""
)

xpcrmodulelane_selected = dcc.Store(
    id="xpcrmodulelane-selected", storage_type="session", data=""
)

xpcrmodule_options = dcc.Store(
    id="xpcrmodule-options", storage_type="session", data="")

xpcrmodule_selected = dcc.Store(
    id="xpcrmodule-selected", storage_type="session", data=""
)

runset_subject_ids = dcc.Store(
    id="runset-subject-ids", storage_type="session", data="")

runset_subject_descriptions = dcc.Store(
    id="runset-subject-descriptions", storage_type="session"
)

pcrcurve_sample_info = dcc.Store(
    id="pcrcurve-sample-info", storage_type="session")

issue_selected = dcc.Store(id="issue-selected", storage_type="session")

flat_data_download = dcc.Download(id="flat-data-download")

remediation_action_selection = dcc.Store(
    id="remediation-action-selection", storage_type="session"
)

remediation_action_loader = dcc.Interval(
    id="remediation-action-loader", interval=60 * 1000, n_intervals=0  # in milliseconds
)

related_runsets = dcc.Store(id="related-runsets", storage_type="session")

issue_remediation_url = dcc.Store(
    id="issue-remediation-url", storage_type="session")

issue_delete_url = dcc.Store(id="issue-delete-url", storage_type="session")

issue_resolution_remediation_action_selection = dcc.Store(
    id="issue-resolution-remediation-action-selection", storage_type="session"
)

issue_remediation_type = dcc.Store(
    id="issue-remediation-type", storage_type="session")

layout = html.Div(
    [
        review_loader,
        dcc.Loading(
            id="run-review-href-loader",
            fullscreen=True,
            type="dot",
            children=[dcc.Location(id="run-review-url")],
        ),
        sidebar,
        content,
        runset_selection,
        runset_sample_data,
        runset_review,
        runset_severity_options,
        runset_channel_options,
        channel_selected,
        runset_run_options,
        run_option_selected,
        spc_channel,
        runset_xpcrmodulelane_options,
        xpcrmodulelane_selected,
        severity_selected,
        runset_subject_ids,
        xpcrmodule_options,
        xpcrmodule_selected,
        pcrcurve_sample_info,
        issue_selected,
        runset_subject_descriptions,
        flat_data_download,
        remediation_action_selection,
        related_runsets,
        issue_remediation_url,
        issue_resolution_remediation_action_selection,
        issue_remediation_type,
        remediation_action_loader,
        issue_delete_url,
    ]
)


def Add_Dash(app):
    app = Dash(
        __name__,
        server=app,
        url_base_pathname=url_base,
        use_pages=True,
        pages_folder="pages",
        external_stylesheets=[dbc.themes.COSMO],
    )
    server = app.server
    server.config["MAIL_SERVER"] = "smtp.gmail.com"
    server.config["MAIL_PORT"] = 465
    server.config["MAIL_USERNAME"] = "neumodxsystemqcdatasync@gmail.com"
    server.config["MAIL_PASSWORD"] = os.environ["EMAIL_PASSWORD"]
    server.config["MAIL_USE_TLS"] = False
    server.config["MAIL_USE_SSL"] = True
    mail = Mail(app.server)

    apply_layout_with_auth(app, layout)

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
            review_group_options[review_group["id"]
                                 ] = review_group["description"]
        return review_group_options, session["user"].group_id

    @app.callback(
        Output("review-queue-table", "rowData"),
        Output("review-queue-table", "columnDefs"),
        Input("refresh-review-queue", "n_clicks"),
        Input("runset-status-selections", "value"),
        Input("review-assignment-selections", "value"),
        Input("review-group-completed-filter", "value"),
        Input("delete-runset-response", "is_open"),
    )
    def refresh_review_queue(
        n,
        runset_status_selections,
        review_assignment_selections,
        review_group_completed_filter,
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
                {"headerName": "Sample Count",
                    "field": "Sample Count", "filter": True},
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

            if True in review_group_completed_filter:
                review_group_filter = session["user"].group_id
            else:
                review_group_filter = None

            rowData, columnDefs = populate_review_queue(
                session["user"].id,
                session["user"].group_display,
                review_group_ids=review_assignment_selections,
                runset_statuses=runset_status_selections,
                reviewer_group_id=review_group_filter,
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
        if "delete" in ctx.triggered_id:
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
            response = requests.delete(
                url=delete_cartridge_picture_url, verify=False)
            print("Runset Delete Status Code: ", response.status_code)
            if response.status_code == 200:
                message = "Runset was deleted successfully"
            else:
                message = "Runset was not deleted successfully"
            return not is_open, message
        else:
            return no_update

    @app.callback(
        Output("runset-selection-data", "data"),
        [Input("review-queue-table", "selectionChanged")],
    )
    def get_runset_selection_data(selected):
        if selected == None:
            return no_update
        runsetsample_url = os.environ[
            "RUN_REVIEW_API_BASE"
        ] + "RunSets/{}/Samples".format(selected[0]["Id"])
        _runset_samples = requests.get(runsetsample_url, verify=False).json()
        return _runset_samples

    @app.callback(
        [
            Output("runset-sample-data", "data"),
            Output("run-review-url", "href"),
            Output("runset-review", "data"),
            Output("runset-severity-options", "data"),
            Output("runset-channel-options", "data"),
            Output("runset-run-options", "data"),
            Output("spc-channel", "data"),
            Output("runset-xpcrmodulelane-options", "data"),
            Output("runset-subject-ids", "data"),
            Output("xpcrmodule-options", "data"),
            Output("runset-subject-descriptions", "data"),
        ],
        [Input("get-runset-data", "n_clicks"),
         State("runset-selection-data", "data")],
        prevent_inital_call=True,
    )
    def initialize_runset_data(n, runset_data):
        logging.info("initializing runset_data")
        if n == 0:
            logging.info("Button not pressed.")
            return no_update
        """
        Get Data associated with Runset.
        """
        print("collecting runset sample ids")
        logging.info("collecting runset sample ids")
        runset_sample_ids = []
        runset_map_df = pd.DataFrame(
            columns=[
                "RawDataDatabaseId",
                "RunSetSampleId",
                "SampleId",
                "XPCRModuleLaneId",
                "RunSetXPCRModuleLaneId",
                "CartridgeId",
                "RunSetCartridgeId",
                "XPCRModuleId",
                "RunSetXPCRModuleId",
                "NeuMoDxSystemId",
                "RunSetNeuMoDxSystemId",
            ]
        )
        idx = 0
        for runsetsample in runset_data["runSetSamples"]:
            runset_sample_ids.append(
                runsetsample["sample"]["rawDataDatabaseId"])

            runset_map = [
                runsetsample["sample"]["rawDataDatabaseId"],
                runsetsample["id"],
                runsetsample["sample"]["id"],
                runsetsample["sample"]["xpcrModuleLaneId"],
                runsetsample["sample"]["runSetXPCRModuleLaneSamples"][0][
                    "runSetXPCRModuleLaneId"
                ],
                runsetsample["sample"]["cartridgeId"],
                runsetsample["sample"]["runSetCartridgeSamples"][0][
                    "runSetCartridgeId"
                ],
                runsetsample["sample"]["xpcrModuleId"],
                runsetsample["sample"]["runSetXPCRModuleSamples"][0][
                    "runSetXPCRModuleId"
                ],
                runsetsample["sample"]["neuMoDxSystemId"],
                runsetsample["sample"]["runSetNeuMoDxSystemSamples"][0][
                    "runSetNeuMoDxSystemId"
                ],
            ]
            idx += 1
            runset_map_df.loc[idx] = runset_map
        print(
            "collected runset sample ids, {} samples in dataset".format(
                str(len(runset_sample_ids))
            )
        )
        runset_map_df.set_index("RawDataDatabaseId", inplace=True)
        sample_data = getSampleDataAsync(runset_sample_ids)

        jsonReader = SampleJSONReader(json.dumps(sample_data))
        jsonReader.standardDecode()
        dataframe = jsonReader.DataFrame
        dataframe["RawDataDatabaseId"] = dataframe.reset_index()["id"].values
        dataframe["Channel"] = dataframe["Channel"].replace(
            "Far_Red", "Far Red")
        dataframe["XPCR Module Side"] = np.where(
            dataframe["XPCR Module Lane"] < 7, "Right", "Left"
        )
        dataframe = (
            dataframe.set_index("RawDataDatabaseId").join(
                runset_map_df).reset_index()
        )

        """
        Get or Add RunSet Review
        """

        runsetreview = {}
        runsetreview["userId"] = session["user"].id
        runsetreview["reviewerName"] = session["user"].display_name
        runsetreview["reviewGroupId"] = session["user"].group_id
        runsetreview["reviewerEmail"] = session["user"].emails[0]
        runsetreview["runSetId"] = runset_data["id"]
        resp = requests.post(
            url=os.environ["RUN_REVIEW_API_BASE"] + "RunSetReviews",
            json=runsetreview,
            verify=False,
        ).json()

        runset_update_url = os.environ[
            "RUN_REVIEW_API_BASE"
        ] + "RunSets/{}/status".format(resp["runSetId"])
        runset_update_response = requests.put(
            url=runset_update_url, verify=False)
        print("Runset Update Response: " +
              str(runset_update_response.status_code))
        """
        Get Severity Options
        """
        severity_url = os.environ["RUN_REVIEW_API_BASE"] + "SeverityRatings"
        severity_resp = requests.get(severity_url, verify=False).json()
        severity_options = []
        for severity in severity_resp:
            severity_options.append(
                {"label": severity["name"], "value": severity["id"]}
            )

        """
        Get Run Set Channel options
        """
        channels_data = runset_data["runSetType"]["qualificationAssay"]["assayChannels"]
        channel_options = {}
        for channel in channels_data:
            channel_options[channel["id"]] = channel["channel"]
        dataframe.sort_values(["Start Date Time"], inplace=True)

        """
        Get Run Options
        """
        i = 0
        run_options = {}
        run_options["NoFilter"] = "All"
        for run in dataframe["RunSetCartridgeId"].unique():
            i += 1
            run_options[run] = "Run " + str(i)

        dataframe["Run"] = dataframe["RunSetCartridgeId"].replace(run_options)

        dataframe["Run"] = dataframe["Run"].str.replace("Run ", "").astype(int)

        """
        Get Lane Options
        """
        lane_options = {}
        lane_options["NoFilter"] = "All"
        dataframe.sort_values(["XPCR Module Lane"], inplace=True)
        for idx in dataframe.drop_duplicates(
            subset=["XPCR Module Lane", "RunSetXPCRModuleLaneId"]
        ).index:
            lane_options[dataframe.loc[idx, "RunSetXPCRModuleLaneId"]] = "Lane " + str(
                dataframe.loc[idx, "XPCR Module Lane"]
            )

        """
        Get SPC Channel
        """
        spc_channel_color = dataframe.loc[
            dataframe["Target Name"].str.contains("SPC"), "Channel"
        ].values[0]
        for channel_id in channel_options:
            if channel_options[channel_id] == spc_channel_color:
                spc_channel = channel_id
        """
        Return Data associated with Runset, URL for RunsetReview Page, Runset Review Id, Severity Options.
        """

        """
        Create RunSetSubject / Subject Dictionary
        """
        runset_subject_ids = {}
        runset_subject_descriptions = {}
        runset_sample_subject_ids_dict = {}
        runset_sample_subject_ids_descriptions = {}
        for idx in dataframe.drop_duplicates(
            subset=["RunSetSampleId", "SampleId"]
        ).index:
            runset_sample_subject_ids_dict[
                dataframe.loc[idx, "RunSetSampleId"]
            ] = dataframe.loc[idx, "SampleId"]
            runset_sample_subject_ids_descriptions[
                dataframe.loc[idx, "RunSetSampleId"]
            ] = str(dataframe.loc[idx, "Sample ID"])

        runset_subject_ids["Sample"] = runset_sample_subject_ids_dict
        runset_subject_descriptions["Sample"] = runset_sample_subject_ids_descriptions

        runset_xpcrmodulelane_subject_ids_dict = {}
        runset_xpcrmodulelane_subject_ids_descriptions = {}

        for idx in dataframe.drop_duplicates(
            subset=["RunSetXPCRModuleLaneId", "XPCRModuleLaneId"]
        ).index:
            runset_xpcrmodulelane_subject_ids_dict[
                dataframe.loc[idx, "RunSetXPCRModuleLaneId"]
            ] = dataframe.loc[idx, "XPCRModuleLaneId"]
            runset_xpcrmodulelane_subject_ids_descriptions[
                dataframe.loc[idx, "RunSetXPCRModuleLaneId"]
            ] = (
                dataframe.loc[idx, "XPCR Module Serial"]
                + " Lane "
                + str(dataframe.loc[idx, "XPCR Module Lane"])
            )

        runset_subject_ids["XPCRModuleLane"] = runset_xpcrmodulelane_subject_ids_dict
        runset_subject_descriptions[
            "XPCR Module Lane"
        ] = runset_xpcrmodulelane_subject_ids_descriptions

        runset_cartridge_subject_ids_dict = {}
        runset_cartridge_subject_id_descriptions = {}
        for idx in dataframe.drop_duplicates(
            subset=["RunSetCartridgeId", "CartridgeId"]
        ).index:
            runset_cartridge_subject_ids_dict[
                dataframe.loc[idx, "RunSetCartridgeId"]
            ] = dataframe.loc[idx, "CartridgeId"]
            runset_cartridge_subject_id_descriptions[
                dataframe.loc[idx, "RunSetCartridgeId"]
            ] = "Run " + str(dataframe.loc[idx, "Run"])

        runset_subject_ids["Cartridge"] = runset_cartridge_subject_ids_dict
        runset_subject_descriptions["Run"] = runset_cartridge_subject_id_descriptions

        runset_xpcrmodule_subject_ids_dict = {}
        runset_xpcrmodule_descriptions = {}
        xpcrmodule_options = {}
        # xpcrmodule_options['NoFilter'] = 'All'

        for idx in dataframe.drop_duplicates(
            subset=["RunSetXPCRModuleId", "XPCRModuleId"]
        ).index:
            runset_xpcrmodule_subject_ids_dict[
                dataframe.loc[idx, "RunSetXPCRModuleId"]
            ] = dataframe.loc[idx, "XPCRModuleId"]
            xpcrmodule_options[
                dataframe.loc[idx, "RunSetXPCRModuleId"]
            ] = dataframe.loc[idx, "XPCR Module Serial"]
            runset_xpcrmodule_descriptions[
                dataframe.loc[idx, "RunSetXPCRModuleId"]
            ] = dataframe.loc[idx, "XPCR Module Serial"]

        runset_subject_ids["XPCRModule"] = runset_xpcrmodule_subject_ids_dict
        runset_subject_descriptions["XPCR Module"] = runset_xpcrmodule_descriptions

        runset_neumodx_subject_ids_dict = {}
        for idx in dataframe.drop_duplicates(
            subset=["RunSetNeuMoDxSystemId", "NeuMoDxSystemId"]
        ).index:
            runset_neumodx_subject_ids_dict[
                dataframe.loc[idx, "RunSetNeuMoDxSystemId"]
            ] = dataframe.loc[idx, "NeuMoDxSystemId"]

        runset_subject_ids["NeuMoDxSystem"] = runset_neumodx_subject_ids_dict

        dataframe.drop(
            [
                "Cartridge Id",
                "Buffer Trough Id",
                "Extraction Plate Id",
                "Test Strip Id",
                "LDT Test Strip MM Id",
                "LDT Test Strip PPM Id",
                "Release Reagent Id",
                "Wash Reagent Id",
                "NeuMoDx System Id",
                "XPCR Module Configuration Id",
                "xpcrModuleLaneId",
                "Heater Module Configuration Id",
                "Assay Id",
                "XPCR Module Id",
                "Heater Module Id",
                "Sample Definition Id",
                "LhpA Trace Id",
                "Lysis Binding Trace Id",
                "LhpB Trace Id",
                "Extraction Trace Id",
                "Pcr Trace Id",
                "Operator Id",
                "Buffer Large Tip Rack Id",
                "Sample Large Tip Rack Id",
                "Buffer Large Tip Rack Carrier Group Id",
                "Sample Large Tip Rack Carrier Group Id",
                "LhpB Large Tip Rack Carrier Group Id",
                "Small Tip Rack Carrier Group Id",
                "Test Strip id",
                "Test Strip PPM id",
                "Reading Set Id",
            ],
            axis=1,
            inplace=True,
        )
        # with open('output.json', 'w') as f:
        # json.dump(dataframe.to_dict('records'), f)
        return (
            dataframe.to_dict("records"),
            "/dashboard/run-review/view-results",
            resp,
            severity_options,
            channel_options,
            run_options,
            spc_channel,
            lane_options,
            runset_subject_ids,
            xpcrmodule_options,
            runset_subject_descriptions,
        )

    @app.callback(
        [
            Output("sample-issue-options", "options"),
            Output("lane-issue-options", "options"),
            Output("module-issue-options", "options"),
            Output("run-issue-options", "options"),
            Output("tadm-issue-options", "options"),
        ],
        Input("submit-sample-issue", "children"),
    )
    def getIssueTypes(_):
        async def getIssueTypeOptions(session, url):
            async with session.get(url) as resp:
                issueTypes = await resp.json()
                return issueTypes

        async def main():
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=False)
            ) as session:
                issueTypeEndpoints = [
                    "SampleIssueTypes",
                    "XPCRModuleLaneIssueTypes",
                    "CartridgeIssueTypes",
                    "XPCRModuleIssueTypes",
                    "XPCRModuleTADMIssueTypes",
                ]
                tasks = []
                tasksTracker = {}
                for issueType in issueTypeEndpoints:
                    url = os.environ["RUN_REVIEW_API_BASE"] + issueType
                    tasks.append(
                        asyncio.ensure_future(
                            getIssueTypeOptions(session, url))
                    )

                responses = await asyncio.gather(*tasks)

                return {
                    issueTypeEndpoints[i]: responses[i] for i in range(len(responses))
                }

        issueTypes = asyncio.run(main())

        issueTypeOptions = {}
        issueTypeEndpoints = [
            "SampleIssueTypes",
            "XPCRModuleLaneIssueTypes",
            "CartridgeIssueTypes",
            "XPCRModuleIssueTypes",
            "XPCRModuleTADMIssueTypes",
        ]
        for endpoint in issueTypeEndpoints:
            issue_type_options = []
            for issueType in issueTypes[endpoint]:
                issue_type_options.append(
                    {"label": issueType["name"], "value": issueType["id"]}
                )
            issueTypeOptions[endpoint] = issue_type_options

        return (
            issueTypeOptions["SampleIssueTypes"],
            issueTypeOptions["XPCRModuleLaneIssueTypes"],
            issueTypeOptions["XPCRModuleIssueTypes"],
            issueTypeOptions["CartridgeIssueTypes"],
            issueTypeOptions["XPCRModuleTADMIssueTypes"],
        )

    @app.callback(
        [
            Output("sample-issue-severity-options", "options"),
            Output("lane-issue-severity-options", "options"),
            Output("run-issue-severity-options", "options"),
            Output("module-issue-severity-options", "options"),
            Output("tadm-issue-severity-options", "options"),
        ],
        Input("runset-severity-options", "data"),
    )
    def update_severity_options(data):
        return data, data, data, data, data

    @app.callback(
        Output("severity-selected", "data"),
        [
            Input("sample-issue-severity-options", "value"),
            Input("lane-issue-severity-options", "value"),
            Input("run-issue-severity-options", "value"),
            Input("module-issue-severity-options", "value"),
            Input("tadm-issue-severity-options", "value"),
        ],
        prevent_initial_call=True,
    )
    def update_severity_selection(
        sample_issue_severity,
        lane_issue_severity,
        run_issue_severity,
        module_issue_severity,
        tadm_issue_severity,
    ):
        trigger = ctx.triggered_id
        print(trigger)
        if trigger == "sample-issue-severity-options":
            return sample_issue_severity
        elif trigger == "lane-issue-severity-options":
            return lane_issue_severity
        elif trigger == "run-issue-severity-options":
            return run_issue_severity
        elif trigger == "module-issue-severity-options":
            return module_issue_severity
        elif trigger == "tadm-issue-severity-options":
            return tadm_issue_severity

    @app.callback(
        [
            Output("sample-issue-severity-options", "value"),
            Output("lane-issue-severity-options", "value"),
            Output("run-issue-severity-options", "value"),
            Output("module-issue-severity-options", "value"),
        ],
        Input("severity-selected", "data"),
        prevent_initial_call=True,
    )
    def update_channel_selection_value(channel):
        return channel, channel, channel, channel

    @app.callback(
        [
            Output("run-review-curves", "figure"),
            Output("runset-sample-results", "rowData"),
            Output("runset-sample-results", "columnDefs"),
            Output("pcrcurve-sample-info", "data"),
        ],
        [
            Input("channel-selected", "data"),
            Input("run-review-process-step-selector", "value"),
            Input("run-review-color-selector", "value"),
            State("runset-sample-data", "data"),
            State("runset-selection-data", "data"),
            State("runset-channel-options", "data"),
            Input("xpcrmodulelane-selected", "data"),
            Input("run-option-selected", "data"),
            Input("issue-selected", "data"),
        ],
        prevent_intial_call=True,
    )
    def update_pcr_curves(
        channel_selected,
        process_step,
        color_option_selected,
        data,
        runset_data,
        channel_options,
        lane_selection,
        run_selection,
        issue_selected,
    ):
        try:
            if ctx.triggered_id == "issue-selected":
                channel = issue_selected["Channel"]
                dataframe = pd.DataFrame.from_dict(data)
                dataframe["Channel"] = dataframe["Channel"].replace(
                    "Far_Red", "Far Red"
                )
                fig = go.Figure()
                df = dataframe.reset_index().set_index(
                    ["Channel", "Processing Step", "XPCR Module Serial"]
                )
                df_Channel = df.loc[channel]
                if issue_selected["RunSetId"] == runset_data["id"]:
                    if issue_selected["Level"] == "Sample":
                        df_Channel = df_Channel[
                            df_Channel["RunSetSampleId"]
                            == issue_selected["RunSetSubjectReferrerId"]
                        ]
                    elif issue_selected["Level"] == "XPCR Module Lane":
                        df_Channel = df_Channel[
                            df_Channel["XPCRModuleLaneId"]
                            == issue_selected["SubjectId"]
                        ]
                    elif issue_selected["Level"] == "Run":
                        df_Channel = df_Channel[
                            df_Channel["CartridgeId"] == issue_selected["SubjectId"]
                        ]
                    elif issue_selected["Level"] == "XPCR Module":
                        df_Channel = df_Channel[
                            df_Channel["XPCRModuleId"] == issue_selected["SubjectId"]
                        ]
                else:
                    if issue_selected["Level"] == "Sample":
                        df_Channel = df_Channel[
                            df_Channel["XPCRModuleLaneId"]
                            == issue_selected["SubjectId"]
                        ]
                    elif issue_selected["Level"] == "XPCR Module Lane":
                        df_Channel = df_Channel[
                            df_Channel["XPCRModuleLaneId"]
                            == issue_selected["SubjectId"]
                        ]
                    elif issue_selected["Level"] == "Run":
                        df_Channel = df_Channel[
                            df_Channel["XPCRModuleId"] == issue_selected["SubjectId"]
                        ]
                        print(df_Channel)
                    elif issue_selected["Level"] == "XPCR Module":
                        df_Channel = df_Channel[
                            df_Channel["XPCRModuleId"] == issue_selected["SubjectId"]
                        ]

            else:
                if channel_selected == None:
                    channel = "Yellow"
                else:
                    channel = channel_options[channel_selected]

                dataframe = pd.DataFrame.from_dict(data)
                dataframe["Channel"] = dataframe["Channel"].replace(
                    "Far_Red", "Far Red"
                )
                # Start making graph...
                fig = go.Figure()
                df = dataframe.reset_index().set_index(
                    ["Channel", "Processing Step", "XPCR Module Serial"]
                )
                df_Channel = df.loc[channel]

                """Filter Dataframe with current Run & Module Lane Selections"""

                if lane_selection != "NoFilter" and lane_selection != None:
                    df_Channel = df_Channel[
                        df_Channel["RunSetXPCRModuleLaneId"] == lane_selection
                    ]

                if run_selection != "NoFilter" and run_selection != None:
                    df_Channel = df_Channel[
                        df_Channel["RunSetCartridgeId"] == run_selection
                    ]

            df_Channel_Step = df_Channel.loc[process_step].reset_index()
            df_Channel_Step.sort_values(color_option_selected, inplace=True)

            """
            Make the Readings Array
            """

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

            samples_selected = []
            for idx in df_Channel_Step.index:
                X = np.array(
                    [read for read in df_Channel_Step.loc[idx, "Readings Array"]][0]
                )
                Y = np.array(
                    [read for read in df_Channel_Step.loc[idx, "Readings Array"]][1]
                )
                _name = str(df_Channel_Step.loc[idx, color_option_selected])
                fig.add_trace(
                    go.Scatter(
                        x=X,
                        y=Y,
                        mode="lines",
                        name=_name,
                        line=dict(
                            color=colorDict[
                                df_Channel_Step.loc[idx, color_option_selected]
                            ]
                        ),
                    )
                )
                sample_info = {}
                sample_info["RunSetSampleId"] = df_Channel_Step.loc[
                    idx, "RunSetSampleId"
                ]
                sample_info["SampleId"] = df_Channel_Step.loc[idx, "SampleId"]
                samples_selected.append(sample_info)

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
                x for x in df_Channel_Step.columns if "Baseline" in x or "Reading" in x
            ]
            groupables = ["XPCR Module Serial"] + [
                x
                for x in df_Channel_Step.columns
                if "Lot" in x or "Serial" in x or "Barcode" in x
            ]
            floats = ["Ct", "EPR"]
            ints = ["End Point Fluorescence", "Max Peak Height"]
            for column in df_Channel_Step.columns:
                column_definition = {
                    "headerName": column,
                    "field": column,
                    "filter": True,
                    "sortable": True,
                }
                if column not in inital_selection:
                    column_definition["hide"] = True
                if column in aggregates:
                    column_definition["enableValue"] = True
                if column in groupables:
                    column_definition["enableRowGroup"] = True
                column_definitions.append(column_definition)
            return (
                fig,
                df_Channel_Step.to_dict("records"),
                column_definitions,
                samples_selected,
            )
        except:
            return no_update

    @app.callback(
        Output("run-summary-table", "rowData"),
        Output("run-summary-table", "columnDefs"),
        Input("review-tabs", "active_tab"),
        Input("run-summary-channel-selector", "value"),
        State("runset-sample-data", "data"),
        State("spc-channel", "data"),
        State("runset-channel-options", "data"),
    )
    def get_run_summary(active_tab, channel, data, spc2_channel, channel_dict):
        """
        Define internal Function to calculate %CV Agg Type.
        """

        def cv(series):
            return series.std() / series.mean()

        if (
            ctx.triggered_id == "review-tabs"
            or ctx.triggered_id == "run-summary-channel-selector"
        ) and active_tab == "run-summary-data":
            """
            Initialize / Filter Dataset to Only Raw of Channel of Interest Data, Add Target Detected Column.
            """

            raw_data = pd.DataFrame.from_dict(data)
            raw_data = raw_data[raw_data["Channel"] == channel_dict[channel]]
            raw_data = raw_data[raw_data["Processing Step"] == "Raw"]

            raw_data["Target Detected"] = np.where(
                raw_data["Localized Result"] == "TargetAmplified", 1, 0
            )

            run_summary_df = raw_data.copy()

            if channel != spc2_channel:
                """
                Calculate Baseline Stats for Channel of Interest.
                """

                run_summary_df["Baseline Mean"] = run_summary_df[
                    [x for x in run_summary_df.columns if "Reading " in x]
                ].mean(axis=1)
                run_summary_df["Baseline Std"] = run_summary_df[
                    [x for x in run_summary_df.columns if "Reading " in x]
                ].std(axis=1)
                run_summary_df["Max Step"] = (
                    run_summary_df[
                        [x for x in run_summary_df.columns if "Reading " in x]
                    ]
                    .diff(axis=1)
                    .max(axis=1)
                )
                run_summary_df["Baseline %CV"] = (
                    run_summary_df["Baseline Std"] /
                    run_summary_df["Baseline Mean"]
                )

                initial_selection = [
                    "XPCR Module Serial",
                    "XPCR Module Lane",
                    "Run",
                    "Baseline %CV",
                    "Baseline Std",
                    "Max Step",
                ]

                run_summary_df = run_summary_df[
                    [
                        "N500 Serial Number",
                        "XPCR Module Serial",
                        "XPCR Module Lane",
                        "Run",
                        "Baseline Mean",
                        "Baseline Std",
                        "Baseline %CV",
                        "Max Step",
                    ]
                ]

                run_summary_df.sort_values(
                    ["XPCR Module Serial", "XPCR Module Lane", "Run"], inplace=True
                )
            elif channel == spc2_channel:
                """
                Define / Apply Aggregations to Dataset.
                """
                agg_types = {
                    "Ct": ["mean", "std", cv, "min", "max"],
                    "End Point Fluorescence": ["mean", "std", cv, "min", "max"],
                    "EPR": ["mean", "std", cv, "min", "max"],
                    "Max Peak Height": ["mean", "std", cv, "min", "max"],
                    "Target Detected": ["mean"],
                }
                run_summary_df_overall = run_summary_df.groupby(
                    ["N500 Serial Number", "XPCR Module Serial"]
                ).agg(agg_types)
                run_summary_df_overall["Run"] = "Overall"
                run_summary_df_overall.set_index(
                    "Run", append=True, inplace=True)
                run_summary_df = run_summary_df.groupby(
                    ["N500 Serial Number", "XPCR Module Serial", "Run"]
                ).agg(agg_types)
                run_summary_df = pd.concat(
                    [run_summary_df, run_summary_df_overall], axis=0
                )
                run_summary_df.columns = [
                    "Ct mean",
                    "Ct std",
                    "Ct %CV",
                    "Ct min",
                    "Ct max",
                    "EP mean",
                    "EP std",
                    "EP %CV",
                    "EP min",
                    "EP max",
                    "MPH mean",
                    "MPH std",
                    "MPH %CV",
                    "MPH min",
                    "MPH max",
                    "EPR mean",
                    "EPR std",
                    "EPR %CV",
                    "EPR min",
                    "EPR max",
                    "Detection %",
                ]

                """
                Calculate Left vs Right EP Split
                """

                for idx in run_summary_df.index.unique():
                    run_number = idx[2]
                    if run_number != "Overall":
                        run_summary_df.loc[idx, "Left vs Right EP Split"] = abs(
                            raw_data.loc[
                                (
                                    (raw_data["Run"] == run_number)
                                    & (raw_data["XPCR Module Side"] == "Left")
                                ),
                                "End Point Fluorescence",
                            ].mean()
                            - raw_data.loc[
                                (
                                    (raw_data["Run"] == run_number)
                                    & (raw_data["XPCR Module Side"] == "Right")
                                ),
                                "End Point Fluorescence",
                            ].mean()
                        )
                    else:
                        run_summary_df.loc[idx, "Left vs Right EP Split"] = abs(
                            raw_data.loc[
                                ((raw_data["XPCR Module Side"] == "Left")),
                                "End Point Fluorescence",
                            ].mean()
                            - raw_data.loc[
                                ((raw_data["XPCR Module Side"] == "Right")),
                                "End Point Fluorescence",
                            ].mean()
                        )

                """
                Format Data For Rendering
                """

                run_summary_df.reset_index(inplace=True)
                initial_selection = [
                    "XPCR Module Serial",
                    "Run",
                    "Ct %CV",
                    "EP %CV",
                    "Detection %",
                    "Left vs Right EP Split",
                ]

            column_definitions = []
            for column in run_summary_df.columns:
                if "%" in column:
                    run_summary_df[column] = run_summary_df[column] * 100
                    run_summary_df[column] = run_summary_df[column].round(2)
                elif (
                    "Run" not in column
                    and "N500" not in column
                    and "XPCR Module Serial" not in column
                    and "Lane" not in column
                ):
                    run_summary_df[column] = run_summary_df[column].round(2)
                column_definition = {
                    "headerName": column,
                    "field": column,
                    "filter": True,
                    "sortable": True,
                }
                if column not in initial_selection:
                    column_definition["hide"] = True
                column_definitions.append(column_definition)
            return run_summary_df.to_dict(orient="records"), column_definitions

        return no_update

    @app.callback(
        [
            Output("sample-issue-channel-options", "options"),
            Output("lane-issue-channel-options", "options"),
            Output("run-issue-channel-options", "options"),
            Output("module-issue-channel-options", "options"),
            Output("run-review-channel-selector", "options"),
            Output("run-summary-channel-selector", "options"),
        ],
        Input("runset-channel-options", "data"),
    )
    def update_channel_options(data):
        return data, data, data, data, data, data

    @app.callback(
        Output("channel-selected", "data"),
        [
            Input("sample-issue-channel-options", "value"),
            Input("lane-issue-channel-options", "value"),
            Input("run-issue-channel-options", "value"),
            Input("module-issue-channel-options", "value"),
            Input("run-review-channel-selector", "value"),
            Input("run-summary-channel-selector", "value"),
            State("spc-channel", "data"),
        ],
        prevent_initial_call=True,
    )
    def update_channel_selection(
        sample_issue_channel,
        lane_issue_channel,
        run_issue_channel,
        module_issue_channel,
        run_review_channel,
        run_summary_channel,
        spc_channel,
    ):
        channel_adjusted = ctx.triggered_id

        if channel_adjusted == "sample-issue-channel-options":
            if sample_issue_channel == None:
                return spc_channel
            return sample_issue_channel
        elif channel_adjusted == "lane-issue-channel-options":
            if lane_issue_channel == None:
                return spc_channel
            return lane_issue_channel
        elif channel_adjusted == "run-issue-channel-options":
            if run_issue_channel == None:
                return spc_channel
            return run_issue_channel
        elif channel_adjusted == "module-issue-channel-options":
            if module_issue_channel == None:
                return spc_channel
            return module_issue_channel
        elif channel_adjusted == "run-review-channel-selector":
            if run_review_channel == None:
                return spc_channel
            return run_review_channel
        elif channel_adjusted == "run-summary-channel-selector":
            if run_summary_channel == None:
                return spc_channel
            return run_summary_channel

    @app.callback(
        [
            Output("sample-issue-channel-options", "value"),
            Output("lane-issue-channel-options", "value"),
            Output("run-issue-channel-options", "value"),
            Output("module-issue-channel-options", "value"),
            Output("run-review-channel-selector", "value"),
            Output("run-summary-channel-selector", "value"),
        ],
        Input("channel-selected", "data"),
        prevent_initial_call=True,
    )
    def update_channel_selection_value(channel):
        return channel, channel, channel, channel, channel, channel

    @app.callback(
        [
            Output("run-issue-run-options", "options"),
            Output("sample-issue-run-options", "options"),
            Output("run-review-run-selector", "options"),
        ],
        Input("runset-run-options", "data"),
    )
    def update_run_options(data):
        return data, data, data

    @app.callback(
        [
            Output("run-issue-run-options", "value"),
            Output("sample-issue-run-options", "value"),
            Output("run-review-run-selector", "value"),
        ],
        Input("run-option-selected", "data"),
        prevent_initial_call=True,
    )
    def update_run_option_selected(data):
        return data, data, data

    @app.callback(
        Output("run-option-selected", "data"),
        [
            Input("run-issue-run-options", "value"),
            Input("sample-issue-run-options", "value"),
            Input("run-review-run-selector", "value"),
            Input("review-tabs", "active_tab"),
            State("run-option-selected", "data"),
        ],
        prevent_initial_call=True,
    )
    def update_run_option_selections(
        run_issue_run_selection,
        sample_issue_run_selection,
        run_review_run_selection,
        tab_selected,
        current_selection,
    ):
        trigger = ctx.triggered_id

        if trigger == "review-tabs":
            if tab_selected == "run-review-module-issues":
                return "NoFilter"
            if tab_selected == "run-review-module-lane-issues":
                return "NoFilter"
            if tab_selected == "run-review-line-data":
                return "NoFilter"
            else:
                return current_selection

        if trigger == "run-issue-run-options":
            if trigger == None:
                return "NoFilter"
            return run_issue_run_selection
        elif trigger == "sample-issue-run-options":
            if sample_issue_run_selection == None:
                return "NoFilter"
            return sample_issue_run_selection
        elif trigger == "run-review-run-selector":
            if run_review_run_selection == None:
                return "NoFilter"
            return run_review_run_selection

    @app.callback(
        [
            Output("lane-issue-lane-options", "options"),
            Output("sample-issue-lane-options", "options"),
            Output("run-review-lane-selector", "options"),
        ],
        Input("runset-xpcrmodulelane-options", "data"),
    )
    def update_lane_options(data):
        return data, data, data

    @app.callback(
        [
            Output("lane-issue-lane-options", "value"),
            Output("sample-issue-lane-options", "value"),
            Output("run-review-lane-selector", "value"),
        ],
        Input("xpcrmodulelane-selected", "data"),
        prevent_initial_call=True,
    )
    def update_lane_option_selected(data):
        return data, data, data

    @app.callback(
        Output("xpcrmodulelane-selected", "data"),
        [
            Input("lane-issue-lane-options", "value"),
            Input("sample-issue-lane-options", "value"),
            Input("run-review-lane-selector", "value"),
            Input("review-tabs", "active_tab"),
            State("xpcrmodulelane-selected", "data"),
        ],
        prevent_initial_call=True,
    )
    def update_lane_option_selections(
        lane_issue_lane_selection,
        sample_issue_lane_selection,
        run_review_lane_selection,
        tab_selected,
        current_selection,
    ):
        trigger = ctx.triggered_id

        if trigger == "review-tabs":
            if tab_selected == "run-review-module-issues":
                return "NoFilter"
            if tab_selected == "run-review-run-issues":
                return "NoFilter"
            if tab_selected == "run-review-line-data":
                return "NoFilter"
            else:
                return current_selection

        if trigger == "lane-issue-lane-options":
            if lane_issue_lane_selection == None:
                return "NoFilter"
            return lane_issue_lane_selection
        elif trigger == "sample-issue-lane-options":
            if sample_issue_lane_selection == None:
                return "NoFilter"
            return sample_issue_lane_selection
        elif trigger == "run-review-lane-selector":
            if run_review_lane_selection == None:
                return "NoFilter"
            return run_review_lane_selection

    @app.callback(
        Output("run-review-run-selector", "disabled"),
        Input("review-tabs", "active_tab"),
    )
    def control_run_selector_validity(tab_selected):
        if tab_selected in [
            "run-review-module-issues",
            "run-review-module-lane-issues",
            "run-review-active-issues",
        ]:
            return True
        else:
            return False

    @app.callback(
        Output("run-review-lane-selector", "disabled"),
        Input("review-tabs", "active_tab"),
    )
    def control_lane_selector_validity(tab_selected):
        if tab_selected in [
            "run-review-module-issues",
            "run-review-run-issues",
            "run-review-active-issues",
        ]:
            return True
        else:
            return False

    @app.callback(
        Output("run-review-xpcrmodule-selector", "disabled"),
        Input("review-tabs", "active_tab"),
    )
    def control_module_selector_validity(tab_selected):
        if tab_selected in ["run-review-active-issues"]:
            return True
        else:
            return False

    @app.callback(
        Output("run-review-channel-selector", "disabled"),
        Input("review-tabs", "active_tab"),
    )
    def control_channel_selector_validity(tab_selected):
        if tab_selected in ["run-review-active-issues"]:
            return True
        else:
            return False

    @app.callback(
        [
            Output("module-issue-module-options", "options"),
            Output("run-issue-module-options", "options"),
            Output("lane-issue-module-options", "options"),
            Output("sample-issue-module-options", "options"),
            Output("tadm-issue-module-options", "options"),
            Output("run-review-xpcrmodule-selector", "options"),
        ],
        Input("xpcrmodule-options", "data"),
    )
    def update_run_options(data):
        return data, data, data, data, data, data

    @app.callback(
        Output("xpcrmodule-selected", "data"),
        [
            Input("module-issue-module-options", "value"),
            Input("run-issue-module-options", "value"),
            Input("lane-issue-module-options", "value"),
            Input("sample-issue-module-options", "value"),
            Input("run-review-xpcrmodule-selector", "value"),
            Input("run-review-xpcrmodule-selector", "options"),
            Input("tadm-issue-module-options", "value"),
        ],
        prevent_initial_call=True,
    )
    def update_module_selections(
        module_issue_mod_selection,
        run_issue_mod_selection,
        lane_issue_mod_selection,
        sample_issue_mod_selection,
        run_review_mod_selection,
        run_review_mod_options,
        tadm_issue_mod_selection,
    ):
        trigger = ctx.triggered_id
        print(run_review_mod_options)
        if trigger == "module-issue-module-options":
            if module_issue_mod_selection == None:
                return "NoFilter"
            return module_issue_mod_selection
        elif trigger == "run-issue-module-options":
            if run_issue_mod_selection == None:
                return "NoFilter"
            return run_issue_mod_selection
        elif trigger == "lane-issue-module-options":
            if lane_issue_mod_selection == None:
                return "NoFilter"
            return lane_issue_mod_selection
        elif trigger == "sample-issue-module-options":
            if sample_issue_mod_selection == None:
                return "NoFilter"
            return sample_issue_mod_selection
        elif trigger == "tadm-issue-module-options":
            if tadm_issue_mod_selection == None:
                return "NoFilter"
            return tadm_issue_mod_selection
        elif (
            trigger == "run-review-xpcrmodule-selector"
            and run_review_mod_selection != None
        ):
            return run_review_mod_selection
        elif (
            trigger == "run-review-xpcrmodule-selector"
            and run_review_mod_selection == None
        ):
            for module_id in run_review_mod_options:
                return module_id

    @app.callback(
        [
            Output("module-issue-module-options", "value"),
            Output("run-issue-module-options", "value"),
            Output("lane-issue-module-options", "value"),
            Output("sample-issue-module-options", "value"),
            Output("run-review-xpcrmodule-selector", "value"),
            Output("tadm-issue-module-options", "value"),
        ],
        Input("xpcrmodule-selected", "data"),
        prevent_initial_call=True,
    )
    def update_lane_option_selected(data):
        return data, data, data, data, data, data

    @app.callback(
        [
            Output("issue-post-response", "is_open"),
            Output("submit-module-issue", "n_clicks"),
            Output("submit-run-issue", "n_clicks"),
            Output("submit-lane-issue", "n_clicks"),
            Output("submit-sample-issue", "n_clicks"),
            Output("submit-tadm-issue", "n_clicks"),
        ],
        [
            Input("submit-module-issue", "n_clicks"),
            Input("submit-run-issue", "n_clicks"),
            Input("submit-lane-issue", "n_clicks"),
            Input("submit-sample-issue", "n_clicks"),
            Input("submit-tadm-issue", "n_clicks"),
            State("issue-post-response", "is_open"),
            State("runset-review", "data"),
            State("channel-selected", "data"),
            State("severity-selected", "data"),
            State("module-issue-options", "value"),
            State("runset-subject-ids", "data"),
            State("xpcrmodule-selected", "data"),
            State("run-issue-options", "value"),
            State("run-option-selected", "data"),
            State("lane-issue-options", "value"),
            State("xpcrmodulelane-selected", "data"),
            State("sample-issue-options", "value"),
            State("pcrcurve-sample-info", "data"),
            State("tadm-issue-options", "value"),
        ],
        prevent_intial_call=True,
    )
    def post_issue(
        mod_issue,
        run_issue,
        lane_issue,
        sample_issue,
        tadm_issue,
        is_open,
        runset_review,
        channel_id,
        severity_id,
        module_issue_id,
        runset_subject_ids,
        xpcrmodule_selected,
        run_issue_id,
        run_selected,
        lane_issue_id,
        lane_selected,
        sample_issue_id,
        samples_selected,
        tadm_issue_id,
    ):
        print("attempting post.")

        issue = {}
        issue["userId"] = session["user"].id
        issue["runSetReviewReferrerId"] = runset_review["id"]
        issue["runSetReviewResolverId"] = "00000000-0000-0000-0000-000000000000"
        issue["severityRatingId"] = severity_id
        issue["assayChannelId"] = channel_id

        if mod_issue:
            """
            Post information to XPCR Module Issue Endpoint
            """
            issue["issueTypeId"] = module_issue_id
            issue["subjectId"] = runset_subject_ids["XPCRModule"][xpcrmodule_selected]
            issue["runSetSubjectReferrerId"] = xpcrmodule_selected
            mod_issue_url = os.environ["RUN_REVIEW_API_BASE"] + \
                "XPCRModuleIssues"
            requests.post(url=mod_issue_url, json=issue, verify=False)

        if run_issue:
            """
            Post information to XPCR Module Issue Endpoint
            """
            issue["issueTypeId"] = run_issue_id
            issue["subjectId"] = runset_subject_ids["Cartridge"][run_selected]
            issue["runSetSubjectReferrerId"] = run_selected
            cartridge_issue_url = os.environ["RUN_REVIEW_API_BASE"] + \
                "CartridgeIssues"
            requests.post(url=cartridge_issue_url, json=issue, verify=False)

        if lane_issue:
            """
            Post information to XPCR Module Issue Endpoint
            """
            issue["issueTypeId"] = lane_issue_id
            issue["subjectId"] = runset_subject_ids["XPCRModuleLane"][lane_selected]
            issue["runSetSubjectReferrerId"] = lane_selected
            lane_issue_url = os.environ["RUN_REVIEW_API_BASE"] + \
                "XPCRModuleLaneIssues"
            print(issue)
            requests.post(url=lane_issue_url, json=issue, verify=False)

        if sample_issue:
            """
            Post information to XPCR Module Issue Endpoint
            """
            issue["issueTypeId"] = sample_issue_id
            issue["subjectId"] = samples_selected[0]["SampleId"]
            issue["runSetSubjectReferrerId"] = samples_selected[0]["RunSetSampleId"]
            sample_issue_url = os.environ["RUN_REVIEW_API_BASE"] + \
                "SampleIssues"
            requests.post(url=sample_issue_url, json=issue, verify=False)

        if tadm_issue:
            """
            Post information to XPCR Module TADM Issue Endpoint
            """
            issue["assayChannelId"] = "00000000-0000-0000-0000-000000000000"
            issue["issueTypeId"] = tadm_issue_id
            issue["subjectId"] = runset_subject_ids["XPCRModule"][xpcrmodule_selected]
            issue["runSetSubjectReferrerId"] = xpcrmodule_selected
            print(issue)
            mod_tadm_issue_url = (
                os.environ["RUN_REVIEW_API_BASE"] + "XPCRModuleTADMIssues"
            )
            response = requests.post(
                url=mod_tadm_issue_url, json=issue, verify=False)
            print(response.content)

        if mod_issue or run_issue or lane_issue or sample_issue or tadm_issue:
            return not is_open, None, None, None, None, None

        return is_open, None, None, None, None, None

    @app.callback(
        [Output("issues-table", "rowData"),
         Output("issues-table", "columnDefs")],
        [
            Input("review-tabs", "active_tab"),
            Input("issue-delete-response", "is_open"),
            State("runset-selection-data", "data"),
            State("runset-subject-descriptions", "data"),
            State("related-runsets", "data"),
        ],
    )
    def get_active_XPCRModule_issues(
        tab_selected,
        issue_delete_response,
        runset_selection_data,
        runset_subject_descriptions,
        related_runsets,
    ):
        trigger_id = ctx.triggered_id
        if tab_selected in ["run-review-active-issues"] or (
            trigger_id == "issue-delete-response" and issue_delete_response == False
        ):
            """
            1. Call API Endpoint to get active issue data.
            """
            issue_dataframe = pd.DataFrame(
                columns=[
                    "IssueId",
                    "UserId",
                    "Attempt",
                    "Level",
                    "Status",
                    "Severity",
                    "Channel",
                    "Reviewer Name",
                    "Type",
                    "ChannelId",
                    "IssueTypeId",
                    "RunSetSubjectReferrerId",
                    "SubjectId",
                    "RunSetId",
                ]
            )

            idx = 0
            for runset_id in related_runsets:
                runset_issues_url = os.environ[
                    "RUN_REVIEW_API_BASE"
                ] + "RunSets/{}/issues".format(runset_id)

                runset_data = requests.get(
                    url=runset_issues_url, verify=False).json()

                for runset_review in runset_data["runSetReviews"]:
                    reviewer_name = runset_review["reviewerName"]
                    reviewerEmail = runset_review["reviewerEmail"]

                    issue_levels = {
                        "Sample": "sampleIssuesReferred",
                        "XPCR Module Lane": "xpcrModuleLaneIssuesReferred",
                        "Run": "cartridgeIssuesReferred",
                        "XPCR Module": "xpcrModuleIssuesReferred",
                        "TADM": "xpcrModuleTADMIssuesReferred",
                    }

                    for issue_level in issue_levels:
                        for issue in runset_review[issue_levels[issue_level]]:
                            issue_id = issue["id"]
                            issue_user_id = issue["validFromUser"]
                            attempt = related_runsets[runset_id]
                            # description = runset_subject_descriptions[
                            #     issue_level][issue['runSetSubjectReferrerId']]
                            severity = issue["severityRating"]["name"]
                            channel = issue["assayChannel"]["channel"]
                            status = issue["issueStatus"]["name"]
                            channel_id = issue["assayChannel"]["id"]
                            issue_type = issue["issueType"]["name"]
                            issue_type_id = issue["issueType"]["id"]
                            subject_referrer_id = issue["runSetSubjectReferrerId"]

                            if runset_id == runset_selection_data["id"]:
                                """
                                If the runset is the one being displayed, we can just use the subject id.
                                """
                                subject_id = issue["subjectId"]

                            else:
                                """
                                If the runset is not the one being displayed,
                                we need to sometimes use something more generic because the
                                subject id might not be present in the dataset being displayed.
                                """
                                if issue_level == "Sample":
                                    subject_id = issue["subject"]["xpcrModuleLaneId"]

                                elif issue_level == "XPCR Module Lane":
                                    subject_id = issue["subjectId"]

                                elif issue_level == "Run":
                                    subject_id = issue["subject"]["xpcrModuleId"]

                                elif issue_level == "XPCR Module":
                                    subject_id = issue["subjectId"]

                                elif issue_level == "TADM":
                                    subject_id = issue["subjectId"]

                            issue_entry = [
                                issue_id,
                                issue_user_id,
                                attempt,
                                issue_level,
                                status,
                                severity,
                                channel,
                                reviewer_name,
                                issue_type,
                                channel_id,
                                issue_type_id,
                                subject_referrer_id,
                                subject_id,
                                runset_id,
                            ]
                            issue_dataframe.loc[idx] = issue_entry
                            idx += 1

            column_definitions = []
            for column in issue_dataframe.columns:
                if "Id" not in column:
                    column_definitions.append(
                        {
                            "headerName": column,
                            "field": column,
                            "filter": True,
                            "sortable": True,
                        }
                    )
                else:
                    column_definitions.append(
                        {
                            "headerName": column,
                            "field": column,
                            "filter": True,
                            "sortable": True,
                            "hide": True,
                        }
                    )

            return issue_dataframe.to_dict("records"), column_definitions
        else:
            return no_update

    @app.callback(
        Output("issue-selected", "data"),
        Input("issues-table", "selectionChanged"),
        prevent_initial_call=True,
    )
    def get_issue_selected(selected_row):
        if selected_row == None:
            return no_update
        return selected_row[0]

    @app.callback(
        Output("run-review-status-update-post-response", "is_open"),
        [
            Input("run-review-completed-button", "n_clicks"),
            State("run-review-status-update-post-response", "is_open"),
            State("runset-review", "data"),
            State("run-review-acceptance", "value"),
        ],
        prevent_intital_call=True,
    )
    def update_run_review_status(n, is_open, runset_review, run_review_acceptance):
        if n:
            runsetreview_update_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSetReviews/{}/status".format(runset_review["id"])
            query_params = {
                "acceptable": run_review_acceptance,
                "newStatusName": "Completed",
            }
            print(query_params)
            resp = requests.put(
                url=runsetreview_update_url, params=query_params, verify=False
            )

            runsetreview_update = resp.json()
            runset_update_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSets/{}/status".format(runsetreview_update["runSetId"])
            runset_update_response = requests.put(
                url=runset_update_url, verify=False)
            print("Runset Update Response: " +
                  str(runset_update_response.status_code))
            return not is_open

        return is_open

    @app.callback(
        [
            Output("flat-data-download", "data"),
            Output("run-review-download-data", "n_clicks"),
        ],
        [
            Input("run-review-download-data", "n_clicks"),
            State("runset-sample-data", "data"),
            State("runset-selection-data", "data"),
        ],
        prevent_initial_call=True,
    )
    def download_function(n, data, runset_selection):
        if n:
            data_output = pd.DataFrame.from_dict(data)
            data_output.set_index(
                [
                    "Sample ID",
                    "Test Guid",
                    "Replicate Number",
                    "Processing Step",
                    "Channel",
                ],
                inplace=True,
            )
            data_output.drop(
                [x for x in data_output.columns if x[-2:] == "Id" or "Array" in x],
                axis=1,
                inplace=True,
            )
            return (
                dcc.send_data_frame(
                    data_output.reset_index().to_csv,
                    runset_selection["id"] + ".csv",
                    index=False,
                ),
                None,
            )
        return no_update, None

    @app.callback(
        Output("remediation-action-options", "options"),
        Input("remediation-action-loader", "n_intervals"),
    )
    def load_remediation_action_options(intervals):
        remediation_action_types_url = (
            os.environ["RUN_REVIEW_API_BASE"] + "RemediationActionTypes"
        )
        remediation_actions = requests.get(
            url=remediation_action_types_url, verify=False
        ).json()
        remediation_action_options = {}
        for remediation_action in remediation_actions:
            remediation_action_options[remediation_action["id"]] = remediation_action[
                "name"
            ]

        return remediation_action_options

    @app.callback(
        Output("remediation-action-post-response", "is_open"),
        [
            Input("remediation-action-submit", "n_clicks"),
            State("remediation-action-post-response", "is_open"),
            State("runset-selection-data", "data"),
            State("runset-review", "data"),
            State("xpcrmodule-selected", "data"),
            State("remediation-action-options", "value"),
            State("runset-subject-ids", "data"),
        ],
        prevent_inital_call=True,
    )
    def post_remediation_action(
        n,
        is_open,
        runset_selection,
        runset_review,
        xpcr_module_runset_id,
        remediation_action_id,
        runset_subject_ids,
    ):
        if n:
            if ctx.triggered_id == "remediation-action-submit":
                remediation_action_payload = {
                    "userId": session["user"].id,
                    "neuMoDxSystemId": "00000000-0000-0000-0000-000000000000",
                    "xpcrModuleId": runset_subject_ids["XPCRModule"][
                        xpcr_module_runset_id
                    ],
                    "runSetReferrerId": runset_selection["id"],
                    "runSetResolverId": "00000000-0000-0000-0000-000000000000",
                    "runSetReviewReferrerId": runset_review["id"],
                    "runSetReviewResolverId": "00000000-0000-0000-0000-000000000000",
                    "remediationActionTypeId": remediation_action_id,
                }
                # print(remediation_action_payload)
                remediation_action_url = (
                    os.environ["RUN_REVIEW_API_BASE"] + "RemediationActions"
                )

                response = requests.post(
                    url=remediation_action_url,
                    json=remediation_action_payload,
                    verify=False,
                ).json()
                print(response)
                return not is_open

        return is_open

    @app.callback(
        [
            Output("remediation-action-table", "rowData"),
            Output("remediation-action-table", "columnDefs"),
        ],
        [
            Input("review-tabs", "active_tab"),
            Input("remediation-action-delete-response", "is_open"),
            Input("remediation-action-post-response", "is_open"),
            State("xpcrmodule-selected", "data"),
            State("runset-subject-ids", "data"),
            State("related-runsets", "data"),
        ],
    )
    def get_remediation_actions(
        tab_selected,
        delete_response,
        post_response,
        runset_xpcr_module_selection_id,
        runset_subject_ids,
        related_runsets,
    ):
        trigger_id = ctx.triggered_id
        if (
            (
                tab_selected in ["run-review-remediation-actions"]
                and runset_xpcr_module_selection_id != "NoFilter"
            )
            or (
                trigger_id == "remediation-action-delete-response"
                and delete_response == False
            )
            or (
                trigger_id == "remediation-action-post-response"
                and post_response == False
            )
        ):
            """
            1. Call API Endpoint to get active issue data.
            """

            xpcrmodule_remediation_issues_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "XPCRModules/{}/remediationactions".format(
                runset_subject_ids["XPCRModule"][runset_xpcr_module_selection_id]
            )
            xpcrmodule = requests.get(
                url=xpcrmodule_remediation_issues_url, verify=False
            ).json()

            actions_dataframe = pd.DataFrame(
                columns=[
                    "RemediationActionId",
                    "Status",
                    "Action",
                    "Assigned By",
                    "Origin Attempt",
                    "Completed Attempt",
                    "Assigned By Id",
                ]
            )

            idx = 0
            for remediation_action in xpcrmodule["remediationActions"]:
                remediation_action_id = remediation_action["id"]
                remediation_action_owner = remediation_action["validFromUser"]
                status = remediation_action["remediationActionStatus"]["name"]
                action = remediation_action["remediationActionType"]["name"]
                assignee = remediation_action["runSetReviewReferrer"]["reviewerName"]
                try:
                    origin = related_runsets[remediation_action["runSetReferrer"]["id"]]
                except:
                    origin = "N/A"
                try:
                    completed = related_runsets[remediation_action["runSetResolverId"]]
                except:
                    completed = "N/A"
                actions_dataframe.loc[idx] = [
                    remediation_action_id,
                    status,
                    action,
                    assignee,
                    origin,
                    completed,
                    remediation_action_owner,
                ]
                idx += 1
            column_definitions = []
            for column in actions_dataframe.columns:
                if "Id" not in column:
                    column_definitions.append(
                        {
                            "headerName": column,
                            "field": column,
                            "filter": True,
                            "sortable": True,
                        }
                    )
                else:
                    column_definitions.append(
                        {
                            "headerName": column,
                            "field": column,
                            "filter": True,
                            "sortable": True,
                            "hide": True,
                        }
                    )

            return actions_dataframe.to_dict("records"), column_definitions
        else:
            return no_update

    @app.callback(
        Output("cartridge-images", "items"),
        Input("cartridge-pictures-table", "selectionChanged"),
        Input("cartridge-pictures-table", "rowData"),
    )
    def get_cartridge_pictures(selection, data):
        if ctx.triggered_id == "cartridge-pictures-table" and data:
            items = []
            item = add_item_to_carousel(
                title="Some ID",
                description="Some Photo",
                container_name="neumodxsystemqc-cartridgepictures",
                blob_name=selection[0]["FileId"],
            )
            items.append(item)
            return items

        return []

    @app.callback(
        Output("upload-cartridge-message", "children"),
        Output("upload-cartridge-response", "is_open"),
        Input("upload-cartridge-pictures", "contents"),
        State("upload-cartridge-pictures", "filename"),
        State("runset-selection-data", "data"),
        State("runset-review", "data"),
        State("upload-cartridge-response", "is_open"),
    )
    def upload_cartridge_image_to_blob_storage(
        list_of_contents, list_of_filenames, runset_selection, runset_review, is_open
    ):
        if list_of_contents:
            files = {
                list_of_filenames[i]: list_of_contents[i]
                for i in range(len(list_of_filenames))
            }
            upload_status = []
            for file in files:
                """
                Upload file to blob storage
                """
                content_type, content_string = files[file].split(",")
                file_content = base64.b64decode(content_string)
                file_id = str(uuid.uuid4()) + ".jpg"
                file_url = save_uploaded_file_to_blob_storage(
                    file_content, file_id, "neumodxsystemqc-cartridgepictures"
                )
                """
                Create Database Entry
                """
                file_payload = {
                    "userId": session["user"].id,
                    "runSetId": runset_selection["id"],
                    "runSetReviewId": runset_review["id"],
                    "uri": file_url,
                    "name": file,
                    "fileid": file_id,
                }
                cartridge_picture_url = (
                    os.environ["RUN_REVIEW_API_BASE"] + "CartridgePictures"
                )
                resp = requests.post(
                    url=cartridge_picture_url, json=file_payload, verify=False
                )
                upload_status.append(html.Li(file))
            # Return a message with the URL of the uploaded file
            return upload_status, not is_open

        else:
            return no_update

    @app.callback(
        Output("cartridge-pictures-table", "rowData"),
        Output("cartridge-pictures-table", "columnDefs"),
        Input("review-tabs", "active_tab"),
        Input("upload-cartridge-message", "children"),
        Input("delete-cartridge-picture-response", "is_open"),
        State("runset-selection-data", "data"),
    )
    def get_cartridge_picture_table(active_tab, message_children, is_open, runset_data):
        if (
            (ctx.triggered_id == "upload-cartridge-message")
            or ctx.triggered_id == "review-tabs"
            or (
                ctx.triggered_id == "delete-cartridge-picture-response"
                and is_open == False
            )
        ) and active_tab == "cartidge-pictures":
            """
            Get Cartridge Picture Info from API
            """
            cartridge_pictures_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSets/{}/cartridgepictures".format(runset_data["id"])
            runset = requests.get(cartridge_pictures_url, verify=False).json()
            """
            Extract Details from each Cartridge Picture into pandas DataFrame
            """
            cartridge_picture_data = pd.DataFrame(
                columns=[
                    "Id",
                    "FileId",
                    "File Name",
                    "Uploaded By",
                    "Upload Date",
                    "UserId",
                ]
            )

            idx = 0
            for cartridge_picture in runset["cartridgePictures"]:
                entry = {}
                entry["Id"] = cartridge_picture["id"]
                entry["UserId"] = cartridge_picture["validFromUser"]
                entry["FileId"] = cartridge_picture["fileid"]
                entry["File Name"] = cartridge_picture["name"]
                entry["Uploaded By"] = cartridge_picture["runSetReview"]["reviewerName"]
                entry["Upload Date"] = cartridge_picture["validFrom"]

                cartridge_picture_data.loc[idx] = entry
                idx += 1

            """
            Create Column Definitions for Table
            """

            column_definitions = []
            initial_selection = [
                x for x in cartridge_picture_data.columns if "Id" not in x
            ]

            for column in cartridge_picture_data.columns:
                column_definition = {
                    "headerName": column,
                    "field": column,
                    "filter": True,
                    "sortable": True,
                }
                if column not in initial_selection:
                    column_definition["hide"] = True

                if "Date" in column:
                    cartridge_picture_data[column] = (
                        cartridge_picture_data[column]
                        .astype("datetime64")
                        .dt.strftime("%d %B %Y %H:%M:%S")
                    )

                column_definitions.append(column_definition)

            return cartridge_picture_data.to_dict(orient="records"), column_definitions
        return no_update

    @app.callback(
        Output("delete-cartridge-picture-button", "disabled"),
        Input("cartridge-pictures-table", "selectionChanged"),
    )
    def check_cartridge_delete_validity(selection):
        if ctx.triggered_id == "cartridge-pictures-table":
            if selection[0]["UserId"] == session["user"].id:
                return False

        return True

    @app.callback(
        Output("delete-cartridge-picture-confirmation", "is_open"),
        Input("delete-cartridge-picture-button", "n_clicks"),
        Input("delete-cartridge-picture-confirm", "n_clicks"),
        Input("delete-cartridge-picture-cancel", "n_clicks"),
        State("delete-cartridge-picture-confirmation", "is_open"),
        prevent_intitial_call=True,
    )
    def control_delete_cartridge_picture_popup(
        delete_click, confirm_click, cancel_click, is_open
    ):
        if "delete" in ctx.triggered_id:
            return not is_open
        return is_open

    @app.callback(
        Output("delete-cartridge-picture-response", "is_open"),
        Input("delete-cartridge-picture-confirm", "n_clicks"),
        State("cartridge-pictures-table", "selectionChanged"),
        State("delete-cartridge-picture-response", "is_open"),
    )
    def delete_cartridge_picture(confirm_click, selection, is_open):
        if ctx.triggered_id == "delete-cartridge-picture-confirm":
            delete_cartridge_picture_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "cartridgepictures/{}".format(selection[0]["Id"])
            print(delete_cartridge_picture_url)
            response = requests.delete(
                url=delete_cartridge_picture_url, verify=False)
            print("Cartridge Picture Delete Status Code: ", response.status_code)

            return not is_open
        else:
            return is_open

    @app.callback(
        Output("tadm-images", "items"),
        Input("tadm-pictures-table", "selectionChanged"),
        Input("tadm-pictures-table", "rowData"),
    )
    def get_tadm_pictures(selection, data):
        if ctx.triggered_id == "tadm-pictures-table" and data:
            items = []
            item = add_item_to_carousel(
                title="Some ID",
                description="Some Photo",
                container_name="neumodxsystemqc-tadmpictures",
                blob_name=selection[0]["FileId"],
            )
            items.append(item)
            return items

        return []

    @app.callback(
        Output("upload-tadm-message", "children"),
        Output("upload-tadm-response", "is_open"),
        Input("upload-tadm-pictures", "contents"),
        State("upload-tadm-pictures", "filename"),
        State("runset-selection-data", "data"),
        State("runset-review", "data"),
        State("upload-tadm-response", "is_open"),
    )
    def upload_tadm_image_to_blob_storage(
        list_of_contents, list_of_filenames, runset_selection, runset_review, is_open
    ):
        if list_of_contents:
            files = {
                list_of_filenames[i]: list_of_contents[i]
                for i in range(len(list_of_filenames))
            }
            upload_status = []
            for file in files:
                """
                Upload file to blob storage
                """
                content_type, content_string = files[file].split(",")
                file_content = base64.b64decode(content_string)
                file_id = str(uuid.uuid4()) + ".jpg"
                file_url = save_uploaded_file_to_blob_storage(
                    file_content, file_id, "neumodxsystemqc-tadmpictures"
                )
                """
                Create Database Entry
                """
                file_payload = {
                    "userId": session["user"].id,
                    "runSetId": runset_selection["id"],
                    "runSetReviewId": runset_review["id"],
                    "uri": file_url,
                    "name": file,
                    "fileid": file_id,
                }
                tadm_picture_url = os.environ["RUN_REVIEW_API_BASE"] + \
                    "TADMPictures"
                resp = requests.post(
                    url=tadm_picture_url, json=file_payload, verify=False
                )
                upload_status.append(html.Li(file))
            # Return a message with the URL of the uploaded file
            return upload_status, not is_open

        else:
            return no_update

    @app.callback(
        Output("tadm-pictures-table", "rowData"),
        Output("tadm-pictures-table", "columnDefs"),
        Input("review-tabs", "active_tab"),
        Input("upload-tadm-message", "children"),
        Input("delete-tadm-picture-response", "is_open"),
        State("runset-selection-data", "data"),
    )
    def get_tadm_picture_table(active_tab, message_children, is_open, runset_data):
        if (
            (ctx.triggered_id == "upload-tadm-message")
            or ctx.triggered_id == "review-tabs"
            or (ctx.triggered_id == "delete-tadm-picture-response" and is_open == False)
        ) and active_tab == "tadm-pictures":
            """
            Get TADM Picture Info from API
            """
            tadm_pictures_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSets/{}/tadmpictures".format(runset_data["id"])
            runset = requests.get(tadm_pictures_url, verify=False).json()
            """
            Extract Details from each TADM Picture into pandas DataFrame
            """
            tadm_picture_data = pd.DataFrame(
                columns=[
                    "Id",
                    "FileId",
                    "File Name",
                    "Uploaded By",
                    "Upload Date",
                    "UserId",
                ]
            )

            idx = 0
            for tadm_picture in runset["tadmPictures"]:
                entry = {}
                entry["Id"] = tadm_picture["id"]
                entry["UserId"] = tadm_picture["validFromUser"]
                entry["FileId"] = tadm_picture["fileid"]
                entry["File Name"] = tadm_picture["name"]
                entry["Uploaded By"] = tadm_picture["runSetReview"]["reviewerName"]
                entry["Upload Date"] = tadm_picture["validFrom"]

                tadm_picture_data.loc[idx] = entry
                idx += 1

            """
            Create Column Definitions for Table
            """

            column_definitions = []
            initial_selection = [
                x for x in tadm_picture_data.columns if "Id" not in x]

            for column in tadm_picture_data.columns:
                column_definition = {
                    "headerName": column,
                    "field": column,
                    "filter": True,
                    "sortable": True,
                }
                if column not in initial_selection:
                    column_definition["hide"] = True

                if "Date" in column:
                    tadm_picture_data[column] = (
                        tadm_picture_data[column]
                        .astype("datetime64")
                        .dt.strftime("%d %B %Y %H:%M:%S")
                    )

                column_definitions.append(column_definition)

            return tadm_picture_data.to_dict(orient="records"), column_definitions
        return no_update

    @app.callback(
        Output("delete-tadm-picture-button", "disabled"),
        Input("tadm-pictures-table", "selectionChanged"),
    )
    def check_tadm_delete_validity(selection):
        if ctx.triggered_id == "tadm-pictures-table":
            if selection[0]["UserId"] == session["user"].id:
                return False

        return True

    @app.callback(
        Output("delete-tadm-picture-confirmation", "is_open"),
        Input("delete-tadm-picture-button", "n_clicks"),
        Input("delete-tadm-picture-confirm", "n_clicks"),
        Input("delete-tadm-picture-cancel", "n_clicks"),
        State("delete-tadm-picture-confirmation", "is_open"),
        prevent_intitial_call=True,
    )
    def control_delete_tadm_picture_popup(
        delete_click, confirm_click, cancel_click, is_open
    ):
        if "delete" in ctx.triggered_id:
            return not is_open
        return is_open

    @app.callback(
        Output("delete-tadm-picture-response", "is_open"),
        Input("delete-tadm-picture-confirm", "n_clicks"),
        State("tadm-pictures-table", "selectionChanged"),
        State("delete-tadm-picture-response", "is_open"),
    )
    def delete_tadm_picture(confirm_click, selection, is_open):
        if ctx.triggered_id == "delete-tadm-picture-confirm":
            delete_tadm_picture_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "tadmpictures/{}".format(selection[0]["Id"])
            print(delete_tadm_picture_url)
            response = requests.delete(
                url=delete_tadm_picture_url, verify=False)
            print("TADM Picture Delete Status Code: ", response.status_code)

            return not is_open
        else:
            return is_open

    @app.callback(
        [Output("runset-description", "children"),
         Output("related-runsets", "data")],
        Input("runset-selection-data", "data"),
    )
    def update_runset_description(runset_selection):
        """
        Get The RunSetXPCRModules associated with the XPCR Module of Interest.
        """
        runset_xpcrmodules_url = os.environ[
            "RUN_REVIEW_API_BASE"
        ] + "RunSets/{}/runsetxpcrmodules".format(runset_selection["id"])
        runset_xpcrmodules = requests.get(
            url=runset_xpcrmodules_url, verify=False
        ).json()["runSetXPCRModules"]

        if len(runset_xpcrmodules) == 1:
            """
            Get Runsets associated with XPCR Module
            """

            xpcrmodule_runsets_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "XPCRModules/{}/runsets".format(
                runset_xpcrmodules[0]["xpcrModule"]["id"]
            )
            xpcrmodule = requests.get(
                url=xpcrmodule_runsets_url, verify=False).json()

            """
            Get Related runset basic info (by xpcr module & runset type match)
            """
            xpcrmodule_runsets_df = pd.DataFrame(
                columns=[x for x in xpcrmodule["runSetXPCRModules"][0]["runSet"]]
            )

            idx = 0
            for xpcrmodule_runset in xpcrmodule["runSetXPCRModules"]:
                if (
                    xpcrmodule_runset["runSet"]["runSetTypeId"]
                    == runset_selection["runSetTypeId"]
                ):
                    xpcrmodule_runsets_df.loc[idx] = xpcrmodule_runset["runSet"]
                    idx += 1

            """
            Determine the attempt for this runset type for this particular module.
            """

            xpcrmodule_runsets_df = xpcrmodule_runsets_df.sort_values(
                "runSetStartDate"
            ).reset_index(drop=True)

            xpcrmodule_runset_number = (
                xpcrmodule_runsets_df[
                    xpcrmodule_runsets_df["id"] == runset_selection["id"]
                ].index.values[0]
                + 1
            )

            """
            Save Related RunSetIds in a dictionary for later reference
            """

            related_xpcrmodule_runsets = {}

            i = 1
            for idx in xpcrmodule_runsets_df.index:
                related_xpcrmodule_runsets[xpcrmodule_runsets_df.loc[idx, "id"]] = i
                i += 1

            return (
                runset_selection["name"]
                + " Attempt # "
                + str(xpcrmodule_runset_number),
                related_xpcrmodule_runsets,
            )

        else:
            return no_update

    @app.callback(
        [
            Output("issue-remediation-grade-button", "disabled"),
            Output("issue-remediation-url", "data"),
            Output("issue-resolution-remediation-action-options", "options"),
            Output("issue-remediation-type", "data"),
        ],
        [
            Input("issue-selected", "data"),
            State("related-runsets", "data"),
            State("runset-selection-data", "data"),
            State("xpcrmodule-selected", "data"),
            State("runset-subject-ids", "data"),
        ],
        prevent_intial_call=True,
    )
    def activate_remediation_grading(
        issue_selected,
        related_runsets,
        runset_selection_data,
        runset_xpcr_module_selection_id,
        runset_subject_ids,
    ):
        issue_urls = {
            "Sample": "SampleIssues",
            "XPCR Module Lane": "XPCRModuleLaneIssues",
            "Run": "CartridgeIssues",
            "XPCR Module": "XPCRModuleIssues",
            "TADM": "XPCRModuleTADMIssues",
        }

        issue_remediation_url = (
            os.environ["RUN_REVIEW_API_BASE"]
            + issue_urls[issue_selected["Level"]]
            + "/{}/status".format(issue_selected["IssueId"])
        )

        remediation_action_options = {}
        if (
            session["user"].id == issue_selected["UserId"]
            and related_runsets[runset_selection_data["id"]] > issue_selected["Attempt"]
        ):
            xpcrmodule_remediation_issues_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "XPCRModules/{}/remediationactions".format(
                runset_subject_ids["XPCRModule"][runset_xpcr_module_selection_id]
            )
            xpcrmodule = requests.get(
                url=xpcrmodule_remediation_issues_url, verify=False
            ).json()

            for remediation_action in xpcrmodule["remediationActions"]:
                if (
                    remediation_action["runSetResolverId"]
                    == runset_selection_data["id"]
                ):
                    remediation_action_id = remediation_action["id"]
                    action = remediation_action["remediationActionType"]["name"]
                    remediation_action_options[remediation_action_id] = action

            return (
                False,
                issue_remediation_url,
                remediation_action_options,
                issue_selected["Level"],
            )
        else:
            return (
                True,
                issue_remediation_url,
                remediation_action_options,
                issue_selected["Level"],
            )

    @app.callback(
        Output("remediation-action-update-response", "is_open"),
        [
            Input("remediation-action-resolution", "n_clicks"),
            State("remediation-action-update-response", "is_open"),
            State("runset-review", "data"),
            State("runset-selection-data", "data"),
            State("remediation-action-table", "selectionChanged"),
        ],
        prevent_intial_call=True,
    )
    def update_remediation_action(
        resolution_submit, is_open, runset_review, runset_selection_data, selected_row
    ):
        if resolution_submit:
            remediation_action_update_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RemediationActions/{}/status".format(
                selected_row[0]["RemediationActionId"]
            )

            query_params = {
                "runSetReviewId": runset_review["id"],
                "runSetId": runset_selection_data["id"],
                "newStatusName": "Completed",
            }

            print(query_params)
            resp = requests.put(
                url=remediation_action_update_url, params=query_params, verify=False
            )

            print(resp.status_code)

            return not is_open

        return is_open

    @app.callback(
        [
            Output("issue-delete-button", "disabled"),
            Output("issue-delete-url", "data"),
        ],
        [
            Input("issue-selected", "data"),
            State("related-runsets", "data"),
            State("runset-selection-data", "data"),
        ],
        prevent_intial_call=True,
    )
    def activate_issue_delete_button(
        issue_selected, related_runsets, runset_selection_data
    ):
        issue_urls = {
            "Sample": "SampleIssues",
            "XPCR Module Lane": "XPCRModuleLaneIssues",
            "Run": "CartridgeIssues",
            "XPCR Module": "XPCRModuleIssues",
            "TADM": "XPCRModuleTADMIssues",
        }

        issue_remediation_url = (
            os.environ["RUN_REVIEW_API_BASE"]
            + issue_urls[issue_selected["Level"]]
            + "/{}".format(issue_selected["IssueId"])
        )

        if (
            session["user"].id == issue_selected["UserId"]
            and related_runsets[runset_selection_data["id"]]
            == issue_selected["Attempt"]
        ):
            return False, issue_remediation_url
        else:
            return True, issue_remediation_url

    @app.callback(
        Output("issue-delete-confirmation", "is_open"),
        State("issue-delete-confirmation", "is_open"),
        Input("issue-delete-button", "n_clicks"),
        Input("issue-delete-confirmed-button", "n_clicks"),
        Input("issue-delete-canceled-button", "n_clicks"),
    )
    def confirm_delete_issue(
        is_open,
        remediation_action_button,
        remediation_action_delete_confirmed_button,
        remediation_action_delete_canceled_button,
    ):
        trigger = ctx.triggered_id
        if (
            trigger == "issue-delete-button"
            or trigger == "issue-delete-confirmed-button"
            or trigger == "issue-delete-canceled-button"
        ):
            return not is_open
        return is_open

    @app.callback(
        Output("issue-delete-response", "is_open"),
        State("issue-delete-response", "is_open"),
        State("issue-delete-url", "data"),
        Input("issue-delete-confirmed-button", "n_clicks"),
    )
    def delete_issue(is_open, delete_url, remediation_action_delete_confirmed_button):
        trigger = ctx.triggered_id
        if trigger == "issue-delete-confirmed-button":
            requests.delete(delete_url, verify=False)

            return not is_open
        return is_open

    @app.callback(
        Output("issue-resolution-remediation-action-selection-prompt", "is_open"),
        [
            Input("issue-remediation-grade-button", "n_clicks"),
            Input("issue-resolution-submit", "n_clicks"),
            State("issue-remediation-url", "data"),
            State("issue-resolution-remediation-action-selection-prompt", "is_open"),
            State("issue-remediation-type", "data"),
            State("issue-resolution-remediation-action-options", "value"),
            State("issue-selected", "data"),
            State("issue-resolution-remediation-success", "value"),
            State("runset-review", "data"),
        ],
    )
    def select_remediation_action(
        grade_button,
        submit_button,
        issue_remediation_url,
        is_open,
        issue_remediation_type,
        remediation_action_selected,
        issue_selected,
        success_selected,
        runset_review,
    ):
        trigger = ctx.triggered_id
        print(trigger)
        if trigger == "issue-remediation-grade-button":
            return not is_open
        if trigger == "issue-resolution-submit":
            """
            Submit Issue Remediation Attempt
            """

            remediation_attempt_urls = {
                "Sample": "SampleIssueRemediationAttempts",
                "XPCR Module Lane": "XPCRModuleLaneIssueRemediationAttempts",
                "Run": "CartridgeIssueRemediationAttempts",
                "XPCR Module": "XPCRModuleIssueRemediationAttempts",
                "TADM": "XPCRModuleTADMIssueRemediationAttempts",
            }

            issue_remediation_attempt_url = (
                os.environ["RUN_REVIEW_API_BASE"]
                + remediation_attempt_urls[issue_remediation_type]
            )

            issue_remediation_attempt = {
                "userId": session["user"].id,
                "issueId": issue_selected["IssueId"],
                "remediationActionId": remediation_action_selected,
                "success": bool(success_selected),
            }

            resp = requests.post(
                url=issue_remediation_attempt_url,
                json=issue_remediation_attempt,
                verify=False,
            )

            """
            Update Issue Status if the issue is resolved.
            """
            if issue_remediation_attempt["success"] == True:
                issue_update_url = issue_remediation_url
                print(issue_update_url)

                query_params = {
                    "runSetReviewId": runset_review["id"],
                    "newStatusName": "Closed",
                }
                resp = requests.put(
                    url=issue_update_url, params=query_params, verify=False
                )

                print(resp.status_code)

            return not is_open

        return is_open

    @app.callback(
        Output("remediation-action-delete-confirmation", "is_open"),
        State("remediation-action-delete-confirmation", "is_open"),
        Input("remediation-action-delete-button", "n_clicks"),
        Input("remediation-action-delete-confirmed-button", "n_clicks"),
        Input("remediation-action-delete-canceled-button", "n_clicks"),
    )
    def confirm_delete_remediation_action(
        is_open,
        remediation_action_button,
        remediation_action_delete_confirmed_button,
        remediation_action_delete_canceled_button,
    ):
        trigger = ctx.triggered_id
        if (
            trigger == "remediation-action-delete-button"
            or trigger == "remediation-action-delete-confirmed-button"
            or trigger == "remediation-action-delete-canceled-button"
        ):
            return not is_open
        return is_open

    @app.callback(
        Output("remediation-action-delete-response", "is_open"),
        State("remediation-action-table", "selectionChanged"),
        State("remediation-action-delete-response", "is_open"),
        Input("remediation-action-delete-confirmed-button", "n_clicks"),
    )
    def delete_remediation_action(
        selected_row, is_open, remediation_action_delete_confirmed_button
    ):
        trigger = ctx.triggered_id
        if trigger == "remediation-action-delete-confirmed-button":
            print(selected_row[0]["RemediationActionId"])
            delete_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RemediationActions/{}".format(selected_row[0]["RemediationActionId"])
            print(delete_url)
            requests.delete(delete_url, verify=False)

            return not is_open
        return is_open

    @app.callback(
        Output("remediation-action-delete-button", "disabled"),
        Input("remediation-action-table", "selectionChanged"),
    )
    def check_delete_action_validity(selected_row):
        trigger_id = ctx.triggered_id
        if trigger_id == "remediation-action-table":
            if selected_row[0]["Assigned By Id"] == session["user"].id:
                return False
            else:
                return True

    @app.callback(
        Output("runset-reviews-table", "rowData"),
        Output("runset-reviews-table", "columnDefs"),
        Input("review-tabs", "active_tab"),
        State("runset-selection-data", "data"),
    )
    def get_runset_reviews(active_tab, runset_data):
        if ctx.triggered_id == "review-tabs" and active_tab == "runset-reviews":
            runset_reviews_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSets/{}/runsetreviews".format(runset_data["id"])

            runset_reviews_response = requests.get(
                url=runset_reviews_url, verify=False
            ).json()

            runset_reviews_dataframe = pd.DataFrame(
                columns=[
                    "RunSetReviewId",
                    "Status",
                    "Reviewer Name",
                    "Reviewer Group",
                    "Accepted?",
                ]
            )

            print(runset_reviews_response)
            idx = 0
            for runset_review in runset_reviews_response["runSetReviews"]:
                runset_review_dict = {}
                runset_review_dict["RunSetReviewId"] = runset_review["id"]
                runset_review_dict["Status"] = runset_review["runSetReviewStatus"][
                    "name"
                ]
                runset_review_dict["Reviewer Name"] = runset_review["reviewerName"]
                runset_review_dict["Reviewer Group"] = runset_review["reviewGroup"][
                    "description"
                ]

                if runset_review["acceptable"] == False:
                    runset_review_dict["Accepted?"] = "No"
                elif runset_review["acceptable"] == True:
                    runset_review_dict["Accepted?"] = "Yes"
                else:
                    runset_review_dict["Accepted?"] = "N/A"
                runset_reviews_dataframe.loc[idx] = runset_review_dict
                idx += 1

            column_definitions = []
            initial_selection = [
                x for x in runset_reviews_dataframe.columns if "Id" not in x
            ]

            for column in runset_reviews_dataframe.columns:
                column_definition = {
                    "headerName": column,
                    "field": column,
                    "filter": True,
                    "sortable": True,
                }
                if column not in initial_selection:
                    column_definition["hide"] = True
                column_definitions.append(column_definition)

            return (
                runset_reviews_dataframe.to_dict(orient="records"),
                column_definitions,
            )

        return no_update

    @app.callback(
        Output("reviewgroup-selector-modal", "is_open"),
        Output("review-group-options", "options"),
        [
            Input("add-review-group-button", "n_clicks"),
            Input("submit-reviewgroup-selection-button", "n_clicks"),
        ],
        [State("reviewgroup-selector-modal", "is_open")],
        prevent_initial_call=True,
    )
    def open_reviewgroup_addition_modal(create_clicks, submit_clicks, is_open):
        if create_clicks or submit_clicks:
            """
            Get Review Groups
            """
            reviewgroup_options = {}
            reviewgroups_url = os.environ["RUN_REVIEW_API_BASE"] + \
                "ReviewGroups"

            reviewgroups_response = requests.get(
                reviewgroups_url, verify=False).json()

            for reviewgroup in reviewgroups_response:
                if reviewgroup["description"] != "System QC Tech I":
                    reviewgroup_options[reviewgroup["id"]
                                        ] = reviewgroup["description"]
            return not is_open, reviewgroup_options

        return is_open, {}

    @app.callback(
        Output("add-review-assignment-response", "is_open"),
        Input("submit-reviewgroup-selection-button", "n_clicks"),
        State("review-group-options", "value"),
        State("review-group-options", "options"),
        State("runset-selection-data", "data"),
        State("add-review-assignment-response", "is_open"),
        prevent_initial_call=True,
    )
    def add_runsetreviewassignments(
        submit_button,
        review_groups_selected,
        review_groups_dictionary,
        runset_data,
        post_response_is_open,
    ):
        if ctx.triggered_id == "submit-reviewgroup-selection-button":
            review_groups = []
            review_group_subscribers = {}
            for review_group_id in review_groups_selected:
                runsetreviewassignmenturl = (
                    os.environ["RUN_REVIEW_API_BASE"] +
                    "RunSetReviewAssignments"
                )
                queryParams = {}
                queryParams["runsetid"] = runset_data["id"]
                queryParams["reviewgroupid"] = review_group_id
                queryParams["userid"] = session["user"].id
                response = requests.post(
                    runsetreviewassignmenturl, params=queryParams, verify=False
                )
                print(response.status_code)
                review_groups.append(review_groups_dictionary[review_group_id])

            print("Review Groups Assigned: ", review_groups)

            if "System QC Reviewer" in review_groups:
                for user in system_qc_reviewers:
                    review_group_subscribers[user] = system_qc_reviewers[user]

            if "System Integration Lead" in review_groups:
                for user in system_integration_reviewers:
                    review_group_subscribers[user] = system_integration_reviewers[user]

            if "Engineering" in review_groups:
                for user in engineering_reviewers:
                    review_group_subscribers[user] = engineering_reviewers[user]

            if "Admin" in review_groups:
                for user in admin_reviewers:
                    review_group_subscribers[user] = admin_reviewers[user]
            if "System QC Tech" in review_groups:
                for user in system_qc_tech_IIs:
                    review_group_subscribers[user] = system_qc_tech_IIs[user]

            print("Subscribers: ", review_group_subscribers)

            runset_update_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSets/{}/status".format(runset_data["id"])
            runset_update_response = requests.put(
                url=runset_update_url, verify=False)
            print("Runset Update Response: " +
                  str(runset_update_response.status_code))

            if os.environ["SEND_EMAILS"] == "Yes":
                """
                Get reviewers to send email too
                """
                runset_url = os.environ["RUN_REVIEW_API_BASE"] + "RunSets/{}".format(
                    runset_data["id"]
                )
                runset = requests.get(url=runset_url, verify=False).json()
                # if 'XPCR Module Qualification' in runset_type_selection_options[runset_type_selection_id]:
                msg = Message(
                    runset["name"] + " Ready for review",
                    sender="neumodxsystemqcdatasync@gmail.com",
                    recipients=["aripley2008@gmail.com"],
                )

                with mail.connect() as conn:
                    for user in review_group_subscribers:
                        message = (
                            "Hello "
                            + user
                            + ", this message is sent to inform you that "
                            + runset["name"]
                            + " is now ready for your review."
                        )
                        subject = runset["name"] + " Ready for review"
                        msg = Message(
                            recipients=[review_group_subscribers[user]],
                            body=message,
                            subject=subject,
                            sender="neumodxsystemqcdatasync@gmail.com",
                        )

                        conn.send(msg)
            return not post_response_is_open
        return post_response_is_open

    @app.callback(
        Output("file-upload-response", "is_open"),
        Input("misc-file-upload-button", "contents"),
        Input("file-upload-response-close-button", "n_clicks"),
        State("misc-file-upload-button", "filename"),
        State("runset-selection-data", "data"),
        State("runset-review", "data"),
        State("file-upload-response", "is_open"),
    )
    def upload_misc_file_to_blob_storage(
        list_of_contents,
        n_clicks,
        list_of_filenames,
        runset_selection,
        runset_review,
        is_open,
    ):
        if ctx.triggered_id == "misc-file-upload-button" and list_of_contents:
            files = {
                list_of_filenames[i]: list_of_contents[i]
                for i in range(len(list_of_filenames))
            }
            upload_status = []

            for file in files:
                """
                Upload file to blob storage
                """
                content_type, content_string = files[file].split(",")
                file_content = base64.b64decode(content_string)
                file_id = str(uuid.uuid4()) + file[file.rfind("."):]
                file_url = save_uploaded_file_to_blob_storage(
                    file_content, file_id, "neumodxsystemqc-miscellaneousfiles"
                )

                """
                Create Database Entry
                """
                file_payload = {
                    "userId": session["user"].id,
                    "runSetId": runset_selection["id"],
                    "runSetReviewId": runset_review["id"],
                    "uri": file_url,
                    "name": file,
                    "fileid": file_id,
                }

                misc_file_url = os.environ["RUN_REVIEW_API_BASE"] + \
                    "MiscellaneousFiles"
                print(file_payload)
                resp = requests.post(
                    url=misc_file_url, json=file_payload, verify=False)
                print(resp.status_code)

            # Return a message with the URL of the uploaded file
            return not is_open

        elif ctx.triggered_id == "file-upload-response-close-button" and n_clicks:
            return not is_open
        else:
            return is_open

    @app.callback(
        Output("misc-files-table", "rowData"),
        Output("misc-files-table", "columnDefs"),
        Input("review-tabs", "active_tab"),
        Input("file-upload-response", "is_open"),
        Input("delete-misc-file-response", "is_open"),
        State("runset-selection-data", "data"),
    )
    def get_misc_files(
        active_tab, upload_response_is_open, delete_response_is_open, runset_data
    ):
        if (
            (
                ctx.triggered_id == "file-upload-response"
                and upload_response_is_open == False
            )
            or (
                ctx.triggered_id == "delete-misc-file-response"
                and delete_response_is_open == False
            )
            or ctx.triggered_id == "review-tabs"
        ) and active_tab == "misc-files":
            """
            Get Misc file Info from API
            """
            misc_files_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSets/{}/miscellaneousfiles".format(runset_data["id"])
            runset = requests.get(misc_files_url, verify=False).json()

            """
            Extract Details from each Misc File into pandas DataFrame
            """

            misc_file_data = pd.DataFrame(
                columns=[
                    "Id",
                    "FileId",
                    "File Name",
                    "Uploaded By",
                    "Upload Date",
                    "UserId",
                ]
            )

            idx = 0
            for misc_file in runset["miscellaneousFiles"]:
                entry = {}
                entry["Id"] = misc_file["id"]
                entry["FileId"] = misc_file["fileid"]
                entry["File Name"] = misc_file["name"]
                entry["Uploaded By"] = misc_file["runSetReview"]["reviewerName"]
                entry["Upload Date"] = misc_file["validFrom"]
                entry["UserId"] = misc_file["validFromUser"]

                misc_file_data.loc[idx] = entry
                idx += 1

            """
            Create Column Definitions for Table
            """

            column_definitions = []
            initial_selection = [
                x for x in misc_file_data.columns if "Id" not in x]

            for column in misc_file_data.columns:
                column_definition = {
                    "headerName": column,
                    "field": column,
                    "filter": True,
                    "sortable": True,
                }
                if column not in initial_selection:
                    column_definition["hide"] = True

                if "Date" in column:
                    misc_file_data[column] = (
                        misc_file_data[column]
                        .astype("datetime64")
                        .dt.strftime("%d %B %Y %H:%M:%S")
                    )

                column_definitions.append(column_definition)

            return misc_file_data.to_dict(orient="records"), column_definitions
        return no_update

    @app.callback(
        Output("misc-file-download", "data"),
        Input("misc-file-download-button", "n_clicks"),
        State("misc-files-table", "selectionChanged"),
    )
    def download_misc_file(n_clicks, misc_file_selection):
        if ctx.triggered_id == "misc-file-download-button" and n_clicks:
            print("doing this...")
            print(misc_file_selection)
            file_data = download_file(
                misc_file_selection[0]["FileId"], "neumodxsystemqc-miscellaneousfiles"
            )
            print("got file data.")
            return dict(
                content=file_data,
                filename=misc_file_selection[0]["File Name"],
                base64=True,
            )
        return no_update

    @app.callback(
        Output("delete-misc-file-button", "disabled"),
        Input("misc-files-table", "selectionChanged"),
    )
    def check_misc_file_delete_validity(selection):
        if ctx.triggered_id == "misc-files-table":
            if selection[0]["UserId"] == session["user"].id:
                return False

        return True

    @app.callback(
        Output("delete-misc-file-confirmation", "is_open"),
        Input("delete-misc-file-button", "n_clicks"),
        Input("delete-misc-file-confirm", "n_clicks"),
        Input("delete-misc-file-cancel", "n_clicks"),
        State("delete-misc-file-confirmation", "is_open"),
        prevent_intitial_call=True,
    )
    def control_delete_cartridge_picture_popup(
        delete_click, confirm_click, cancel_click, is_open
    ):
        if "delete" in ctx.triggered_id:
            return not is_open
        return is_open

    @app.callback(
        Output("delete-misc-file-response", "is_open"),
        Input("delete-misc-file-confirm", "n_clicks"),
        State("misc-files-table", "selectionChanged"),
        State("delete-misc-file-response", "is_open"),
    )
    def delete_cartridge_picture(confirm_click, selection, is_open):
        if ctx.triggered_id == "delete-misc-file-confirm":
            delete_cartridge_picture_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "miscellaneousfiles/{}".format(selection[0]["Id"])
            print(delete_cartridge_picture_url)
            response = requests.delete(
                url=delete_cartridge_picture_url, verify=False)
            print("Cartridge Picture Delete Status Code: ", response.status_code)

            return not is_open
        else:
            return is_open

    @app.callback(
        Output("comments-modal", "is_open"),
        Input("create-comment-button", "n_clicks"),
        Input("cancel-comment-button", "n_clicks"),
        Input("add-comment-button", "n_clicks"),
        State("comments-modal", "is_open"),
    )
    def open_comment_entry(create_click, cancel_click, add_click, is_open):
        if ctx.triggered_id in [
            "create-comment-button",
            "cancel-comment-button",
            "add-comment-button",
        ]:
            return not is_open
        return is_open

    @app.callback(
        Output("comments-post-response", "is_open"),
        Input("add-comment-button", "n_clicks"),
        State("comments-text", "value"),
        State("runset-review", "data"),
        State("comments-post-response", "is_open"),
    )
    def add_comment(add_click, entrytext, runset_review, is_open):
        if ctx.triggered_id == "add-comment-button":
            add_comment_url = os.environ["RUN_REVIEW_API_BASE"] + "Comments"
            add_comment_payload = {
                "entry": entrytext,
                "runsetReviewId": runset_review["id"],
                "userId": session["user"].id,
            }
            response_status_code = requests.post(
                url=add_comment_url, json=add_comment_payload, verify=False
            ).status_code
            return not is_open
        return is_open

    @app.callback(
        Output("comments-table", "rowData"),
        Output("comments-table", "columnDefs"),
        Input("review-tabs", "active_tab"),
        Input("comments-post-response", "is_open"),
        Input("comments-delete-response", "is_open"),
        State("runset-selection-data", "data"),
    )
    def get_comments(
        active_tab, post_response_is_open, delete_response_is_open, runset_data
    ):
        print("function found")
        if (
            (ctx.triggered_id == "review-tabs" and active_tab == "runset-comments")
            or (
                ctx.triggered_id == "comments-post-response"
                and post_response_is_open == False
            )
            or (
                ctx.triggered_id == "comments-delete-response"
                and delete_response_is_open == False
            )
        ):
            # if True:
            print("getting comments")
            """
            Get Comments for runset
            """
            get_runset_comments_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSets/{}/Comments".format(runset_data["id"])

            runset = requests.get(get_runset_comments_url, verify=False).json()
            """
            Extract Details from each Misc File into pandas DataFrame
            """

            comment_data = pd.DataFrame(
                columns=[
                    "Entry",
                    "Added By",
                    "Added Date",
                    "CommentId",
                    "RunSetReviewId",
                ]
            )

            idx = 0
            for runset_review in runset["runSetReviews"]:
                if runset_review["comments"]:
                    for comment in runset_review["comments"]:
                        entry = {}
                        entry["CommentId"] = comment["id"]
                        entry["RunSetReviewId"] = runset_review["id"]
                        entry["Entry"] = comment["entry"]
                        entry["Added By"] = runset_review["reviewerName"]
                        entry["Added Date"] = comment["validFrom"]

                        comment_data.loc[idx] = entry
                        idx += 1

            """
            Create Column Definitions for Table
            """

            column_definitions = []
            initial_selection = [
                x for x in comment_data.columns if "Id" not in x]

            for column in comment_data.columns:
                column_definition = {
                    "headerName": column,
                    "field": column,
                    "filter": True,
                    "sortable": True,
                }
                if column not in initial_selection:
                    column_definition["hide"] = True

                if "Date" in column:
                    comment_data[column] = (
                        comment_data[column]
                        .astype("datetime64")
                        .dt.strftime("%d %B %Y %H:%M:%S")
                    )

                column_definitions.append(column_definition)

            return comment_data.to_dict(orient="records"), column_definitions
        return no_update

    @app.callback(
        Output("delete-comment-button", "disabled"),
        Input("comments-table", "selectionChanged"),
        State("runset-review", "data"),
    )
    def check_delete_comment_validity(selection, runset_review):
        if (
            ctx.triggered_id == "comments-table"
            and selection[0]["RunSetReviewId"] == runset_review["id"]
        ):
            return False
        return True

    @app.callback(
        Output("comments-delete-confirmation", "is_open"),
        Input("delete-comment-button", "n_clicks"),
        Input("confirm-comment-delete-button", "n_clicks"),
        Input("cancel-comment-delete-button", "n_clicks"),
        State("comments-delete-confirmation", "is_open"),
    )
    def confirm_comment_delete(delete_click, confirm_click, cancel_click, is_open):
        if ctx.triggered_id in [
            "delete-comment-button",
            "confirm-comment-delete-button",
            "cancel-comment-delete-button",
        ]:
            return not is_open
        return is_open

    @app.callback(
        Output("comments-delete-response", "is_open"),
        Input("confirm-comment-delete-button", "n_clicks"),
        State("comments-table", "selectionChanged"),
        State("comments-delete-response", "is_open"),
    )
    def confirm_comment_delete(confirm_click, selection, is_open):
        if ctx.triggered_id == "confirm-comment-delete-button":
            delete_comment_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "Comments/{}".format(selection[0]["CommentId"])
            requests.delete(url=delete_comment_url, verify=False)
            return not is_open

        return is_open

    @app.callback(
        Output("view-comment-button", "disabled"),
        Input("comments-table", "selectionChanged"),
    )
    def check_view_comment_validity(selection):
        print(selection)
        if ctx.triggered_id == "comments-table" and selection:
            return False
        return True

    @app.callback(
        Output("comments-view-modal", "is_open"),
        Output("comments-view-text", "children"),
        Input("view-comment-button", "n_clicks"),
        State("comments-table", "selectionChanged"),
        State("comments-view-modal", "is_open"),
    )
    def view_selected_comment(view_click, selection, is_open):
        if ctx.triggered_id == "view-comment-button":
            return not is_open, selection[0]["Entry"]
        return is_open, ""

    return app.server


if __name__ == "__main__":
    app = Dash(
        __name__,
        use_pages=True,
        pages_folder="run-review-pages",
        url_base_pathname=url_base,
        external_stylesheets=[dbc.themes.COSMO],
    )
    app.layout = html.Div(
        [review_loader, dcc.Location(id="run-review-url"), sidebar, content]
    )
    app.run_server(debug=True)
