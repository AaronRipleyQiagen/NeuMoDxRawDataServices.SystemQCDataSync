from flask import session
from dash import Input, Output, dcc, html, no_update, ctx
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
import aiohttp
import asyncio

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
runset_review_id = dcc.Store(id='runset-review-id', storage_type='session')

runset_channel_options = dcc.Store(
    id='runset-channel-options', storage_type='session')
channel_selected = dcc.Store(id='channel-selected', storage_type='session')
spc_channel = dcc.Store(id='spc-channel', storage_type='session')

runset_severity_options = dcc.Store(
    id='runset-severity-options', storage_type='session')

severity_selected = dcc.Store(id='severity-selected', storage_type='session')

runset_run_options = dcc.Store(id='runset-run-options', storage_type='session')
run_option_selected = dcc.Store(
    id='run-option-selected', storage_type='session')

runset_xpcrmodulelane_options = dcc.Store(
    id='runset-xpcrmodulelane-options', storage_type='session')
xpcrmodulelane_selected = dcc.Store(
    id='xpcrmodulelane-selected', storage_type='session')


layout = html.Div([review_loader, dcc.Loading(id='run-review-href-loader', fullscreen=True, type='dot', children=[dcc.Location(
    id="run-review-url", refresh=True)]), sidebar, content, runset_selection, runset_sample_data, runset_review_id, runset_severity_options, runset_channel_options, channel_selected, runset_run_options, run_option_selected, spc_channel, runset_xpcrmodulelane_options, xpcrmodulelane_selected, severity_selected])


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
        _runset_samples = requests.get(runsetsample_url, verify=False).json()
        return _runset_samples

    @app.callback([Output("runset-sample-data", "data"),
                   Output("run-review-url", "href"),
                   Output('runset-review-id', 'data'),
                   Output('runset-severity-options', 'data'),
                   Output('runset-channel-options', 'data'),
                   Output('runset-run-options', 'data'),
                   Output('spc-channel', 'data'),
                   Output('runset-xpcrmodulelane-options', 'data')],
                  [Input('get-runset-data', 'n_clicks'),
                   State('runset-selection-data', 'data')],
                  prevent_inital_call=True)
    def initialize_runset_data(n, runset_data):

        if n == 0:
            return no_update
        """
        Get Data associated with Runset.
        """
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

        """
        Get or Add RunSet Review
        """

        runsetreview = {}
        runsetreview['userId'] = session['user'].id
        runsetreview['reviewerName'] = session['user'].display_name
        runsetreview['reviewerEmail'] = session['user'].emails[0]
        runsetreview['runSetId'] = runset_data['id']
        resp = requests.post(url=os.environ['RUN_REVIEW_API_BASE'] +
                             "RunSetReviews", json=runsetreview, verify=False).json()

        """
        Get Severity Options
        """
        severity_url = os.environ['RUN_REVIEW_API_BASE'] + "SeverityRatings"
        severity_resp = requests.get(severity_url, verify=False).json()
        severity_options = []
        for severity in severity_resp:
            severity_options.append(
                {'label': severity['name'], 'value': severity['id']})

        """
        Get Run Set Channel options
        """
        channels_data = runset_data['runSetType']['qualificationAssay']['assayChannels']
        channel_options = {}
        for channel in channels_data:
            channel_options[channel['id']] = channel['channel']
        dataframe.sort_values(['Start Date Time'], inplace=True)

        """
        Get Run Options
        """
        i = 0
        run_options = {}
        run_options['NoFilter'] = 'All'
        for run in dataframe['RunSetCartridgeId'].unique():
            i += 1
            run_options[run] = "Run "+str(i)
        dataframe.to_csv('test.csv')

        dataframe['Run'] = dataframe['RunSetCartridgeId'].replace(
            run_options)

        dataframe['Run'] = dataframe['Run'].str.replace(
            'Run ', '').astype(int)

        """
        Get Lane Options
        """
        lane_options = {}
        lane_options['NoFilter'] = 'All'
        dataframe.sort_values(['XPCR Module Lane'], inplace=True)
        for idx in dataframe.drop_duplicates(subset=['XPCR Module Lane', 'RunSetXPCRModuleLaneId']).index:
            lane_options[dataframe.loc[idx, 'RunSetXPCRModuleLaneId']
                         ] = "Lane "+str(dataframe.loc[idx, 'XPCR Module Lane'])

        dataframe.to_csv('test.csv')

        """
        Get SPC Channel
        """
        spc_channel_color = dataframe.loc[dataframe["Target Name"].str.contains(
            "SPC"), 'Channel'].values[0]
        for channel_id in channel_options:
            if channel_options[channel_id] == spc_channel_color:
                spc_channel = channel_id
        """
        Return Data associated with Runset, URL for RunsetReview Page, Runset Review Id, Severity Options.
        """

        return dataframe.to_dict('records'), '/dashboard/run-review/view-results', resp['id'], severity_options, channel_options, run_options, spc_channel, lane_options

    @app.callback([Output('sample-issue-options', 'options'), Output('lane-issue-options', 'options'), Output('module-issue-options', 'options'), Output('run-issue-options', 'options')],
                  Input('submit-sample-issue', 'children'))
    def getIssueTypes(_):

        async def getIssueTypeOptions(session, url):
            async with session.get(url) as resp:
                issueTypes = await resp.json()
                return issueTypes

        async def main():

            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                issueTypeEndpoints = [
                    'SampleIssueTypes', 'XPCRModuleLaneIssueTypes', 'CartridgeIssueTypes', 'XPCRModuleIssueTypes']
                tasks = []
                tasksTracker = {}
                for issueType in issueTypeEndpoints:
                    url = os.environ['RUN_REVIEW_API_BASE'] + issueType
                    tasks.append(asyncio.ensure_future(
                        getIssueTypeOptions(session, url)))

                responses = await asyncio.gather(*tasks)

                return {issueTypeEndpoints[i]: responses[i] for i in range(len(responses))}

        issueTypes = asyncio.run(main())

        issueTypeOptions = {}
        issueTypeEndpoints = ['SampleIssueTypes', 'XPCRModuleLaneIssueTypes',
                              'CartridgeIssueTypes', 'XPCRModuleIssueTypes']
        for endpoint in issueTypeEndpoints:
            issue_type_options = []
            for issueType in issueTypes[endpoint]:
                issue_type_options.append(
                    {'label': issueType['name'], 'value': issueType['id']})
            issueTypeOptions[endpoint] = issue_type_options

        return issueTypeOptions['SampleIssueTypes'], issueTypeOptions['XPCRModuleLaneIssueTypes'], issueTypeOptions['XPCRModuleIssueTypes'], issueTypeOptions['CartridgeIssueTypes']

    @app.callback([Output('sample-issue-severity-options', 'options'),
                   Output('lane-issue-severity-options', 'options'),
                   Output('run-issue-severity-options', 'options'),
                   Output('module-issue-severity-options', 'options')
                   ],
                  Input('runset-severity-options', 'data'))
    def update_severity_options(data):
        return data, data, data, data

    @app.callback(Output('severity-selected', 'data'),
                  [Input('sample-issue-severity-options', 'value'),
                   Input('lane-issue-severity-options', 'value'),
                   Input('run-issue-severity-options', 'value'),
                   Input('module-issue-severity-options', 'value')
                   ], prevent_initial_call=True
                  )
    def update_severity_selection(sample_issue_severity, lane_issue_severity, run_issue_severity, module_issue_severity):
        trigger = ctx.triggered_id
        print(trigger)
        if trigger == 'sample-issue-severity-options':
            return sample_issue_severity
        elif trigger == 'lane-issue-severity-options':
            return lane_issue_severity
        elif trigger == 'run-issue-severity-options':
            return run_issue_severity
        elif trigger == 'module-issue-severity-options':
            return module_issue_severity

    @app.callback([Output('sample-issue-severity-options', 'value'),
                   Output('lane-issue-severity-options', 'value'),
                   Output('run-issue-severity-options', 'value'),
                   Output('module-issue-severity-options', 'value')],
                  Input('severity-selected', 'data'), prevent_initial_call=True)
    def update_channel_selection_value(channel):
        return channel, channel, channel, channel

    @app.callback([Output('run-review-description', 'children'), Output('run-review-curves', 'figure'), Output('runset-sample-results', 'data')],
                  [Input('channel-selected', 'data'),
                   Input('run-review-process-step-selector', 'value'),
                   Input('run-review-color-selector', 'value'),
                   State('runset-sample-data', 'data'),
                   State('runset-selection-data', 'data'),
                   State('runset-channel-options', 'data'),
                   Input('xpcrmodulelane-selected', 'data'),
                   Input('run-option-selected', 'data')], prevent_initial_call=True)
    def update_pcr_curves(channel_selected, process_step, color_option_selected, data, runset_data, channel_options, lane_selection, run_selection):
        if channel_selected == None:
            channel = 'Yellow'
        else:
            channel = channel_options[channel_selected]

        dataframe = pd.DataFrame.from_dict(data)
        dataframe['Channel'] = dataframe['Channel'].replace(
            'Far_Red', 'Far Red')
        # Start making graph...
        fig = go.Figure()
        df = dataframe.reset_index().set_index(
            ['Channel', 'Processing Step', 'XPCR Module Serial'])
        df_Channel = df.loc[channel]

        """Filter Dataframe with current Run & Module Lane Selections"""

        if lane_selection != 'NoFilter' and lane_selection != None:
            df_Channel = df_Channel[df_Channel['RunSetXPCRModuleLaneId']
                                    == lane_selection]

        if run_selection != 'NoFilter' and run_selection != None:
            df_Channel = df_Channel[df_Channel['RunSetCartridgeId']
                                    == run_selection]
        df_Channel_Step = df_Channel.loc[process_step].reset_index()
        df_Channel_Step.sort_values(color_option_selected, inplace=True)

        for idx in df_Channel_Step.index:
            X = np.array(
                [read for read in df_Channel_Step.loc[idx, 'Readings Array']][0])
            Y = np.array(
                [read for read in df_Channel_Step.loc[idx, 'Readings Array']][1])
            _name = str(df_Channel_Step.loc[idx, color_option_selected])
            fig.add_trace(go.Scatter(x=X,
                                     y=Y,
                                     mode='lines',
                                     name=_name,
                                     line=dict(color=colorDict[df_Channel_Step.loc[idx, color_option_selected]])))

        return [runset_data['name'] + " Attempt # " + str(runset_data['number'])], fig, df_Channel_Step[['XPCR Module Serial', 'XPCR Module Lane', 'Sample ID', 'Target Name', 'Localized Result', 'Overall Result', 'Ct', 'End Point Fluorescence', 'Max Peak Height', 'EPR']].round(1).to_dict('records')

    @app.callback([Output('sample-issue-channel-options', 'options'),
                   Output('lane-issue-channel-options', 'options'),
                   Output('run-issue-channel-options', 'options'),
                   Output('module-issue-channel-options', 'options'),
                   Output('run-review-channel-selector', 'options')],
                  Input('runset-channel-options', 'data'))
    def update_channel_options(data):
        return data, data, data, data, data

    @app.callback(Output('channel-selected', 'data'),
                  [Input('sample-issue-channel-options', 'value'),
                   Input('lane-issue-channel-options', 'value'),
                   Input('run-issue-channel-options', 'value'),
                   Input('module-issue-channel-options', 'value'),
                   Input('run-review-channel-selector', 'value'),
                   State('spc-channel', 'data')
                   ], prevent_initial_call=True
                  )
    def update_channel_selection(sample_issue_channel, lane_issue_channel, run_issue_channel, module_issue_channel, run_review_channel, spc_channel):
        channel_adjusted = ctx.triggered_id

        if channel_adjusted == 'sample-issue-channel-options':
            if sample_issue_channel == None:
                return spc_channel
            return sample_issue_channel
        elif channel_adjusted == 'lane-issue-channel-options':
            if lane_issue_channel == None:
                return spc_channel
            return lane_issue_channel
        elif channel_adjusted == 'run-issue-channel-options':
            if run_issue_channel == None:
                return spc_channel
            return run_issue_channel
        elif channel_adjusted == 'module-issue-channel-options':
            if module_issue_channel == None:
                return spc_channel
            return module_issue_channel
        elif channel_adjusted == 'run-review-channel-selector':
            if run_review_channel == None:
                return spc_channel
            return run_review_channel

    @app.callback([Output('sample-issue-channel-options', 'value'),
                   Output('lane-issue-channel-options', 'value'),
                   Output('run-issue-channel-options', 'value'),
                   Output('module-issue-channel-options', 'value'),
                   Output('run-review-channel-selector', 'value')],
                  Input('channel-selected', 'data'), prevent_initial_call=True)
    def update_channel_selection_value(channel):
        return channel, channel, channel, channel, channel

    @app.callback([Output('run-issue-run-options', 'options'),
                   Output('sample-issue-run-options', 'options'),
                   Output('run-review-run-selector', 'options')],
                  Input('runset-run-options', 'data'))
    def update_run_options(data):
        return data, data, data

    @app.callback([Output('run-issue-run-options', 'value'),
                   Output('sample-issue-run-options', 'value'),
                   Output('run-review-run-selector', 'value')],
                  Input('run-option-selected', 'data'), prevent_initial_call=True)
    def update_run_option_selected(data):
        return data, data, data

    @app.callback(Output('run-option-selected', 'data'),
                  [Input('run-issue-run-options', 'value'),
                   Input('sample-issue-run-options', 'value'),
                   Input('run-review-run-selector', 'value'),
                   Input('review-tabs', 'active_tab'),
                   State('run-option-selected', 'data')], prevent_initial_call=True
                  )
    def update_run_option_selections(run_issue_run_selection, sample_issue_run_selection, run_review_run_selection, tab_selected, current_selection):
        trigger = ctx.triggered_id

        if trigger == 'review-tabs':
            if tab_selected == 'run-review-module-issues':
                return "NoFilter"
            if tab_selected == 'run-review-module-lane-issues':
                return "NoFilter"
            else:
                return current_selection

        if trigger == 'run-issue-run-options':
            if trigger == None:
                return "NoFilter"
            return run_issue_run_selection
        elif trigger == 'sample-issue-run-options':
            if sample_issue_run_selection == None:
                return "NoFilter"
            return sample_issue_run_selection
        elif trigger == 'run-review-run-selector':
            if run_review_run_selection == None:
                return "NoFilter"
            return run_review_run_selection

    @app.callback([Output('lane-issue-lane-options', 'options'),
                   Output('sample-issue-lane-options', 'options'),
                   Output('run-review-lane-selector', 'options')],
                  Input('runset-xpcrmodulelane-options', 'data'))
    def update_lane_options(data):
        return data, data, data

    @app.callback([Output('lane-issue-lane-options', 'value'),
                   Output('sample-issue-lane-options', 'value'),
                   Output('run-review-lane-selector', 'value')],
                  Input('xpcrmodulelane-selected', 'data'), prevent_initial_call=True)
    def update_lane_option_selected(data):
        return data, data, data

    @app.callback(Output('xpcrmodulelane-selected', 'data'),
                  [Input('lane-issue-lane-options', 'value'),
                   Input('sample-issue-lane-options', 'value'),
                   Input('run-review-lane-selector', 'value'),
                   Input('review-tabs', 'active_tab'),
                   State('xpcrmodulelane-selected', 'data')], prevent_initial_call=True
                  )
    def update_lane_option_selections(lane_issue_lane_selection, sample_issue_lane_selection, run_review_lane_selection, tab_selected, current_selection):
        trigger = ctx.triggered_id

        if trigger == 'review-tabs':
            if tab_selected == 'run-review-module-issues':
                return "NoFilter"
            if tab_selected == 'run-review-run-issues':
                return "NoFilter"
            else:
                return current_selection

        if trigger == 'lane-issue-lane-options':
            if lane_issue_lane_selection == None:
                return "NoFilter"
            return lane_issue_lane_selection
        elif trigger == 'sample-issue-lane-options':
            if sample_issue_lane_selection == None:
                return "NoFilter"
            return sample_issue_lane_selection
        elif trigger == 'run-review-lane-selector':
            if run_review_lane_selection == None:
                return "NoFilter"
            return run_review_lane_selection

    @app.callback(Output('run-review-run-selector', 'disabled'),
                  Input('review-tabs', 'active_tab')
                  )
    def control_run_selector_validity(tab_selected):

        if tab_selected in ['run-review-module-issues', 'run-review-module-lane-issues']:
            return True
        else:
            return False

    @app.callback(Output('run-review-lane-selector', 'disabled'),
                  Input('review-tabs', 'active_tab')
                  )
    def control_lane_selector_validity(tab_selected):

        if tab_selected in ['run-review-module-issues', 'run-review-run-issues']:
            return True
        else:
            return False

    @app.callback(Output('issue-post-response', 'is_open'),
                  [Input('submit-module-issue', 'n_clicks'),
                   Input('submit-run-issue', 'n_clicks'),
                   Input('submit-lane-issue', 'n_clicks'),
                   Input('submit-sample-issue', 'n_clicks'),
                   State('issue-post-response', 'is_open'),
                   State('runset-review-id', 'data'),
                   State('channel-selected', 'data'),
                   State('severity-selected', 'data')], prevent_intial_call=True)
    def post_issue(mod_issue, run_issue, lane_issue, sample_issue, is_open, runset_review_id, channel_id, severity_id):

        if mod_issue:
            """
            Post information to Sample Issue Endpoint
            """

            """
            public Guid RunSetReviewReferrerId { get; set; }

            public Guid RunSetReviewResolverId { get; set; }

            public Guid SeverityRatingId { get; set; }

            public Guid AssayChannelId { get; set; }

            public Guid IssueTypeId { get; set; }

            public Guid SubjectId { get; set; }

            public Guid RunSetSubjectReferrerId { get; set; }
            """
            mod_issue_url = os.environ['RUN_REVIEW_API_BASE'] + \
                "XPCRModuleIssues"

            issue = {}
            issue['RunSetReviewReferrerId'] = runset_review_id
            issue['RunSetReviewResolverId'] = runset_review_id
            issue['SeverityRatingId'] = severity_id
            issue['AssayChannelId'] = channel_id
            # issue['IssueTypeId'] =
            # issue['SubjectId'] =
            # issue['RunSetSubjectReferrerId'] =
            # requests.post(url=mod_issue_url, json=issue, verify=False)

            print(issue)

        if sample_issue:
            """
            Post information to Sample Issue Endpoint
            """
            print('test')

        if mod_issue or run_issue or lane_issue or sample_issue:
            return not is_open

        return is_open

    return app.server


if __name__ == '__main__':

    app = Dash(__name__, use_pages=True, pages_folder="run-review-pages",
               url_base_pathname=url_base, external_stylesheets=[dbc.themes.COSMO])
    app.layout = html.Div([review_loader, dcc.Location(
        id="run-review-url"), sidebar, content])
    app.run_server(debug=True)
