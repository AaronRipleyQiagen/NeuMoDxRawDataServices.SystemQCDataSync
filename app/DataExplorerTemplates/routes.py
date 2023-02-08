
from . import blueprint
from flask import render_template, request
from app.webapp import login_required
from DataExplorer import data_explorer


@blueprint.route('/', methods=['GET'])
@login_required
def dataexplorer():
    return render_template('data-explorer.html', dash_url=data_explorer.url_base)
