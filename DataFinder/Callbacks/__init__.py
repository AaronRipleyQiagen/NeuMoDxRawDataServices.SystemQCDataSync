from dash import Output, Input, State, no_update
import pandas as pd
import requests
import os
from Shared.functions import save_json_response, get_dash_ag_grid_from_records


def update_modules():
    modules_update = {}
    module_results = requests.get(
        os.environ["API_HOST"] + "/api/xpcrmodules", verify=False
    ).json()
    for module in module_results:
        if pd.isnull(module["xpcrModuleSerial"]) == False:
            modules_update[module["id"]] = module["xpcrModuleSerial"]
    return modules_update


def add_data_finder_callbacks(app):
    @app.callback(
        Output("xpcr-module-options", "options"), Input("load-interval", "children")
    )
    def update_module_options(n):
        return update_modules()

    @app.callback(
        Output("module-runs-table", "rowData"),
        Output("module-runs-table", "columnDefs"),
        Input("xpcr-module-options", "value"),
        prevent_inital_call=True,
    )
    def get_run_options(module_id: str):
        if module_id:
            run_details_url = os.environ[
                "API_HOST"
            ] + "/api/reports/xpcrmodule/{}/rundetails".format(module_id)

            run_details = requests.get(url=run_details_url)

            column_map = {
                "id": "Id",
                "runStartTime": "Run Start Date",
                "runEndTime": "Run End Date",
                "assayListString": "Assays",
                "sampleCount": "Sample Count",
            }

            return get_dash_ag_grid_from_records(
                records=run_details.json(), column_map=column_map
            )
        else:
            return no_update

    @app.callback(
        Output("cartridge-ids-selected", "data"),
        Input("module-runs-table", "selectionChanged"),
        prevent_inital_call=True,
    )
    def get_selected_samples(selection: list[dict]):
        if not selection:
            return no_update
        else:
            return [x["Id"] for x in selection]

    """
    Following Javascript function allows for users to redirect the user to a specific run-review page.
    Note that because the way this is used (Dash App embedded inside of Flask App), it is necessary to 
    use javascript to do this redirect.
    """

    app.clientside_callback(
        """
            function goToRunSetPage(n_clicks, runset_ids) {
                if (n_clicks && n_clicks > 0) {
                    var currentHref = window.top.location.href;
                    var splitString = '/data-finder/';
                    var hrefParts = currentHref.split(splitString);
                    var runset_ids_query_params = runset_ids.map(id => 'runset_ids=' + encodeURIComponent(id)).join('&');
                    if (hrefParts.length > 1) {
                        var newHref = hrefParts[0] + '/data-explorer/' + runset_ids_query_params;
                        window.top.location.href = newHref;
                    }
                }
            }
            """,
        Output("data-finder-external-redirect", "children"),
        Input("get-data", "n_clicks"),
        State("cartridge-ids-selected", "data"),
    )
