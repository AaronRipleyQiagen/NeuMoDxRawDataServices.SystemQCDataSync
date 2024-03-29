from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from Shared.Components import *
from Shared.neumodx_objects import colorDict

fig = go.Figure()

"""
Layout Components
"""
data_explorer_external_link_redirect = html.Div(
    id="data-explorer-external-link-redirect"
)
created_runset_id = dcc.Store(id="created-runset-id", storage_type="session")
cartridge_ids = dcc.Store(id="cartridge-ids", storage_type="session")
sample_info = dcc.Store(id="sample-info", storage_type="session")
sample_results_table = dag.AgGrid(
    enableEnterpriseModules=True,
    rowData=[],
    columnSize="sizeToFit",
    defaultColDef=dict(
        resizable=True,
    ),
    rowSelection="single",
    id="sample-results-table",
)
reviewgroup_selector_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Add Runset Review Assignemnts")),
        dbc.ModalBody(
            children=[
                html.Label("Select Groups required to review this runset."),
                dbc.Checklist(id="review-group-options", switch=True),
            ]
        ),
        dbc.ModalFooter(
            [
                dbc.Button(
                    "Submit",
                    id="submit-reviewgroup-selection-button",
                    className="ms-auto",
                    n_clicks=0,
                ),
                dbc.Button(
                    "Cancel",
                    id="cancel-reviewgroup-selection-button",
                    className="ms-auto",
                    n_clicks=0,
                ),
            ]
        ),
    ],
    id="reviewgroup-selector-modal-data-explorer",
    is_open=False,
)
post_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Runset Creation Result")),
        dbc.ModalBody(
            children=[
                html.P("Runset was successfully created."),
                GoToRunSetButtonAIO(
                    aio_id="data-reviewer-go-to-runset", split_string="/data-reviewer/"
                ),
            ]
        ),
        dbc.ModalFooter(),
    ],
    id="post-response",
    is_open=False,
)
runset_selector_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Run Type Selector")),
        dbc.ModalBody("Please Make A Run Type Selection"),
        dcc.Dropdown(id="runset-type-options"),
        dbc.ModalFooter(
            [
                dbc.Button(
                    "Submit", id="submit-button", className="ms-auto", n_clicks=0
                ),
                dbc.Button(
                    "Cancel", id="cancel-button", className="ms-auto", n_clicks=0
                ),
            ]
        ),
    ],
    id="runset-selector-modal",
    is_open=False,
)
runset_attempt_prompt = UserInputModal(
    aio_id="data-explorer",
    title_text="Define Runset Attempt Number",
    modal_body=RunSetAttemptModalBody(aio_id="data-explorer"),
)
channel_selector = html.Div(
    [
        html.H3("Select Channel:", style=halfstyle),
        dcc.Dropdown(
            ["Yellow", "Green", "Orange", "Red", "Far Red"],
            value="Yellow",
            id="channel-selector",
            style=halfstyle,
        ),
    ],
    style=halfstyle,
)
process_step_selector = html.Div(
    [
        html.H3("Select Process Step:", style=halfstyle),
        dcc.Dropdown(
            ["Normalized", "Raw", "2nd"],
            value="Raw",
            id="process-step-selector",
            style=halfstyle,
        ),
    ],
    style=halfstyle,
)
create_run_review_button = dbc.Button(
    "Create Run Review from Dataset", id="create-run-review-button", style=double_button
)
run_review_confirmation = html.H1(id="run-review-confirmation")
fig = dcc.Graph(id="curves", figure=fig)
run_attempt_validation_check_pass = dcc.Store(
    id="data-explorer-validation-check-pass", storage_type="session"
)
run_attempt_validation = UserInputModal(
    aio_id="data-explorer-run-attempt-validation",
    title_text="Previously created Runset Matching Description Found",
    submit_text="Continue",
    modal_body=RunSetAttemptNumberValidation(
        aio_id="data-explorer-run-attempt-validation", split_string="/data-explorer/"
    ),
)
back_to_search_button = FindXPCRModuleRunsButton(
    aio_id="data-explorer", split_string="/data-reviewer/"
)

data_reviewer_layout = html.Div(
    children=[
        dcc.Location(id="url"),
        cartridge_ids,
        created_runset_id,
        sample_info,
        html.H1(children="Results Viewer"),
        html.Br(),
        dcc.Loading(
            id="samples-loading",
            type="graph",
            fullscreen=True,
            children=[
                html.Div([channel_selector, process_step_selector]),
                fig,
                sample_results_table,
                html.Br(),
                html.Div(
                    [create_run_review_button, back_to_search_button],
                ),
                run_review_confirmation,
            ],
        ),
        dcc.Loading(
            id="pending-post",
            type="cube",
            fullscreen="true",
            children=[reviewgroup_selector_modal, post_response, runset_selector_modal],
        ),
        data_explorer_external_link_redirect,
        runset_attempt_prompt,
        run_attempt_validation,
        run_attempt_validation_check_pass,
    ]
)
