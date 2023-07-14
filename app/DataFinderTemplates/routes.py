from . import blueprint
from flask import render_template, request
from app.webapp import login_required
from DataFinder import data_finder
from urllib.parse import urlencode


@blueprint.route("/", methods=["GET"])
@login_required
def datafinder():
    xpcr_module_ids = request.args.getlist("xpcrmoduleid")
    query_string = urlencode({"xpcrmoduleid": xpcr_module_ids}, doseq=True)
    return render_template(
        "data-finder.html", dash_url=data_finder.url_base + "?" + query_string
    )
