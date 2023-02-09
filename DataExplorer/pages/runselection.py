from flask import redirect, url_for
from dash import Dash, dcc, html, Input, Output, State, dash_table, callback, register_page
import dash_bootstrap_components as dbc
import dash
import requests
import pandas as pd
import os

register_page(__name__, path="/")


def update_modules():
    modules_update = {}
    module_results = requests.get(
        os.environ['API_HOST']+"/api/xpcrmodules", verify=False).json()
    for module in module_results:
        if pd.isnull(module['xpcrModuleSerial']) == False:
            modules_update[module['id']] = module['xpcrModuleSerial']
    return modules_update


def getXPCRModuleCartridges(module_id):
    request_url = os.environ['API_HOST']+"/api/xpcrmodules/{}/xpcrmoduleconfigurations".format(
        module_id)

    module_data = pd.DataFrame(
        columns=['Run Start Time', 'Run End Time', '# of Samples', 'Assays'])
    module_data.index.names = ['id']

    def cartridgeToDataFrame(cartridge):
        module_data.loc[cartridge['id'], ['Run Start Time', 'Run End Time', '# of Samples', 'Assays']] = [
            cartridge['validFrom'], cartridge['validTo'], cartridge['sampleCount'], cartridge['assays']]

    xpcrModule = requests.get(
        os.environ['API_HOST']+"/api/xpcrmodules/{}/xpcrmoduleconfigurations".format(module_id), verify=False).json()
    cartridge_samples = {}
    for xpcrconfiguration in xpcrModule['xpcrModuleConfigurations']:

        xpcrconfiguration = requests.get(
            os.environ['API_HOST']+"/api/xpcrmoduleconfigurations/{}/cartridges".format(xpcrconfiguration['id']), verify=False).json()

        for cartridge in xpcrconfiguration['cartridges']:

            cartridge_details = requests.get(
                os.environ['API_HOST']+"/api/cartridges/{}/samples/assays".format(cartridge['id']), verify=False).json()
            sample_ids = []
            cartridge_assays = []
            for sample in cartridge_details['samples']:
                sample_ids.append(sample['id'])
                # requests.get("https://localhost:7107/api/samples/{}/info-channelsummary-readings".format(sample['id']), verify=False).json()

                if sample['assay']['assayName'] not in cartridge_assays:
                    cartridge_assays.append(sample['assay']['assayName'])

            cartridge['assays'] = ','.join(cartridge_assays)
            cartridgeToDataFrame(cartridge)
            cartridge_samples[cartridge['id']] = sample_ids

    #print(cartridge_samples)

    module_data.sort_values('Run Start Time', inplace=True, ascending=False)
    module_data.dropna(subset=['Run Start Time'], inplace=True)
    module_data['Run Start Time'] = module_data['Run Start Time'].astype(
        'datetime64').dt.strftime("%d %B %Y %H:%M:%S")
    module_data['Run End Time'] = module_data['Run End Time'].astype(
        'datetime64').dt.strftime("%d %B %Y %H:%M:%S")
    return module_data.reset_index().to_dict('records'), cartridge_samples


module_data = pd.DataFrame(
    columns=['id', 'Run Start Time', 'Run End Time', '# of Samples', 'Assays'])
module_data.loc[0] = ['Test', 'Test', 'Test', 'Test', 'Test']

layout = html.Div([
    html.Div(id='load-interval'),
    html.Div([
        html.P([
            html.H2(["Select Module of Interest:"]),
            dcc.Dropdown(id="xpcr-module-options")
        ]),
    ]),
    html.Div([
        html.P([html.H2(['Choose Run(s) of Interest'])]),
        dcc.Loading(id='samples-loading',
                    type='default',
                    fullscreen=True,
                    children=dash_table.DataTable(id='runs', sort_action='native', row_selectable='multi', columns=[{'name': i, 'id': i, 'deletable': True} for i in module_data.columns
                                                                                                                    # omit the id column
                                                                                                                    if i != 'id'
                                                                                                                    ]))
    ]),
    html.Div([
        dbc.Button('Get Data', id='view-run-data',
                   n_clicks=0, href="/dashboard/data-explorer/results"),
    ])


])


@callback(Output("xpcr-module-options", "options"), [Input("load-interval", "children")])
def update_module_options(n):
    return update_modules()


@callback([Output("runs", "data"), Output("cartridge-sample-ids", "data")], [Input("xpcr-module-options", "value")], prevent_inital_call=True)
def get_run_options(module):
    if pd.isnull(module):
        return module_data.to_dict("records"), {}
    else:
        return getXPCRModuleCartridges(module)


@callback(Output("selected-cartridge-sample-ids", "data"),
          [Input('view-run-data', 'n_clicks'),
           State('runs', 'selected_row_ids'),
           State('cartridge-sample-ids', 'data')],
          prevent_inital_call=True)
def get_selected_samples(n, selected_cartridge_ids, cartridge_sample_ids):

    if selected_cartridge_ids == None:
        return dash.no_update
    selected_cartridge_sample_ids = cartridge_sample_ids.copy()

    for cartridge_id in cartridge_sample_ids:
        if cartridge_id not in selected_cartridge_ids:
            selected_cartridge_sample_ids.pop(cartridge_id)

    print("got selected samples")
    return selected_cartridge_sample_ids
