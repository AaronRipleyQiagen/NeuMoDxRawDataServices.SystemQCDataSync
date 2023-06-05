from .dependencies import *


def get_tadm_picture_callbacks(app):
    @app.callback(
        Output("tadm-images", "items"),
        Input("tadm-pictures-table", "selectionChanged"),
        Input("tadm-pictures-table", "rowData"),
    )
    def get_tadm_pictures(selection, data):
        if ctx.triggered_id == "tadm-pictures-table" and data:
            items = []
            item = add_item_to_carousel(
                title="Some ID",
                description="Some Photo",
                container_name="neumodxsystemqc-tadmpictures",
                blob_name=selection[0]["FileId"],
            )
            items.append(item)
            return items

        return []

    @app.callback(
        Output("upload-tadm-message", "children"),
        Output("upload-tadm-response", "is_open"),
        Input("upload-tadm-pictures", "contents"),
        State("upload-tadm-pictures", "filename"),
        State("runset-selection-data", "data"),
        State("runset-review", "data"),
        State("upload-tadm-response", "is_open"),
    )
    def upload_tadm_image_to_blob_storage(
        list_of_contents, list_of_filenames, runset_selection, runset_review, is_open
    ):
        if list_of_contents:
            files = {
                list_of_filenames[i]: list_of_contents[i]
                for i in range(len(list_of_filenames))
            }
            upload_status = []
            for file in files:
                """
                Upload file to blob storage
                """
                content_type, content_string = files[file].split(",")
                file_content = base64.b64decode(content_string)
                file_id = str(uuid.uuid4()) + ".jpg"
                file_url = save_uploaded_file_to_blob_storage(
                    file_content, file_id, "neumodxsystemqc-tadmpictures"
                )
                """
              Create Database Entry
              """
                file_payload = {
                    "userId": session["user"].id,
                    "runSetId": runset_selection["id"],
                    "runSetReviewId": runset_review["id"],
                    "uri": file_url,
                    "name": file,
                    "fileid": file_id,
                }
                tadm_picture_url = os.environ["RUN_REVIEW_API_BASE"] + "TADMPictures"
                resp = requests.post(
                    url=tadm_picture_url, json=file_payload, verify=False
                )
                upload_status.append(html.Li(file))
            # Return a message with the URL of the uploaded file
            return upload_status, not is_open

        else:
            return no_update

    @app.callback(
        Output("tadm-pictures-table", "rowData"),
        Output("tadm-pictures-table", "columnDefs"),
        Input("review-tabs", "active_tab"),
        Input("upload-tadm-message", "children"),
        Input("delete-tadm-picture-response", "is_open"),
        Input("update-tadm-run-confirmation", "is_open"),
        State("runset-selection-data", "data"),
        State("runset-subject-ids", "data"),
        State("runset-subject-descriptions", "data"),
    )
    def get_tadm_picture_table(
        active_tab,
        message_children,
        delete_response_is_open,
        update_run_response_is_open,
        runset_data,
        runset_subject_ids,
        runset_subject_descriptions,
    ):
        if (
            (ctx.triggered_id == "upload-tadm-message")
            or ctx.triggered_id == "review-tabs"
            or (
                ctx.triggered_id == "delete-tadm-picture-response"
                and delete_response_is_open == True
            )
            or (
                ctx.triggered_id == "update-tadm-run-confirmation"
                and update_run_response_is_open == True
            )
        ) and active_tab == "tadm-pictures":
            """
            Get TADM Picture Info from API
            """
            tadm_pictures_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSets/{}/tadmpictures".format(runset_data["id"])
            runset = requests.get(tadm_pictures_url, verify=False).json()
            """
          Extract Details from each TADM Picture into pandas DataFrame
          """
            tadm_picture_data = pd.DataFrame(
                columns=[
                    "Id",
                    "FileId",
                    "File Name",
                    "Uploaded By",
                    "Upload Date",
                    "Run Number",
                    "UserId",
                ]
            )

            idx = 0
            runset_tadm_ids = runset_subject_ids["Cartridge"]
            runset_run_descriptions = runset_subject_descriptions["Run"]

            for tadm_picture in runset["tadmPictures"]:
                entry = {}
                entry["Id"] = tadm_picture["id"]
                entry["UserId"] = tadm_picture["validFromUser"]
                entry["FileId"] = tadm_picture["fileid"]
                entry["File Name"] = tadm_picture["name"]
                entry["Uploaded By"] = tadm_picture["runSetReview"]["reviewerName"]
                entry["Upload Date"] = tadm_picture["validFrom"]

                if tadm_picture["cartridgeId"]:
                    tadm_id = tadm_picture["cartridgeId"]
                    runset_tadm_id = [
                        key for key, val in runset_tadm_ids.items() if val == tadm_id
                    ][0]
                    run_number = runset_run_descriptions[runset_tadm_id]
                    entry["Run Number"] = run_number
                else:
                    entry["Run Number"] = tadm_picture["cartridgeId"]

                tadm_picture_data.loc[idx] = entry
                idx += 1

            """
          Create Column Definitions for Table
          """

            column_definitions = []
            initial_selection = [x for x in tadm_picture_data.columns if "Id" not in x]

            for column in tadm_picture_data.columns:
                column_definition = {
                    "headerName": column,
                    "field": column,
                    "filter": True,
                    "sortable": True,
                }
                if column not in initial_selection:
                    column_definition["hide"] = True

                if "Date" in column:
                    tadm_picture_data[column] = (
                        tadm_picture_data[column]
                        .astype("datetime64")
                        .dt.strftime("%d %B %Y %H:%M:%S")
                    )

                column_definitions.append(column_definition)

            return tadm_picture_data.to_dict(orient="records"), column_definitions
        return no_update

    @app.callback(
        Output("delete-tadm-picture-button", "disabled"),
        Input("tadm-pictures-table", "selectionChanged"),
    )
    def check_tadm_delete_validity(selection):
        if ctx.triggered_id == "tadm-pictures-table":
            if selection[0]["UserId"] == session["user"].id:
                return False

        return True

    @app.callback(
        Output("update-tadm-run-button", "disabled"),
        Input("tadm-pictures-table", "selectionChanged"),
    )
    def check_tadm_run_update_validity(selection):
        if ctx.triggered_id == "tadm-pictures-table":
            if selection[0]:
                return False

        return True

    @app.callback(
        Output("update-tadm-run-selection", "is_open"),
        Output("update-tadm-run-options", "options"),
        Output("update-tadm-run-options", "value"),
        Input("update-tadm-run-button", "n_clicks"),
        Input("update-tadm-run-submit", "n_clicks"),
        Input("update-tadm-run-cancel", "n_clicks"),
        State("update-tadm-run-selection", "is_open"),
        State("runset-subject-descriptions", "data"),
        State("runset-subject-ids", "data"),
    )
    def control_update_tadm_run_selection_popup(
        update_click,
        submit_click,
        cancel_click,
        is_open,
        runset_subject_descriptions,
        runset_subject_ids,
    ):
        runset_tadm_descriptions = runset_subject_descriptions["Run"]
        runset_tadm_ids = runset_subject_ids["Cartridge"]
        run_options = {}

        for runset_tadm_id in runset_tadm_ids:
            run_options[runset_tadm_ids[runset_tadm_id]] = runset_tadm_descriptions[
                runset_tadm_id
            ]

        if ctx.triggered_id:
            return (not is_open, run_options, [x for x in run_options][0])
        else:
            return is_open, run_options, [x for x in run_options][0]

    @app.callback(
        Output("update-tadm-run-confirmation", "is_open"),
        Output("update-tadm-run-message", "children"),
        Input("update-tadm-run-submit", "n_clicks"),
        State("update-tadm-run-options", "value"),
        State("tadm-pictures-table", "selectionChanged"),
        State("update-tadm-run-confirmation", "is_open"),
    )
    def update_tadm_run(submit_button, cartridge_id, rowSelection, is_open):
        confirmation_message = ""

        if ctx.triggered_id:
            update_tadm_picture_run_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "TADMPictures/{}/cartridge".format(rowSelection[0]["Id"])
            query_params = {"cartridgeid": cartridge_id}
            response = requests.put(
                url=update_tadm_picture_run_url, params=query_params, verify=False
            )

            if response.status_code == 200:
                confirmation_message = "Run for TADM Picture was successfully updated."
            else:
                confirmation_message = (
                    "Run for TADM Picture was not successful updated."
                )

            return (not is_open, confirmation_message)

        else:
            return is_open, confirmation_message

    @app.callback(
        Output("delete-tadm-picture-confirmation", "is_open"),
        Input("delete-tadm-picture-button", "n_clicks"),
        Input("delete-tadm-picture-confirm", "n_clicks"),
        Input("delete-tadm-picture-cancel", "n_clicks"),
        State("delete-tadm-picture-confirmation", "is_open"),
        prevent_intitial_call=True,
    )
    def control_delete_tadm_picture_popup(
        delete_click, confirm_click, cancel_click, is_open
    ):
        if ctx.triggered_id and "delete" in ctx.triggered_id:
            return not is_open
        return is_open

    @app.callback(
        Output("delete-tadm-picture-response", "is_open"),
        Input("delete-tadm-picture-confirm", "n_clicks"),
        State("tadm-pictures-table", "selectionChanged"),
        State("delete-tadm-picture-response", "is_open"),
    )
    def delete_tadm_picture(confirm_click, selection, is_open):
        if ctx.triggered_id == "delete-tadm-picture-confirm":
            delete_tadm_picture_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "tadmpictures/{}".format(selection[0]["Id"])
            print(delete_tadm_picture_url)
            response = requests.delete(url=delete_tadm_picture_url, verify=False)
            print("TADM Picture Delete Status Code: ", response.status_code)

            return not is_open
        else:
            return is_open
