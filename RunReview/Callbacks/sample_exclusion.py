from .dependencies import *


def get_sample_exclusion_callbacks(app):
    @app.callback(
        Output(
            AddSampleExclusionButton.ids.runset_id(
                "run-review-add-sample-exclusion-button"
            ),
            "data",
        ),
        Input("runset-id", "data"),
    )
    def update_sample_exclusion_control_runset_id(runset_id: str):
        """
        A server-side callback that updates the runset_id component for the SampleExclusionController associated with run-review page.
        """
        return runset_id

    @app.callback(
        Output(
            AddSampleExclusionButton.ids.runset_review_id(
                "run-review-add-sample-exclusion-button"
            ),
            "data",
        ),
        Input("runset-review", "data"),
    )
    def update_sample_exclusion_control_runset_review_id(runset_review: dict):
        """
        A server-side callback that updates the runset_review_id component for the SampleExclusionController associated with run-review page.
        """
        return runset_review["id"]

    @app.callback(
        Output(
            AddSampleExclusionButton.ids.user_id(
                "run-review-add-sample-exclusion-button"
            ),
            "data",
        ),
        Input("runset-review", "data"),
    )
    def update_sample_exclusion_control_user_id(runset_review: dict):
        """
        A server-side callback that updates the user_id component for the SampleExclusionController associated with run-review page.
        """
        return runset_review["validFromUser"]

    @app.callback(
        Output(
            AddSampleExclusionButton.ids.sample_id(
                "run-review-add-sample-exclusion-button"
            ),
            "data",
        ),
        Input("runset-sample-results", "selectionChanged"),
        prevent_initial_call=True,
    )
    def update_sample_exclusion_control_sample_id(selection: list[dict]):
        """
        A server-side callback that updates the sample_id component for the SampleExclusionController associated with run-review page.
        """
        if selection:
            return selection[0]["SampleId"]
        else:
            return no_update

    @app.callback(
        Output(
            ManageRunsetSampleExclusions.ids.runset_id(
                "run-review-manage-runset-sample-exclusions"
            ),
            "data",
        ),
        Input("runset-id", "data"),
        # prevent_initial_call=True,
    )
    def update_runset_sample_exclusions(runset_id: str):
        if runset_id:
            return runset_id
        else:
            return no_update

    @app.callback(
        Output(
            ManageRunsetSampleExclusions.ids.sample_details(
                "run-review-manage-runset-sample-exclusions"
            ),
            "data",
        ),
        Input("runset-sample-data", "data"),
    )
    def get_sample_details(runset_sample_data: list[dict]):
        if runset_sample_data:
            sample_details = pd.DataFrame.from_dict(runset_sample_data)
            sample_details.drop_duplicates(["SampleId"], inplace=True)
            sample_details.rename({"SampleId": "sampleId"}, axis=1, inplace=True)
            sample_details = sample_details[
                [
                    "sampleId",
                    "Sample ID",
                    "N500 Serial Number",
                    "XPCR Module Serial",
                    "XPCR Module Lane",
                    "Overall Result",
                ]
            ]

            return sample_details.to_dict(orient="records")

        else:
            return no_update

    @app.callback(
        Output(
            ManageRunsetSampleExclusions.ids.sample_exclusions(
                "run-review-manage-runset-sample-exclusions"
            ),
            "data",
            allow_duplicate=True,
        ),
        Input(
            PostResponse.ids.modal("run-review-add-sample-exclusion-button"), "is_open"
        ),
        State(
            ManageRunsetSampleExclusions.ids.runset_id(
                "run-review-manage-runset-sample-exclusions"
            ),
            "data",
        ),
        State(
            ManageRunsetSampleExclusions.ids.sample_details(
                "run-review-manage-runset-sample-exclusions"
            ),
            "data",
        ),
        prevent_initial_call=True,
    )
    def get_sample_exclusions(
        is_open: bool,
        runset_id: str,
        sample_details: list[dict],
    ):
        if runset_id and sample_details and not is_open:
            runset_sample_exclusions_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "Reports/RunSet/{}/SampleExclusionDetails".format(runset_id)

            sample_exclusion_results = pd.DataFrame(
                requests.get(url=runset_sample_exclusions_url).json()
            ).set_index("sampleId")

            if len(sample_exclusion_results) > 0:
                sample_details_frame = pd.DataFrame.from_dict(sample_details).set_index(
                    "sampleId"
                )
                sample_exclusion_results = sample_exclusion_results.join(
                    sample_details_frame
                )
                save_json_response(
                    sample_exclusion_results.to_dict(orient="records")[0],
                    "sample-exclusion-details.json",
                )

                return sample_exclusion_results.reset_index().to_dict(orient="records")
            else:
                return []
        else:
            return no_update
