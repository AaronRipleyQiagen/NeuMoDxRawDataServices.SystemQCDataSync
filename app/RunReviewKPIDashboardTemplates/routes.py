from . import blueprint
from flask import render_template, request
from app.webapp import login_required
from RunReviewKPIDashboard import run_review_kpi_dashboard


@blueprint.route("/", methods=["GET"])
@login_required
def runreview():
    return render_template(
        "run_review_kpi_dashboard.html", dash_url=run_review_kpi_dashboard.url_base
    )
