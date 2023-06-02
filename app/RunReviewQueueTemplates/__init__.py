from flask import Blueprint

blueprint = Blueprint(
    'runreviewqueue',
    __name__,
    url_prefix='/run-review-queue',
    template_folder='templates',
    static_folder='static'
)
