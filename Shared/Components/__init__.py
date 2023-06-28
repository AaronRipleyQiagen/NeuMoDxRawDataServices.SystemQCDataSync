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

    ## Make ids publically accessible.
    ids = ids
    app = Dash(__name__)

    def __init__(
        self,
        aio_id=None,
        button_text: str = "Go To RunSet",
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
                html.Div(id=self.ids.div(aio_id)),
                dcc.Store(id=self.ids.store(aio_id), storage_type="session"),
            ],
            **main_props
        )

    def add_callbacks(app):
        app.clientside_callback(
            """
        function navigateToRunReview(n_clicks, runset_id) {
            if (n_clicks && n_clicks > 0) {
                var currentHref = window.top.location.href;
                console.log('test')
                var splitString = '/dashboard/XPCRModuleHistory/';
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


def add_AIO_callbacks(app):
    GoToRunSetButtonAIO.add_callbacks(app)
    DownloadBlobFileButton.add_callbacks(app)
