import dash_bootstrap_components as dbc
from dash import Dash
from .Layout import data_reviewer_layout
from .Callbacks import add_data_reviewer_callbacks
from Shared.appbuildhelpers import apply_layout_with_auth

url_base = "/dashboard/data-reviewer/"

layout = data_reviewer_layout


def Add_Dash(app):
    app = Dash(
        __name__,
        server=app,
        url_base_pathname=url_base,
        external_stylesheets=[dbc.themes.COSMO],
    )

    apply_layout_with_auth(app, layout)
    add_data_reviewer_callbacks(app)
    return app.server
