
from . import blueprint
from flask import render_template, request
from app.webapp import login_required
from RunReview import run_review


@blueprint.route('/', methods=['GET'])
@login_required
def runreview():
    return render_template('run-review.html', dash_url=run_review.url_base)
