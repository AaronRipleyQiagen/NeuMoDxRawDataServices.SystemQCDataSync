from .dependencies import *


def get_comment_callbacks(app):
    @app.callback(
        Output("comments-modal", "is_open"),
        Input("create-comment-button", "n_clicks"),
        Input("cancel-comment-button", "n_clicks"),
        Input("add-comment-button", "n_clicks"),
        State("comments-modal", "is_open"),
    )
    def open_comment_entry(create_click, cancel_click, add_click, is_open):
        if ctx.triggered_id in [
            "create-comment-button",
            "cancel-comment-button",
            "add-comment-button",
        ]:
            return not is_open
        return is_open

    @app.callback(
        Output("comments-post-response", "is_open"),
        Input("add-comment-button", "n_clicks"),
        State("comments-text", "value"),
        State("runset-review", "data"),
        State("comments-post-response", "is_open"),
    )
    def add_comment(add_click, entrytext, runset_review, is_open):
        if ctx.triggered_id == "add-comment-button":
            add_comment_url = os.environ["RUN_REVIEW_API_BASE"] + "Comments"
            add_comment_payload = {
                "entry": entrytext,
                "runsetReviewId": runset_review["id"],
                "userId": session["user"].id,
            }
            response_status_code = requests.post(
                url=add_comment_url, json=add_comment_payload, verify=False
            ).status_code
            return not is_open
        return is_open

    @app.callback(
        Output("comments-table", "rowData"),
        Output("comments-table", "columnDefs"),
        Input("review-tabs", "active_tab"),
        Input("comments-post-response", "is_open"),
        Input("comments-delete-response", "is_open"),
        State("runset-selection-data", "data"),
    )
    def get_comments(
        active_tab, post_response_is_open, delete_response_is_open, runset_data
    ):
        if (
            (ctx.triggered_id == "review-tabs" and active_tab == "runset-comments")
            or (
                ctx.triggered_id == "comments-post-response"
                and post_response_is_open == False
            )
            or (
                ctx.triggered_id == "comments-delete-response"
                and delete_response_is_open == False
            )
        ):
            # if True:
            """
            Get Comments for runset
            """
            get_runset_comments_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "RunSets/{}/Comments".format(runset_data["id"])

            runset = requests.get(get_runset_comments_url, verify=False).json()
            """
            Extract Details from each Misc File into pandas DataFrame
            """

            comment_data = pd.DataFrame(
                columns=[
                    "Entry",
                    "Added By",
                    "Added Date",
                    "CommentId",
                    "RunSetReviewId",
                ]
            )

            idx = 0
            for runset_review in runset["runSetReviews"]:
                if runset_review["comments"]:
                    for comment in runset_review["comments"]:
                        entry = {}
                        entry["CommentId"] = comment["id"]
                        entry["RunSetReviewId"] = runset_review["id"]
                        entry["Entry"] = comment["entry"]
                        entry["Added By"] = runset_review["reviewerName"]
                        entry["Added Date"] = comment["validFrom"]

                        comment_data.loc[idx] = entry
                        idx += 1

            """
            Create Column Definitions for Table
            """

            column_definitions = []
            initial_selection = [x for x in comment_data.columns if "Id" not in x]

            for column in comment_data.columns:
                column_definition = {
                    "headerName": column,
                    "field": column,
                    "filter": True,
                    "sortable": True,
                }
                if column not in initial_selection:
                    column_definition["hide"] = True

                if "Date" in column:
                    comment_data[column] = (
                        comment_data[column]
                        .astype("datetime64")
                        .dt.strftime("%d %B %Y %H:%M:%S")
                    )

                column_definitions.append(column_definition)

            return comment_data.to_dict(orient="records"), column_definitions
        return no_update

    """
    Callbacks related to deleting a comment.
    """

    @app.callback(
        Output("delete-comment-button", "disabled"),
        Input("comments-table", "selectionChanged"),
        State("runset-review", "data"),
    )
    def check_delete_comment_validity(selection, runset_review):
        if (
            ctx.triggered_id == "comments-table"
            and selection[0]["RunSetReviewId"] == runset_review["id"]
        ):
            return False
        return True

    @app.callback(
        Output("comments-delete-confirmation", "is_open"),
        Input("delete-comment-button", "n_clicks"),
        Input("confirm-comment-delete-button", "n_clicks"),
        Input("cancel-comment-delete-button", "n_clicks"),
        State("comments-delete-confirmation", "is_open"),
    )
    def confirm_comment_delete(delete_click, confirm_click, cancel_click, is_open):
        if ctx.triggered_id in [
            "delete-comment-button",
            "confirm-comment-delete-button",
            "cancel-comment-delete-button",
        ]:
            return not is_open
        return is_open

    @app.callback(
        Output("comments-delete-response", "is_open"),
        Input("confirm-comment-delete-button", "n_clicks"),
        State("comments-table", "selectionChanged"),
        State("comments-delete-response", "is_open"),
    )
    def confirm_comment_delete(confirm_click, selection, is_open):
        if ctx.triggered_id == "confirm-comment-delete-button":
            delete_comment_url = os.environ[
                "RUN_REVIEW_API_BASE"
            ] + "Comments/{}".format(selection[0]["CommentId"])
            requests.delete(url=delete_comment_url, verify=False)
            return not is_open

        return is_open

    """
    Callbacks related to viewing the text of a comment.
    """

    @app.callback(
        Output("view-comment-button", "disabled"),
        Input("comments-table", "selectionChanged"),
    )
    def check_view_comment_validity(selection):
        if ctx.triggered_id == "comments-table" and selection:
            return False
        return True

    @app.callback(
        Output("comments-view-modal", "is_open"),
        Output("comments-view-text", "children"),
        Input("view-comment-button", "n_clicks"),
        State("comments-table", "selectionChanged"),
        State("comments-view-modal", "is_open"),
    )
    def view_selected_comment(view_click, selection, is_open):
        if ctx.triggered_id == "view-comment-button":
            return not is_open, selection[0]["Entry"]
        return is_open, ""
