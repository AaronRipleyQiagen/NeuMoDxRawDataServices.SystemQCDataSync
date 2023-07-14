from dash import Output, Input, State, no_update
import pandas as pd
import requests
import os
from urllib.parse import urlparse, parse_qs


def add_data_reviewer_callbacks(app) -> None:
    @app.callback(Output("cartridge-ids", "data"), Input("url", "href"))
    def get_runset_id(url):
        if url:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)

            params_list = []
            for param, values in query_params.items():
                params_list.extend(values)

            print(params_list)

            return params_list
        else:
            return no_update
