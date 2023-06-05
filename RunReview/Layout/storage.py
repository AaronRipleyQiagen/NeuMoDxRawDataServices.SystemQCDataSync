from dash import dcc, callback, Output, Input, State
from dash import html

runset_id = dcc.Store(id="runset-id", storage_type="session")

runset_selection = dcc.Store(
    id="runset-selection-data", storage_type="session", data=""
)

runset_sample_data = dcc.Store(id="runset-sample-data", storage_type="session")

runset_review = dcc.Store(id="runset-review", storage_type="session")

runset_channel_options = dcc.Store(
    id="runset-channel-options", storage_type="session", data=""
)

channel_selected = dcc.Store(id="channel-selected", storage_type="session", data="")

spc_channel = dcc.Store(id="spc-channel", storage_type="session", data="")

runset_severity_options = dcc.Store(
    id="runset-severity-options", storage_type="session", data=""
)

severity_selected = dcc.Store(id="severity-selected", storage_type="session", data="")

runset_run_options = dcc.Store(id="runset-run-options", storage_type="session", data="")

run_option_selected = dcc.Store(
    id="run-option-selected", storage_type="session", data=""
)

runset_xpcrmodulelane_options = dcc.Store(
    id="runset-xpcrmodulelane-options", storage_type="session", data=""
)

xpcrmodulelane_selected = dcc.Store(
    id="xpcrmodulelane-selected", storage_type="session", data=""
)

xpcrmodule_options = dcc.Store(id="xpcrmodule-options", storage_type="session", data="")

xpcrmodule_selected = dcc.Store(
    id="xpcrmodule-selected", storage_type="session", data=""
)

runset_subject_ids = dcc.Store(id="runset-subject-ids", storage_type="session", data="")

runset_subject_descriptions = dcc.Store(
    id="runset-subject-descriptions", storage_type="session"
)

pcrcurve_sample_info = dcc.Store(id="pcrcurve-sample-info", storage_type="session")

issue_selected = dcc.Store(id="issue-selected", storage_type="session")

flat_data_download = dcc.Download(id="flat-data-download")

remediation_action_selection = dcc.Store(
    id="remediation-action-selection", storage_type="session"
)

remediation_action_loader = dcc.Interval(
    id="remediation-action-loader", interval=60 * 1000, n_intervals=0  # in milliseconds
)

related_runsets = dcc.Store(id="related-runsets", storage_type="session")

issue_remediation_url = dcc.Store(id="issue-remediation-url", storage_type="session")

issue_delete_url = dcc.Store(id="issue-delete-url", storage_type="session")

issue_resolution_remediation_action_selection = dcc.Store(
    id="issue-resolution-remediation-action-selection", storage_type="session"
)

issue_remediation_type = dcc.Store(id="issue-remediation-type", storage_type="session")

url = dcc.Location(id="url")

storage_objects = html.Div(
    [
        url,
        runset_id,
        runset_selection,
        runset_sample_data,
        runset_review,
        runset_channel_options,
        channel_selected,
        spc_channel,
        runset_severity_options,
        severity_selected,
        runset_run_options,
        run_option_selected,
        runset_xpcrmodulelane_options,
        xpcrmodulelane_selected,
        xpcrmodule_options,
        xpcrmodule_selected,
        runset_subject_ids,
        runset_subject_descriptions,
        pcrcurve_sample_info,
        issue_selected,
        remediation_action_selection,
        related_runsets,
        issue_remediation_url,
        issue_delete_url,
        issue_resolution_remediation_action_selection,
        issue_remediation_type,
    ]
)

download_objects = html.Div([flat_data_download])

interval_objects = html.Div([remediation_action_loader])
