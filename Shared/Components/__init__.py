from dash import (
    html,
    dcc,
    Input,
    Output,
    State,
    clientside_callback,
    callback,
    MATCH,
    Dash,
)
import dash_bootstrap_components as dbc
import uuid
from Shared.functions import *
from Shared.styles import *

## For Information related to All-In-One Component (AIO) Pattern please see https://dash.plotly.com/all-in-one-components


class GoToRunSetButtonAIO(html.Div):
    """An All-In-One (AIO) component that generates a button that will redirect to a particular RunSet page.

    Parameters:
        aio_id: The id to give to the GoToRunSetButton (Defaults to a randomly generated guid).
        button_text (str): The text to add to the button (Defaults to Go to RunSet).
        button_props (dict): Other properties to pass to the button. (Defaults to None).

    Subcomponents:
        button (dbc.button): The button to be displayed.
        div (html.Div): An empty div that acts as a target for the callback for redirect.
        store (dcc.Store): Storage component that stores the RunSetId of interest to target for redirect.

    """

    class ids:
        button = lambda aio_id: {
            "component": "GoToRunSetButtonAIO",
            "subcomponent": "button",
            "aio_id": aio_id,
        }

        div = lambda aio_id: {
            "component": "GoToRunSetButtonAIO",
            "subcomponent": "div",
            "aio_id": aio_id,
        }

        store = lambda aio_id: {
            "component": "GoToRunSetButtonAIO",
            "subcomponent": "store",
            "aio_id": aio_id,
        }

        split_string = lambda aio_id: {
            "component": "GoToRunSetButtonAIO",
            "subcomponent": "split_string",
            "aio_id": aio_id,
        }

    ## Make ids publically accessible.
    ids = ids
    app = Dash(__name__)

    def __init__(
        self,
        aio_id=None,
        button_text: str = "Go To RunSet",
        button_props: dict = None,
        split_string: str = None,
        main_props: dict = None,
    ):
        if not aio_id:
            aio_id = str(uuid.uuid4())

        button_props = button_props if button_props else {}
        button_props["children"] = button_text
        main_props = main_props if main_props else {}
        super().__init__(
            [
                dbc.Button(id=self.ids.button(aio_id), **button_props),
                html.Div(id=self.ids.div(aio_id)),
                dcc.Store(id=self.ids.store(aio_id), storage_type="session"),
                dcc.Store(
                    id=self.ids.split_string(aio_id),
                    storage_type="session",
                    data=split_string,
                ),
            ],
            **main_props,
        )

    def add_callbacks(app):
        app.clientside_callback(
            """
        function navigateToRunReview(n_clicks, runset_id, splitString) {
            if (n_clicks && n_clicks > 0) {
                var currentHref = window.top.location.href;
                console.log('test')
                var hrefParts = currentHref.split(splitString);
                if (hrefParts.length > 1) {
                    var newHref = hrefParts[0] + '/run-review/' + runset_id;
                    window.top.location.href = newHref;
                }
            }
        }
        """,
            Output(GoToRunSetButtonAIO.ids.div(MATCH), "children"),
            Input(GoToRunSetButtonAIO.ids.button(MATCH), "n_clicks"),
            State(GoToRunSetButtonAIO.ids.store(MATCH), "data"),
            State(GoToRunSetButtonAIO.ids.split_string(MATCH), "data"),
        )


