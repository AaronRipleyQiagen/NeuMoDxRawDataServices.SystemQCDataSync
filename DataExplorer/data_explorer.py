from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import dash
from .appbuildhelpers import apply_layout_with_auth
import pandas as pd

url_base = '/dashboard/data-explorer/'
loader = html.Div(id='loader')
cartridge_sample_ids = dcc.Store(
    id='cartridge-sample-ids', storage_type='session')
selected_cartridge_sample_ids = dcc.Store(
    id='selected-cartridge-sample-ids', storage_type='session')
sample_info = dcc.Store(id='sample-info', storage_type='session')
runset_type_selection = dcc.Store(
    id='runset-type-selection', storage_type='session')


layout = dbc.Container(
    [loader, cartridge_sample_ids, selected_cartridge_sample_ids, sample_info, runset_type_selection,
        dash.page_container, dcc.Location(id="url", refresh=True)],
)



def Add_Dash(app):
    app = Dash(__name__, server=app,
               url_base_pathname=url_base,
               use_pages=True, external_stylesheets=[dbc.themes.COSMO])

    apply_layout_with_auth(app, layout)
    return app.server
