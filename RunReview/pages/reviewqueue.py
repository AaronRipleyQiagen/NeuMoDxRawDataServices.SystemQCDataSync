from flask import redirect, url_for
from dash import Dash, dcc, html, Input, Output, State, dash_table, callback, register_page
import dash_bootstrap_components as dbc
import pandas as pd

register_page(__name__, path="/reviewqueue")

test = html.H1("Test")
layout = [test]
