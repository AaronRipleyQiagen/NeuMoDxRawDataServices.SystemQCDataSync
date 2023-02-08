from flask import redirect, url_for
from dash import Dash, dcc, html, Input, Output, State, dash_table, callback, register_page
import dash_bootstrap_components as dbc
import pandas as pd
import dash_ag_grid as dag
import os
import requests

register_page(__name__, path="/run-review/module-history/")

test_mod_history = html.H1("Coming Soon")

layout = [test_mod_history]
