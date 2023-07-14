from dash import html, dcc, callback, clientside_callback, Input, Output, State, MATCH
import dash_bootstrap_components as dbc
from Shared.styles import *


class FindXPCRModuleRunsButton(html.Div):
    class ids:
        link_div = lambda aio_id: {
            "component": "FindXPCRModuleRunsButton",
            "subcomponent": "link_div",
            "aio_id": aio_id,
        }

        button = lambda aio_id: {
            "component": "FindXPCRModuleRunsButton",
            "subcomponent": "button",
            "aio_id": aio_id,
        }

        xpcrmodule_id = lambda aio_id: {
            "component": "FindXPCRModuleRunsButton",
            "subcomponent": "xpcrmodule_id",
            "aio_id": aio_id,
        }

        split_string = lambda aio_id: {
            "component": "FindXPCRModuleRunsButton",
            "subcomponent": "split_string",
            "aio_id": aio_id,
        }

    ids = ids

    def __init__(self, aio_id: str = None, split_string: str = None):
        super().__init__(
            [
                html.Div(id=self.ids.link_div(aio_id)),
                dbc.Button(
                    id=self.ids.button(aio_id),
                    children=["Find More Runs for XPCR Module"],
                    style={"width": "100%", "vertical-align": "middle"},
                ),
                dcc.Store(id=self.ids.xpcrmodule_id(aio_id), storage_type="session"),
                dcc.Store(
                    id=self.ids.split_string(aio_id),
                    storage_type="session",
                    data=split_string,
                ),
            ],
            style={"margin-left": "10%", "width": "35%", "display": "inline-block"},
        )

    def add_callbacks(app):
        app.clientside_callback(
            """
        function navigateToRunReview(n_clicks, xpcrmodule_id, splitString) {
            if (n_clicks && n_clicks > 0) {
                var currentHref = window.top.location.href;
                var hrefParts = currentHref.split(splitString);
                if (hrefParts.length > 1) {
                    var newHref = hrefParts[0] + '/data-finder/?xpcrmoduleid=' + xpcrmodule_id;
                    window.top.location.href = newHref;
                }
            }
        }
        """,
            Output(FindXPCRModuleRunsButton.ids.link_div(MATCH), "children"),
            Input(FindXPCRModuleRunsButton.ids.button(MATCH), "n_clicks"),
            State(FindXPCRModuleRunsButton.ids.xpcrmodule_id(MATCH), "data"),
            State(FindXPCRModuleRunsButton.ids.split_string(MATCH), "data"),
        )
