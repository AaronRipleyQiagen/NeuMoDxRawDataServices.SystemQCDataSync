from . import blueprint
from flask import render_template, request
from urllib.parse import urlencode
from app.webapp import login_required
from DataReviewer import data_reviewer


@blueprint.route("/", methods=["GET"])
@login_required
def runreview():
    runset_ids = request.args.getlist("runset_ids")
    query_string = urlencode({"my_list": runset_ids}, doseq=True)
    return render_template(
        "data-reviewer.html", dash_url=data_reviewer.url_base + "?" + query_string
    )
