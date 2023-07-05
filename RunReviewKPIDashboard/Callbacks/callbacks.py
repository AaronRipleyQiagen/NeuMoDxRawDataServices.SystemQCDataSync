from dash import Input, Output, State, no_update, ctx
import requests
import plotly.express as px
import os
import datetime
import pandas as pd
from Shared.functions import *
from Shared.Components import *
from functools import reduce


def add_run_review_kpi_callbacks(app):
    @app.callback(
        Output("run-type-selector", "options"), Input("settings-div", "children")
    )
    def get_run_type_options(children):
        run_type_options_url = os.environ["RUN_REVIEW_API_BASE"] + "RunSetTypes"

        run_type_options_response = requests.get(
            url=run_type_options_url, verify=False
        ).json()

        run_type_options = {}
        for run_type_option in run_type_options_response:
            if run_type_option["description"]:
                run_type_options[run_type_option["id"]] = run_type_option["description"]

        return run_type_options

    @app.callback(
        Output("runset-status-selector", "options"), Input("settings-div", "children")
    )
    def get_runset_status_options(children):
        runset_status_options_url = os.environ["RUN_REVIEW_API_BASE"] + "RunSetStatuses"

        runset_statuses = requests.get(
            url=runset_status_options_url, verify=False
        ).json()

        runset_status_options = {}
        for option in runset_statuses:
            if option["name"]:
                runset_status_options[option["id"]] = option["name"]

        return runset_status_options

    @app.callback(
        Output("runset-status-selector", "value"),
        Input("runset-status-selector", "options"),
    )
    def set_runset_status_values(options):
        if ctx.triggered_id == "runset-status-selector":
            values = []
            for option in options:
                values.append(option)
            return values
        return no_update

    @app.callback(
        Output("runsets", "data"),
        Input("date-range-selector", "start_date"),
        Input("date-range-selector", "end_date"),
        Input("run-type-selector", "value"),
        Input("runset-status-selector", "value"),
    )
    def update_runsets(start_date, end_date, assays, statuses):
        runsets_url = (
            os.environ["RUN_REVIEW_API_BASE"] + "Reports/runsetxpcrmoduledetails"
        )
        query_params = {}
        if start_date:
            query_params["MinDateTime"] = datetime.datetime.strptime(
                start_date, "%Y-%m-%d"
            ).isoformat()
        if end_date:
            query_params["MaxDateTime"] = datetime.datetime.strptime(
                end_date, "%Y-%m-%d"
            ).isoformat()
        if assays:
            query_params["RunSetTypeIds"] = assays
        if statuses:
            query_params["RunSetStatusIds"] = statuses
        runset_data_response = requests.get(
            url=runsets_url, params=query_params, verify=False
        )
        return runset_data_response.json()

    @app.callback(
        Output("status-summary-table", "rowData"),
        Output("status-summary-table", "columnDefs"),
        Input("runsets", "data"),
    )
    def populate_status_summary_table(data):
        """
        A server-side callback method that populates the status summary table associated with Run Review KPIs
        """
        column_map = {
            "runSetId": "RunSetId",
            "xpcrModuleId": "XPCRModuleId",
            "runSetType": "Type",
            "xpcrModuleSerial": "XPCR Module Serial",
            "runSetStatus": "Status",
            "runSetStartDate": "Start Date",
            "runSetEndDate": "End Date",
        }

        return get_dash_ag_grid_from_records(
            records=data,
            column_map=column_map,
            group_columns=["Type", "XPCR Module Serial"],
        )

    @app.callback(
        Output(GoToRunSetButtonAIO.ids.store("run-review-kpis-status-summary"), "data"),
        Output(
            GoToXPCRModuleButtonAIO.ids.module_id("run-review-kpis-status-summary"),
            "data",
        ),
        Input("status-summary-table", "selectionChanged"),
    )
    def get_ids_from_status_summary_selection(selection):
        """
        A server-side callback method that populates the runset_id & module_id
        properities of the GoToRunSetButton & GoToXPCRModuleButton associated with
        the status-summary-table.
        """
        if selection:
            return selection[0]["RunSetId"], selection[0]["XPCRModuleId"]
        else:
            return no_update

    @app.callback(Output("status-summary-barchart", "figure"), Input("runsets", "data"))
    def plot_runset_status_summary(runsets):
        runset_data = pd.DataFrame.from_dict(runsets)
        aggTypes = {"runSetId": "count"}
        runset_status_summary_data = (
            runset_data.groupby(
                [
                    "runSetType",
                    "runSetStatus",
                ]
            )
            .agg(aggTypes)
            .reset_index()
        )
        runset_status_summary_data.columns = ["Type", "Status", "Run Count"]
        fig = px.histogram(
            runset_status_summary_data,
            color="Status",
            x="Type",
            y="Run Count",
            barmode="group",
        )

        return fig

    @app.callback(
        Output("issues", "data"),
        Input("runsets", "data"),
    )
    def get_issues(runset_data):
        URLS = []
        runset_xpcrmodule_serials = {}
        runset_xpcrmodule_ids = {}
        for runset in runset_data:
            runset_xpcrmodule_ids[runset["runSetId"]] = runset["xpcrModuleId"]
            runset_xpcrmodule_serials[runset["runSetId"]] = runset["xpcrModuleSerial"]
            url = os.environ["RUN_REVIEW_API_BASE"] + "Reports/{}/runsetissues".format(
                runset["runSetId"]
            )
            URLS.append(url)

        runset_issues = HttpGetAsync(urls=URLS)
        runset_issues = reduce(lambda x, y: x + y, runset_issues, [])
        runset_issues = [
            {
                **x,
                "xpcrModuleId": runset_xpcrmodule_ids[x["runSetId"]],
                "xpcrModuleSerial": runset_xpcrmodule_serials[x["runSetId"]],
            }
            for x in runset_issues
        ]
        return runset_issues

    @app.callback(
        Output("filtered-issues", "data"),
        Input("issues", "data"),
        Input("issue-severity-selector", "value"),
        Input("issue-level-selector", "value"),
        State("issue-level-selector", "options"),
    )
    def filter_issues(issues_data, severity_values, level_values, issue_levels_dict):
        filtered_issues_data = issues_data

        if severity_values != []:
            filtered_issues_data = [
                x for x in filtered_issues_data if x["severity"] in severity_values
            ]
        if level_values != []:
            filtered_issues_data = [
                x for x in filtered_issues_data if x["level"] in level_values
            ]

        filtered_issues_data = list(
            map(
                lambda d: {**d, "level": issue_levels_dict.get(d["level"], d["level"])},
                filtered_issues_data,
            )
        )
        return filtered_issues_data

    @app.callback(
        Output("issues-summary-table", "rowData"),
        Output("issues-summary-table", "columnDefs"),
        Input("filtered-issues", "data"),
    )
    def populate_issues_summary_table(data):
        """
        A server-side callback method that populates the status summary table associated with Run Review KPIs
        """
        column_map = {
            "issueId": "IssueId",
            "runSetId": "RunSetId",
            "runSetReviewId": "RunSetReviewId",
            "xpcrModuleId": "XPCRModuleId",
            "severity": "Severity",
            "xpcrModuleSerial": "XPCR Module Serial",
            "level": "Level",
            "type": "Type",
            "status": "Status",
            "assayChannel": "Assay Channel",
            "targetName": "Target Name",
        }

        return get_dash_ag_grid_from_records(
            records=data,
            column_map=column_map,
            group_columns=["Severity", "XPCR Module Serial", "Level", "Type"],
        )

    @app.callback(
        Output("issues-summary-barchart", "figure"),
        Input("filtered-issues", "data"),
    )
    def plot_issue_summary(filtered_issues_data):
        issues_dataframe = pd.DataFrame.from_dict(filtered_issues_data)
        issues_dataframe["Issue Count"] = 1
        issues_dataframe.rename({"level": "Level"}, axis=1, inplace=True)
        fig = px.histogram(
            issues_dataframe, color="type", x="Level", y="Issue Count", barmode="group"
        )

        return fig

    @app.callback(
        Output(GoToRunSetButtonAIO.ids.store("run-review-kpis-issue-summary"), "data"),
        Output(
            GoToXPCRModuleButtonAIO.ids.module_id("run-review-kpis-issue-summary"),
            "data",
        ),
        Input("issues-summary-table", "selectionChanged"),
    )
    def get_ids_from_issues_summary_selection(selection):
        """
        A server-side callback method that populates the runset_id & module_id
        properities of the GoToRunSetButton & GoToXPCRModuleButton associated with
        the issues-summary-table.
        """
        if selection:
            return selection[0]["RunSetId"], selection[0]["XPCRModuleId"]
        else:
            return no_update

    @app.callback(
        Output("module-runset-summaries", "data"),
        Input("runsets", "data"),
        State("date-range-selector", "start_date"),
    )
    def get_module_runset_summaries(runset_data, minimum_start_date):
        URLS = []
        runsets_dataframe = pd.DataFrame.from_dict(runset_data)
        module_ids = []
        for runset in runset_data:
            if runset["xpcrModuleId"] not in module_ids:
                module_ids.append(runset["xpcrModuleId"])
                url = os.environ[
                    "RUN_REVIEW_API_BASE"
                ] + "Reports/{}/RelatedRunSetsSummary".format(runset["xpcrModuleId"])
                URLS.append(url)

        module_runsets_summaries = HttpGetAsync(urls=URLS)
        module_runsets_summaries_dataframe = pd.DataFrame()
        idx = 0
        for module in module_runsets_summaries:
            for summary in module:
                if len(module_runsets_summaries_dataframe) == 0:
                    module_runsets_summaries_dataframe = pd.DataFrame(
                        columns=[x for x in summary]
                    )

                if (
                    len(
                        runsets_dataframe[
                            (
                                (
                                    runsets_dataframe["xpcrModuleSerial"]
                                    == summary["xpcrModuleSerial"]
                                )
                                & (
                                    runsets_dataframe["runSetType"]
                                    == summary["runSetType"]
                                )
                            )
                        ]
                    )
                    > 0
                ):
                    module_runsets_summaries_dataframe.loc[idx] = summary
                    idx += 1

        module_runsets_summaries_dataframe = module_runsets_summaries_dataframe[
            module_runsets_summaries_dataframe["minRunSetDateTime"] > minimum_start_date
        ]

        return module_runsets_summaries_dataframe.to_dict(orient="records")

    @app.callback(
        Output("module-run-count-summary-table", "rowData"),
        Output("module-run-count-summary-table", "columnDefs"),
        Input("module-runset-summaries", "data"),
    )
    def populate_module_run_count_summary_table(data):
        column_map = {
            "xpcrModuleId": "XPCRModuleId",
            "xpcrModuleSerial": "XPCR Module Serial",
            "runSetType": "Runset Type",
            "minRunSetDateTime": "First Runset Start Date",
            "maxRunSetDateTime": "Last Runset Start Date",
            "runSetCount": "# of Runsets",
            "lastRunSetStatus": "Status of Last Runset",
        }

        return get_dash_ag_grid_from_records(
            records=data,
            column_map=column_map,
            group_columns=["Runset Type"],
        )

    @app.callback(
        Output("first-time-pass-rate", "value"),
        Output("first-time-pass-rate", "label"),
        Input("module-runset-summaries", "data"),
    )
    def update_first_time_pass_rate(module_runset_summaries):
        module_runset_summaries_dataframe = pd.DataFrame.from_dict(
            module_runset_summaries
        )

        module_runset_summaries_dataframe["valid?"] = 0
        module_runset_summaries_dataframe["valid?"] = np.where(
            module_runset_summaries_dataframe["lastRunSetStatus"] == "Approved",
            1,
            module_runset_summaries_dataframe["valid?"],
        )
        module_runset_summaries_dataframe["valid?"] = np.where(
            module_runset_summaries_dataframe["lastRunSetStatus"] == "Rejected",
            1,
            module_runset_summaries_dataframe["valid?"],
        )
        module_runset_summaries_dataframe["valid?"] = np.where(
            module_runset_summaries_dataframe["runSetCount"] > 1,
            1,
            module_runset_summaries_dataframe["valid?"],
        )

        module_runset_summaries_dataframe = module_runset_summaries_dataframe[
            module_runset_summaries_dataframe["valid?"] == 1
        ]

        total_modules_count = len(module_runset_summaries_dataframe)
        print("TOTAL MODULES COUNT:", total_modules_count)
        if total_modules_count > 0:
            first_time_pass_count = len(
                module_runset_summaries_dataframe[
                    (
                        (
                            module_runset_summaries_dataframe["lastRunSetStatus"]
                            == "Approved"
                        )
                        & (module_runset_summaries_dataframe["runSetCount"] == 1)
                    )
                ]
            )

            first_time_pass_rate = (first_time_pass_count / total_modules_count) * 100

        else:
            first_time_pass_rate = 0

        return first_time_pass_rate, "First Time Pass Rate (n={})".format(
            total_modules_count
        )

    @app.callback(
        Output(
            GoToXPCRModuleButtonAIO.ids.module_id(
                "run-review-kpis-module-run-count-summary"
            ),
            "data",
        ),
        Input("module-run-count-summary-table", "selectionChanged"),
    )
    def get_ids_from_status_summary_selection(selection):
        """
        A server-side callback method that populates the runset_id & module_id
        properities of the GoToRunSetButton & GoToXPCRModuleButton associated with
        the module-run-count-summary-table.
        """
        if selection:
            return selection[0]["XPCRModuleId"]
        else:
            return no_update

    @app.callback(
        Output("number-of-runs-boxplot", "figure"),
        Input("module-runset-summaries", "data"),
    )
    def update_number_of_runs(module_runset_summaries):
        module_runset_summaries_dataframe = pd.DataFrame.from_dict(
            module_runset_summaries
        )

        fig = px.box(module_runset_summaries_dataframe, x="runSetType", y="runSetCount")

        return fig

    @app.callback(
        Output(
            RemediationActionEffectivenessCard.ids.runset_ids("run-review-kpis"),
            "data",
        ),
        Input("runsets", "data"),
        prevent_initial_call=True,
    )
    def get_runset_ids(runsets_data: list[dict]):
        if runsets_data:
            return list(set(map(lambda x: x["runSetId"], runsets_data)))
        else:
            return no_update
