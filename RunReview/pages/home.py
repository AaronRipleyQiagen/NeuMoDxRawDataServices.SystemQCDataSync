from flask import redirect, url_for
from dash import Dash, dcc, html, Input, Output, State, dash_table, callback
import dash
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__, path="/run-review/")

run_review_welcome = html.H1("Welcome to the Run Review Module")
run_review_message = html.H2(
    "Please begin by selecting an option on side-bar")
layout = [run_review_welcome, run_review_message]


