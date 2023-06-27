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
import json
import time


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


def download_file_from_url(file_url):
    # Extract the account URL from the file URL
    account_url = file_url[
        : file_url.index("/", 8)
    ]  # Find the second "/" after "https://"

    # Create a BlobServiceClient using the account URL
    blob_service_client = BlobServiceClient(
        account_url=account_url,
        credential=os.environ["NEUMODXSYSTEMQC_RAWDATAFILES_KEY"],
    )

    # Extract the container name and blob name from the file URL
    container_name = file_url[
        file_url.index("/", 8) + 1 : file_url.index("/", file_url.index("/", 8) + 1)
    ]
    blob_name = file_url[file_url.rindex("/") + 1 :]

    # Create a BlobClient using the BlobServiceClient, container name, and blob name
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=blob_name
    )

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


class GetRequestArguments:
    """
    A class used to represent request objects to be passed into HttpGetWithQueryParametersAsync.

    Properities:
        url: Url to send the request to.
        params: Query Parameters to pass into the request.
        label: What to label the response.
    """

    url: str
    params: dict
    label: str

    def __init__(self, url: str, params: dict, label: str):
        self.url = url
        self.params = params
        self.label = label


def HttpGetWithQueryParametersAsync(
    get_request_arguments_list: list[GetRequestArguments],
) -> list[dict]:
    """
    Used to perform async requests to retreive data from a list of urls data while including query parameters for each request made.

    Args:
        request_arguments_list: A List of request_arguments (dictionary with url & parameter keys).
    """

    async def HttpGet(session, get_request_arguments: GetRequestArguments):
        async with session.get(
            get_request_arguments.url, params=get_request_arguments.params
        ) as resp:
            data = await resp.json()
            return {get_request_arguments.label: data}

    async def main():
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(verify_ssl=False)
        ) as session:
            tasks = []
            for get_request_arguments in get_request_arguments_list:
                tasks.append(
                    asyncio.ensure_future(HttpGet(session, get_request_arguments))
                )
            return await asyncio.gather(*tasks)

    responses = asyncio.run(main())

    labeled_responses = []

    for response in responses:
        for record in [
            [{**record, "label": key} for record in values]
            for key, values in response.items()
        ][0]:
            labeled_responses.append(record)

    return labeled_responses


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
        else:
            column_definition["hide"] = False

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


def save_json_response(response: dict, filepath: str) -> None:
    """
    A function that is used to save a json file to a given filepath

    Args:
        response: The response to be saved.
        filepath:  Where the response should be save to.

    """
    # Serialize the JSON response
    json_data = json.dumps(response)

    # Save the JSON data to a file
    with open(filepath, "w") as file:
        file.write(json_data)


def unpack_multi_level_dictionary(
    primary_dictionary: dict, sub_dictionary_fields: list[str], valueFields: list[str]
) -> dict:
    """
    A function used to unpack sub dictonary to values contained within the primary dictionary.
    Args:
        primary_dictionary: The primary dictionary to unpack values from.
        sub_dictionary_fields:  Keys within the primary dictionary that correspond to dictionaries that should be unpacked.
        valueFields: Fields in the the sub_dictionary_field that are targets for unpacking.
    Returns
        The primary_dictionary with additional keys that correspond to the values unpacked from the sub_dictionary_fields. The original sub_dictionary_fields are removed from the primary dictionary.
    """
    for sub_dictionary_field in sub_dictionary_fields:
        for valueField in valueFields:
            primary_dictionary.update(
                {
                    sub_dictionary_field
                    + "_"
                    + valueField: primary_dictionary[sub_dictionary_field][valueField]
                }
            )

        primary_dictionary.pop(sub_dictionary_field)
    return primary_dictionary


def timer_decorator(func):
    """
    A Decorator to time the execution of a function.
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(
            f"Function '{func.__name__}' took {execution_time:.6f} seconds to execute."
        )
        return result

    return wrapper
