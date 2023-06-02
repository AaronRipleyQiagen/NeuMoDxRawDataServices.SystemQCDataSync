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
    blob_client.upload_blob(file_content, overwrite=True,
                            connection_verify=False)
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
