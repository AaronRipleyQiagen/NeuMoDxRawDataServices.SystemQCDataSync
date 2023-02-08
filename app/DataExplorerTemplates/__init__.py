from flask import Blueprint

blueprint = Blueprint(
    'dataexplorer',
    __name__,
    url_prefix='/data-explorer',
    template_folder='templates',
    static_folder='static'
)
