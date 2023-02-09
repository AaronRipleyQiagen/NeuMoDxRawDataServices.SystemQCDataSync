from dash import Input, Output, dcc, html, no_update
import dash_bootstrap_components as dbc
from dash import Dash
from .appbuildhelpers import apply_layout_with_auth
from dash import html, callback, Output, Input, State, register_page, dcc, dash_table, page_container
from .functions import populate_review_queue, getSampleDataAsync, SampleJSONReader
import os
import requests
import json
import pandas as pd
import numpy as np
import warnings
import plotly.graph_objects as go

warnings.filterwarnings('ignore')

colorDict = {1: '#FF0000',  # Red 1
             2: '#00B050',  # Green 2
             3: '#0070C0',  # Blue 3
             4: '#7030A0',  # Purple 4
             5: '#808080',  # Light Grey 5
             6: '#FF6600',  # Orange 6
             7: '#FFCC00',  # Yellow 7
             8: '#9999FF',  # Light Purple 8
             9: '#333333',  # Black 9
             10: '#808000',  # Goldish 10
             11: '#FF99CC',  # Hot Pink 11
             12: '#003300',  # Dark Green 12
             }

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
runset_selection = dcc.Store(
    id='runset-selection-data', storage_type='session')
runset_sample_data = dcc.Store(id='runset-sample-data', storage_type='session')
layout = html.Div([review_loader, dcc.Location(
    id="run-review-url", refresh=True), sidebar, content, runset_selection, runset_sample_data])


def Add_Dash(app):
    app = Dash(__name__, server=app,
               url_base_pathname=url_base,
               use_pages=True, pages_folder="pages", external_stylesheets=[dbc.themes.COSMO])

    apply_layout_with_auth(app, layout)

    @app.callback([Output('review-queue-table', 'rowData'), Output('review-queue-table', 'columnDefs')],
                  [Input('refresh-review-queue', 'n_clicks')])
    def refresh_review_queue(n):
        intial_data, initial_columnDefs = populate_review_queue()
        return intial_data, initial_columnDefs

    @app.callback(Output('runset-selection-data', 'data'),
                  [Input('review-queue-table', 'selectionChanged')])
    def get_runset_selection(selected):
        if selected == None:
            return no_update
        runsetsample_url = os.environ['RUN_REVIEW_API_BASE'] + \
            "RunSets/Samples/{}".format(selected[0]['id'])
        print(runsetsample_url)
        _runset_samples = requests.get(runsetsample_url, verify=False).json()
        return _runset_samples
        #    Output('run-review-channel-selector', 'options'),
        #    Output('run-review-process-step-selector', 'options')],

    @app.callback(Output("runset-sample-data", "data"),
                  [Input('get-runset-data', 'n_clicks'),
                   State('runset-selection-data', 'data')],
                  prevent_inital_call=True)
    def get_runset_samples(n, runset_data):
        print("trying...")
        runset_sample_ids = []
        runset_map_df = pd.DataFrame(columns=['RawDataDatabaseId', 'RunSetXPCRModuleLaneId',
                                              'RunSetCartridgeId', 'RunSetXPCRModuleId', 'RunSetNeuMoDxSystemId'])
        idx = 0
        for runsetsample in runset_data['runSetSamples']:
            runset_sample_ids.append(
                runsetsample['sample']['rawDataDatabaseId'])

            runset_map = [runsetsample['sample']['rawDataDatabaseId'],
                          runsetsample['sample']['runSetXPCRModuleLaneSamples'][0]['runSetXPCRModuleLaneId'],
                          runsetsample['sample']['runSetCartridgeSamples'][0]['runSetCartridgeId'],
                          runsetsample['sample']['runSetXPCRModuleSamples'][0]['runSetXPCRModuleId'],
                          runsetsample['sample']['runSetNeuMoDxSystemSamples'][0]['runSetNeuMoDxSystemId']]
            idx += 1
            runset_map_df.loc[idx] = runset_map
        runset_map_df.set_index('RawDataDatabaseId', inplace=True)
        sample_data = getSampleDataAsync(runset_sample_ids)

        jsonReader = SampleJSONReader(json.dumps(sample_data))
        jsonReader.standardDecode()
        dataframe = jsonReader.DataFrame
        # dataframe.to_csv('test3.csv')
        dataframe['RawDataDatabaseId'] = dataframe.reset_index()['id'].values
        dataframe['Channel'] = dataframe['Channel'].replace(
            'Far_Red', 'Far Red')
        dataframe = dataframe.set_index(
            'RawDataDatabaseId').join(runset_map_df).reset_index()
        # dataframe.to_csv('test-merged.csv')
        # print(runset_data['name'] + " " + str(runset_data['number']))
        return dataframe.to_dict('records')

    @app.callback([Output('run-review-description', 'children'), Output('run-review-curves', 'figure'), Output('runset-sample-results', 'data')],
                  [Input('run-review-channel-selector', 'value'),
                   Input('run-review-process-step-selector', 'value'),
                   Input('runset-sample-data', 'data'),
                   State('runset-selection-data', 'data')], prevent_initial_call=True)
    def update_pcr_curves(channel, process_step, data, runset_data):
        dataframe = pd.DataFrame.from_dict(data)
        dataframe['Channel'] = dataframe['Channel'].replace(
            'Far_Red', 'Far Red')
        # Start making graph...
        fig = go.Figure()
        df = dataframe.reset_index().set_index(
            ['Channel', 'Processing Step', 'XPCR Module Serial'])
        df_Channel = df.loc[channel]

        df_Channel_Step = df_Channel.loc[process_step].reset_index()
        df_Channel_Step.sort_values('XPCR Module Lane', inplace=True)

        for idx in df_Channel_Step.index:
            X = np.array(
                [read for read in df_Channel_Step.loc[idx, 'Readings Array']][0])
            Y = np.array(
                [read for read in df_Channel_Step.loc[idx, 'Readings Array']][1])
            _name = str(df_Channel_Step.loc[idx, 'XPCR Module Lane'])
            fig.add_trace(go.Scatter(x=X,
                                     y=Y,
                                     mode='lines',
                                     name=_name,
                                     line=dict(color=colorDict[df_Channel_Step.loc[idx, 'XPCR Module Lane']])))

        return [runset_data['name'] + " Attempt # " + str(runset_data['number'])], fig, df_Channel_Step[['XPCR Module Serial', 'XPCR Module Lane', 'Sample ID', 'Target Name', 'Localized Result', 'Overall Result', 'Ct', 'End Point Fluorescence', 'Max Peak Height', 'EPR']].round(1).to_dict('records')
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
