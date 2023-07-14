from dash import Output, Input, State, no_update, ctx
import pandas as pd
import requests
import os
from urllib.parse import urlparse, parse_qs
from Shared.communication import *
from Shared.Components import *
from Shared.neumodx_objects import *
from itertools import chain
from flask import session


def add_data_reviewer_callbacks(app) -> None:
    @app.callback(
        Output("cartridge-ids", "data"),
        Output(FindXPCRModuleRunsButton.ids.xpcrmodule_id("data-explorer"), "data"),
        Input("url", "href"),
    )
    def get_cartridge_ids(url):
        if url:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)

            cartridge_list = []
            module_list = []
            for param, values in query_params.items():
                if param == "cartridgeid":
                    cartridge_list.extend(values)
                elif param == "xpcrmoduleid":
                    module_list.extend(values)
                # else:

            print(cartridge_list)
            print("XPCR", module_list)

            return cartridge_list, module_list[0]
        else:
            return no_update, no_update

    @app.callback(
        Output("channel-selector", "value"),
        Output("process-step-selector", "value"),
        Output("sample-info", "data"),
        Output("runset-type-options", "options"),
        Input("cartridge-ids", "data"),
    )
    def get_sample_ids_from_dcc_store(cartridge_ids: list[str]):
        selected_sample_ids = [
            x["id"]
            for x in list(
                chain.from_iterable(
                    [
                        x["samples"]
                        for x in HttpGetAsync(
                            [
                                os.environ["RAW_DATA_API_BASE"]
                                + "/cartridges/{}/samples".format(cartridge_id)
                                for cartridge_id in cartridge_ids
                            ]
                        )
                    ]
                )
            )
        ]

        sample_data = getSampleDataAsync(selected_sample_ids)

        print("Got Sample Data")
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

    @app.callback(
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
            X = np.array(
                [read for read in df_Channel_Step.loc[idx, "Readings Array"]][0]
            )
            Y = np.array(
                [read for read in df_Channel_Step.loc[idx, "Readings Array"]][1]
            )
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
            x
            for x in output_frame.columns
            if "Lot" in x or "Serial" in x or "Barcode" in x
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

    @app.callback(
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

    @app.callback(
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

    @app.callback(
        Output(UserInputModal.ids.modal("data-explorer"), "is_open"),
        Input("submit-button", "n_clicks"),
        State(UserInputModal.ids.modal("data-explorer"), "is_open"),
        prevent_initial_call=True,
    )
    def control_attempt_number_modal(confirm_runset_type_click, is_open):
        return not is_open

    @app.callback(
        Output(
            UserInputModal.ids.modal("data-explorer-run-attempt-validation"), "is_open"
        ),
        Output(
            GoToRunSetButtonAIO.ids.store("data-explorer-run-attempt-validation"),
            "data",
        ),
        Output("data-explorer-validation-check-pass", "data"),
        Input(UserInputModal.ids.submit("data-explorer"), "n_clicks"),
        State("sample-info", "data"),
        State("runset-type-options", "value"),
        State(RunSetAttemptModalBody.ids.attempt_number("data-explorer"), "value"),
        State(
            UserInputModal.ids.modal("data-explorer-run-attempt-validation"), "is_open"
        ),
        prevent_inital_call=True,
    )
    def validate_runset_attempt_number(
        attempt_number_submit: int,
        sample_data: list[dict],
        runset_type_id: str,
        attempt_number: int,
        is_open: bool,
    ):
        print("RUNNING VALIDATION CHECK")
        validate_runset_attempt_number_url = (
            os.environ["RUN_REVIEW_API_BASE"] + "/RunSets/check-for-existing"
        )

        query_params = {
            "xpcrmoduleserial": sample_data[0]["XPCR Module Serial"],
            "runsettypeId": runset_type_id,
            "attemptnumber": attempt_number,
        }

        print(query_params)

        response = requests.get(
            url=validate_runset_attempt_number_url, params=query_params, verify=False
        )
        print(response.status_code)

        if response.status_code == 200:
            return not is_open, response.json()["id"], no_update
        else:
            return is_open, no_update, True

    @app.callback(
        Output("review-group-options", "options"),
        Output("created-runset-id", "data"),
        Input(
            UserInputModal.ids.submit("data-explorer-run-attempt-validation"),
            "n_clicks",
        ),
        Input("data-explorer-validation-check-pass", "data"),
        State("sample-info", "data"),
        State("runset-type-options", "value"),
        State("runset-type-options", "options"),
        State(RunSetAttemptModalBody.ids.attempt_number("data-explorer"), "value"),
        State("post-response", "is_open"),
        prevent_initial_call=True,
    )
    def create_runset(
        submit_clicks,
        validation_check_pass,
        data: list[dict],
        runset_type_selection_id: str,
        runset_type_selection_options: dict,
        runset_attempt_number: int,
        is_open: bool,
    ):
        print("Runset Attempt Number: ", runset_attempt_number)
        reviewgroup_options = {}
        if submit_clicks or validation_check_pass:
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
            print("GETTING REVIEW GROUPS")
            reviewgroups_url = os.environ["RUN_REVIEW_API_BASE"] + "ReviewGroups"

            reviewgroups_response = requests.get(reviewgroups_url, verify=False).json()

            for reviewgroup in reviewgroups_response:
                if reviewgroup["description"] != "System QC Tech I":
                    reviewgroup_options[reviewgroup["id"]] = reviewgroup["description"]

            return reviewgroup_options, created_runset_id
        else:
            return no_update

    @app.callback(
        Output(GoToRunSetButtonAIO.ids.store("data-reviewer-go-to-runset"), "data"),
        Input("created-runset-id", "data"),
    )
    def update_runset_id(runset_id):
        if runset_id:
            return runset_id
        else:
            no_update

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
