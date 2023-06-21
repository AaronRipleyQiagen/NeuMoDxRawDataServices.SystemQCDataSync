import dash_bootstrap_components as dbc
from dash import Dash
import os
import warnings
from flask_mail import Mail, Message
from .Layout import *
from .Callbacks import *
from Shared.appbuildhelpers import *

warnings.filterwarnings("ignore")

url_base = "/dashboard/XPCRModuleHistory/"

# layout = xpcrmodulesummary_layout


def Add_Dash(app):
    app = Dash(
        __name__,
        server=app,
        url_base_pathname=url_base,
        external_stylesheets=[dbc.themes.COSMO],
    )
    layout = get_xpcrmodulehistory_layout(app)
    apply_layout_with_auth(app, layout)
    add_callbacks(app)

    return app.server
