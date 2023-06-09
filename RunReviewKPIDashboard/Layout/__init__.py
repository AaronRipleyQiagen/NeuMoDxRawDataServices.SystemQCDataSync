from dash import html, dcc
import dash_bootstrap_components as dbc
from Shared.appbuildhelpers import *
import datetime
import dash_daq as daq

"""
Define reusable_styles
"""
style_50 = {"width": "50%", "display": "inline-block", "vertical-align": "top"}

"""
Define Date Filtering Parameters
"""

date_range_selector_label = html.H4("Select Date Range:")
# Get today's date
today = datetime.date.today()

# Calculate the date one week ago
one_week_ago = today - datetime.timedelta(days=7)

date_range_selector = dcc.DatePickerRange(
    start_date=one_week_ago, end_date=today, id="date-range-selector"
)

date_settings = html.Div(
    children=[date_range_selector_label, date_range_selector],
    style={"width": "50%", "display": "inline-block", "vertical-align": "top"},
)

"""
Define Assay Filtering Parameters
"""

run_type_type_filter_label = html.H4("Select Run Type(s) of Interest:", style=style_50)

run_type_selector = dcc.Dropdown(id="run-type-selector", multi=True)

run_type_settings = html.Div(
    children=[run_type_type_filter_label, run_type_selector],
    style={"width": "50%", "display": "inline-block", "vertical-align": "top"},
)

runset_status_selector_label = html.H4("Select Statuses Of Interest:", style=style_50)

runset_status_selector = dcc.Dropdown(id="runset-status-selector", multi=True)

runset_status_settings = html.Div(
    children=[runset_status_selector_label, runset_status_selector],
    style={"width": "50%", "display": "inline-block", "vertical-align": "top"},
)

settings_label = html.H2("Filter Parameters:")
settings = html.Div(
    [settings_label, date_settings, run_type_settings, runset_status_settings],
    id="settings-div",
    style={"border": "1px solid black", "padding": "5px"},
)

"""
Define elements used to store data.
"""

runsets = dcc.Store(id="runsets", storage_type="session")
issues = dcc.Store(id="issues", storage_type="session")
module_runset_summaries = dcc.Store("module-runset-summaries", storage_type="session")

"""
Generate Figures
"""

status_summary = dcc.Loading(
    children=[runsets, dcc.Graph(id="status-summary-barchart")]
)
status_summary_card = dbc.Card(dbc.CardBody([status_summary]), className="mt-3")

issues_severity_selector_label = html.H4("Select Severity Level(s) To Include:")
issues_severity_selector = dcc.Dropdown(
    options=["Objectionable", "Informational"],
    value=["Objectionable", "Informational"],
    multi=True,
    id="issue-severity-selector",
)
issues_severity_settings = html.Div(
    children=[issues_severity_selector_label, issues_severity_selector],
    style={"width": "50%", "display": "inline-block", "vertical-align": "top"},
)

issues_level_selector_label = html.H4("Select Issue Level(s) To Include:")
issues_level_selector = dcc.Dropdown(
    options={
        "XPCRModuleIssue": "Module Issue",
        "CartridgeIssue": "Run Issue",
        "XPCRModuleLaneIssue": "Lane Issue",
        "SampleIssue": "Sample Issue",
        "XPCRModuleTADMIssue": "TADM Issue",
    },
    value=[
        "XPCRModuleIssue",
        "CartridgeIssue",
        "XPCRModuleLaneIssue",
        "SampleIssue",
        "XPCRModuleTADMIssue",
    ],
    multi=True,
    id="issue-level-selector",
)
issues_level_settings = html.Div(
    children=[issues_level_selector_label, issues_level_selector],
    style={"width": "50%", "display": "inline-block", "vertical-align": "top"},
)

issues_summary = dcc.Loading(children=[issues, dcc.Graph(id="issues-summary-barchart")])
issues_summary_card = dbc.Card(
    dbc.CardBody([issues_severity_settings, issues_level_settings, issues_summary]),
    className="mt-3",
)

first_time_pass_rate = daq.Gauge(
    color={
        "default": "black",
        "gradient": True,
        "ranges": {"red": [0, 50], "yellow": [50, 80], "green": [80, 100]},
    },
    label="First Time Pass Rate",
    max=100,
    min=0,
    units="%",
    id="first-time-pass-rate",
    showCurrentValue=True,
    # style=sensitivity_specificity_style,
    theme=dbc.themes.SOLAR,
)

first_time_pass_rate_description = html.P(
    "First time Pass Rate is calculated as the percentage of modules that achieved approval during the first review performed for a given Run Type in DataSync."
)
first_time_pass_rate_exclusion_note = html.P(
    "*Modules that are in queue or reviewing state with only 1 run available in DataSync are excluded from this calculation."
)
number_of_runs = dcc.Graph(id="number-of-runs-boxplot")

kpis_summary = dcc.Loading(
    children=[
        first_time_pass_rate,
        first_time_pass_rate_description,
        first_time_pass_rate_exclusion_note,
        module_runset_summaries,
        number_of_runs,
    ]
)
kpis_summary_card = dbc.Card(dbc.CardBody([kpis_summary]), className="mt-3")

dashboard_tabs = dbc.Tabs(
    children=[
        dbc.Tab(
            status_summary_card, label="Status Summary", tab_id="status-summary-tab"
        ),
        dbc.Tab(
            issues_summary_card, label="Issues Summary", tab_id="issue-summary-tab"
        ),
        dbc.Tab(kpis_summary_card, label="Other KPIs", tab_id="kpis-summary-tab"),
    ],
    id="review-tabs",
)

layout = html.Div(children=[settings, dashboard_tabs])