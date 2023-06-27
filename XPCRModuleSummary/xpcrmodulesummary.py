import dash_bootstrap_components as dbc
from dash import Dash
import os
import warnings
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


if __name__ == "__main__":
    from Layout import *
    from Callbacks import *

    # from ..Shared.appbuildhelpers import *
    # from ..Shared.Components import *

    url_base = "/dashboard/XPCRModuleHistory/"

    dash_app = Dash(
        __name__, url_base_pathname=url_base, external_stylesheets=[dbc.themes.COSMO]
    )
    app = dash_app.server

    dash_app.title = "XPCR Module History"
    add_callbacks(dash_app)
    dash_app.layout = get_xpcrmodulehistory_layout(app)
    dash_app.run_server(debug=True)

else:
    from .Layout import *
    from .Callbacks import *
    from Shared.appbuildhelpers import *
