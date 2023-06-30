from . import blueprint
from flask import render_template, request
from app.webapp import login_required
from XPCRModuleSummary import xpcrmodulesummary


@blueprint.route("/<xpcrmouleId>", methods=["GET"])
@login_required
def runreview(xpcrmouleId):
    return render_template(
        "xpcrmodule-history.html",
        dash_url=xpcrmodulesummary.url_base + "/xpcrmodule-history/" + xpcrmouleId,
    )
