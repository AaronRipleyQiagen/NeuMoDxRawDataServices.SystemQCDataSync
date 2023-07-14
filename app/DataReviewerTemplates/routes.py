from . import blueprint
from flask import render_template, request
from urllib.parse import urlencode
from app.webapp import login_required
from DataReviewer import data_reviewer


@blueprint.route("/", methods=["GET"])
@login_required
def runreview():
    cartridge_ids = request.args.getlist("cartridgeid")
    xpcrmodule_ids = request.args.getlist("xpcrmoduleid")
    query_string = urlencode(
        {"cartridgeid": cartridge_ids, "xpcrmoduleid": xpcrmodule_ids}, doseq=True
    )
    return render_template(
        "data-reviewer.html", dash_url=data_reviewer.url_base + "?" + query_string
    )
