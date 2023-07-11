from .dependencies import *

"""
Callback used to update data related pcr data (curves & summaries)
"""


def get_pcr_data_callbacks(app):
    @app.callback(
        Output("run-review-curves", "figure"),
        Output("runset-sample-results", "rowData"),
        Output("runset-sample-results", "columnDefs"),
        Output("pcrcurve-sample-info", "data"),
        Input("channel-selected", "data"),
        Input("run-review-process-step-selector", "value"),
        Input("run-review-color-selector", "value"),
        State("runset-sample-data", "data"),
        State("runset-selection-data", "data"),
        State("runset-channel-options", "data"),
        Input("xpcrmodulelane-selected", "data"),
        Input("run-option-selected", "data"),
        Input("issue-selected", "data"),
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
        if issue_selected or channel_selected or channel_options:
            if ctx.triggered_id == "issue-selected" and issue_selected:
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
                    elif issue_selected["Level"] == "XPCR Module":
                        df_Channel = df_Channel[
                            df_Channel["XPCRModuleId"] == issue_selected["SubjectId"]
                        ]

            else:
                if channel_selected == "":
                    return no_update
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
            df_Channel_Step = df_Channel_Step[
                df_Channel_Step["Overall Result"] != "NoResult"
            ]

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

            """
            Move N500 Serial Number to front.
            """
            columns = df_Channel_Step.columns.tolist()
            columns.remove("N500 Serial Number")
            new_columns = ["N500 Serial Number"] + columns

            df_Channel_Step = df_Channel_Step[new_columns]
            inital_selection = [
                "N500 Serial Number",
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
        else:
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
                    run_summary_df["Baseline Std"] / run_summary_df["Baseline Mean"]
                )

                initial_selection = [
                    "XPCR Module Serial",
                    "XPCR Module Lane",
                    "Run",
                    "Baseline Mean",
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
                run_summary_df_overall.set_index("Run", append=True, inplace=True)
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
    def download_pcr_data(n, data, runset_selection):
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
        Output(
            SampleExclusionControls.ids.sample_id(
                "run-review-add-sample-exclusion-result"
            ),
            "data",
        ),
        Input("runset-sample-results", "selectionChanged"),
    )
    def update_sample_exclusion_control_sample_id(selection: list[dict]):
        """
        A server-side callback that updates the sample_id component for the SampleExclusionController associated with run-review page.
        """
        return selection[0]["SampleId"]
