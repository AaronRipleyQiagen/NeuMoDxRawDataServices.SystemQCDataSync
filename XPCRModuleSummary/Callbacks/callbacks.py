from dash import Input, Output, State, no_update, Dash
import requests
import plotly.figure_factory as ff
import plotly.graph_objects as go
from datetime import datetime
from dateutil import parser
import pandas as pd
from Shared.functions import *
from Shared.Components import *

RUN_REVIEW_API_BASE = "https://neumodx-systemqc-runreview.azurewebsites.net/api/"


def add_callbacks(app: Dash) -> None:
    """
    A helper function used to add callbacks to a Dash application.

    Args:
        app: The Dash application to add callbacks to.

    """

    @app.callback(
        Output("xpcrmodule-history-data", "data"),
        Input("url", "href"),
        prevent_inital_call=True,
    )
    @timer_decorator
    def getXPCRModuleHistoryData(url: str) -> dict:
        """
        A server-side callback function used to retrieve the data regarding the History of an XPCR Module in DataSync.

        Args:
            url: The url of the web-page.

        Returns:
            A json-serializable dictionary representation of the History of an XPCR Module in DataSync.
        """
        # Get the id of the module of interest:
        xpcrmodule_id = url.split("/")[-1]

        # Build a url string and make request to API endpoint.
        xpcrmodule_report_url = (
            RUN_REVIEW_API_BASE + f"Reports/xpcrmodule/{xpcrmodule_id}/RelatedInfo"
        )

        response = requests.get(url=xpcrmodule_report_url, verify=False)

        xpcrmodule_history_data: dict

        # Determine if request was successful or not by checking status_code.
        if response.status_code == 200:
            # if successful return content of respose.
            xpcrmodule_history_data = response.json()
        else:
            # if successful return content of respose.
            xpcrmodule_history_data = {}

        return xpcrmodule_history_data

    @app.callback(
        Output("runset-stats-data-by-runset", "data"),
        Input("xpcrmodule-history-data", "data"),
    )
    @timer_decorator
    def get_runset_stats_data_by_runset(xpcrmodule_history_data: dict) -> dict:
        """
        A server-side callback used to retrieve summary stats that describe run performance on a per cartridge basis for cartridges associated with XPCR Module of Interest.
        """

        cartridges_groups = {}

        for runsetDetail in xpcrmodule_history_data["runSetDetails"]:
            cartridges_groups[runsetDetail["id"]] = [
                x for x in runsetDetail["cartridgeRawDataBaseIds"]
            ]

        request_arguments_list = []

        for runset_id in cartridges_groups:
            request_arguments_list.append(
                GetRequestArguments(
                    url=os.environ["API_HOST"]
                    + "/api/Reports/cartridges/datasetchannelsummaries",
                    params={"cartridgeIds": cartridges_groups[runset_id]},
                    label=runset_id,
                )
            )

        runset_stats = HttpGetWithQueryParametersAsync(request_arguments_list)
        unpacked_stats = [
            unpack_multi_level_dictionary(
                record,
                ["ct", "endPointFluorescence", "maxPeakHeight", "epr"],
                ["mean", "std", "cv", "min", "max"],
            )
            for record in runset_stats
        ]
        return unpacked_stats

    @app.callback(
        Output("runset-stats-data-by-cartridge", "data"),
        Input("xpcrmodule-history-data", "data"),
    )
    @timer_decorator
    def get_runset_stats_data_by_cartridge(xpcrmodule_history_data: dict) -> dict:
        """
        A server-side callback used to retrieve summary stats that describe run performance on a per cartridge basis for cartridges associated with XPCR Module of Interest.
        """

        cartridges = []

        for runsetDetail in xpcrmodule_history_data["runSetDetails"]:
            cartridges = cartridges + [
                x for x in runsetDetail["cartridgeRawDataBaseIds"]
            ]

        request_arguments_list = []

        for cartridge in cartridges:
            request_arguments_list.append(
                GetRequestArguments(
                    url=os.environ["API_HOST"]
                    + "/api/Reports/cartridges/datasetchannelsummaries",
                    params={"cartridgeIds": [cartridge]},
                    label=cartridge,
                )
            )
        cartridge_stats = HttpGetWithQueryParametersAsync(request_arguments_list)
        unpacked_stats = [
            unpack_multi_level_dictionary(
                record,
                ["ct", "endPointFluorescence", "maxPeakHeight", "epr"],
                ["mean", "std", "cv", "min", "max"],
            )
            for record in cartridge_stats
        ]

        return unpacked_stats

    @app.callback(
        Output("xpcrmodule-history-gantt", "figure"),
        Input("xpcrmodule-history-data", "data"),
    )
    def plotXPCRModuleHistoryGantt(
        xpcrmodule_history_data: dict,
    ) -> go.Figure:
        """
        A server-side callback used to plot key details related to the XPCR Module's history in DataSync on a Gantt chart.

        Args:
            xpcrmodule_history_data: Data related to the history of the XPCR Module in DataSync.

        Returns:
            A Figure containing a Gantt Chart summarizing an XPCR Module's history.
        """

        # Extract runsets, remediationactions, issues and runsetreviewassignements from xpcr_module_history.
        runsets = xpcrmodule_history_data["runSetDetails"]
        remedationactions = xpcrmodule_history_data["remediationActionsDetails"]
        issues = xpcrmodule_history_data["issueDetails"]
        runsetreviewassignments = xpcrmodule_history_data[
            "runSetReviewAssignmentDetails"
        ]

        # create a list used to capture the lines of the gantt chart.
        gantt_lines = []

        # Add runset entries to gantt lines.
        for runset in runsets:
            runset_data = dict(
                Task=runset["qualificationProtocol"],
                Start=datetime.strptime(runset["startDate"], "%Y-%m-%dT%H:%M:%S.%f"),
                Finish=datetime.strptime(runset["endDate"], "%Y-%m-%dT%H:%M:%S.%f"),
                Resource="Run Execution",
            )
            gantt_lines.append(runset_data)

        # Add remediation entries to gantt lines.
        for remediationaction in remedationactions:
            if remediationaction["closedDate"]:
                finish = datetime.strptime(
                    remediationaction["closedDate"][:-1], "%Y-%m-%dT%H:%M:%S.%f"
                )
            else:
                finish = datetime.now()

            remediationaction_data = dict(
                Task=remediationaction["type"],
                Start=datetime.strptime(
                    remediationaction["assignedDate"][:-1], "%Y-%m-%dT%H:%M:%S.%f"
                ),
                Finish=finish,
                Resource="Remediation Action",
            )
            gantt_lines.append(remediationaction_data)

        # Add issue entries to gantt lines.
        for issue in issues:
            if issue["closedDate"]:
                finish = datetime.strptime(
                    issue["closedDate"][:-1], "%Y-%m-%dT%H:%M:%S.%f"
                )
            else:
                finish = datetime.now()

            issue_data = dict(
                Task=issue["type"],
                Start=datetime.strptime(
                    issue["assignedDate"][:-1], "%Y-%m-%dT%H:%M:%S.%f"
                ),
                Finish=finish,
                Resource=issue["level"],
            )

            gantt_lines.append(issue_data)

        # Add runsetreviewassignment entries to gantt lines.
        for runsetreviewassignment in runsetreviewassignments:
            if runsetreviewassignment["completedDate"]:
                finish = (
                    datetime.strptime(
                        runsetreviewassignment["completedDate"][:-1],
                        "%Y-%m-%dT%H:%M:%S.%f",
                    ),
                )
            else:
                finish = datetime.now()

            runsetreviewassignment_data = dict(
                Task=runsetreviewassignment["qualificationProtocol"],
                Start=datetime.strptime(
                    runsetreviewassignment["assignedDate"][:-1],
                    "%Y-%m-%dT%H:%M:%S.%f",
                ),
                Finish=finish,
                Resource="Review Assignment",
            )

            gantt_lines.append(runsetreviewassignment_data)

        # Define colors to use on Gantt Chart.
        colors = {
            "Sample Issue": "#8152BD",
            "Lane Issue": "#8152BD",
            "Run Issue": "#8152BD",
            "Module Issue": "#8152BD",
            "Remediation Action": "#FF8DAB",
            "Run Execution": "#2C92FF",
            "Review Assignment": "#5F7092",
        }

        # Create the Gantt chart.
        fig = ff.create_gantt(
            gantt_lines,
            colors=colors,
            index_col="Resource",
            show_colorbar=True,
            group_tasks=True,
        )
        return fig

    @app.callback(
        Output(DownloadBlobFileButton.ids.fileurl("files-download-button"), "data"),
        Output(DownloadBlobFileButton.ids.filename("files-download-button"), "data"),
        Input("files-table", "selectionChanged"),
    )
    def get_file_download_info(selection):
        """
        A server-side callback used to retrieve the fileurl and filename of the row selected for the files table.
        """

        if selection:
            return selection[0]["uri"], selection[0]["Name"]
        else:
            return no_update

    add_runset_id_callbacks(app)
    add_xpcrmodule_history_tables_callbacks(app)