class DownloadBlobFileButton(html.Div):
    """An All-In-One (AIO) component that generates a button that will download a file from an azure blob storage account.

    Parameters:
        aio_id: The id to give to the GoToRunSetButton (Defaults to a randomly generated guid).
        button_text (str): The text to add to the button (Defaults to Go to RunSet).
        button_props (dict): Other properties to pass to the button. (Defaults to None).

    Subcomponents:
        button (dbc.button): The button to be displayed.
        download (dcc.Download): An empty div that acts as a target for the callback for redirect.
        fileurl (dcc.Store): Storage component that stores the uri of BlobFile off Interest to target for redirect.

    """

    class ids:
        button = lambda aio_id: {
            "component": "DownloadBlobFileButton",
            "subcomponent": "button",
            "aio_id": aio_id,
        }

        download = lambda aio_id: {
            "component": "DownloadBlobFileButton",
            "subcomponent": "download",
            "aio_id": aio_id,
        }

        fileurl = lambda aio_id: {
            "component": "DownloadBlobFileButton",
            "subcomponent": "fileurl",
            "aio_id": aio_id,
        }

        filename = lambda aio_id: {
            "component": "DownloadBlobFileButton",
            "subcomponent": "filename",
            "aio_id": aio_id,
        }

    ids = ids

    def __init__(
        self,
        aio_id=None,
        button_text: str = "Download File",
        button_props: dict = None,
        main_props: dict = None,
    ):
        if not aio_id:
            aio_id = str(uuid.uuid4())

        button_props = button_props if button_props else {}
        button_props["children"] = button_text
        main_props = main_props if main_props else {}

        super().__init__(
            [
                dbc.Button(id=self.ids.button(aio_id), **button_props),
                dcc.Download(id=self.ids.download(aio_id)),
                dcc.Store(id=self.ids.fileurl(aio_id), storage_type="session"),
                dcc.Store(id=self.ids.filename(aio_id), storage_type="session"),
            ],
            **main_props,
        )

    def add_callbacks(app):
        @app.callback(
            Output(DownloadBlobFileButton.ids.download(MATCH), "data"),
            Input(DownloadBlobFileButton.ids.button(MATCH), "n_clicks"),
            State(DownloadBlobFileButton.ids.fileurl(MATCH), "data"),
            State(DownloadBlobFileButton.ids.filename(MATCH), "data"),
        )
        def download_file(n_clicks, file_url, file_name):
            if n_clicks:
                file_data = download_file_from_url(file_url)
                return dict(
                    content=file_data,
                    filename=file_name,
                    base64=True,
                )


class UserInputModal(dbc.Modal):
    """An All-In-One (AIO) component that generates a generic user input modal that allows the user to provide & confirm input, or cancel action.

    Parameters:
        aio_id: The id to give to the GoToRunSetButton (Defaults to a randomly generated guid).
        submit_text: Text to label the submit button with (Defaults to "Submit").
        cancel_text: Text to label the cancel button with (Defaults to "Cancel").
        title_text: Text to add to the ModalTitle (Defaults to None).
        modal_body: Variable content to add to modal to capture user input (Defaults to None).
        submit_props: Other properties to pass to the submit button. (Defaults to None).
        cancel_props: Other properties to pass to the cancel button. (Defaults to None).
        title_props: Other properties to pass to the Modal Title. (Defaults to None).

    Subcomponents:
        submit (dbc.Button): The submit button that confirms an action.
        cancel (dbc.Button): The submit button that cancels an action.
        modal (dbc.Modal): The parent element that wrapps the input.

    """

    class ids:
        submit = lambda aio_id: {
            "component": "UserInputModal",
            "subcomponent": "submit",
            "aio_id": aio_id,
        }

        cancel = lambda aio_id: {
            "component": "UserInputModal",
            "subcomponent": "cancel",
            "aio_id": aio_id,
        }

        modal = lambda aio_id: {
            "component": "UserInputModal",
            "subcomponent": "modal",
            "aio_id": aio_id,
        }

    ids = ids

    def __init__(
        self,
        aio_id: str = None,
        submit_text: str = "Submit",
        cancel_text: str = "Cancel",
        title_text: str = None,
        modal_body: dbc.Modal = None,
        submit_props: dict = None,
        cancel_props: dict = None,
        title_props: dict = None,
    ):
        if not aio_id:
            aio_id = str(uuid.uuid4())
        submit_props = submit_props if submit_props else {}
        cancel_props = cancel_props if submit_props else {}
        title_props = title_props if title_props else {}
        submit_props["children"] = submit_text
        cancel_props["children"] = cancel_text
        title_props["children"] = title_text

        super().__init__(
            [
                dbc.ModalHeader(dbc.ModalTitle(**title_props)),
                modal_body,
                dbc.ModalFooter(
                    [
                        dbc.Button(
                            id=self.ids.submit(aio_id),
                            className="ms-auto",
                            **submit_props,
                        ),
                        dbc.Button(
                            id=self.ids.cancel(aio_id),
                            className="ms-auto",
                            **cancel_props,
                        ),
                    ]
                ),
            ],
            id=self.ids.modal(aio_id),
            is_open=False,
        )

    def add_callbacks(app):
        @app.callback(
            Output(UserInputModal.ids.modal(MATCH), "is_open", allow_duplicate=True),
            Input(UserInputModal.ids.submit(MATCH), "n_clicks"),
            Input(UserInputModal.ids.cancel(MATCH), "n_clicks"),
            State(UserInputModal.ids.modal(MATCH), "is_open"),
            prevent_initial_call=True,
        )
        def download_file(submit_click, cancel_click, is_open):
            return not is_open


