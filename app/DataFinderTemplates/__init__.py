from flask import Blueprint

blueprint = Blueprint(
    "data-finder",
    __name__,
    url_prefix="/data-finder",
    template_folder="templates",
    static_folder="static",
)
