from .dependencies import *
import app_config


def get_initialization_callbacks(app):
    @app.callback(
        Output("run-review-url", "href"),
        Input("get-runset-data", "n_clicks"),
        State("review-queue-table", "selectionChanged"),
        prevent_intial_call=True,
    )
    def get_runset_url(view_runset_click, rowSelection):
        if ctx.triggered_id:
            return "/dashboard/run-review/view-results/{}".format(rowSelection[0]["Id"])
        else:
            return no_update

    @app.callback(Output("runset-id", "data"), Input("url", "href"))
    def get_runset_id(url):
        guid = url.split("/")[-1]
        return guid

    @app.callback(
        Output("runset-selection-data", "data"),
        [Input("runset-id", "data")],
        prevent_intial_call=True,
    )
    def get_runset_selection_data(runsetid):
        if runsetid:
            runsetsample_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSets/{}/Samples".format(runsetid)
            _runset_samples = requests.get(runsetsample_url, verify=False).json()
            return _runset_samples
        else:
            return no_update

    @app.callback(
        [
            Output("runset-sample-data", "data"),
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
        Input("runset-selection-data", "data"),
        prevent_intial_call=True,
    )
    def initialize_runset_data(runset_data):
        logging.info("initializing runset_data")
        """
        Get Data associated with Runset.
        """
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
            runset_sample_ids.append(runsetsample["sample"]["rawDataDatabaseId"])

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

        runset_map_df.set_index("RawDataDatabaseId", inplace=True)
        sample_data = getSampleDataAsync(runset_sample_ids)

        jsonReader = SampleJSONReader(json.dumps(sample_data))
        jsonReader.standardDecode()
        dataframe = jsonReader.DataFrame
        dataframe["RawDataDatabaseId"] = dataframe.reset_index()["id"].values
        dataframe["Channel"] = dataframe["Channel"].replace("Far_Red", "Far Red")
        dataframe["XPCR Module Side"] = np.where(
            dataframe["XPCR Module Lane"] < 7, "Right", "Left"
        )
        dataframe = (
            dataframe.set_index("RawDataDatabaseId").join(runset_map_df).reset_index()
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
        runset_update_response = requests.put(url=runset_update_url, verify=False)

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
        runset_neumodx_descriptions = {}
        for idx in dataframe.drop_duplicates(
            subset=["RunSetNeuMoDxSystemId", "NeuMoDxSystemId"]
        ).index:
            runset_neumodx_subject_ids_dict[
                dataframe.loc[idx, "RunSetNeuMoDxSystemId"]
            ] = dataframe.loc[idx, "NeuMoDxSystemId"]
            runset_neumodx_descriptions[
                dataframe.loc[idx, "RunSetNeuMoDxSystemId"]
            ] = dataframe.loc[idx, "N500 Serial Number"]

        runset_subject_ids["NeuMoDxSystem"] = runset_neumodx_subject_ids_dict
        runset_subject_descriptions["NeuMoDxSystem"] = runset_neumodx_descriptions
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

        return (
            dataframe.to_dict("records"),
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
        [Output("runset-description", "children"), Output("related-runsets", "data")],
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
            xpcrmodule = requests.get(url=xpcrmodule_runsets_url, verify=False).json()

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
                + str(runset_selection["number"]),
                related_xpcrmodule_runsets,
            )

        else:
            return no_update

    @app.callback(
        Output("runset-creator-name", "children"),
        Input("runset-selection-data", "data"),
    )
    def get_runset_creator_details(runset_data):
        if ctx.triggered_id == "runset-selection-data":
            tenant_id = app_config.TENANT_ID
            client_id = app_config.CLIENT_ID
            client_secret = app_config.CLIENT_SECRET
            user_id = runset_data["validFromUser"]
            token_url = (
                f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
            )

            # Set the token request parameters
            token_data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "https://graph.microsoft.com/.default",
            }

            # Request the access token
            response = requests.post(token_url, data=token_data)

            # Check if the request was successful
            if response.status_code == 200:
                access_token = response.json().get("access_token")

                # Construct the endpoint URL
                endpoint = f"https://graph.microsoft.com/v1.0/users/{user_id}"

                # Set the headers with the access token
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                }

                # Send the request to retrieve user details
                response = requests.get(endpoint, headers=headers)

                # Check if the request was successful
                if response.status_code == 200:
                    user_data = response.json()
                    first_name = user_data.get("displayName")
                    last_name = user_data.get("surname")
                else:
                    print(f"Error: {response.status_code} - {response.text}")
            else:
                print(f"Access Token Error: {response.status_code} - {response.text}")
            return f"Runset created by: {first_name} {last_name}"
        else:
            return no_update

    @app.callback(
        Output("runset-system-description", "children"),
        Input("runset-subject-descriptions", "data"),
    )
    def get_runset_neumodx_system_details(runset_subject_descriptions):
        neumodx_system_list = [
            runset_subject_descriptions["NeuMoDxSystem"][x]
            for x in runset_subject_descriptions["NeuMoDxSystem"]
        ]
        neumodx_system_details_string = "Processed on: "

        ## Append each system in neumodx system list to details string.
        for neumodx_system in neumodx_system_list:
            neumodx_system_details_string = (
                neumodx_system_details_string + neumodx_system + ", "
            )

        ## Remove trailing ", "
        neumodx_system_details_string = neumodx_system_details_string[:-2]

        return neumodx_system_details_string
