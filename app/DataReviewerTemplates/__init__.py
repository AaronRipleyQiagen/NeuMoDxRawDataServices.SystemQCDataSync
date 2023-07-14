from flask import Blueprint

blueprint = Blueprint(
    "datareviewer",
    __name__,
    url_prefix="/data-reviewer",
    template_folder="templates",
    static_folder="static",
)
