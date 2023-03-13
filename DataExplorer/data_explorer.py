from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import dash
from .appbuildhelpers import apply_layout_with_auth
import pandas as pd
from flask import Flask, session
from flask_mail import Mail, Message
import json
from .neumodx_objects import *
import os
import requests

mod_qual_review_subscribers = {'Aaron': 'aaron.ripley@qiagen.com',
                               'Vik': 'viktoriah.slusher@qiagen.com',
                               'Catherine': 'catherine.couture@qiagen.com',
                               'David': 'david.edwin@qiagen.com'}

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
        dash.page_container, dcc.Loading(id='page-changing', fullscreen=True, type='dot', children=[dcc.Location(id="url", refresh=True)])],
)


def Add_Dash(app):
    app = Dash(__name__, server=app,
               url_base_pathname=url_base,
               use_pages=True, external_stylesheets=[dbc.themes.COSMO])
    server = app.server
    server.config['MAIL_SERVER'] = 'smtp.gmail.com'
    server.config['MAIL_PORT'] = 465
    server.config['MAIL_USERNAME'] = 'neumodxsystemqcdatasync@gmail.com'
    server.config['MAIL_PASSWORD'] = os.environ['EMAIL_PASSWORD']
    server.config['MAIL_USE_TLS'] = False
    server.config['MAIL_USE_SSL'] = True
    mail = Mail(app.server)
    apply_layout_with_auth(app, layout)

    @app.callback(Output('post-response', 'is_open'),
                  [Input('submit-button', 'n_clicks')],
                  [State('sample-info', 'data'), State('runset-type-options', 'value'), State('runset-type-options', 'options'), State('post-response', 'is_open')], prevent_initial_call=True)
    def create_run_review(submit_clicks, data, runset_type_selection_id, runset_type_selection_options, is_open):

        if submit_clicks:
            dataframe = pd.DataFrame.from_dict(data)
            dataframe.drop_duplicates(
                ['Test Guid', 'Replicate Number'], inplace=True)

            """
            This Block creates the run review dataset.
            """
            runset = {}
            runset['userId'] = session['user'].id
            runset['description'] = ""
            runset['number'] = 0
            runset['runSetStartDate'] = dataframe['Start Date Time'].astype(
                'datetime64[ms]').min().isoformat(timespec='milliseconds')
            runset['runSetEndDate'] = dataframe['End Date Time'].astype(
                'datetime64[ms]').max().isoformat(timespec='milliseconds')

            runset['runSetTypeId'] = runset_type_selection_id
            runset['samples'] = []

            for idx in dataframe.index:
                sample = {}

                sample['rawDataDatabaseId'] = dataframe.loc[idx,
                                                            'RawDataDatabaseId']
                sample['cosmosDatabaseId'] = dataframe.loc[idx, 'cosmosId']
                sample['neuMoDxSystem'] = NeuMoDxSystem(
                    dataframe.loc[[idx]]).create_object()
                sample['neuMoDxSystem']['RawDataDatabaseId'] = dataframe.loc[idx,
                                                                             'NeuMoDx System Id']
                sample['xpcrModule'] = XPCRModule(
                    dataframe.loc[[idx]]).create_object()
                sample['xpcrModule']['RawDataDatabaseId'] = dataframe.loc[idx,
                                                                          'XPCR Module Id']
                sample['cartridge'] = {}
                sample['cartridge']['barcode'] = dataframe.loc[idx,
                                                               'Cartridge Barcode']
                sample['cartridge']['lot'] = dataframe.loc[idx, 'Cartridge Lot']
                sample['cartridge']['serial'] = dataframe.loc[idx,
                                                              'Cartridge Serial']
                sample['cartridge']['expiration'] = dataframe.loc[idx,
                                                                  'Cartridge Expiration']
                sample['cartridge']['RawDataDatabaseId'] = dataframe.loc[idx,
                                                                         'Cartridge Id']

                sample['xpcrModuleLane'] = {}
                sample['xpcrModuleLane']['moduleLane'] = int(dataframe.loc[idx,
                                                                           'XPCR Module Lane'])
                sample['xpcrModuleLane']['RawDataDatabaseId'] = dataframe.loc[idx,
                                                                              'xpcrModuleLaneId']

                runset['samples'].append(sample)

                runset["parseRunSetNeuMoDxSystems"] = True
                runset["parseRunSetXPCRModules"] = True
                runset["parseRunSetCartridges"] = True
                runset["parseRunSetXPCRModuleLanes"] = True
            print(runset_type_selection_options)
            runset['samplecount'] = len(runset['samples'])
            runset['name'] = dataframe.loc[idx, 'XPCR Module Serial'] + " " + \
                runset_type_selection_options[runset_type_selection_id]

            with open("data.json", "w") as file:
                json.dump(runset, file)

            print("--"*30)
            resp = requests.post(url=os.environ['RUN_REVIEW_API_BASE'] +
                                 "RunSets", json=runset, verify=False)

            if os.environ['SEND_EMAILS'] == "Yes":
                if 'XPCR Module Qualification' in runset_type_selection_options[runset_type_selection_id]:
                    msg = Message(runset['name']+" Ready for review", sender='neumodxsystemqcdatasync@gmail.com',
                                  recipients=['aripley2008@gmail.com'])

                    with mail.connect() as conn:
                        for user in mod_qual_review_subscribers:
                            message = 'Hello '+user+", this message is sent to inform you that " + \
                                runset['name']+" is now ready for your review."
                            subject = runset['name']+" Ready for review"
                            msg = Message(recipients=[mod_qual_review_subscribers[user]],
                                          body=message,
                                          subject=subject,
                                          sender='neumodxsystemqcdatasync@gmail.com')

                            conn.send(msg)
        if submit_clicks:
            return not is_open
        return is_open
    return app.server