def add_runset_id_callbacks(app: Dash) -> None:
    """
    Adds callbacks responsible for retrieving the RunSetId from the various tables related to xpcrmodule-history.

    Args:
        app: Dash Application to add callbacks to.
    """

    @app.callback(
        Output(
            GoToRunSetButtonAIO.ids.store("runset-details-go-to-runset-button"), "data"
        ),
        Input("runset-details-table", "selectionChanged"),
    )
    def get_runset_id_from_runset_detail_selection(selection):
        """
        A server-side callback used to retrieve the RunSetId of the row selected for the RunSet Details table.
        """

        if selection:
            return selection[0]["RunSetId"]
        else:
            return None

    @app.callback(
        Output(
            GoToRunSetButtonAIO.ids.store("runset-reviews-go-to-runset-button"), "data"
        ),
        Input("runset-reviews-table", "selectionChanged"),
    )
    def get_runset_id_from_runset_review_selection(selection):
        """
        A server-side callback used to retrieve the RunSetId of the row selected for the RunSet Reviews table.
        """

        if selection:
            return selection[0]["RunSetId"]
        else:
            return None

    @app.callback(
        Output(GoToRunSetButtonAIO.ids.store("issues-go-to-runset-button"), "data"),
        Input("issues-table", "selectionChanged"),
    )
    def get_runset_id_from_issue_selection(selection):
        """
        A server-side callback used to retrieve the RunSetId of the row selected for the Issues table.
        """

        if selection:
            return selection[0]["RunSetId"]
        else:
            return None

    @app.callback(
        Output(
            GoToRunSetButtonAIO.ids.store("remediation-actions-go-to-runset-button"),
            "data",
        ),
        Input("remediation-actions-table", "selectionChanged"),
    )
    def get_runset_id_from_remediation_action_selection(selection):
        """
        A server-side callback used to retrieve the RunSetId of the row selected for the Remediation Actions table.
        """

        if selection:
            return selection[0]["RunSetId"]
        else:
            return None

    @app.callback(
        Output(GoToRunSetButtonAIO.ids.store("files-go-to-runset-button"), "data"),
        Input("files-table", "selectionChanged"),
    )
    def get_runset_id_from_file_selection(selection):
        """
        A server-side callback used to retrieve the RunSetId of the row selected for the Files table.
        """

        if selection:
            return selection[0]["RunSetId"]
        else:
            return None


