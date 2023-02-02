from flask import Blueprint

blueprint = Blueprint(
    'dashboards',
    __name__,
    url_prefix='/dashboards',
    template_folder='templates',
    static_folder='static'
)