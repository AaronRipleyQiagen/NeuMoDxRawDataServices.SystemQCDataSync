from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
from dash import Dash
from .appbuildhelpers import apply_layout_with_auth
from dash import html, callback, Output, Input, State, register_page, dcc, dash_table, page_container
from .functions import populate_review_queue

url_base = '/dashboard/'
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H3("Run Review Options", className="display-6"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/dashboard/run-review/",
                            active="exact"),
                dbc.NavLink("Run Review Queue",
                            href="/dashboard/run-review/review-queue", active="exact"),
                dbc.NavLink("View Module History",
                            href="/dashboard/run-review/module-history", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

review_loader = html.Div(id='run-reviewer-loader')
content = html.Div(id="run-reviewer-page-content", style=CONTENT_STYLE,
                   children=page_container)

layout = html.Div([review_loader, dcc.Location(
    id="run-review-url", refresh=True), sidebar, content])


def Add_Dash(app):
    app = Dash(__name__, server=app,
               url_base_pathname=url_base,
               use_pages=True, pages_folder="pages", external_stylesheets=[dbc.themes.COSMO])

    apply_layout_with_auth(app, layout)

    @app.callback([Output('review-queue-table', 'rowData'), Output('review-queue-table', 'columnDefs')],
                  [Input('refresh-review-queue', 'n_clicks')])
    def loader_molder(n):
        print('Firing'*30)
        intial_data, initial_columnDefs = populate_review_queue()
        return intial_data, initial_columnDefs

    @app.callback([Output('test-hello', 'children')],
                  [Input('refresh-review-queue', 'n_clicks')])
    def hello_tester(n):
        return ['Hello, Hello, Hello'+str(n)]
    return app.server


if __name__ == '__main__':

    app = Dash(__name__, use_pages=True, pages_folder="run-review-pages",
               url_base_pathname=url_base, external_stylesheets=[dbc.themes.COSMO])
    app.layout = html.Div([review_loader, dcc.Location(
        id="run-review-url"), sidebar, content])
    app.run_server(debug=True)

# Start Test

# from dash import Dash
# # from .appbuildhelpers import apply_layout_with_auth
# from dash import html, callback, Output, Input, State, register_page, dcc, dash_table, page_container

# import dash_bootstrap_components as dbc
# from dash import Input, Output, dcc, html


# # the style arguments for the sidebar. We use position:fixed and a fixed width
# SIDEBAR_STYLE = {
#     "position": "fixed",
#     "top": 0,
#     "left": 0,
#     "bottom": 0,
#     "width": "16rem",
#     "padding": "2rem 1rem",
#     "background-color": "#f8f9fa",
# }

# # the styles for the main content position it to the right of the sidebar and
# # add some padding.
# CONTENT_STYLE = {
#     "margin-left": "18rem",
#     "margin-right": "2rem",
#     "padding": "2rem 1rem",
# }

# sidebar = html.Div(
#     [
#         html.H3("Run Review Options", className="display-6"),
#         html.Hr(),
#         dbc.Nav(
#             [
#                 dbc.NavLink("Home", href="/dashboard/run-review/",
#                             active="exact"),
#                 dbc.NavLink("Run Review Queue",
#                             href="/dashboard/run-review/review-queue", active="exact"),
#                 dbc.NavLink("View Module History",
#                             href="/dashboard/run-review/module-history", active="exact"),
#             ],
#             vertical=True,
#             pills=True,
#         ),
#     ],
#     style=SIDEBAR_STYLE,
# )

# review_loader = html.Div(id='run-reviewer-loader')
# content = html.Div(id="run-reviewer-page-content", style=CONTENT_STYLE,
#                    children=page_container)
