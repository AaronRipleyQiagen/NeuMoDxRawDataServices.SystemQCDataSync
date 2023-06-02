
from . import blueprint
from flask import render_template, request
from app.webapp import login_required
from RunReviewQueue import run_review_queue


@blueprint.route('/', methods=['GET'])
@login_required
def runreview():
    return render_template('run_review_queue.html', dash_url=run_review_queue.url_base+"queue")
