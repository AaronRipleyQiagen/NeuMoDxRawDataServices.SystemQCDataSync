import dash
import requests
from flask import Flask, render_template, session, request, redirect, url_for
from flask.helpers import get_root_path
from RunReview import run_review
from RunReviewQueue import run_review_queue
from RunReviewKPIDashboard import run_review_kpi_dashboard
from XPCRModuleSummary import xpcrmodulesummary
from flask_session import Session
import msal
import app_config
from DataFinder import data_finder
from DataReviewer import data_reviewer


def create_app():
    server = Flask(__name__)
    server.secret_key = app_config.SECRET_KEY
    server.config.from_object(app_config)
    Session(server)

    # register_extensions(server)
    register_blueprints(server)

    server = data_finder.Add_Dash(server)
    server = data_reviewer.Add_Dash(server)
    server = run_review.Add_Dash(server)
    server = run_review_queue.Add_Dash(server)
    server = run_review_kpi_dashboard.Add_Dash(server)
    server = xpcrmodulesummary.Add_Dash(server)

    return server


def _protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(
                dashapp.server.view_functions[view_func]
            )


def register_blueprints(server):
    from importlib import import_module
    from app.webapp import server_bp

    server.register_blueprint(server_bp)
    for module_name in [
        "RunReviewTemplates",
        "RunReviewQueueTemplates",
        "RunReviewKPIDashboardTemplates",
        "XPCRModuleHistoryTemplates",
        "DataFinderTemplates",
        "DataReviewerTemplates",
    ]:
        print("Registering Blueprints for: ", module_name)
        module = import_module("app.{}.routes".format(module_name))

        server.register_blueprint(module.blueprint)
