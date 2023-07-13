from . import blueprint
from flask import render_template, request
from app.webapp import login_required
from DataFinder import data_finder


@blueprint.route("/", methods=["GET"])
@login_required
def datafinder():
    return render_template("data-finder.html", dash_url=data_finder.url_base)
