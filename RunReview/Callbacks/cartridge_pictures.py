from .dependencies import *


def get_cartridge_picture_callbacks(app):
    @app.callback(
        Output("cartridge-images", "items"),
        Input("cartridge-pictures-table", "selectionChanged"),
        Input("cartridge-pictures-table", "rowData"),
    )
    def get_cartridge_pictures(selection, data):
        if ctx.triggered_id == "cartridge-pictures-table" and selection:
            items = []
            item = add_item_to_carousel(
                title="Some ID",
                description="Some Photo",
                container_name="neumodxsystemqc-cartridgepictures",
                blob_name=selection[0]["FileId"],
            )
            items.append(item)
            return items

        return []

    @app.callback(
        Output("upload-cartridge-message", "children"),
        Output("upload-cartridge-response", "is_open"),
        Input("upload-cartridge-pictures", "contents"),
        State("upload-cartridge-pictures", "filename"),
        State("runset-selection-data", "data"),
        State("runset-review", "data"),
        State("upload-cartridge-response", "is_open"),
    )
    def upload_cartridge_image_to_blob_storage(
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
                    file_content, file_id, "neumodxsystemqc-cartridgepictures"
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
                cartridge_picture_url = (
                    os.environ["RUN_REVIEW_API_BASE"] + "CartridgePictures"
                )
                resp = requests.post(
                    url=cartridge_picture_url, json=file_payload, verify=False
                )
                upload_status.append(html.Li(file))
            # Return a message with the URL of the uploaded file
            return upload_status, not is_open

        else:
            return no_update

    @app.callback(
        Output("cartridge-pictures-table", "rowData"),
        Output("cartridge-pictures-table", "columnDefs"),
        Input("review-tabs", "active_tab"),
        Input("upload-cartridge-message", "children"),
        Input("delete-cartridge-picture-response", "is_open"),
        Input("update-cartridge-run-confirmation", "is_open"),
        State("runset-selection-data", "data"),
        State("runset-subject-ids", "data"),
        State("runset-subject-descriptions", "data"),
    )
    def get_cartridge_picture_table(
        active_tab,
        message_children,
        delete_response_is_open,
        update_run_response_is_open,
        runset_data,
        runset_subject_ids,
        runset_subject_descriptions,
    ):
        if (
            (ctx.triggered_id == "upload-cartridge-message")
            or ctx.triggered_id == "review-tabs"
            or (
                ctx.triggered_id == "delete-cartridge-picture-response"
                and delete_response_is_open == True
            )
            or (
                ctx.triggered_id == "update-cartridge-run-confirmation"
                and update_run_response_is_open == True
            )
        ) and active_tab == "cartidge-pictures":
            """
            Get Cartridge Picture Info from API
            """
            cartridge_pictures_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSets/{}/cartridgepictures".format(runset_data["id"])
            runset = requests.get(cartridge_pictures_url, verify=False).json()
            """
          Extract Details from each Cartridge Picture into pandas DataFrame
          """
            cartridge_picture_data = pd.DataFrame(
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
            runset_cartridge_ids = runset_subject_ids["Cartridge"]
            runset_run_descriptions = runset_subject_descriptions["Run"]

            for cartridge_picture in runset["cartridgePictures"]:
                entry = {}
                entry["Id"] = cartridge_picture["id"]
                entry["UserId"] = cartridge_picture["validFromUser"]
                entry["FileId"] = cartridge_picture["fileid"]
                entry["File Name"] = cartridge_picture["name"]
                entry["Uploaded By"] = cartridge_picture["runSetReview"]["reviewerName"]
                entry["Upload Date"] = cartridge_picture["validFrom"]

                if cartridge_picture["cartridgeId"]:
                    cartridge_id = cartridge_picture["cartridgeId"]
                    runset_cartridge_id = [
                        key
                        for key, val in runset_cartridge_ids.items()
                        if val == cartridge_id
                    ][0]
                    run_number = runset_run_descriptions[runset_cartridge_id]
                    entry["Run Number"] = run_number
                else:
                    entry["Run Number"] = cartridge_picture["cartridgeId"]

                cartridge_picture_data.loc[idx] = entry
                idx += 1

            """
          Create Column Definitions for Table
          """

            column_definitions = []
            initial_selection = [
                x for x in cartridge_picture_data.columns if "Id" not in x
            ]

            for column in cartridge_picture_data.columns:
                column_definition = {
                    "headerName": column,
                    "field": column,
                    "filter": True,
                    "sortable": True,
                }
                if column not in initial_selection:
                    column_definition["hide"] = True

                if "Date" in column:
                    cartridge_picture_data[column] = (
                        cartridge_picture_data[column]
                        .astype("datetime64")
                        .dt.strftime("%d %B %Y %H:%M:%S")
                    )

                column_definitions.append(column_definition)

            return cartridge_picture_data.to_dict(orient="records"), column_definitions
        return no_update

    @app.callback(
        Output("delete-cartridge-picture-button", "disabled"),
        Input("cartridge-pictures-table", "selectionChanged"),
    )
    def check_cartridge_delete_validity(selection):
        if ctx.triggered_id == "cartridge-pictures-table":
            if selection[0]["UserId"] == session["user"].id:
                return False

        return True

    @app.callback(
        Output("update-cartridge-run-button", "disabled"),
        Input("cartridge-pictures-table", "selectionChanged"),
    )
    def check_cartridge_run_update_validity(selection):
        if ctx.triggered_id == "cartridge-pictures-table":
            if selection[0]:
                return False

        return True

    @app.callback(
        Output("update-cartridge-run-selection", "is_open"),
        Output("update-cartridge-run-options", "options"),
        Output("update-cartridge-run-options", "value"),
        Input("update-cartridge-run-button", "n_clicks"),
        Input("update-cartridge-run-submit", "n_clicks"),
        Input("update-cartridge-run-cancel", "n_clicks"),
        State("update-cartridge-run-selection", "is_open"),
        State("runset-subject-descriptions", "data"),
        State("runset-subject-ids", "data"),
    )
    def control_update_cartridge_run_selection_popup(
        update_click,
        submit_click,
        cancel_click,
        is_open,
        runset_subject_descriptions,
        runset_subject_ids,
    ):
        runset_cartridge_descriptions = runset_subject_descriptions["Run"]
        runset_cartridge_ids = runset_subject_ids["Cartridge"]
        cartridge_options = {}

        for runset_cartridge_id in runset_cartridge_ids:
            cartridge_options[
                runset_cartridge_ids[runset_cartridge_id]
            ] = runset_cartridge_descriptions[runset_cartridge_id]

        if ctx.triggered_id:
            return (not is_open, cartridge_options, [x for x in cartridge_options][0])
        else:
            return is_open, cartridge_options, [x for x in cartridge_options][0]

    @app.callback(
        Output("update-cartridge-run-confirmation", "is_open"),
        Output("update-cartridge-run-message", "children"),
        Input("update-cartridge-run-submit", "n_clicks"),
        State("update-cartridge-run-options", "value"),
        State("cartridge-pictures-table", "selectionChanged"),
        State("update-cartridge-run-confirmation", "is_open"),
    )
    def update_cartridge_run(submit_button, cartridge_id, rowSelection, is_open):
        confirmation_message = ""

        if ctx.triggered_id:
            update_cartridge_picture_run_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "CartridgePictures/{}/cartridge".format(rowSelection[0]["Id"])
            query_params = {"cartridgeid": cartridge_id}
            response = requests.put(
                url=update_cartridge_picture_run_url, params=query_params, verify=False
            )

            if response.status_code == 200:
                confirmation_message = (
                    "Run for Cartridge Picture was successfully updated."
                )
            else:
                confirmation_message = (
                    "Run for Cartridge Picture was not successful updated."
                )

            return (not is_open, confirmation_message)

        else:
            return is_open, confirmation_message

    @app.callback(
        Output("delete-cartridge-picture-confirmation", "is_open"),
        Input("delete-cartridge-picture-button", "n_clicks"),
        Input("delete-cartridge-picture-confirm", "n_clicks"),
        Input("delete-cartridge-picture-cancel", "n_clicks"),
        State("delete-cartridge-picture-confirmation", "is_open"),
        prevent_intitial_call=True,
    )
    def control_delete_cartridge_picture_popup(
        delete_click, confirm_click, cancel_click, is_open
    ):
        if ctx.triggered_id and "delete" in ctx.triggered_id:
            return not is_open
        return is_open

    @app.callback(
        Output("delete-cartridge-picture-response", "is_open"),
        Input("delete-cartridge-picture-confirm", "n_clicks"),
        State("cartridge-pictures-table", "selectionChanged"),
        State("delete-cartridge-picture-response", "is_open"),
    )
    def delete_cartridge_picture(confirm_click, selection, is_open):
        if ctx.triggered_id == "delete-cartridge-picture-confirm":
            delete_cartridge_picture_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "cartridgepictures/{}".format(selection[0]["Id"])
            print(delete_cartridge_picture_url)
            response = requests.delete(url=delete_cartridge_picture_url, verify=False)
            print("Cartridge Picture Delete Status Code: ", response.status_code)

            return not is_open
        else:
            return is_open
