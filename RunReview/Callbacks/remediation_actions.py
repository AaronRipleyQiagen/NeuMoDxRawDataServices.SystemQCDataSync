from .dependencies import *


def get_remediation_action_callbacks(app):
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
                remediation_action_url = (
                    os.environ["RUN_REVIEW_API_BASE"] + "RemediationActions"
                )

                response = requests.post(
                    url=remediation_action_url,
                    json=remediation_action_payload,
                    verify=False,
                ).json()
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

            resp = requests.put(
                url=remediation_action_update_url, params=query_params, verify=False
            )
            return not is_open

        return is_open

    """
    Callbacks related to deleting a remediation action.
    """

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
            delete_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RemediationActions/{}".format(selected_row[0]["RemediationActionId"])
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
