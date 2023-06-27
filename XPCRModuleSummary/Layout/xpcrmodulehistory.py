from dash import html, dcc
from Shared.Components import *
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_ag_grid as dag
from Shared.styles import *


def get_xpcrmodulehistory_layout(app):
    url = dcc.Location(id="url")

    """
    Component related to data storage
    """

    xpcrmodule_history_data = dbc.Spinner(
        children=[dcc.Store(id="xpcrmodule-history-data", storage_type="session")],
        fullscreen=True,
    )

    runset_stats_data_by_cartridge = dcc.Store(
        id="runset-stats-data-by-cartridge", storage_type="session"
    )
    runset_stats_data_by_runset = dcc.Store(
        id="runset-stats-data-by-runset", storage_type="session"
    )
    channel_options = dcc.Store(id="channel-options", storage_type="session", data=None)
    assay_options = dcc.Store(id="assay-options", storage_type="session", data=None)
    runset_id_selected = dcc.Store(id="runset-id-selected", storage_type="session")
    spc_channel = dcc.Store(id="spc-channel", storage_type="session")
    storage_div = html.Div(
        [
            xpcrmodule_history_data,
            runset_stats_data_by_cartridge,
            runset_stats_data_by_runset,
            channel_options,
            assay_options,
            runset_id_selected,
            spc_channel,
        ]
    )
    """
    Components related to Gantt chart for XPCR Module History
    """

    fig = go.Figure()
    xpcrmodule_history_gantt = dcc.Graph(figure=fig, id="xpcrmodule-history-gantt")

    """
    Components related to Details on RunSets for XPCR Module History.
    """
    runset_details_table = dag.AgGrid(
        id="runset-details-table",
        enableEnterpriseModules=True,
        columnSize="sizeToFit",
        defaultColDef=dict(
            resizable=True,
        ),
        rowSelection="single",
    )
    runset_details_go_to_runset_button = GoToRunSetButtonAIO(
        aio_id="runset-details-go-to-runset-button"
    )
    runset_details_content = dbc.Card(
        dbc.CardBody(
            children=[runset_details_table, runset_details_go_to_runset_button]
        )
    )

    """
    Components related to details on Remediation Actions for XPCR Module History.
    """

    remediation_actions_table = dag.AgGrid(
        id="remediation-actions-table",
        enableEnterpriseModules=True,
        columnSize="sizeToFit",
        defaultColDef=dict(
            resizable=True,
        ),
        rowSelection="single",
    )

    remediation_actions_go_to_runset_button = GoToRunSetButtonAIO(
        aio_id="remediation-actions-go-to-runset-button"
    )
    remediation_actions_content = dbc.Card(
        dbc.CardBody(
            children=[
                remediation_actions_table,
                remediation_actions_go_to_runset_button,
            ]
        )
    )

    """
    Components related to details on Issues for XPCR Module History.
    """

    issues_table = dag.AgGrid(
        id="issues-table",
        enableEnterpriseModules=True,
        columnSize="sizeToFit",
        defaultColDef=dict(
            resizable=True,
        ),
        rowSelection="single",
    )
    issues_go_to_runset_button = GoToRunSetButtonAIO(
        aio_id="issues-go-to-runset-button"
    )
    issues_content = dbc.Card(
        dbc.CardBody(children=[issues_table, issues_go_to_runset_button])
    )

    """
    Components related to details on RunSetReviews for XPCR Module History.
    """

    runset_reviews_table = dag.AgGrid(
        id="runset-reviews-table",
        enableEnterpriseModules=True,
        columnSize="sizeToFit",
        defaultColDef=dict(
            resizable=True,
        ),
        rowSelection="single",
    )
    runset_reviews_go_to_runset_button = GoToRunSetButtonAIO(
        aio_id="runset-reviews-go-to-runset-button"
    )
    runset_reviews_content = dbc.Card(
        dbc.CardBody(
            children=[runset_reviews_table, runset_reviews_go_to_runset_button]
        )
    )

    """
    Components related to details on Files for XPCR Module History.
    """

    files_table = dag.AgGrid(
        id="files-table",
        enableEnterpriseModules=True,
        columnSize="sizeToFit",
        defaultColDef=dict(
            resizable=True,
        ),
        rowSelection="single",
    )
    files_go_to_runset_button = GoToRunSetButtonAIO(
        aio_id="files-go-to-runset-button",
        main_props={"style": double_button},
        button_props={"style": {"width": "100%"}},
    )
    files_download_button = DownloadBlobFileButton(
        aio_id="files-download-button",
        main_props={"style": double_button},
        button_props={"style": {"width": "100%"}},
    )

    files_content = dbc.Card(
        children=[
            dbc.CardBody(
                children=[
                    files_table,
                    files_go_to_runset_button,
                    files_download_button,
                ]
            ),
        ]
    )

    """
    Components related to run performance details for XPCR Module of Interest.
    """

    run_performance_aggregate_label = html.P(
        "Select Performance Aggregation Type: ", style=halfstyle
    )
    run_performance_aggregate_options = dcc.Dropdown(
        id="run-performance-aggregate-type",
        options=["RunSet", "Run"],
        value="RunSet",
        style=halfstyle,
    )
    run_performance_aggregate_type = html.Div(
        [
            run_performance_aggregate_label,
            run_performance_aggregate_options,
        ],
        style=halfstyle,
    )

    run_performance_statistic_label = html.P(
        "Select Performance Statistic: ", style=halfstyle
    )
    run_performance_statistic_options = dcc.Dropdown(
        id="run-performance-statistic-type", style=halfstyle
    )
    run_performance_statistic_types = html.Div(
        [run_performance_statistic_label, run_performance_statistic_options],
        style=halfstyle,
    )

    run_performance_channel_label = html.P(
        "Select Channel of Interest", style=halfstyle
    )
    run_performance_channel_options = dcc.Dropdown(
        id="run-performance-channel-type", style=halfstyle
    )
    run_performance_channel_types = html.Div(
        [run_performance_channel_label, run_performance_channel_options],
        style=halfstyle,
    )

    run_performance_assay_label = html.P(
        "Select Result Code of Interest", style=halfstyle
    )
    run_performance_assay_options = dcc.Dropdown(
        id="run-performance-assay-type", style=halfstyle
    )
    run_performance_assay_types = html.Div(
        [run_performance_assay_label, run_performance_assay_options],
        style=halfstyle,
    )

    run_performance_table = dag.AgGrid(
        id="run-performance-table",
        enableEnterpriseModules=True,
        columnSize="sizeToFit",
        defaultColDef=dict(
            resizable=True,
        ),
        rowSelection="single",
    )

    run_performance_content = dbc.Card(
        children=[
            dbc.CardBody(
                children=[
                    run_performance_aggregate_type,
                    run_performance_statistic_types,
                    run_performance_channel_types,
                    run_performance_assay_types,
                    run_performance_table,
                ]
            ),
        ]
    )

    """
    Components related to building the Tabs for XPCR Module Related History.
    """
    xpcrmodule_history_tabs = dbc.Tabs(
        children=[
            dbc.Tab(
                runset_details_content, tab_id="runset-details-tab", label="RunSets"
            ),
            dbc.Tab(
                runset_reviews_content,
                tab_id="runset-reviews-tab",
                label="RunSet Reviews",
            ),
            dbc.Tab(issues_content, tab_id="issues-tab", label="Issues"),
            dbc.Tab(
                remediation_actions_content,
                tab_id="remediation-actions-tab",
                label="Remediation Actions",
            ),
            dbc.Tab(files_content, tab_id="files-tab", label="Files"),
            dbc.Tab(
                run_performance_content,
                tab_id="run-performance-tab",
                label="Run Performance",
            ),
        ],
        id="xpcrmodule-history-tabs",
    )

    """
    Wrapper for all components related XPCR Module History.
    """
    xpcrmodulehistory = html.Div(
        children=[
            url,
            storage_div,
            xpcrmodule_history_gantt,
            html.Br(),
            xpcrmodule_history_tabs,
        ]
    )

    return xpcrmodulehistory
