from datetime import datetime, timedelta
from flask import session
from dash import html
import pandas as pd
import uuid
import os
import pickle


def save_object(obj, session_id, name):
    os.makedirs("Dir_Store", exist_ok=True)
    file = "Dir_Store/{}_{}".format(session_id, name)
    pickle.dump(obj, open(file, "wb"))


def load_object(session_id, name):
    file = "Dir_Store/{}_{}".format(session_id, name)
    obj = pickle.load(open(file, "rb"))
    os.remove(file)
    return obj


def clean_Dir_Store():
    if os.path.isdir("Dir_Store"):
        file_list = pd.Series("Dir_Store/" + i for i in os.listdir("Dir_Store"))
        mt = file_list.apply(
            lambda x: datetime.fromtimestamp(os.path.getmtime(x))
        ).astype(str)
        for i in file_list[mt < str(datetime.now() - timedelta(hours=3))]:
            os.remove(i)


def apply_layout_with_auth(app, layout):
    def serve_layout():
        if session.get("user"):
            return layout
        return html.Div("403 Access Denied")

    app.config.suppress_callback_exceptions = True
    app.layout = serve_layout
