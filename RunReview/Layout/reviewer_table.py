import dash_bootstrap_components as dbc
from .ReviewCards import *


review_tabs = dbc.Tabs(
    children=[
        dbc.Tab(
            line_data_content, label="View Line Data", tab_id="run-review-line-data"
        ),
        dbc.Tab(run_summary_content, label="View Run Stats",
                tab_id="run-summary-data"),
        dbc.Tab(
            module_issue_content,
            label="Note Module Issue",
            tab_id="run-review-module-issues",
        ),
        dbc.Tab(
            run_issue_content, label="Note Run Issue", tab_id="run-review-run-issues"
        ),
        dbc.Tab(
            module_lane_issue_content,
            label="Note Lane Issue",
            tab_id="run-review-module-lane-issues",
        ),
        dbc.Tab(
            sample_issue_content,
            label="Note Sample Issue",
            tab_id="run-review-sample-issues",
        ),
        dbc.Tab(
            tadm_issue_content, label="Note TADM Issue", tab_id="run-review-tadm-issues"
        ),
        dbc.Tab(
            active_issues_content,
            label="View Active Issues",
            tab_id="run-review-active-issues",
        ),
        dbc.Tab(
            remediation_action_content,
            label="Manage Remediation Actions",
            tab_id="run-review-remediation-actions",
        ),
        dbc.Tab(
            cartridge_pictures_content,
            label="Cartridge Pictures",
            tab_id="cartidge-pictures",
        ),
        dbc.Tab(tadm_pictures_content, label="TADM Pictures",
                tab_id="tadm-pictures"),
        dbc.Tab(misc_files_content, label="Miscellaneous Files",
                tab_id="misc-files"),
        dbc.Tab(run_review_content, label="Runset Reviews",
                tab_id="runset-reviews"),
        dbc.Tab(comments_content, label="Comments", tab_id="runset-comments"),
    ],
    id="review-tabs",
)
