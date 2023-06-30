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
    user_id: str,
    user_group_id: str,
    review_group_ids: list = [],
    runset_status_ids: list = [],
    my_runsets_filter: bool = False,
):
    """
    A function used to retrieve & process information necessary to populate the run review queue.

    Args:
        user_id: The id of the user of interest.
        user_group_id: the id of the review group associated with the user of interest.
        reviewer_group_ids: The ids of the review groups to filter the runset review assignments to (Defaults to None).
        runset_status_ids: The names of the of the runset statuses to filter the runset review assignments to (Defaults to None).
        my_runsets_filter: Whether or not to filter the runsets to results that were created by the user of interest (Defaults to False).

    """

    ## Construct endpoint url by passing user_id into template string.
    runsets_url = os.environ[
        "RUN_REVIEW_API_BASE"
    ] + "RunSets/{}/reviewerstatus".format(user_id)

    ## Create a dictionary that captures the query_params.
    runsets_params = {}
    if len(review_group_ids) > 0:
        runsets_params["reviewgroupids"] = review_group_ids
    if len(runset_status_ids) > 0:
        runsets_params["runsetstatuses"] = runset_status_ids
    if user_group_id:
        runsets_params["reviewergroupid"] = user_group_id
    runsets_params["createdbyuserfilter"] = my_runsets_filter

    ## Make request
    resp = requests.get(url=runsets_url, verify=False, params=runsets_params)

    ## Process Request
    runsets = resp.json()

    ## Get User Names for unique user_ids
    unique_user_ids = list(set(map(lambda item: item.get("validFromUser"), runsets)))
    users = get_users_info_async(unique_user_ids)
    user_names = dict([(user, users[user]["displayName"]) for user in users])

    runsets = [
        {
            **record,
            "XPCR Module": record["runSetXPCRModules"][0]["xpcrModule"][
                "xpcrModuleSerial"
            ],
            "My Status": record["runSetReviews"][0]["runSetReviewStatus"]["name"]
            if len(record["runSetReviews"]) > 0
            else "Not Yet Reviewed",
            "Overall Status": record["runSetStatus"]["name"],
            "Created By": user_names[record["validFromUser"]],
        }
        for record in runsets
    ]

    column_map = {
        "id": "Id",
        "Overall Status": "Overall Status",
        "My Status": "My Status",
        "XPCR Module": "XPCR Module",
        "name": "Description",
        "Created By": "Created By",
        "runSetStartDate": "Start Date",
        "validFrom": "Created Date",
    }

    groupable_columns = ["My Status", "Overall Status"]

    return get_dash_ag_grid_from_records(
        records=runsets, column_map=column_map, group_columns=groupable_columns
    )
