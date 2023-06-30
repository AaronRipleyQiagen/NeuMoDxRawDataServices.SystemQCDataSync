from flask import Blueprint

blueprint = Blueprint(
    "xpcrmodule-history",
    __name__,
    url_prefix="/xpcrmodule-history",
    template_folder="templates",
    static_folder="static",
)
