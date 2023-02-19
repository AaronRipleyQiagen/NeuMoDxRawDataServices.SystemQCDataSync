from flask import session
from dash import Input, Output, dcc, html, no_update, ctx
import dash_bootstrap_components as dbc
from dash import Dash
from .appbuildhelpers import apply_layout_with_auth
from dash import html, callback, Output, Input, State, register_page, dcc, dash_table, page_container
from .functions import populate_review_queue, getSampleDataAsync, SampleJSONReader, save_uploaded_file_to_blob_storage, add_item_to_carousel
import os
import requests
import json
import pandas as pd
import numpy as np
import warnings
import plotly.graph_objects as go
import aiohttp
import asyncio
import base64
import uuid


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
    id='runset-selection-data', storage_type='session', data='')
runset_sample_data = dcc.Store(
    id='runset-sample-data', storage_type='session', data='')
runset_review_id = dcc.Store(
    id='runset-review-id', storage_type='session', data='')

runset_channel_options = dcc.Store(
    id='runset-channel-options', storage_type='session', data='')
channel_selected = dcc.Store(
    id='channel-selected', storage_type='session', data='')
spc_channel = dcc.Store(id='spc-channel', storage_type='session', data='')

runset_severity_options = dcc.Store(
    id='runset-severity-options', storage_type='session', data='')

severity_selected = dcc.Store(
    id='severity-selected', storage_type='session', data='')

runset_run_options = dcc.Store(
    id='runset-run-options', storage_type='session', data='')
run_option_selected = dcc.Store(
    id='run-option-selected', storage_type='session', data='')

runset_xpcrmodulelane_options = dcc.Store(
    id='runset-xpcrmodulelane-options', storage_type='session', data='')
xpcrmodulelane_selected = dcc.Store(
    id='xpcrmodulelane-selected', storage_type='session', data='')
xpcrmodule_options = dcc.Store(
    id='xpcrmodule-options', storage_type='session', data='')
xpcrmodule_selected = dcc.Store(
    id='xpcrmodule-selected', storage_type='session', data='')
runset_subject_ids = dcc.Store(
    id='runset-subject-ids', storage_type='session', data='')
runset_subject_descriptions = dcc.Store(
    id='runset-subject-descriptions', storage_type='session')

pcrcurve_sample_info = dcc.Store(
    id='pcrcurve-sample-info', storage_type='session')

issue_selected = dcc.Store(id='issue-selected', storage_type='session')
flat_data_download = dcc.Download(id="flat-data-download")

remediation_action_selection = dcc.Store(
    id='remediation-action-selection', storage_type='session')

related_runsets = dcc.Store(id='related-runsets', storage_type='session')

layout = html.Div([review_loader, dcc.Loading(id='run-review-href-loader', fullscreen=True, type='dot', children=[dcc.Location(
    id="run-review-url", refresh=True)]), sidebar, content,
    runset_selection, runset_sample_data, runset_review_id, runset_severity_options,
    runset_channel_options, channel_selected, runset_run_options, run_option_selected,
    spc_channel, runset_xpcrmodulelane_options, xpcrmodulelane_selected, severity_selected,
    runset_subject_ids, xpcrmodule_options, xpcrmodule_selected, pcrcurve_sample_info, issue_selected, runset_subject_descriptions, flat_data_download, remediation_action_selection, related_runsets])


