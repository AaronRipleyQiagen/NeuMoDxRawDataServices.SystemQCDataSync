from flask import Blueprint

blueprint = Blueprint(
    'runreview',
    __name__,
    url_prefix='/run-review',
    template_folder='templates',
    static_folder='static'
)
