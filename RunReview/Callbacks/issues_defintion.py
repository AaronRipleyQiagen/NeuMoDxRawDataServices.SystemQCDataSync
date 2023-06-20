from .dependencies import *

"""
File contains callback methods related to issue defintion functions.
"""


def get_issue_definition_callbacks(app):
    @app.callback(
        [
            Output("sample-issue-options", "options"),
            Output("lane-issue-options", "options"),
            Output("module-issue-options", "options"),
            Output("run-issue-options", "options"),
            Output("tadm-issue-options", "options"),
        ],
        Input("submit-sample-issue", "children"),
        prevent_intial_call=True,
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
                        asyncio.ensure_future(getIssueTypeOptions(session, url))
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

    """
    These functions relate to getting & setting a the selected issue severity rating thoughout applicable components.
    """

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
    def update_channel_selection_value(severity):
        return severity, severity, severity, severity

    """
    These functions relate to getting & setting the selected channel thoughout applicable components.
    """

    @app.callback(
        Output("sample-issue-channel-options", "options"),
        Output("lane-issue-channel-options", "options"),
        Output("run-issue-channel-options", "options"),
        Output("module-issue-channel-options", "options"),
        Output("run-review-channel-selector", "options"),
        Output("run-summary-channel-selector", "options"),
        Input("runset-channel-options", "data"),
    )
    def update_channel_options(data):
        return data, data, data, data, data, data

    @app.callback(
        Output("channel-selected", "data"),
        Input("sample-issue-channel-options", "value"),
        Input("lane-issue-channel-options", "value"),
        Input("run-issue-channel-options", "value"),
        Input("module-issue-channel-options", "value"),
        Input("run-review-channel-selector", "value"),
        Input("run-summary-channel-selector", "value"),
        Input("spc-channel", "data"),
        prevent_inital_call=True,
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
        elif channel_adjusted == "spc-channel":
            return spc_channel

    @app.callback(
        Output("sample-issue-channel-options", "value"),
        Output("lane-issue-channel-options", "value"),
        Output("run-issue-channel-options", "value"),
        Output("module-issue-channel-options", "value"),
        Output("run-review-channel-selector", "value"),
        Output("run-summary-channel-selector", "value"),
        Input("channel-selected", "data"),
    )
    def update_channel_selection_value(channel):
        if channel:
            return channel, channel, channel, channel, channel, channel
        else:
            return no_update

    """
    These functions relate to getting & setting the selected run number thoughout applicable components.
    """

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

    """
    These functions relate to getting & setting the selected XPCR Module Lane thoughout applicable components.
    """

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

    """
    These functions relate to getting & setting the selected XPCR Module thoughout applicable components.
    """

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
        prevent_intial_call=True,
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
        if run_review_mod_options:
            if trigger == "module-issue-module-options":
                if module_issue_mod_selection == None:
                    return [x for x in run_review_mod_options][0]
                return module_issue_mod_selection
            elif trigger == "run-issue-module-options":
                if run_issue_mod_selection == None:
                    return [x for x in run_review_mod_options][0]
                return run_issue_mod_selection
            elif trigger == "lane-issue-module-options":
                if lane_issue_mod_selection == None:
                    return [x for x in run_review_mod_options][0]
                return lane_issue_mod_selection
            elif trigger == "sample-issue-module-options":
                if sample_issue_mod_selection == None:
                    return [x for x in run_review_mod_options][0]
                return sample_issue_mod_selection
            elif trigger == "tadm-issue-module-options":
                if tadm_issue_mod_selection == None:
                    return [x for x in run_review_mod_options][0]
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
                    if module_id != "NoFilter":
                        return module_id
        else:
            return no_update

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

    """
    The functions control which "top-level" adjustments a user can interact with depending on which page they are on.
    """

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

    """
    Functions related to adding an issue to a runset review.
    """

    @app.callback(
        [
            Output("issue-post-response", "is_open"),
            Output("issue-post-response-message", "children"),
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
        if runset_review:
            issue = {}
            issue["userId"] = session["user"].id
            issue["runSetReviewReferrerId"] = runset_review["id"]
            issue["runSetReviewResolverId"] = "00000000-0000-0000-0000-000000000000"
            issue["severityRatingId"] = severity_id
            issue["assayChannelId"] = channel_id

            try:
                if mod_issue:
                    """
                    Post information to XPCR Module Issue Endpoint
                    """
                    issue["issueTypeId"] = module_issue_id
                    issue["subjectId"] = runset_subject_ids["XPCRModule"][
                        xpcrmodule_selected
                    ]
                    issue["runSetSubjectReferrerId"] = xpcrmodule_selected
                    issue_url = os.environ["RUN_REVIEW_API_BASE"] + "XPCRModuleIssues"

                if run_issue:
                    """
                    Post information to XPCR Module Issue Endpoint
                    """
                    issue["issueTypeId"] = run_issue_id
                    issue["subjectId"] = runset_subject_ids["Cartridge"][run_selected]
                    issue["runSetSubjectReferrerId"] = run_selected
                    issue_url = os.environ["RUN_REVIEW_API_BASE"] + "CartridgeIssues"

                if lane_issue:
                    """
                    Post information to XPCR Module Issue Endpoint
                    """
                    issue["issueTypeId"] = lane_issue_id
                    issue["subjectId"] = runset_subject_ids["XPCRModuleLane"][
                        lane_selected
                    ]
                    issue["runSetSubjectReferrerId"] = lane_selected
                    issue_url = (
                        os.environ["RUN_REVIEW_API_BASE"] + "XPCRModuleLaneIssues"
                    )

                if sample_issue:
                    """
                    Post information to XPCR Module Issue Endpoint
                    """
                    issue["issueTypeId"] = sample_issue_id
                    issue["subjectId"] = samples_selected[0]["SampleId"]
                    issue["runSetSubjectReferrerId"] = samples_selected[0][
                        "RunSetSampleId"
                    ]
                    issue_url = os.environ["RUN_REVIEW_API_BASE"] + "SampleIssues"

                if tadm_issue:
                    """
                    Post information to XPCR Module TADM Issue Endpoint
                    """
                    issue["assayChannelId"] = "00000000-0000-0000-0000-000000000000"
                    issue["issueTypeId"] = tadm_issue_id
                    issue["subjectId"] = runset_subject_ids["XPCRModule"][
                        xpcrmodule_selected
                    ]
                    issue["runSetSubjectReferrerId"] = xpcrmodule_selected
                    issue_url = (
                        os.environ["RUN_REVIEW_API_BASE"] + "XPCRModuleTADMIssues"
                    )

                response = requests.post(url=issue_url, json=issue, verify=False)

                status_code = response.status_code

                if status_code == 200:
                    response_message = "Issue was created successfully."
                else:
                    response_message = "Issue creation was unsuccessful."
            except:
                response_message = "Issue creation was unsuccessful."

            if mod_issue or run_issue or lane_issue or sample_issue or tadm_issue:
                return not is_open, response_message, None, None, None, None, None

        return no_update
