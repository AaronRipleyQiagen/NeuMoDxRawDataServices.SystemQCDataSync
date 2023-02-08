import os
import requests
import pandas as pd


def populate_review_queue():
    runsets_url = os.environ['RUN_REVIEW_API_BASE'] + "RunSets"

    runsets = requests.get(url=runsets_url, verify=False).json()

    df = pd.DataFrame.from_dict(runsets)
    df['Status'] = [x[0]['runSetStatus']['name']
                    for x in df['runSetRunSetStatuses']]

    df['XPCR Module'] = [x[0]['xpcrModule']
                          ['xpcrModuleSerial'] for x in df['runSetXPCRModules']]

    columns = ['id', 'Status', 'XPCR Module', 'name', 'number', 'runSetStartDate',
               'sampleCount']

    groupable_columns = ['Status', 'XPCR Module']

    column_names = {'name': 'Description', 'number': 'Number',
                    'runSetStartDate': 'Start Date', 'sampleCount': 'Sample Count'}
    df = df[columns].rename(column_names, axis=1)

    df_columnDefs = []
    for column in df.columns:
        if 'Date' in column:
            df[column] = df[column].astype(
                'datetime64').dt.strftime("%d %B %Y %H:%M:%S")
        if column in groupable_columns:
            df_columnDefs.append(
                {"headerName": column, "field": column, "rowGroup": True, "filter": True})
        else:
            if column != 'id':
                df_columnDefs.append(
                    {"headerName": column, "field": column, "filter": True})
    return df.to_dict('records'), df_columnDefs
