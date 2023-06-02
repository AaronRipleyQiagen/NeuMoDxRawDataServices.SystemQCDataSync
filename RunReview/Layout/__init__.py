from dash import html, dcc
from .storage import storage_objects, interval_objects, download_objects
from .display import filter_option_objects, graph_objects
from .messages import message_objects
from .reviewer_table import review_tabs


layout = html.Div(
    [
        # dcc.Loading(id='display-objects-loading', fullscreen=True,
        #             type='circle', children=[]),
        interval_objects,
        download_objects,
        message_objects,
        storage_objects,
        filter_option_objects,
        graph_objects,
        review_tabs
        # dcc.Loading(id='review-tabs-loading', fullscreen=True,
        #             type='circle', children=[], debug=True),
    ],
    style={'margin-left': '2.5%',
           'margin-right': '2.5%',
           'margin-top': '2.5%'})