class RunSetAttemptModalBody(dbc.ModalBody):
    """An All-In-One (AIO) component that generates a ModalBody that can be used to capture a RunSetAttempt from a user.

    Parameters:
        aio_id: The id to give to the GoToRunSetButton (Defaults to a randomly generated guid).
        title_props: Other properties to pass to the Modal Title. (Defaults to None).
        prompt_label_text: Text to pass into the input label (Defaults to "Provide Runset Attempt Number:").
        attempt_number_default: The default value to be displayed in the input (Defaults to 1).
        prompt_label_props: Other properties to pass to the input label. (Defaults to None).
        attempt_number_props: dict = Other properties to pass to the input (Defaults to None).
    Subcomponents:
        attempt_number (dbc.Input): Input prompt used to capture a numeric value.
        prompt_label (html.P): Label to provide to the input prompt.

    """

    class ids:
        attempt_number = lambda aio_id: {
            "component": "RunSetAttemptModalBody",
            "subcomponent": "attempt_number",
            "aio_id": aio_id,
        }

        prompt_label = lambda aio_id: {
            "component": "RunSetAttemptModalBody",
            "subcomponent": "prompt_label",
            "aio_id": aio_id,
        }

    def __init__(
        self,
        aio_id: str = None,
        prompt_label_text: str = "Provide Runset Attempt Number:",
        prompt_label_props: dict = None,
        attempt_number_default: int = 1,
        attempt_number_props: dict = None,
    ):
        if not aio_id:
            aio_id = str(uuid.uuid4())

        prompt_label_props = prompt_label_props if prompt_label_props else {}
        prompt_label_props["children"] = prompt_label_text
        attempt_number_props = attempt_number_props if attempt_number_props else {}
        attempt_number_props["value"] = attempt_number_default
        attempt_number_props["type"] = "number"
        attempt_number_props["min"] = 1
        super().__init__(
            children=html.Div(
                [
                    html.Div(
                        [
                            html.P(
                                id=self.ids.prompt_label(aio_id),
                                style=threequarterstyle,
                                **prompt_label_props,
                            ),
                            dbc.Input(
                                id=self.ids.attempt_number(aio_id),
                                style=quarterstyle,
                                **attempt_number_props,
                            ),
                        ]
                    ),
                ]
            )
        )