def Add_Dash(app):
    app = Dash(__name__, server=app,
               url_base_pathname=url_base,
               use_pages=True, pages_folder="pages", external_stylesheets=[dbc.themes.COSMO])

    apply_layout_with_auth(app, layout)

    @app.callback([Output('review-queue-table', 'rowData'), Output('review-queue-table', 'columnDefs')],
                  [Input('refresh-review-queue', 'n_clicks')])
    def refresh_review_queue(n):
        intial_data, initial_columnDefs = populate_review_queue(
            session['user'].id)
        return intial_data, initial_columnDefs

    @app.callback(Output('runset-selection-data', 'data'),
                  [Input('review-queue-table', 'selectionChanged')])
    def get_runset_selection_data(selected):
        if selected == None:
            return no_update
        runsetsample_url = os.environ['RUN_REVIEW_API_BASE'] + \
            "RunSets/{}/Samples".format(selected[0]['id'])
        _runset_samples = requests.get(runsetsample_url, verify=False).json()
        return _runset_samples

    @app.callback([Output("runset-sample-data", "data"),
                   Output("run-review-url", "href"),
                   Output('runset-review-id', 'data'),
                   Output('runset-severity-options', 'data'),
                   Output('runset-channel-options', 'data'),
                   Output('runset-run-options', 'data'),
                   Output('spc-channel', 'data'),
                   Output('runset-xpcrmodulelane-options', 'data'),
                   Output('runset-subject-ids', 'data'),
                   Output('xpcrmodule-options', 'data'),
                   Output('runset-subject-descriptions', 'data')],
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
        runset_map_df = pd.DataFrame(columns=['RawDataDatabaseId',
                                              'RunSetSampleId', 'SampleId',
                                              'XPCRModuleLaneId', 'RunSetXPCRModuleLaneId',
                                              'CartridgeId', 'RunSetCartridgeId',
                                              'XPCRModuleId', 'RunSetXPCRModuleId',
                                              'NeuMoDxSystemId', 'RunSetNeuMoDxSystemId'])
        idx = 0
        for runsetsample in runset_data['runSetSamples']:
            runset_sample_ids.append(
                runsetsample['sample']['rawDataDatabaseId'])

            runset_map = [runsetsample['sample']['rawDataDatabaseId'],
                          runsetsample['id'],
                          runsetsample['sample']['id'],
                          runsetsample['sample']['xpcrModuleLaneId'],
                          runsetsample['sample']['runSetXPCRModuleLaneSamples'][0]['runSetXPCRModuleLaneId'],
                          runsetsample['sample']['cartridgeId'],
                          runsetsample['sample']['runSetCartridgeSamples'][0]['runSetCartridgeId'],
                          runsetsample['sample']['xpcrModuleId'],
                          runsetsample['sample']['runSetXPCRModuleSamples'][0]['runSetXPCRModuleId'],
                          runsetsample['sample']['neuMoDxSystemId'],
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

        # dataframe.to_csv('test.csv')

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

        """
        Create RunSetSubject / Subject Dictionary
        """
        runset_subject_ids = {}
        runset_subject_descriptions = {}
        runset_sample_subject_ids_dict = {}
        runset_sample_subject_ids_descriptions = {}
        for idx in dataframe.drop_duplicates(subset=['RunSetSampleId', 'SampleId']).index:
            runset_sample_subject_ids_dict[dataframe.loc[idx, 'RunSetSampleId']
                                           ] = dataframe.loc[idx, 'SampleId']
            runset_sample_subject_ids_descriptions[dataframe.loc[idx, 'RunSetSampleId']
                                                   ] = str(dataframe.loc[idx, 'Sample ID'])

        runset_subject_ids['Sample'] = runset_sample_subject_ids_dict
        runset_subject_descriptions['Sample'] = runset_sample_subject_ids_descriptions

        runset_xpcrmodulelane_subject_ids_dict = {}
        runset_xpcrmodulelane_subject_ids_descriptions = {}

        for idx in dataframe.drop_duplicates(subset=['RunSetXPCRModuleLaneId', 'XPCRModuleLaneId']).index:
            runset_xpcrmodulelane_subject_ids_dict[dataframe.loc[idx, 'RunSetXPCRModuleLaneId']
                                                   ] = dataframe.loc[idx, 'XPCRModuleLaneId']
            runset_xpcrmodulelane_subject_ids_descriptions[dataframe.loc[idx, 'RunSetXPCRModuleLaneId']
                                                           ] = dataframe.loc[idx, 'XPCR Module Serial'] + " Lane " + str(dataframe.loc[idx, 'XPCR Module Lane'])

        runset_subject_ids['XPCRModuleLane'] = runset_xpcrmodulelane_subject_ids_dict
        runset_subject_descriptions['XPCR Module Lane'] = runset_xpcrmodulelane_subject_ids_descriptions

        runset_cartridge_subject_ids_dict = {}
        runset_cartridge_subject_id_descriptions = {}
        for idx in dataframe.drop_duplicates(subset=['RunSetCartridgeId', 'CartridgeId']).index:
            runset_cartridge_subject_ids_dict[dataframe.loc[idx, 'RunSetCartridgeId']
                                              ] = dataframe.loc[idx, 'CartridgeId']
            runset_cartridge_subject_id_descriptions[dataframe.loc[idx, 'RunSetCartridgeId']
                                                     ] = "Run "+str(dataframe.loc[idx, 'Run'])

        runset_subject_ids['Cartridge'] = runset_cartridge_subject_ids_dict
        runset_subject_descriptions['Run'] = runset_cartridge_subject_id_descriptions

        runset_xpcrmodule_subject_ids_dict = {}
        runset_xpcrmodule_descriptions = {}
        xpcrmodule_options = {}
        xpcrmodule_options['NoFilter'] = 'All'

        for idx in dataframe.drop_duplicates(subset=['RunSetXPCRModuleId', 'XPCRModuleId']).index:
            runset_xpcrmodule_subject_ids_dict[dataframe.loc[idx, 'RunSetXPCRModuleId']
                                               ] = dataframe.loc[idx, 'XPCRModuleId']
            xpcrmodule_options[dataframe.loc[idx, 'RunSetXPCRModuleId']
                               ] = dataframe.loc[idx, 'XPCR Module Serial']
            runset_xpcrmodule_descriptions[dataframe.loc[idx, 'RunSetXPCRModuleId']
                                           ] = dataframe.loc[idx, 'XPCR Module Serial']

        runset_subject_ids['XPCRModule'] = runset_xpcrmodule_subject_ids_dict
        runset_subject_descriptions['XPCR Module'] = runset_xpcrmodule_descriptions

        runset_neumodx_subject_ids_dict = {}
        for idx in dataframe.drop_duplicates(subset=['RunSetNeuMoDxSystemId', 'NeuMoDxSystemId']).index:
            runset_neumodx_subject_ids_dict[dataframe.loc[idx, 'RunSetNeuMoDxSystemId']
                                            ] = dataframe.loc[idx, 'NeuMoDxSystemId']

        runset_subject_ids['NeuMoDxSystem'] = runset_neumodx_subject_ids_dict

        return dataframe.to_dict('records'), '/dashboard/run-review/view-results', resp['id'], severity_options, channel_options, run_options, spc_channel, lane_options, runset_subject_ids, xpcrmodule_options, runset_subject_descriptions

    @ app.callback([Output('sample-issue-options', 'options'), Output('lane-issue-options', 'options'), Output('module-issue-options', 'options'), Output('run-issue-options', 'options')],
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

    @ app.callback([Output('sample-issue-severity-options', 'options'),
                   Output('lane-issue-severity-options', 'options'),
                   Output('run-issue-severity-options', 'options'),
                   Output('module-issue-severity-options', 'options')
                    ],
                   Input('runset-severity-options', 'data'))
    def update_severity_options(data):
        return data, data, data, data

    @ app.callback(Output('severity-selected', 'data'),
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

    @ app.callback([Output('sample-issue-severity-options', 'value'),
                   Output('lane-issue-severity-options', 'value'),
                   Output('run-issue-severity-options', 'value'),
                   Output('module-issue-severity-options', 'value')],
                   Input('severity-selected', 'data'), prevent_initial_call=True)
    def update_channel_selection_value(channel):
        return channel, channel, channel, channel

    @ app.callback([
        Output('run-review-curves', 'figure'),
        Output('runset-sample-results', 'data'),
        Output('pcrcurve-sample-info', 'data')],
        [Input('channel-selected', 'data'),
         Input('run-review-process-step-selector', 'value'),
         Input('run-review-color-selector', 'value'),
         State('runset-sample-data', 'data'),
         State('runset-selection-data', 'data'),
         State('runset-channel-options', 'data'),
         Input('xpcrmodulelane-selected', 'data'),
         Input('run-option-selected', 'data'),
         Input('issue-selected', 'data')], prevent_intial_call=True)
    def update_pcr_curves(channel_selected, process_step, color_option_selected, data, runset_data, channel_options, lane_selection, run_selection, issue_selected):
        try:
            if ctx.triggered_id == 'issue-selected':
                channel = issue_selected['Channel']
                dataframe = pd.DataFrame.from_dict(data)
                dataframe['Channel'] = dataframe['Channel'].replace(
                    'Far_Red', 'Far Red')
                fig = go.Figure()
                df = dataframe.reset_index().set_index(
                    ['Channel', 'Processing Step', 'XPCR Module Serial'])
                df_Channel = df.loc[channel]
                if issue_selected['RunSetId'] == runset_data['id']:
                    if issue_selected['Level'] == 'Sample':
                        df_Channel = df_Channel[df_Channel['RunSetSampleId']
                                                == issue_selected['RunSetSubjectReferrerId']]
                    elif issue_selected['Level'] == 'XPCR Module Lane':
                        df_Channel = df_Channel[df_Channel['XPCRModuleLaneId']
                                                == issue_selected['SubjectId']]
                    elif issue_selected['Level'] == 'Run':
                        df_Channel = df_Channel[df_Channel['CartridgeId']
                                                == issue_selected['SubjectId']]
                    elif issue_selected['Level'] == 'XPCR Module':
                        df_Channel = df_Channel[df_Channel['XPCRModuleId']
                                                == issue_selected['SubjectId']]
                else:
                    if issue_selected['Level'] == 'Sample':
                        df_Channel = df_Channel[df_Channel['XPCRModuleLaneId']
                                                == issue_selected['SubjectId']]
                    elif issue_selected['Level'] == 'XPCR Module Lane':
                        df_Channel = df_Channel[df_Channel['XPCRModuleLaneId']
                                                == issue_selected['SubjectId']]
                    elif issue_selected['Level'] == 'Run':
                        df_Channel = df_Channel[df_Channel['XPCRModuleId']
                                                == issue_selected['SubjectId']]
                        print(df_Channel)
                    elif issue_selected['Level'] == 'XPCR Module':
                        df_Channel = df_Channel[df_Channel['XPCRModuleId']
                                                == issue_selected['SubjectId']]

            else:
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

            samples_selected = []
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
                sample_info = {}
                sample_info['RunSetSampleId'] = df_Channel_Step.loc[idx,
                                                                    'RunSetSampleId']
                sample_info['SampleId'] = df_Channel_Step.loc[idx, 'SampleId']
                samples_selected.append(sample_info)

            return fig, df_Channel_Step[['XPCR Module Serial', 'XPCR Module Lane', 'Sample ID', 'Target Name', 'Localized Result', 'Overall Result', 'Ct', 'End Point Fluorescence', 'Max Peak Height', 'EPR']].round(1).to_dict('records'), samples_selected
        except:
            return no_update

    @ app.callback([Output('sample-issue-channel-options', 'options'),
                   Output('lane-issue-channel-options', 'options'),
                   Output('run-issue-channel-options', 'options'),
                   Output('module-issue-channel-options', 'options'),
                   Output('run-review-channel-selector', 'options')],
                   Input('runset-channel-options', 'data'))
    def update_channel_options(data):
        return data, data, data, data, data

    @ app.callback(Output('channel-selected', 'data'),
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

    @ app.callback([Output('sample-issue-channel-options', 'value'),
                   Output('lane-issue-channel-options', 'value'),
                   Output('run-issue-channel-options', 'value'),
                   Output('module-issue-channel-options', 'value'),
                   Output('run-review-channel-selector', 'value')],
                   Input('channel-selected', 'data'), prevent_initial_call=True)
    def update_channel_selection_value(channel):
        return channel, channel, channel, channel, channel

    @ app.callback([Output('run-issue-run-options', 'options'),
                   Output('sample-issue-run-options', 'options'),
                   Output('run-review-run-selector', 'options')],
                   Input('runset-run-options', 'data'))
    def update_run_options(data):
        return data, data, data

    @ app.callback([Output('run-issue-run-options', 'value'),
                   Output('sample-issue-run-options', 'value'),
                   Output('run-review-run-selector', 'value')],
                   Input('run-option-selected', 'data'), prevent_initial_call=True)
    def update_run_option_selected(data):
        return data, data, data

    @ app.callback(Output('run-option-selected', 'data'),
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
            if tab_selected == 'run-review-line-data':
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

    @ app.callback([Output('lane-issue-lane-options', 'options'),
                   Output('sample-issue-lane-options', 'options'),
                   Output('run-review-lane-selector', 'options')],
                   Input('runset-xpcrmodulelane-options', 'data'))
    def update_lane_options(data):
        return data, data, data

    @ app.callback([Output('lane-issue-lane-options', 'value'),
                   Output('sample-issue-lane-options', 'value'),
                   Output('run-review-lane-selector', 'value')],
                   Input('xpcrmodulelane-selected', 'data'), prevent_initial_call=True)
    def update_lane_option_selected(data):
        return data, data, data

    @ app.callback(Output('xpcrmodulelane-selected', 'data'),
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
            if tab_selected == 'run-review-line-data':
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

    @ app.callback(Output('run-review-run-selector', 'disabled'),
                   Input('review-tabs', 'active_tab')
                   )
    def control_run_selector_validity(tab_selected):

        if tab_selected in ['run-review-module-issues', 'run-review-module-lane-issues', 'run-review-active-issues']:
            return True
        else:
            return False

    @ app.callback(Output('run-review-lane-selector', 'disabled'),
                   Input('review-tabs', 'active_tab')
                   )
    def control_lane_selector_validity(tab_selected):

        if tab_selected in ['run-review-module-issues', 'run-review-run-issues', 'run-review-active-issues']:
            return True
        else:
            return False

    @ app.callback(Output('run-review-xpcrmodule-selector', 'disabled'),
                   Input('review-tabs', 'active_tab')
                   )
    def control_module_selector_validity(tab_selected):

        if tab_selected in ['run-review-active-issues']:
            return True
        else:
            return False

    @ app.callback(Output('run-review-channel-selector', 'disabled'),
                   Input('review-tabs', 'active_tab')
                   )
    def control_channel_selector_validity(tab_selected):

        if tab_selected in ['run-review-active-issues']:
            return True
        else:
            return False

    @ app.callback([Output('module-issue-module-options', 'options'),
                   Output('run-issue-module-options', 'options'),
                   Output('lane-issue-module-options', 'options'),
                   Output('sample-issue-module-options', 'options'),
                   Output('run-review-xpcrmodule-selector', 'options')],
                   Input('xpcrmodule-options', 'data'))
    def update_run_options(data):
        return data, data, data, data, data

    @ app.callback(Output('xpcrmodule-selected', 'data'),
                   [Input('module-issue-module-options', 'value'),
                    Input('run-issue-module-options', 'value'),
                    Input('lane-issue-module-options', 'value'),
                    Input('sample-issue-module-options', 'value'),
                    Input('run-review-xpcrmodule-selector', 'value')], prevent_initial_call=True
                   )
    def update_lane_option_selections(module_issue_mod_selection, run_issue_mod_selection, lane_issue_mod_selection, sample_issue_mod_selection, run_review_mod_selection):
        trigger = ctx.triggered_id
        if trigger == 'module-issue-module-options':
            if module_issue_mod_selection == None:
                return "NoFilter"
            return module_issue_mod_selection
        elif trigger == 'run-issue-module-options':
            if run_issue_mod_selection == None:
                return "NoFilter"
            return run_issue_mod_selection
        elif trigger == 'lane-issue-module-options':
            if lane_issue_mod_selection == None:
                return "NoFilter"
            return lane_issue_mod_selection
        elif trigger == 'sample-issue-module-options':
            if sample_issue_mod_selection == None:
                return "NoFilter"
            return sample_issue_mod_selection
        elif trigger == 'run-review-xpcrmodule-selector':
            if run_review_mod_selection == None:
                return "NoFilter"
            return run_review_mod_selection

    @ app.callback([Output('module-issue-module-options', 'value'),
                    Output('run-issue-module-options', 'value'),
                    Output('lane-issue-module-options', 'value'),
                    Output('sample-issue-module-options', 'value'),
                    Output('run-review-xpcrmodule-selector', 'value')],
                   Input('xpcrmodule-selected', 'data'), prevent_initial_call=True)
    def update_lane_option_selected(data):
        return data, data, data, data, data

    @ app.callback([Output('issue-post-response', 'is_open'),
                   Output('submit-module-issue', 'n_clicks'),
                   Output('submit-run-issue', 'n_clicks'),
                   Output('submit-lane-issue', 'n_clicks'),
                   Output('submit-sample-issue', 'n_clicks')],
                   [Input('submit-module-issue', 'n_clicks'),
                   Input('submit-run-issue', 'n_clicks'),
                   Input('submit-lane-issue', 'n_clicks'),
                   Input('submit-sample-issue', 'n_clicks'),
                   State('issue-post-response', 'is_open'),
                   State('runset-review-id', 'data'),
                   State('channel-selected', 'data'),
                   State('severity-selected', 'data'),
                   State('module-issue-options', 'value'),
                   State('runset-subject-ids', 'data'),
                   State('xpcrmodule-selected', 'data'),
                   State('run-issue-options', 'value'),
                   State('run-option-selected', 'data'),
                   State('lane-issue-options', 'value'),
                   State('xpcrmodulelane-selected', 'data'),
                   State('sample-issue-options', 'value'),
                   State('pcrcurve-sample-info', 'data')], prevent_intial_call=True)
    def post_issue(mod_issue, run_issue, lane_issue, sample_issue, is_open, runset_review_id, channel_id, severity_id, module_issue_id, runset_subject_ids, xpcrmodule_selected, run_issue_id, run_selected, lane_issue_id, lane_selected, sample_issue_id, samples_selected):
        print("attempting post.")

        issue = {}
        issue['userId'] = session['user'].id
        issue['runSetReviewReferrerId'] = runset_review_id
        issue['runSetReviewResolverId'] = '00000000-0000-0000-0000-000000000000'
        issue['severityRatingId'] = severity_id
        issue['assayChannelId'] = channel_id

        if mod_issue:
            """
            Post information to XPCR Module Issue Endpoint
            """
            issue['issueTypeId'] = module_issue_id
            issue['subjectId'] = runset_subject_ids['XPCRModule'][xpcrmodule_selected]
            issue['runSetSubjectReferrerId'] = xpcrmodule_selected
            mod_issue_url = os.environ['RUN_REVIEW_API_BASE'] + \
                "XPCRModuleIssues"
            requests.post(url=mod_issue_url, json=issue, verify=False)

        if run_issue:
            """
            Post information to XPCR Module Issue Endpoint
            """
            issue['issueTypeId'] = run_issue_id
            issue['subjectId'] = runset_subject_ids['Cartridge'][run_selected]
            issue['runSetSubjectReferrerId'] = run_selected
            cartridge_issue_url = os.environ['RUN_REVIEW_API_BASE'] + \
                "CartridgeIssues"
            requests.post(url=cartridge_issue_url, json=issue, verify=False)

        if lane_issue:
            """
            Post information to XPCR Module Issue Endpoint
            """
            issue['issueTypeId'] = lane_issue_id
            issue['subjectId'] = runset_subject_ids['XPCRModuleLane'][lane_selected]
            issue['runSetSubjectReferrerId'] = lane_selected
            lane_issue_url = os.environ['RUN_REVIEW_API_BASE'] + \
                "XPCRModuleLaneIssues"
            print(issue)
            requests.post(url=lane_issue_url, json=issue, verify=False)

        if sample_issue:
            """
            Post information to XPCR Module Issue Endpoint
            """
            issue['issueTypeId'] = sample_issue_id
            issue['subjectId'] = samples_selected[0]['SampleId']
            issue['runSetSubjectReferrerId'] = samples_selected[0]['RunSetSampleId']
            sample_issue_url = os.environ['RUN_REVIEW_API_BASE'] + \
                "SampleIssues"
            requests.post(url=sample_issue_url, json=issue, verify=False)

        if mod_issue or run_issue or lane_issue or sample_issue:
            return not is_open, None, None, None, None

        return is_open, None, None, None, None

    @app.callback([Output('issues-table', 'rowData'),
                   Output('issues-table', 'columnDefs')],
                  [Input('review-tabs', 'active_tab'),
                   State('runset-selection-data', 'data'),
                   State('runset-subject-descriptions', 'data'),
                   State('related-runsets', 'data')])
    def get_active_runset_issues(tab_selected, runset_selection_data, runset_subject_descriptions, related_runsets):

        if tab_selected in ['run-review-active-issues']:
            """
            1. Call API Endpoint to get active issue data.
            """
            issue_dataframe = pd.DataFrame(columns=[
                                           'Attempt', 'Level', 'Status', 'Severity', 'Channel', 'Reviewer Name', 'Type', 'ChannelId', 'IssueTypeId', 'RunSetSubjectReferrerId', 'SubjectId', 'RunSetId'])

            idx = 0
            for runset_id in related_runsets:
                runset_issues_url = os.environ['RUN_REVIEW_API_BASE'] + \
                    "RunSets/{}/issues".format(runset_id)

                runset_data = requests.get(
                    url=runset_issues_url, verify=False).json()

                for runset_review in runset_data['runSetReviews']:
                    reviewer_name = runset_review['reviewerName']
                    reviewerEmail = runset_review['reviewerEmail']

                    issue_levels = {'Sample': 'sampleIssuesReferred',
                                    'XPCR Module Lane': 'xpcrModuleLaneIssuesReferred',
                                    'Run': 'cartridgeIssuesReferred',
                                    'XPCR Module': 'xpcrModuleIssuesReferred'}

                    for issue_level in issue_levels:
                        for issue in runset_review[issue_levels[issue_level]]:
                            attempt = related_runsets[runset_id]
                            # description = runset_subject_descriptions[
                            #     issue_level][issue['runSetSubjectReferrerId']]
                            severity = issue['severityRating']['name']
                            channel = issue['assayChannel']['channel']
                            status = issue['issueStatus']['name']
                            channel_id = issue['assayChannel']['id']
                            issue_type = issue['issueType']['name']
                            issue_type_id = issue['issueType']['id']
                            subject_referrer_id = issue['runSetSubjectReferrerId']

                            if runset_id == runset_selection_data['id']:
                                """
                                If the runset is the one being displayed, we can just use the subject id.
                                """
                                subject_id = issue['subjectId']

                            else:
                                """
                                If the runset is not the one being displayed,
                                we need to sometimes use something more generic because the 
                                subject id might not be present in the dataset being displayed.
                                """
                                if issue_level == 'Sample':
                                    subject_id = issue['subject']['xpcrModuleLaneId']

                                elif issue_level == 'XPCR Module Lane':
                                    subject_id = issue['subjectId']

                                elif issue_level == 'Run':
                                    subject_id = issue['subject']['xpcrModuleId']

                                elif issue_level == 'XPCR Module':
                                    subject_id = issue['subjectId']

                            issue_entry = [attempt, issue_level, status, severity, channel, reviewer_name,
                                           issue_type, channel_id, issue_type_id, subject_referrer_id, subject_id, runset_id]
                            issue_dataframe.loc[idx] = issue_entry
                            idx += 1

            column_definitions = []
            for column in issue_dataframe.columns:
                if 'Id' not in column:
                    column_definitions.append(
                        {"headerName": column, "field": column, "filter": True})
                else:
                    column_definitions.append(
                        {"headerName": column, "field": column, "filter": True, "hide": True})

            return issue_dataframe.to_dict('records'), column_definitions
        else:
            return no_update

    @app.callback(Output('issue-selected', 'data'),
                  Input('issues-table', 'selectionChanged'), prevent_initial_call=True)
    def get_issue_selected(selected_row):
        if selected_row == None:
            return no_update
        return selected_row[0]

    @app.callback(Output('run-review-status-update-post-response', 'is_open'),
                  [Input('run-review-completed-button', 'n_clicks'),
                  State('run-review-status-update-post-response', 'is_open'),
                  State('runset-review-id', 'data'),
                  State('run-review-acceptance', 'value')], prevent_intital_call=True)
    def update_run_review_status(n, is_open, runset_review_id, run_review_acceptance):
        print("I ran :)"*30)
        if n:
            update_url = os.environ['RUN_REVIEW_API_BASE'] + \
                "RunSetReviews/{}".format(runset_review_id)
            query_params = {'acceptable': run_review_acceptance,
                            'newStatusName': 'Completed'}
            print(query_params)
            resp = requests.put(
                url=update_url, params=query_params, verify=False)
            print(resp.url)
            print(resp.status_code)
            return not is_open

        return is_open

    @app.callback([Output("flat-data-download", "data"),
                   Output("run-review-download-data", "n_clicks")],
                  [Input('run-review-download-data', 'n_clicks'),
                   State('runset-sample-data', 'data'),
                   State("runset-selection-data", "data")], prevent_initial_call=True)
    def download_function(n, data, runset_selection):
        if n:
            print("Downloading")
            data_output = pd.DataFrame.from_dict(data)
            print(data_output)
            data_output.set_index(
                ['Sample ID', 'Test Guid', 'Replicate Number', 'Processing Step', 'Channel'], inplace=True)
            data_output.drop(
                [x for x in data_output.columns if x[-2:] == 'Id' or "Array" in x], axis=1, inplace=True)

            return dcc.send_data_frame(data_output.reset_index().to_csv, runset_selection['id']+".csv", index=False), None
        return no_update, None

    @app.callback(Output('remediation-action-options', 'options'),
                  Input('remediation-action-selection', 'data'))
    def load_remediation_action_options(data):
        remediation_action_types_url = os.environ["RUN_REVIEW_API_BASE"] + \
            "RemediationActionTypes"
        remediation_actions = requests.get(
            url=remediation_action_types_url, verify=False).json()
        remediation_action_options = {}
        for remediation_action in remediation_actions:
            remediation_action_options[remediation_action['id']
                                       ] = remediation_action['name']

        return remediation_action_options

    @app.callback([Output("remediation-action-post-response", "is_open"),
                   Output("remediation-action-submit", "n_clicks")],
                  [Input("remediation-action-submit", "n_clicks"),
                   State("remediation-action-post-response", "is_open"),
                   State("runset-selection-data", "data"),
                   State("runset-review-id", "data"),
                   State("xpcrmodule-selected", "data"),
                   State("remediation-action-options", "value"),
                   State("runset-subject-ids", 'data')], prevent_inital_call=True)
    def post_remediation_action(n, is_open, runset_selection, runset_review_id, xpcr_module_runset_id, remediation_action_id, runset_subject_ids):

        if n:
            print("Run it Run it")
            remediation_action_payload = {"userId": session['user'].id,
                                          "neuMoDxSystemId": "00000000-0000-0000-0000-000000000000",
                                          "xpcrModuleId": runset_subject_ids['XPCRModule'][xpcr_module_runset_id],
                                          "runSetReferrerId": runset_selection['id'],
                                          "runSetResolverId": "00000000-0000-0000-0000-000000000000",
                                          "runSetReviewReferrerId": runset_review_id,
                                          "runSetReviewResolverId": "00000000-0000-0000-0000-000000000000",
                                          "remediationActionTypeId": remediation_action_id}
            print(remediation_action_payload)
            remediation_action_url = os.environ["RUN_REVIEW_API_BASE"] + \
                "RemediationActions"

            requests.post(url=remediation_action_url,
                          json=remediation_action_payload,
                          verify=False).json()
            return not is_open, None

        return is_open, None

    @app.callback([Output('remediation-action-table', 'rowData'),
                   Output('remediation-action-table', 'columnDefs')],
                  [Input('review-tabs', 'active_tab'),
                   State('xpcrmodule-selected', 'data'),
                   State('runset-subject-ids', 'data')])
    def get_remediation_actions(tab_selected, runset_xpcr_module_selection_id, runset_subject_ids):

        if tab_selected in ['run-review-remediation-actions'] and runset_xpcr_module_selection_id != 'NoFilter':
            """
            1. Call API Endpoint to get active issue data.
            """

            xpcrmodule_remediation_issues_url = os.environ['RUN_REVIEW_API_BASE'] + \
                "XPCRModules/{}/remediationactions".format(
                    runset_subject_ids['XPCRModule'][runset_xpcr_module_selection_id])
            xpcrmodule = requests.get(
                url=xpcrmodule_remediation_issues_url, verify=False).json()

            actions_dataframe = pd.DataFrame(
                columns=['Status', 'Action', 'Assigned By', 'Origin'])

            idx = 0
            for remediation_action in xpcrmodule['remediationActions']:
                status = remediation_action['remediationActionStatus']['name']
                action = remediation_action['remediationActionType']['name']
                assignee = remediation_action['runSetReviewReferrer']['reviewerName']
                origin = remediation_action['runSetReferrer']['name'] + \
                    " #" + str(remediation_action['runSetReferrer']['number'])
                actions_dataframe.loc[idx] = [status, action, assignee, origin]
                idx += 1
            column_definitions = []
            for column in actions_dataframe.columns:
                if 'Id' not in column:
                    column_definitions.append(
                        {"headerName": column, "field": column, "filter": True})
                else:
                    column_definitions.append(
                        {"headerName": column, "field": column, "filter": True, "hide": True})

            return actions_dataframe.to_dict('records'), column_definitions
        else:
            return no_update

    @app.callback(Output('cartridge-images', 'items'),
                  [Input('review-tabs', 'active_tab'),
                  State("runset-selection-data", "data")])
    def get_cartridge_pictures(active_tab, runset_selection):
        if active_tab == 'cartidge-pictures':
            items = []

            """
            Call API to determine Cartridge Picture Details (name, url etc)
            """

            runset_cartridge_pictures_url = os.environ['RUN_REVIEW_API_BASE'] + \
                "RunSets/{}/cartridgepictures".format(runset_selection['id'])

            print(runset_cartridge_pictures_url)

            runset_cartridge_picture_response = requests.get(
                url=runset_cartridge_pictures_url, verify=False).json()

            for cartridge_picture in runset_cartridge_picture_response['cartridgePictures']:
                item = add_item_to_carousel(
                    title="Some ID",
                    description="Some Photo",
                    container_name="neumodxsystemqc-cartridgepictures",
                    blob_name=cartridge_picture['fileid'],
                )
                items.append(item)
            return items

        else:
            return no_update

    @ app.callback(
        Output('upload-cartridge-message', 'children'),
        [Input('upload-cartridge-pictures', 'contents')],
        [State('upload-cartridge-pictures', 'filename'),
         State("runset-selection-data", "data"),
         State("runset-review-id", "data")])
    def upload_cartridge_image_to_blob_storage(list_of_contents, list_of_filenames, runset_selection, runset_review_id):

        if list_of_contents:
            files = {list_of_filenames[i]: list_of_contents[i]
                     for i in range(len(list_of_filenames))}
            upload_status = []
            for file in files:

                """
                Upload file to blob storage
                """
                content_type, content_string = files[file].split(',')
                file_content = base64.b64decode(content_string)
                file_id = str(uuid.uuid4())+".jpg"
                file_url = save_uploaded_file_to_blob_storage(
                    file_content, file_id, 'neumodxsystemqc-cartridgepictures')
                """
                Create Database Entry
                """
                file_payload = {
                    "userId": session['user'].id,
                    "runSetId": runset_selection['id'],
                    "runSetReviewId": runset_review_id,
                    "uri": file_url,
                    "name": file,
                    "fileid": file_id
                }
                cartridge_picture_url = os.environ['RUN_REVIEW_API_BASE'] + \
                    "CartridgePictures"
                print(file_payload)
                resp = requests.post(
                    url=cartridge_picture_url, json=file_payload, verify=False)
                print(resp.status_code)
                upload_status.append(html.H4(file+" Uploaded successfully"))

            # Return a message with the URL of the uploaded file
            return upload_status

        else:
            return no_update

    @app.callback(Output('tadm-images', 'items'),
                  [Input('review-tabs', 'active_tab'),
                  State("runset-selection-data", "data")])
    def get_tadm_pictures(active_tab, runset_selection):
        if active_tab == 'tadm-pictures':
            items = []

            """
            Call API to determine Cartridge Picture Details (name, url etc)
            """

            runset_tadm_pictures_url = os.environ['RUN_REVIEW_API_BASE'] + \
                "RunSets/{}/tadmpictures".format(runset_selection['id'])

            print(runset_tadm_pictures_url)

            runset_tadm_picture_response = requests.get(
                url=runset_tadm_pictures_url, verify=False).json()

            for tadm_picture in runset_tadm_picture_response['tadmPictures']:
                item = add_item_to_carousel(
                    title="Some ID",
                    description="Some Photo",
                    container_name="neumodxsystemqc-tadmpictures",
                    blob_name=tadm_picture['fileid'],
                )
                items.append(item)
            return items

        else:
            return no_update

    @ app.callback(
        Output('upload-tadm-message', 'children'),
        [Input('upload-tadm-pictures', 'contents')],
        [State('upload-tadm-pictures', 'filename'),
         State("runset-selection-data", "data"),
         State("runset-review-id", "data")])
    def upload_tadm_image_to_blob_storage(list_of_contents, list_of_filenames, runset_selection, runset_review_id):

        if list_of_contents:
            files = {list_of_filenames[i]: list_of_contents[i]
                     for i in range(len(list_of_filenames))}
            upload_status = []
            for file in files:

                """
                Upload file to blob storage
                """
                content_type, content_string = files[file].split(',')
                file_content = base64.b64decode(content_string)
                file_id = str(uuid.uuid4())+".jpg"
                file_url = save_uploaded_file_to_blob_storage(
                    file_content, file_id, 'neumodxsystemqc-tadmpictures')
                """
                Create Database Entry
                """
                file_payload = {
                    "userId": session['user'].id,
                    "runSetId": runset_selection['id'],
                    "runSetReviewId": runset_review_id,
                    "uri": file_url,
                    "name": file,
                    "fileid": file_id
                }
                tadm_picture_url = os.environ['RUN_REVIEW_API_BASE'] + \
                    "TADMPictures"
                print(file_payload)
                resp = requests.post(
                    url=tadm_picture_url, json=file_payload, verify=False)
                print(resp.status_code)
                upload_status.append(html.Br(file+" Uploaded successfully"))

            # Return a message with the URL of the uploaded file
            return upload_status

        else:
            return no_update

    @ app.callback([Output('runset-description', 'children'), Output('related-runsets', 'data')],
                   Input("runset-selection-data", "data"))
    def update_runset_description(runset_selection):
        """
        Get The RunSetXPCRModules associated with the XPCR Module of Interest.
        """
        runset_xpcrmodules_url = os.environ["RUN_REVIEW_API_BASE"] + \
            "RunSets/{}/runsetxpcrmodules".format(runset_selection['id'])
        runset_xpcrmodules = requests.get(
            url=runset_xpcrmodules_url, verify=False).json()['runSetXPCRModules']

        if len(runset_xpcrmodules) == 1:

            """
            Get Runsets associated with XPCR Module
            """

            xpcrmodule_runsets_url = os.environ['RUN_REVIEW_API_BASE'] + \
                "XPCRModules/{}/runsets".format(
                    runset_xpcrmodules[0]['xpcrModule']['id'])
            xpcrmodule = requests.get(
                url=xpcrmodule_runsets_url, verify=False).json()

            """
            Get Related runset basic info (by xpcr module & runset type match)
            """
            xpcrmodule_runsets_df = pd.DataFrame(
                columns=[x for x in xpcrmodule['runSetXPCRModules'][0]['runSet']])

            idx = 0
            for xpcrmodule_runset in xpcrmodule['runSetXPCRModules']:
                if xpcrmodule_runset['runSet']['runSetTypeId'] == runset_selection['runSetTypeId']:
                    xpcrmodule_runsets_df.loc[idx] = xpcrmodule_runset['runSet']
                    idx += 1

            """
            Determine the attempt for this runset type for this particular module. 
            """

            xpcrmodule_runsets_df = xpcrmodule_runsets_df.sort_values(
                'runSetStartDate').reset_index(drop=True)

            xpcrmodule_runset_number = xpcrmodule_runsets_df[
                xpcrmodule_runsets_df['id'] == runset_selection['id']].index.values[0] + 1

            """
            Save Related RunSetIds in a dictionary for later reference
            """

            related_xpcrmodule_runsets = {}

            i = 1
            for idx in xpcrmodule_runsets_df.index:
                related_xpcrmodule_runsets[xpcrmodule_runsets_df.loc[idx, 'id']] = i
                i += 1

            return runset_selection['name'] + " Attempt # " + str(xpcrmodule_runset_number), related_xpcrmodule_runsets

        else:
            return no_update

    return app.server


if __name__ == '__main__':

    app = Dash(__name__, use_pages=True, pages_folder="run-review-pages",
               url_base_pathname=url_base, external_stylesheets=[dbc.themes.COSMO])
    app.layout = html.Div([review_loader, dcc.Location(
        id="run-review-url"), sidebar, content])
    app.run_server(debug=True)
