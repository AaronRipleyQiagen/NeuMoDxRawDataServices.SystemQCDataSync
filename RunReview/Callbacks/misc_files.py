from .dependencies import *


def get_misc_file_callbacks(app):
    @app.callback(
        Output("file-upload-response", "is_open"),
        Input("misc-file-upload-button", "contents"),
        Input("file-upload-response-close-button", "n_clicks"),
        State("misc-file-upload-button", "filename"),
        State("runset-selection-data", "data"),
        State("runset-review", "data"),
        State("file-upload-response", "is_open"),
        prevent_intial_call=True,
    )
    def upload_misc_file_to_blob_storage(
        list_of_contents,
        n_clicks,
        list_of_filenames,
        runset_selection,
        runset_review,
        is_open,
    ):
        if ctx.triggered_id == "misc-file-upload-button" and list_of_contents:
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
                file_id = str(uuid.uuid4()) + file[file.rfind(".") :]
                file_url = save_uploaded_file_to_blob_storage(
                    file_content, file_id, "neumodxsystemqc-miscellaneousfiles"
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

                misc_file_url = os.environ["RUN_REVIEW_API_BASE"] + "MiscellaneousFiles"
                print(file_payload)
                resp = requests.post(url=misc_file_url, json=file_payload, verify=False)
                print(resp.status_code)

            # Return a message with the URL of the uploaded file
            return not is_open

        elif ctx.triggered_id == "file-upload-response-close-button" and n_clicks:
            return not is_open
        else:
            return is_open

    @app.callback(
        Output("misc-files-table", "rowData"),
        Output("misc-files-table", "columnDefs"),
        Input("review-tabs", "active_tab"),
        Input("file-upload-response", "is_open"),
        Input("delete-misc-file-response", "is_open"),
        State("runset-selection-data", "data"),
    )
    def get_misc_files(
        active_tab, upload_response_is_open, delete_response_is_open, runset_data
    ):
        if (
            (
                ctx.triggered_id == "file-upload-response"
                and upload_response_is_open == False
            )
            or (
                ctx.triggered_id == "delete-misc-file-response"
                and delete_response_is_open == False
            )
            or ctx.triggered_id == "review-tabs"
        ) and active_tab == "misc-files":
            """
            Get Misc file Info from API
            """
            misc_files_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSets/{}/miscellaneousfiles".format(runset_data["id"])
            runset = requests.get(misc_files_url, verify=False).json()

            """
            Extract Details from each Misc File into pandas DataFrame
            """

            misc_file_data = pd.DataFrame(
                columns=[
                    "Id",
                    "FileId",
                    "File Name",
                    "Uploaded By",
                    "Upload Date",
                    "UserId",
                ]
            )

            idx = 0
            for misc_file in runset["miscellaneousFiles"]:
                entry = {}
                entry["Id"] = misc_file["id"]
                entry["FileId"] = misc_file["fileid"]
                entry["File Name"] = misc_file["name"]
                entry["Uploaded By"] = misc_file["runSetReview"]["reviewerName"]
                entry["Upload Date"] = misc_file["validFrom"]
                entry["UserId"] = misc_file["validFromUser"]

                misc_file_data.loc[idx] = entry
                idx += 1

            """
            Create Column Definitions for Table
            """

            column_definitions = []
            initial_selection = [x for x in misc_file_data.columns if "Id" not in x]

            for column in misc_file_data.columns:
                column_definition = {
                    "headerName": column,
                    "field": column,
                    "filter": True,
                    "sortable": True,
                }
                if column not in initial_selection:
                    column_definition["hide"] = True

                if "Date" in column:
                    misc_file_data[column] = (
                        misc_file_data[column]
                        .astype("datetime64")
                        .dt.strftime("%d %B %Y %H:%M:%S")
                    )

                column_definitions.append(column_definition)

            return misc_file_data.to_dict(orient="records"), column_definitions
        return no_update

    @app.callback(
        Output("misc-file-download", "data"),
        Input("misc-file-download-button", "n_clicks"),
        State("misc-files-table", "selectionChanged"),
    )
    def download_misc_file(n_clicks, misc_file_selection):
        if ctx.triggered_id == "misc-file-download-button" and n_clicks:
            print("doing this...")
            print(misc_file_selection)
            file_data = download_file(
                misc_file_selection[0]["FileId"], "neumodxsystemqc-miscellaneousfiles"
            )
            print("got file data.")
            return dict(
                content=file_data,
                filename=misc_file_selection[0]["File Name"],
                base64=True,
            )
        return no_update

    """
    Callbacks related to deleting a misc file.
    """

    @app.callback(
        Output("delete-misc-file-button", "disabled"),
        Input("misc-files-table", "selectionChanged"),
    )
    def check_misc_file_delete_validity(selection):
        if ctx.triggered_id == "misc-files-table":
            if selection[0]["UserId"] == session["user"].id:
                return False

        return True

    @app.callback(
        Output("delete-misc-file-confirmation", "is_open"),
        Input("delete-misc-file-button", "n_clicks"),
        Input("delete-misc-file-confirm", "n_clicks"),
        Input("delete-misc-file-cancel", "n_clicks"),
        State("delete-misc-file-confirmation", "is_open"),
        prevent_intitial_call=True,
    )
    def control_delete_cartridge_picture_popup(
        delete_click, confirm_click, cancel_click, is_open
    ):
        if ctx.triggered_id and "delete" in ctx.triggered_id:
            return not is_open
        return is_open

    @app.callback(
        Output("delete-misc-file-response", "is_open"),
        Input("delete-misc-file-confirm", "n_clicks"),
        State("misc-files-table", "selectionChanged"),
        State("delete-misc-file-response", "is_open"),
    )
    def delete_cartridge_picture(confirm_click, selection, is_open):
        if ctx.triggered_id == "delete-misc-file-confirm":
            delete_cartridge_picture_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "miscellaneousfiles/{}".format(selection[0]["Id"])
            print(delete_cartridge_picture_url)
            response = requests.delete(url=delete_cartridge_picture_url, verify=False)
            print("Cartridge Picture Delete Status Code: ", response.status_code)

            return not is_open
        else:
            return is_open
