import dash_bootstrap_components as dbc
from dash import Dash
import os
import warnings
from flask_mail import Mail, Message
from .Layout import layout as run_review_layout
from .Callbacks import *

warnings.filterwarnings("ignore")

url_base = "/dashboard/run-review/"

layout = run_review_layout
# layout = dbc.Progress(children=run_review_layout)


def Add_Dash(app):
    app = Dash(
        __name__,
        server=app,
        url_base_pathname=url_base,
        use_pages=True,
        pages_folder="pages",
        external_stylesheets=[dbc.themes.COSMO],
    )
    apply_layout_with_auth(app, layout)
    get_run_review_callbacks(app)

    return app.server


if __name__ == "__main__":
    app = Dash(
        __name__,
        use_pages=True,
        pages_folder="run-review-pages",
        url_base_pathname=url_base,
        external_stylesheets=[dbc.themes.COSMO],
    )
    app.layout = layout
    app.run_server(debug=True)
