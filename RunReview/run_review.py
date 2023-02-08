from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import dash
from .appbuildhelpers import apply_layout_with_auth

url_base = '/dashboard/run-review/'
test = html.H1("Hello")


layout = dbc.Container(
    [test],
)


def Add_Dash(app):
    app = Dash(__name__, server=app,
               url_base_pathname=url_base,
               use_pages=True, pages_folder="pages", external_stylesheets=[dbc.themes.COSMO])

    apply_layout_with_auth(app, layout)
    return app.server
