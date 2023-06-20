from .dependencies import *


def get_active_issue_callbacks(app):
    @app.callback(
        [Output("issues-table", "rowData"), Output("issues-table", "columnDefs")],
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

                runset_data = requests.get(url=runset_issues_url, verify=False).json()

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

    """
    Remediation action grading workflow callbacks
    """

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
        if issue_selected:
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
                and related_runsets[runset_selection_data["id"]]
                > issue_selected["Attempt"]
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
        else:
            return no_update

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

                query_params = {
                    "runSetReviewId": runset_review["id"],
                    "newStatusName": "Closed",
                }
                resp = requests.put(
                    url=issue_update_url, params=query_params, verify=False
                )

            return not is_open

        return is_open

    """ 
    Functions related to deleting an issue in the active issues table.
    """

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
        if issue_selected:
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
        else:
            return no_update

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
