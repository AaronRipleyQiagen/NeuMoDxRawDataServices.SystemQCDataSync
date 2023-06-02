import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from .styles import *

issue_post_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Issue Creation Result")),
        dbc.ModalBody(html.P(id="issue-post-response-message")),
    ],
    id="issue-post-response",
    is_open=False,
)

issue_delete_confirmation = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Issue Deletion Confirmation")),
        dbc.ModalBody("Are you sure you want to delete this issue?"),
        html.Div(
            [
                dbc.Button(
                    "Yes",
                    id="issue-delete-confirmed-button",
                    style={
                        "width": "35%",
                        "margin-left": "10%",
                        "display": "inline-block",
                    },
                ),
                dbc.Button(
                    "No",
                    id="issue-delete-canceled-button",
                    style={
                        "width": "35%",
                        "margin-left": "10%",
                        "display": "inline-block",
                    },
                ),
            ]
        ),
    ],
    id="issue-delete-confirmation",
    is_open=False,
)

issue_delete_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Issue Deletion Result")),
        dbc.ModalBody("Issue was deleted successfully"),
    ],
    id="issue-delete-response",
    is_open=False,
)

remediation_action_post_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Remediation Action Creation Result")),
        dbc.ModalBody("Remediation Action was added successfully"),
    ],
    id="remediation-action-post-response",
    is_open=False,
)

remediation_action_update_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Remediation Action Update Result")),
        dbc.ModalBody("Remediation Action was updated successfully"),
    ],
    id="remediation-action-update-response",
    is_open=False,
)

remediation_action_delete_confirmation = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle(
            "Remediation Action Deletion Confirmation")),
        dbc.ModalBody(
            "Are you sure you want to delete this remediation action?"),
        html.Div(
            [
                dbc.Button(
                    "Yes",
                    id="remediation-action-delete-confirmed-button",
                    style={
                        "width": "35%",
                        "margin-left": "10%",
                        "display": "inline-block",
                    },
                ),
                dbc.Button(
                    "No",
                    id="remediation-action-delete-canceled-button",
                    style={
                        "width": "35%",
                        "margin-left": "10%",
                        "display": "inline-block",
                    },
                ),
            ]
        ),
    ],
    id="remediation-action-delete-confirmation",
    is_open=False,
)

remediation_action_delete_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Remediation Action Deletion Result")),
        dbc.ModalBody("Remediation Action was deleted successfully"),
    ],
    id="remediation-action-delete-response",
    is_open=False,
)

issue_resolution_remediation_action_selection = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Remediation Action Selection")),
        dbc.ModalBody(
            [
                html.P(
                    "Please select the remediation action intended to address this issue."
                ),
                dcc.Dropdown(id="issue-resolution-remediation-action-options"),
                html.P("Did it work?"),
                dcc.Dropdown(
                    id="issue-resolution-remediation-success",
                    options={1: "Yes", 0: "No"},
                ),
                dbc.Button("Submit", id="issue-resolution-submit"),
            ]
        ),
    ],
    id="issue-resolution-remediation-action-selection-prompt",
    is_open=False,
)

issue_resolution_remediation_action_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Issue Resolution Status")),
        dbc.ModalBody("Remediation Attempt was recorded successfully"),
    ],
    id="issue-remediation-attempt-submission-response",
    is_open=False,
)

run_review_update_response = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle(
            "Run Review Status Updated Successfully")),
        dbc.ModalBody("Run Review Status Changed to Completed."),
    ],
    id="run-review-status-update-post-response",
    is_open=False,
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
    id="reviewgroup-selector-modal",
    is_open=False,
)

add_comment_button = dbc.Button(
    "Add Comment",
    id="add-comment-button",
    style={"width": "35%", "margin-left": "10%", "display": "inline-block"},
)

cancel_comment_button = dbc.Button(
    "Cancel",
    id="cancel-comment-button",
    style={"width": "35%", "margin-left": "10%", "display": "inline-block"},
)

comments_text = (
    dcc.Textarea(
        id="comments-text",
        value="Enter Comment Here",
        style={"width": "100%", "height": 300},
    ),
)

comments_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Add Comment to Runset")),
        dbc.ModalBody(comments_text),
        html.Div([add_comment_button, cancel_comment_button]),
    ],
    id="comments-modal",
    is_open=False,
)

comments_view_text = html.P(id="comments-view-text")

comments_view_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Comment Text")),
        dbc.ModalBody(comments_view_text),
    ],
    id="comments-view-modal",
    is_open=False,
)

comments_post_response = dbc.Modal(
    [dbc.ModalHeader(dbc.ModalTitle("Comment Added to Runset"))],
    id="comments-post-response",
    is_open=False,
)

confirm_comment_delete_button = dbc.Button(
    "Yes",
    id="confirm-comment-delete-button",
    style={"width": "35%", "margin-left": "10%", "display": "inline-block"},
)

cancel_comment_delete_button = dbc.Button(
    "No",
    id="cancel-comment-delete-button",
    style={"width": "35%", "margin-left": "10%", "display": "inline-block"},
)

comments_delete_confirmation = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Confirm Comment Deletion")),
        dbc.ModalBody("Are You Sure you want to delete this comment?"),
        html.Div([confirm_comment_delete_button,
                 cancel_comment_delete_button]),
    ],
    id="comments-delete-confirmation",
    is_open=False,
)

comments_delete_response = dbc.Modal(
    [dbc.ModalHeader(dbc.ModalTitle("Comment Removed from Runset"))],
    id="comments-delete-response",
    is_open=False,
)


message_objects = html.Div([
    issue_post_response,
    issue_delete_confirmation,
    issue_delete_response,
    remediation_action_post_response,
    remediation_action_update_response,
    remediation_action_delete_confirmation,
    remediation_action_delete_response,
    issue_resolution_remediation_action_selection,
    issue_resolution_remediation_action_response,
    run_review_update_response,
    reviewgroup_selector_modal,
    comments_modal,
    comments_view_modal,
    comments_post_response,
    comments_delete_confirmation,
    comments_delete_response,
])
