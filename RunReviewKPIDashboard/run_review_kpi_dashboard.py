import dash_bootstrap_components as dbc
from dash import Dash
import os
import warnings
from flask_mail import Mail, Message
from Shared.appbuildhelpers import *
from .Layout import layout as layout
from .Callbacks import *


url_base = "/dashboard/run-review-kpis/"


def Add_Dash(app):
    app = Dash(
        __name__,
        server=app,
        url_base_pathname=url_base,
        external_stylesheets=[dbc.themes.COSMO],
    )
    apply_layout_with_auth(app, layout)
    add_run_review_kpi_callbacks(app)
    return app.server


if __name__ == "__main__":
    app = Dash(
        __name__,
        url_base_pathname=url_base,
        external_stylesheets=[dbc.themes.COSMO],
    )
    app.layout = layout
    app.run_server(debug=True)
