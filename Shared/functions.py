import os
import requests
import pandas as pd
import asyncio
import aiohttp
import numpy as np
from azure.storage.blob import BlobServiceClient
import io
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, no_update, ctx
import base64


def save_uploaded_file_to_blob_storage(file_content, filename, container_name):
    account_url = "https://prdqianeumodxrdseusst.blob.core.windows.net"

    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient(
        account_url=account_url,
        credential=os.environ["NEUMODXSYSTEMQC_RAWDATAFILES_KEY"],
    )

    # Decode the base64-encoded file content into bytes

    # Get a reference to the Blob Storage container
    container_client = blob_service_client.get_container_client(container_name)

    blob_client = container_client.get_blob_client(filename)
    blob_client.upload_blob(file_content, overwrite=True, connection_verify=False)
    # Return the URL for the uploaded file
    return container_client.url + "/" + filename


def add_item_to_carousel(title, description, container_name, blob_name):
    items = []
    account_url = "https://prdqianeumodxrdseusst.blob.core.windows.net"

    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient(
        account_url=account_url,
        credential=os.environ["NEUMODXSYSTEMQC_RAWDATAFILES_KEY"],
    )

    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=blob_name
    )
    image_bytes = blob_client.download_blob(connection_verify=False).readall()

    item = {
        "src": "data:image/png;base64,{}".format(base64.b64encode(image_bytes).decode())
    }

    return item


def download_file(filename, container_name):
    account_url = "https://prdqianeumodxrdseusst.blob.core.windows.net"

    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient(
        account_url=account_url,
        credential=os.environ["NEUMODXSYSTEMQC_RAWDATAFILES_KEY"],
    )

    # Get a reference to the Blob Storage container
    container_client = blob_service_client.get_container_client(container_name)

    blob_client = container_client.get_blob_client(filename)

    # download the blob to a bytes buffer
    stream_downloader = blob_client.download_blob(connection_verify=False)

    stream = io.BytesIO()
    stream.write(stream_downloader.readall())

    # encode the bytes buffer as base64 for the download link
    base64_blob = base64.b64encode(stream.getvalue()).decode()

    return base64_blob


def HttpGetAsync(urls):
    """
    Used to perform async requests to retreive data from a list of urls data.
    Parameters
    ----------
    urls (List[urls]):  list of urls to request data from
    """

    async def HttpGet(session, url):
        async with session.get(url) as resp:
            data = await resp.json()
            return data

    async def main():
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            tasks = []
            for url in urls:
                tasks.append(asyncio.ensure_future(HttpGet(session, url)))

            return await asyncio.gather(*tasks)

    responses = asyncio.run(main())
    return responses


def get_dataframe_from_records(records: list[dict], column_map: dict) -> pd.DataFrame:
    """
    A function used to populate a dataframe from records (i.e. as stored in a dcc.Store component).
    Args:
        records: Records to be used to populate DataFrame.
        column_map: Dictionary to be used to map properties of records to columns in DataFrame. Key: Source -> Record property, Value: Target -> DataFrame Column
    Returns:
        DataFrame populated from Records.
    """

    # Initialize the dataframe used to collect information from records
    dataframe = pd.DataFrame(columns=[x for x in column_map])

    # Iterate through the records and add each record as a new row.
    idx = 0
    for record in records:
        dataframe.loc[idx] = record
        idx += 1

    # Rename the columns in dataframe to match the column names defined in the column_map.
    dataframe.rename(column_map, axis=1, inplace=True)

    return dataframe


def get_column_defs(
    dataframe: pd.DataFrame, hide_columns: list[str] = None
) -> list[dict]:
    """
    A function used to get the columnDefs for the DataFrame inputed.
    Args:
      dataframe: DataFrame to get columnDefs for.
      hide_columns: Columns in the DataFrame to hide. Defaults to columns containing "Id" or "id".
    """

    column_definitions = []

    if hide_columns == None:
        hide_columns = [x for x in dataframe.columns if "Id" in x or "id" in x]

    for column in dataframe.columns:
        column_definition = {
            "headerName": column,
            "field": column,
            "filter": True,
            "sortable": True,
        }
        if column in hide_columns:
            column_definition["hide"] = True

        column_definitions.append(column_definition)

    return column_definitions


def clean_date_columns(
    dataframe: pd.DataFrame,
    date_columns: list[str] | None = None,
    date_format: str = "%d %B %Y %H:%M:%S",
) -> pd.DataFrame:
    """
    A function used to convert the columns that can be converted to a datetime64 type to a specfied format.

    Args:
        dataframe: DataFrame used for conversion

    Optional Args:
        date_columns: List of columns to be converted.  Defaults to columns containing "Date" or "date".
        date_format: The strftime format to convert target columns to. Defaults to "%d %B %Y %H:%M:%S" (22 February 2023 18:19:43)


    """
    if date_columns == None:
        date_columns = [x for x in dataframe if "Date" in x or "date" in x]
    for column in date_columns:
        dataframe[column] = (
            dataframe[column].astype("datetime64[ns]").dt.strftime(date_format)
        )

    return dataframe


def get_dash_ag_grid_from_records(
    records: list[dict],
    column_map: dict,
    date_columns: list[str] | None = None,
    date_format: str = "%d %B %Y %H:%M:%S",
    hide_columns: list[str] = None,
) -> tuple[list[dict], list[dict]]:
    """
    A function used to provide a standardized method to populate the rowData and columnDefs of a Dash AG Grid from a list of records

    Args:
        records: Records to be used to populate DataFrame.
        column_map: Dictionary to be used to map properties of records to columns in DataFrame. Key: Source -> Record property, Value: Target -> DataFrame Column

    Optional Args:
        date_columns: List of columns to be converted.  Defaults to columns containing "Date" or "date".
        date_format: The strftime format to convert target columns to. Defaults to "%d %B %Y %H:%M:%S" (22 February 2023 18:19:43)
        hide_columns: Columns in the DataFrame to hide. Defaults to columns containing "Id" or "id".

    Returns:
        A tuple containing two list[dict] (RowData, ColumnDefs)
    """

    dataframe = get_dataframe_from_records(records, column_map)
    dataframe.pipe(
        clean_date_columns, date_columns=date_columns, date_format=date_format
    )
    columnDefs = get_column_defs(dataframe, hide_columns=hide_columns)

    return dataframe.to_dict("records"), columnDefs