class PostResponse(dbc.Modal):

    """An All-In-One (AIO) component that generates a Modal that can be used to process a response and dynamically return a message to the user based on the status code of the response.

    Parameters:
        aio_id: The id to give to the GoToRunSetButton (Defaults to a randomly generated guid).
        close_text: Text to label the close button with (Defaults to "Submit").
        title_text: Text to add to the ModalTitle (Defaults to None).
        success_text: Message to display if response code returned is 200 (Defaults to Operation was successful).
        failed_text: Message to display if reponse code returned is not 200 (Defaults to Operation was not successful)..
        close_props: Other properties to pass to the close button. (Defaults to None).
        title_props: Other properties to pass to the Modal Title. (Defaults to None).
        success_props: Other properties to pass to the success message (Defaults to None).
        failed_props: Other properties to pass to the failed message (Defaults to None).

    Subcomponents:
        close (dbc.Button): The button that closes the Modal.
        response_status_code (dcc.Store) The storage of the status code returned.
        failed (html.P): The messsage to display upon a failed response.
        success (html.P): The messsage to display upon a success response.
        modal (dbc.Modal): The parent Modal object.

    """

    class ids:
        response_status_code = lambda aio_id: {
            "component": "PostResponse",
            "subcomponent": "response_status_code",
            "aio_id": aio_id,
        }

        close = lambda aio_id: {
            "component": "PostResponse",
            "subcomponent": "close",
            "aio_id": aio_id,
        }

        success = lambda aio_id: {
            "component": "PostResponse",
            "subcomponent": "success",
            "aio_id": aio_id,
        }

        failed = lambda aio_id: {
            "component": "PostResponse",
            "subcomponent": "failed",
            "aio_id": aio_id,
        }

        modal = lambda aio_id: {
            "component": "PostResponse",
            "subcomponent": "modal",
            "aio_id": aio_id,
        }

    def __init__(
        self,
        aio_id: str = None,
        close_text: str = "Close",
        title_text: str = None,
        success_text: str = "Operation was successful",
        failed_text: str = "Operation was not successful",
        close_props: dict = None,
        title_props: dict = None,
        success_props: dict = None,
        failed_props: dict = None,
    ):
        if not aio_id:
            aio_id = str(uuid.uuid4())
        close_props = close_props if close_props else {}
        title_props = title_props if title_props else {}
        success_props = success_props if success_props else {}
        failed_props = failed_props if failed_props else {}
        close_props["children"] = close_text
        title_props["children"] = title_text
        success_props["children"] = success_text
        failed_props["children"] = failed_text

        super().__init__(
            [
                dbc.ModalHeader(dbc.ModalTitle(**title_props)),
                dbc.ModalBody(
                    children=[
                        html.P(id=self.ids.success(aio_id), **success_props),
                        html.P(id=self.ids.failed(aio_id), **failed_props),
                    ]
                ),
                dbc.ModalFooter(
                    [
                        dbc.Button(
                            id=self.ids.close(aio_id),
                            className="ms-auto",
                            **close_props,
                        )
                    ]
                ),
                dcc.Store(
                    id=self.ids.response_status_code(aio_id), storage_type="session"
                ),
            ],
            id=self.ids.modal(aio_id),
            is_open=False,
        )

    def add_callbacks(app):
        @app.callback(
            Output(PostResponse.ids.success(MATCH), "hidden"),
            Output(PostResponse.ids.failed(MATCH), "hidden"),
            Input(PostResponse.ids.response_status_code(MATCH), "data"),
        )
        def control_message(data):
            print("RAN CONTROL MESSAGE")
            print(data)
            if data == "200":
                return False, True
            else:
                return False, True

        @app.callback(
            Output(PostResponse.ids.modal(MATCH), "is_open", allow_duplicate=True),
            Input(PostResponse.ids.close(MATCH), "n_clicks"),
            State(PostResponse.ids.modal(MATCH), "is_open"),
            prevent_initial_call=True,
        )
        def open_post_response(close_click, is_open):
            return not is_open


class RunSetAttemptNumberValidation(dbc.ModalBody):
    """An All-In-One (AIO) component that generates a ModalBody alert a user if a Particular XPCR Module has a runset matching the attempt number & runset type they have specified that already exists in the database.

    Parameters:
        aio_id: The id to give to the GoToRunSetButton (Defaults to a randomly generated guid).
        message_text: Text to pass into the message (Defaults to "A Runset matching this description already exists.  Are you sure you want to continue?").
        messsage_props: Other properties to pass to the message. (Defaults to None).
    Subcomponents:
        GoToRunSetButtonAIO (GoToRunSetButton): Button used to go to the runset found during runset attempt number validation.
        message (html.P): Label to provide to the input prompt.

    """

    class ids:
        message = lambda aio_id: {
            "component": "RunSetValidationResponse",
            "subcomponent": "message",
            "aio_id": aio_id,
        }

        GoToRunSetButtonAIO = lambda aio_id: {
            "component": "RunSetValidationResponse",
            "subcomponent": "GoToRunSetButtonAIO",
            "aio_id": aio_id,
        }

    def __init__(
        self,
        aio_id: str = None,
        message_text: str = "A Runset matching this description already exists.  Are you sure you want to continue?",
        message_props: dict = None,
        split_string: str = None,
    ):
        if not aio_id:
            aio_id = str(uuid.uuid4())

        message_props = message_props if message_props else {}
        message_props["children"] = message_text

        super().__init__(
            children=html.Div(
                [
                    html.Div(
                        [
                            html.P(
                                id=self.ids.message(aio_id),
                                **message_props,
                            ),
                            GoToRunSetButtonAIO(
                                aio_id,
                                button_text="Go To Matching Runset",
                                split_string=split_string,
                            ),
                        ]
                    ),
                ]
            )
        )


def add_AIO_callbacks(app):
    GoToRunSetButtonAIO.add_callbacks(app)
    DownloadBlobFileButton.add_callbacks(app)
    UserInputModal.add_callbacks(app)
    PostResponse.add_callbacks(app)
