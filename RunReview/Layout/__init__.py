from dash import html, dcc
import dash_bootstrap_components as dbc
from .storage import storage_objects, interval_objects, download_objects
from .display import filter_option_objects, graph_objects
from .messages import message_objects
from .reviewer_table import review_tabs

main_div = html.Div(
    [
        interval_objects,
        download_objects,
        message_objects,
        storage_objects,
        filter_option_objects,
        graph_objects,
        review_tabs,
    ],
    style={"margin-left": "2.5%", "margin-right": "2.5%", "margin-top": "2.5%"},
)


layout = dbc.Spinner(
    fullscreen=True,
    children=[main_div],
    delay_hide=500,
    delay_show=2000,
    spinner_style={"width": "5rem", "height": "5rem"},
    show_initially=True,
)
