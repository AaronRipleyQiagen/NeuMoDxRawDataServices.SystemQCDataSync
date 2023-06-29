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
from Shared.functions import *


def populate_review_queue(
    user_id,
    user_group,
    review_group_ids=[],
    runset_statuses=[],
    reviewer_group_id=None,
    my_runsets_filter=False,
):
    runsets_url = os.environ[
        "RUN_REVIEW_API_BASE"
    ] + "RunSets/{}/reviewerstatus".format(user_id)
    runsets_params = {}
    if len(review_group_ids) > 0:
        runsets_params["reviewgroupids"] = review_group_ids
    if len(runset_statuses) > 0:
        runsets_params["runsetstatuses"] = runset_statuses
    if reviewer_group_id:
        runsets_params["reviewergroupid"] = reviewer_group_id
    runsets_params["createdbyuserfilter"] = my_runsets_filter
    resp = requests.get(url=runsets_url, verify=False, params=runsets_params)
    runsets = resp.json()
    if len(runsets) > 0:
        df = pd.DataFrame.from_dict(runsets)
        df["Status"] = np.nan

        for idx in df.index:
            try:
                df.loc[idx, "Status"] = df.loc[idx, "runSetReviews"][0][
                    "runSetReviewStatus"
                ]["name"]
            except:
                df.loc[idx, "Status"] = "Not Yet Reviewed"

        df["XPCR Module"] = [
            x[0]["xpcrModule"]["xpcrModuleSerial"] for x in df["runSetXPCRModules"]
        ]

        columns = [
            "id",
            "Status",
            "XPCR Module",
            "name",
            "runSetStartDate",
            "sampleCount",
            "validFromUser",
            "validFrom",
            "Created By",
        ]

        groupable_columns = ["Status"]

        """
        Get User Names
        """

        users = get_users_info_async([x for x in df["validFromUser"].unique()])

        user_info = {}
        for user in users:
            user_info[user] = users[user]["givenName"]

        df["Created By"] = df["validFromUser"].replace(user_info)

        column_names = {
            "name": "Description",
            "runSetStartDate": "Start Date",
            "sampleCount": "Sample Count",
            "validFromUser": "UserId",
            "id": "Id",
            "validFrom": "Created Date",
        }

        df = df[columns].rename(column_names, axis=1)

        columnDefs = []
        for column in df.columns:
            columnDef = {"headerName": column, "field": column, "filter": True}
            if "Date" in column:
                df[column] = (
                    df[column].astype("datetime64").dt.strftime("%d %B %Y %H:%M:%S")
                )
            if column in groupable_columns:
                columnDef["rowGroup"] = True
            if "Id" in column:
                columnDef["hide"] = True
            columnDefs.append(columnDef)
        return df.sort_values(["XPCR Module"]).to_dict("records"), columnDefs

    else:
        return None, None
