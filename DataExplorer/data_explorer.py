from dash import Dash, html, dcc, Output, Input, State, ctx
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

system_qc_reviewers = {'Leanna': 'leanna.hoyer@qiagen.com',
                       'Jeremias': 'jeremias.lioi@qiagen.com'}
system_integration_reviewers = {'Catherine': 'catherine.couture@qiagen.com',
                                'Aaron': 'aaron.ripley@qiagen.com'}
engineering_reviewers = {'Vik': 'viktoriah.slusher@qiagen.com'}
admin_reviewers = {'David': 'david.edwin@qiagen.com'}

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

    @app.callback(Output('review-group-options', 'options'),
                  Output('created-runset-id', 'data'),
                  [Input('submit-button', 'n_clicks')],
                  [State('sample-info', 'data'),
                   State('runset-type-options', 'value'),
                   State('runset-type-options', 'options'),
                   State('post-response', 'is_open')], prevent_initial_call=True)
    def create_run_review(submit_clicks, data, runset_type_selection_id, runset_type_selection_options, is_open):
        reviewgroup_options = {}
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

            print("--"*30)
            resp = requests.post(url=os.environ['RUN_REVIEW_API_BASE'] +
                                 "RunSets", json=runset, verify=False)

            created_runset_id = resp.json()
            print("got created runset id "+created_runset_id)

            # if os.environ['SEND_EMAILS'] == "Yes":
            #     if 'XPCR Module Qualification' in runset_type_selection_options[runset_type_selection_id]:
            #         msg = Message(runset['name']+" Ready for review", sender='neumodxsystemqcdatasync@gmail.com',
            #                       recipients=['aripley2008@gmail.com'])

            #         with mail.connect() as conn:
            #             for user in mod_qual_review_subscribers:
            #                 message = 'Hello '+user+", this message is sent to inform you that " + \
            #                     runset['name']+" is now ready for your review."
            #                 subject = runset['name']+" Ready for review"
            #                 msg = Message(recipients=[mod_qual_review_subscribers[user]],
            #                               body=message,
            #                               subject=subject,
            #                               sender='neumodxsystemqcdatasync@gmail.com')

            #                 conn.send(msg)

        """
        Get Review Groups
        """
        reviewgroups_url = os.environ['RUN_REVIEW_API_BASE'] + "ReviewGroups"

        reviewgroups_response = requests.get(
            reviewgroups_url, verify=False).json()

        for reviewgroup in reviewgroups_response:
            reviewgroup_options[reviewgroup['id']] = reviewgroup['description']

        if submit_clicks:
            return reviewgroup_options, created_runset_id
        return dash.no_update

    @app.callback(Output("post-response", 'is_open'),
                  Input('submit-reviewgroup-selection-button', 'n_clicks'),
                  Input('cancel-reviewgroup-selection-button', 'n_clicks'),
                  State('review-group-options', 'value'),
                  State('review-group-options', 'options'),
                  State('created-runset-id', 'data'),
                  State('post-response', 'is_open'),
                  prevent_initial_call=True
                  )
    def add_runsetreviewassignments(submit_button, cancel_button, review_groups_selected, review_groups_dictionary, created_runset_id, post_response_is_open):

        if ctx.triggered_id == 'submit-reviewgroup-selection-button' or ctx.triggered_id == 'cancel-reviewgroup-selection-button':

            review_groups = []
            review_group_subscribers = {}
            for review_group_id in review_groups_selected:
                runsetreviewassignmenturl = os.environ['RUN_REVIEW_API_BASE'] + \
                    "RunSetReviewAssignments"
                queryParams = {}
                queryParams['runsetid'] = created_runset_id
                queryParams['reviewgroupid'] = review_group_id
                queryParams['userid'] = session['user'].id
                response = requests.post(
                    runsetreviewassignmenturl, params=queryParams, verify=False)
                print(response.status_code)
                review_groups.append(review_groups_dictionary[review_group_id])

            print("Review Groups Assigned: ", review_groups)

            if 'System QC Reviewer' in review_groups:
                for user in system_qc_reviewers:
                    review_group_subscribers[user] = system_qc_reviewers[user]

            if 'System Integration Lead' in review_groups:
                for user in system_integration_reviewers:
                    review_group_subscribers[user] = system_integration_reviewers[user]

            if 'Engineering' in review_groups:
                for user in engineering_reviewers:
                    review_group_subscribers[user] = engineering_reviewers[user]

            if 'Admin' in review_groups:
                for user in admin_reviewers:
                    review_group_subscribers[user] = admin_reviewers[user]

            print("Subscribers: ", review_group_subscribers)
            if os.environ['SEND_EMAILS'] == "Yes":
                """
                Get reviewers to send email too
                """
                runset_url = os.environ['RUN_REVIEW_API_BASE'] + \
                    "RunSets/{}".format(created_runset_id)
                runset = requests.get(url=runset_url, verify=False).json()
                # if 'XPCR Module Qualification' in runset_type_selection_options[runset_type_selection_id]:
                msg = Message(runset['name']+" Ready for review", sender='neumodxsystemqcdatasync@gmail.com',
                              recipients=['aripley2008@gmail.com'])

                with mail.connect() as conn:
                    for user in review_group_subscribers:
                        message = 'Hello '+user+", this message is sent to inform you that " + \
                            runset['name']+" is now ready for your review."
                        subject = runset['name']+" Ready for review"
                        msg = Message(recipients=[review_group_subscribers[user]],
                                      body=message,
                                      subject=subject,
                                      sender='neumodxsystemqcdatasync@gmail.com')

                        conn.send(msg)
            return not post_response_is_open
        return post_response_is_open
    return app.server