def add_xpcrmodule_history_tables_callbacks(app: Dash) -> None:
    """
    Adds callbacks related to populating the tables related to xpcrmodule-history.

    Args:
        app: Dash Application to add callbacks to.
    """

    @app.callback(
        Output("runset-details-table", "rowData"),
        Output("runset-details-table", "columnDefs"),
        Input("xpcrmodule-history-data", "data"),
    )
    def get_runset_details_callback(
        xpcrmodule_history_data: dict,
    ) -> tuple[list[dict], list[dict]]:
        """
        A server-side callback used to retrieve the details of RunSets associated with an XPCR Module and return these to a Dash AG Grid component
        """

        # Extract the runset_details from xpcrmodule_history_data.
        records: list[dict] = xpcrmodule_history_data["runSetDetails"]

        # Provide a map that will deterimine which columns to retrieve from the runset_details_data as well as what they will be called in the end dataframe.
        column_map = {
            "id": "RunSetId",
            "runSetName": "Name",
            "startDate": "Start Date",
            "endDate": "End Date",
            "status": "Status",
        }

        return get_dash_ag_grid_from_records(records=records, column_map=column_map)

    @app.callback(
        Output("runset-reviews-table", "rowData"),
        Output("runset-reviews-table", "columnDefs"),
        Input("xpcrmodule-history-data", "data"),
    )
    def get_runset_review_table(
        xpcrmodule_history_data: dict,
    ) -> tuple[list[dict], list[dict]]:
        """
        A server-side callback used to retrieve the details of RunSetReviews associated with an XPCR Module and return these to a Dash AG Grid component
        """

        # Extract the runset_details from xpcrmodule_history_data.
        records: list[dict] = xpcrmodule_history_data["runSetReviewAssignmentDetails"]

        # Provide a map that will deterimine which columns to retrieve from the runset_details_data as well as what they will be called in the end dataframe.
        column_map = {
            "id": "RunSetReviewId",
            "runSetId": "RunSetId",
            "assignedDate": "Assigned On",
            "completedDate": "Completed On",
            "groupName": "Group",
            "qualificationProtocol": "Protocol",
        }

        return get_dash_ag_grid_from_records(
            records=records,
            column_map=column_map,
            date_columns=["Assigned On", "Completed On"],
        )

    @app.callback(
        Output("issues-table", "rowData"),
        Output("issues-table", "columnDefs"),
        Input("xpcrmodule-history-data", "data"),
    )
    def get_issues_table(
        xpcrmodule_history_data: dict,
    ) -> tuple[list[dict], list[dict]]:
        """
        A server-side callback used to retrieve the details of Issues associated with an XPCR Module and return these to a Dash AG Grid component
        """

        # Extract the runset_details from xpcrmodule_history_data.
        records: list[dict] = xpcrmodule_history_data["issueDetails"]

        # Provide a map that will deterimine which columns to retrieve from the runset_details_data as well as what they will be called in the end dataframe.
        column_map = {
            "id": "IssueId",
            "level": "Level",
            "type": "Type",
            "assayChannel": "Channel",
            "assignedDate": "Created Date",
            "closedDate": "Closed Date",
            "runSetReferrerId": "RunSetId",
            "runSetResolverId": "RunSetClosedId",
        }

        return get_dash_ag_grid_from_records(records=records, column_map=column_map)

    @app.callback(
        Output("remediation-actions-table", "rowData"),
        Output("remediation-actions-table", "columnDefs"),
        Input("xpcrmodule-history-data", "data"),
    )
    def get_remediation_action_table(
        xpcrmodule_history_data: dict,
    ) -> tuple[list[dict], list[dict]]:
        """
        A server-side callback used to retrieve the details of RemediationActions associated with an XPCR Module and return these to a Dash AG Grid component
        """

        # Extract the runset_details from xpcrmodule_history_data.
        records: list[dict] = xpcrmodule_history_data["remediationActionsDetails"]

        # Provide a map that will deterimine which columns to retrieve from the runset_details_data as well as what they will be called in the end dataframe.
        column_map = {
            "id": "RemediationActionId",
            "type": "Type",
            "status": "Status",
            "Assignee": "Created By",
            "assignedDate": "Assigned Date",
            "closedDate": "Closed Date",
            "runSetReferrerId": "RunSetId",
            "runSetResolverId": "RunSetClosedId",
        }

        return get_dash_ag_grid_from_records(
            records=records,
            column_map=column_map,
        )

    @app.callback(
        Output("files-table", "rowData"),
        Output("files-table", "columnDefs"),
        Input("xpcrmodule-history-data", "data"),
    )
    def get_files_table(
        xpcrmodule_history_data: dict,
    ) -> tuple[list[dict], list[dict]]:
        """
        A server-side callback used to retrieve the details of Files associated with an XPCR Module and return these to a Dash AG Grid component
        """

        # Extract the runset_details from xpcrmodule_history_data.
        records: list[dict] = xpcrmodule_history_data["fileDetails"]

        # Provide a map that will deterimine which columns to retrieve from the runset_details_data as well as what they will be called in the end dataframe.
        column_map = {
            "id": "FileId",
            "type": "Type",
            "name": "Name",
            "addedBy": "Added By",
            "addedOn": "Date Uploaded",
            "uri": "uri",
            "runSetId": "RunSetId",
        }

        return get_dash_ag_grid_from_records(
            records=records,
            column_map=column_map,
            hide_columns=["FileId", "uri", "RunSetId"],
        )
