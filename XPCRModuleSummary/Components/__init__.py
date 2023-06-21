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
        app: Dash,
        aio_id=None,
        button_text: str = "Go To RunSet",
        button_props: dict = None,
    ):
        if not aio_id:
            aio_id = str(uuid.uuid4())
        if not app:
            self.app = app
        button_props = button_props if button_props else {}
        button_props["children"] = button_text
        super().__init__(
            [
                dbc.Button(id=self.ids.button(aio_id), **button_props),
                html.Div(id=self.ids.div(aio_id)),
                dcc.Store(id=self.ids.store(aio_id), storage_type="session"),
            ]
        )

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
        Output(ids.div(MATCH), "children"),
        Input(ids.button(MATCH), "n_clicks"),
        State(ids.store(MATCH), "data"),
    )


class DownloadBlobFileButton(html.Div):
    """An All-In-One (AIO) component that generates a button that will download a file from an azure blob storage account.

    Parameters:
        aio_id: The id to give to the GoToRunSetButton (Defaults to a randomly generated guid).
        button_text (str): The text to add to the button (Defaults to Go to RunSet).
        button_props (dict): Other properties to pass to the button. (Defaults to None).

    Subcomponents:
        button (dbc.button): The button to be displayed.
        div (html.Div): An empty div that acts as a target for the callback for redirect.
        store (dcc.Store): Storage component that stores the uri of BlobFile off Interest to target for redirect.

    """

    class ids:
        button = lambda aio_id: {
            "component": "DownloadBlobFileButton",
            "subcomponent": "button",
            "aio_id": aio_id,
        }

        div = lambda aio_id: {
            "component": "DownloadBlobFileButton",
            "subcomponent": "div",
            "aio_id": aio_id,
        }

        store = lambda aio_id: {
            "component": "DownloadBlobFileButton",
            "subcomponent": "store",
            "aio_id": aio_id,
        }
