from .dependencies import *
from flask_mail import Mail, Message


def get_runset_review_callbacks(app):
    @app.callback(
        Output("run-review-status-update-post-response", "is_open"),
        [
            Input("run-review-completed-button", "n_clicks"),
            State("run-review-status-update-post-response", "is_open"),
            State("runset-review", "data"),
            State("run-review-acceptance", "value"),
        ],
        prevent_intital_call=True,
    )
    def update_run_review_status(n, is_open, runset_review, run_review_acceptance):
        if n:
            runsetreview_update_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSetReviews/{}/status".format(runset_review["id"])
            query_params = {
                "acceptable": run_review_acceptance,
                "newStatusName": "Completed",
            }
            print(query_params)
            resp = requests.put(
                url=runsetreview_update_url, params=query_params, verify=False
            )

            runsetreview_update = resp.json()
            runset_update_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSets/{}/status".format(runsetreview_update["runSetId"])
            runset_update_response = requests.put(url=runset_update_url, verify=False)
            print("Runset Update Response: " + str(runset_update_response.status_code))
            return not is_open

        return is_open

    @app.callback(
        Output("runset-creator-name", "children"),
        Input("review-tabs", "active_tab"),
        State("runset-selection-data", "data"),
    )
    def get_runset_creator_details(active_tab, runset_data):
        if ctx.triggered_id == "review-tabs" and active_tab == "runset-reviews":
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
                    print(user_data)
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
        Output("runset-reviews-table", "rowData"),
        Output("runset-reviews-table", "columnDefs"),
        Input("review-tabs", "active_tab"),
        State("runset-selection-data", "data"),
    )
    def get_runset_reviews(active_tab, runset_data):
        if ctx.triggered_id == "review-tabs" and active_tab == "runset-reviews":
            runset_reviews_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSets/{}/runsetreviews".format(runset_data["id"])

            runset_reviews_response = requests.get(
                url=runset_reviews_url, verify=False
            ).json()

            runset_reviews_dataframe = pd.DataFrame(
                columns=[
                    "RunSetReviewId",
                    "Status",
                    "Reviewer Name",
                    "Reviewer Group",
                    "Accepted?",
                ]
            )

            print(runset_reviews_response)
            idx = 0
            for runset_review in runset_reviews_response["runSetReviews"]:
                runset_review_dict = {}
                runset_review_dict["RunSetReviewId"] = runset_review["id"]
                runset_review_dict["Status"] = runset_review["runSetReviewStatus"][
                    "name"
                ]
                runset_review_dict["Reviewer Name"] = runset_review["reviewerName"]
                runset_review_dict["Reviewer Group"] = runset_review["reviewGroup"][
                    "description"
                ]

                if runset_review["acceptable"] == False:
                    runset_review_dict["Accepted?"] = "No"
                elif runset_review["acceptable"] == True:
                    runset_review_dict["Accepted?"] = "Yes"
                else:
                    runset_review_dict["Accepted?"] = "N/A"
                runset_reviews_dataframe.loc[idx] = runset_review_dict
                idx += 1

            column_definitions = []
            initial_selection = [
                x for x in runset_reviews_dataframe.columns if "Id" not in x
            ]

            for column in runset_reviews_dataframe.columns:
                column_definition = {
                    "headerName": column,
                    "field": column,
                    "filter": True,
                    "sortable": True,
                }
                if column not in initial_selection:
                    column_definition["hide"] = True
                column_definitions.append(column_definition)

            return (
                runset_reviews_dataframe.to_dict(orient="records"),
                column_definitions,
            )

        return no_update

    @app.callback(
        Output("reviewgroup-selector-modal", "is_open"),
        Output("review-group-options", "options"),
        [
            Input("add-review-group-button", "n_clicks"),
            Input("submit-reviewgroup-selection-button", "n_clicks"),
        ],
        [State("reviewgroup-selector-modal", "is_open")],
        prevent_initial_call=True,
    )
    def open_reviewgroup_addition_modal(create_clicks, submit_clicks, is_open):
        if create_clicks or submit_clicks:
            """
            Get Review Groups
            """
            reviewgroup_options = {}
            reviewgroups_url = os.environ["RUN_REVIEW_API_BASE"] + "ReviewGroups"

            reviewgroups_response = requests.get(reviewgroups_url, verify=False).json()

            for reviewgroup in reviewgroups_response:
                if reviewgroup["description"] != "System QC Tech I":
                    reviewgroup_options[reviewgroup["id"]] = reviewgroup["description"]
            return not is_open, reviewgroup_options

        return is_open, {}

    @app.callback(
        Output("add-review-assignment-response", "is_open"),
        Input("submit-reviewgroup-selection-button", "n_clicks"),
        State("review-group-options", "value"),
        State("review-group-options", "options"),
        State("runset-selection-data", "data"),
        State("add-review-assignment-response", "is_open"),
        State("url", "href"),
        prevent_initial_call=True,
    )
    def add_runsetreviewassignments(
        submit_button,
        review_groups_selected,
        review_groups_dictionary,
        runset_data,
        post_response_is_open,
        url,
    ):
        if ctx.triggered_id == "submit-reviewgroup-selection-button":
            review_groups = []
            review_group_subscribers = {}
            for review_group_id in review_groups_selected:
                runsetreviewassignmenturl = (
                    os.environ["RUN_REVIEW_API_BASE"] + "RunSetReviewAssignments"
                )
                queryParams = {}
                queryParams["runsetid"] = runset_data["id"]
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

            runset_update_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSets/{}/status".format(runset_data["id"])
            runset_update_response = requests.put(url=runset_update_url, verify=False)
            print("Runset Update Response: " + str(runset_update_response.status_code))

            if os.environ["SEND_EMAILS"] == "Yes":
                send_review_ready_messages(
                    app, runset_data["id"], url, review_group_subscribers
                )
            return not post_response_is_open
        return post_response_is_open
