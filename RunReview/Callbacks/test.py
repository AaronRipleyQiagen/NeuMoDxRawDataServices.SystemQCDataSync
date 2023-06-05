from dash import Input, Output, State


def get_callbacks(app):
    @app.callback(Output("runset-id", "data"), Input("url", "href"))
    def get_runset_id(url):
        guid = url.split("/")[-1]
        return guid
