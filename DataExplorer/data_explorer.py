from dash import Dash, html, dcc, Output, Input, State, ctx
import dash_bootstrap_components as dbc
import dash

import pandas as pd
from flask import Flask, session

import json

from Shared.neumodx_objects import *
from Shared.communication import *
from Shared.appbuildhelpers import apply_layout_with_auth
from Shared.Components import *

import os
import requests


url_base = "/dashboard/data-explorer/"
loader = html.Div(id="loader")
cartridge_sample_ids = dcc.Store(id="cartridge-sample-ids", storage_type="session")
selected_cartridge_sample_ids = dcc.Store(
    id="selected-cartridge-sample-ids", storage_type="session"
)
sample_info = dcc.Store(id="sample-info", storage_type="session")
runset_type_selection = dcc.Store(id="runset-type-selection", storage_type="session")
layout = dbc.Container(
    [
        loader,
        cartridge_sample_ids,
        selected_cartridge_sample_ids,
        sample_info,
        runset_type_selection,
        dash.page_container,
        dcc.Loading(
            id="page-changing",
            fullscreen=True,
            type="dot",
            children=[dcc.Location(id="url")],
        ),
    ],
)


def Add_Dash(app):
    app = Dash(
        __name__,
        server=app,
        url_base_pathname=url_base,
        use_pages=True,
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
        Output(UserInputModal.ids.modal("data-explorer"), "is_open"),
        Input("submit-button", "n_clicks"),
        State(UserInputModal.ids.modal("data-explorer"), "is_open"),
        prevent_initial_call=True,
    )
    def control_attempt_number_modal(confirm_runset_type_click, is_open):
        return not is_open

    @app.callback(
        Output("review-group-options", "options"),
        Output("created-runset-id", "data"),
        Input(UserInputModal.ids.submit("data-explorer"), "n_clicks"),
        State("sample-info", "data"),
        State("runset-type-options", "value"),
        State("runset-type-options", "options"),
        State(RunSetAttemptModalBody.ids.attempt_number("data-explorer"), "value"),
        State("post-response", "is_open"),
        prevent_initial_call=True,
    )
    def create_runset(
        submit_clicks,
        data: str,
        runset_type_selection_id: str,
        runset_type_selection_options: dict,
        runset_attempt_number: int,
        is_open: bool,
    ):
        print("Runset Attempt Number: ", runset_attempt_number)
        reviewgroup_options = {}
        if submit_clicks:
            dataframe = pd.DataFrame.from_dict(data)
            dataframe.drop_duplicates(["Test Guid", "Replicate Number"], inplace=True)
            """
            This Block creates the run review dataset.
            """
            runset = {}
            runset["userId"] = session["user"].id
            runset["description"] = ""
            runset["number"] = runset_attempt_number
            runset["runSetStartDate"] = (
                dataframe["Start Date Time"]
                .astype("datetime64[ms]")
                .min()
                .isoformat(timespec="milliseconds")
            )
            runset["runSetEndDate"] = (
                dataframe["End Date Time"]
                .astype("datetime64[ms]")
                .max()
                .isoformat(timespec="milliseconds")
            )

            runset["runSetTypeId"] = runset_type_selection_id
            runset["samples"] = []

            for idx in dataframe.index:
                sample = {}

                sample["rawDataDatabaseId"] = dataframe.loc[idx, "RawDataDatabaseId"]
                sample["cosmosDatabaseId"] = dataframe.loc[idx, "cosmosId"]
                sample["neuMoDxSystem"] = NeuMoDxSystem(
                    dataframe.loc[[idx]]
                ).create_object()
                sample["neuMoDxSystem"]["RawDataDatabaseId"] = dataframe.loc[
                    idx, "NeuMoDx System Id"
                ]
                sample["xpcrModule"] = XPCRModule(dataframe.loc[[idx]]).create_object()
                sample["xpcrModule"]["RawDataDatabaseId"] = dataframe.loc[
                    idx, "XPCR Module Id"
                ]
                sample["cartridge"] = {}
                sample["cartridge"]["barcode"] = dataframe.loc[idx, "Cartridge Barcode"]
                sample["cartridge"]["lot"] = dataframe.loc[idx, "Cartridge Lot"]
                sample["cartridge"]["serial"] = dataframe.loc[idx, "Cartridge Serial"]
                sample["cartridge"]["expiration"] = dataframe.loc[
                    idx, "Cartridge Expiration"
                ]
                sample["cartridge"]["RawDataDatabaseId"] = dataframe.loc[
                    idx, "Cartridge Id"
                ]

                sample["xpcrModuleLane"] = {}
                sample["xpcrModuleLane"]["moduleLane"] = int(
                    dataframe.loc[idx, "XPCR Module Lane"]
                )
                sample["xpcrModuleLane"]["RawDataDatabaseId"] = dataframe.loc[
                    idx, "xpcrModuleLaneId"
                ]

                runset["samples"].append(sample)

                runset["parseRunSetNeuMoDxSystems"] = True
                runset["parseRunSetXPCRModules"] = True
                runset["parseRunSetCartridges"] = True
                runset["parseRunSetXPCRModuleLanes"] = True
            print(runset_type_selection_options)
            runset["samplecount"] = len(runset["samples"])
            runset["name"] = (
                dataframe.loc[idx, "XPCR Module Serial"]
                + " "
                + runset_type_selection_options[runset_type_selection_id]
            )

            print("--" * 30)
            resp = requests.post(
                url=os.environ["RUN_REVIEW_API_BASE"] + "RunSets",
                json=runset,
                verify=False,
            )

            created_runset = resp.json()
            created_runset_id = created_runset["id"]
            print("got created runset id " + created_runset_id)

        """
        Get Review Groups
        """
        reviewgroups_url = os.environ["RUN_REVIEW_API_BASE"] + "ReviewGroups"

        reviewgroups_response = requests.get(reviewgroups_url, verify=False).json()

        for reviewgroup in reviewgroups_response:
            if reviewgroup["description"] != "System QC Tech I":
                reviewgroup_options[reviewgroup["id"]] = reviewgroup["description"]

        if submit_clicks:
            return reviewgroup_options, created_runset_id
        return dash.no_update

    @app.callback(
        Output("post-response", "is_open"),
        Input("submit-reviewgroup-selection-button", "n_clicks"),
        Input("cancel-reviewgroup-selection-button", "n_clicks"),
        State("review-group-options", "value"),
        State("review-group-options", "options"),
        State("created-runset-id", "data"),
        State("post-response", "is_open"),
        State("url", "href"),
        prevent_initial_call=True,
    )
    def add_runsetreviewassignments(
        submit_button,
        cancel_button,
        review_groups_selected,
        review_groups_dictionary,
        created_runset_id,
        post_response_is_open,
        url,
    ):
        if (
            ctx.triggered_id == "submit-reviewgroup-selection-button"
            or ctx.triggered_id == "cancel-reviewgroup-selection-button"
        ):
            review_groups = []
            review_group_subscribers = {}
            for review_group_id in review_groups_selected:
                runsetreviewassignmenturl = (
                    os.environ["RUN_REVIEW_API_BASE"] + "RunSetReviewAssignments"
                )
                queryParams = {}
                queryParams["runsetid"] = created_runset_id
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
            if os.environ["SEND_EMAILS"] == "Yes":
                send_review_ready_messages(
                    app, created_runset_id, url, review_group_subscribers
                )
            return not post_response_is_open
        return post_response_is_open

    return app.server
