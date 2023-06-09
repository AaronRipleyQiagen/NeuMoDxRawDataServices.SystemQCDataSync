from flask import Blueprint

blueprint = Blueprint(
    "runreviewkpidashboard",
    __name__,
    url_prefix="/run-review-kpi-dashboard",
    template_folder="templates",
    static_folder="static",
)
