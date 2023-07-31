from dash import Output, Input, State, no_update
import pandas as pd
import requests
import os
from Shared.functions import (
    save_json_response,
    get_dash_ag_grid_from_records,
    timer_decorator,
)
from urllib.parse import urlparse, parse_qs


@timer_decorator
def update_modules(module_id: str | None):
    print("MODULE_ID", module_id)

    modules_update = {}
    module_results = requests.get(
        os.environ["RAW_DATA_API_BASE"] + "xpcrmodules", verify=False
    ).json()

    for module in module_results:
        if pd.isnull(module["xpcrModuleSerial"]) == False:
            modules_update[module["id"]] = module["xpcrModuleSerial"]
    save_json_response(modules_update, "modules.json")
    module_id = module_id.lower() if module_id else no_update
    return modules_update, module_id


def add_data_finder_callbacks(app):
    @app.callback(
        Output("xpcr-module-options", "options"),
        Output("xpcr-module-options", "value"),
        Input("url", "href"),
        State("xpcrmodule-id-selected", "data"),
    )
    def update_module_options(url, xpcrmodule_id_selected):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        params_list = []

        for param, values in query_params.items():
            params_list.extend(values)

        module_id = (
            params_list[0]
            if len(params_list) > 0
            else xpcrmodule_id_selected
            if xpcrmodule_id_selected
            else None
        )

        return update_modules(module_id=module_id)

    @app.callback(
        Output("xpcrmodule-id-selected", "data"), Input("xpcr-module-options", "value")
    )
    def get_xpcr_module_id_selected(xpcr_module_option: str) -> str:
        if xpcr_module_option:
            return xpcr_module_option
        else:
            return no_update

    @app.callback(
        Output("xpcrmodule-runset-data", "data"),
        Input("xpcrmodule-id-selected", "data"),
        prevent_inital_call=True,
    )
    def get_run_options(module_id: str):
        if module_id:
            module_runs_url = os.environ[
                "RAW_DATA_API_BASE"
            ] + "reports/xpcrmodule/{}/rundetails".format(module_id)
            module_runs_data = requests.get(url=module_runs_url, verify=False)
            return module_runs_data.json()
        else:
            return no_update

    @app.callback(
        Output("module-runs-table", "rowData"),
        Output("module-runs-table", "columnDefs"),
        Input("xpcrmodule-runset-data", "data"),
    )
    def populate_module_runs_table(
        module_runs_data: list[dict],
    ) -> tuple([list[dict], list[dict]]):
        if module_runs_data:
            column_map = {
                "id": "Id",
                "runStartTime": "Run Start Date",
                "runEndTime": "Run End Date",
                "assayListString": "Assays",
                "sampleCount": "Sample Count",
            }

            return get_dash_ag_grid_from_records(
                records=module_runs_data, column_map=column_map
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
            function goToRunSetPage(n_clicks, cartridge_ids, xpcrmodule_id) {
                if (n_clicks && n_clicks > 0) {
                    var currentHref = window.top.location.href;
                    var splitString = '/data-finder/';
                    var hrefParts = currentHref.split(splitString);
                    var cartridge_query_params = cartridge_ids.map(id => 'cartridgeid=' + encodeURIComponent(id)).join('&');
                    var xpcrmodule_query_params = 'xpcrmoduleid=' + xpcrmodule_id;
                    if (hrefParts.length > 1) {
                        var newHref = hrefParts[0] + '/data-reviewer?' + cartridge_query_params + "&" + xpcrmodule_query_params;
                        window.top.location.href = newHref;
                    }
                }
            }
            """,
        Output("data-finder-external-redirect", "children"),
        Input("get-data", "n_clicks"),
        State("cartridge-ids-selected", "data"),
        State("xpcrmodule-id-selected", "data"),
    )
