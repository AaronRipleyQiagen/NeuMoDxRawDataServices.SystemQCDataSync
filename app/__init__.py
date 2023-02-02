import dash
import requests
from flask import Flask, render_template, session, request, redirect, url_for
from flask.helpers import get_root_path
from Dashboard import run_review
from flask_session import Session  # https://pythonhosted.org/Flask-Session
import msal
import app_config


def create_app():
    server = Flask(__name__)
    server.secret_key = app_config.SECRET_KEY
    server.config.from_object(app_config)
    Session(server)

    # register_extensions(server)
    register_blueprints(server)

    server = run_review.Add_Dash(server)
    return server


def _protect_dashviews(dashapp):
    for view_func in dashapp.server.view_functions:
        if view_func.startswith(dashapp.config.url_base_pathname):
            dashapp.server.view_functions[view_func] = login_required(
                dashapp.server.view_functions[view_func])


def register_blueprints(server):
    from importlib import import_module
    from app.webapp import server_bp

    server.register_blueprint(server_bp)
    for module_name in (['DashboardTemplates']):
        print(module_name)
        module = import_module('app.{}.routes'.format(module_name))

        server.register_blueprint(module.blueprint)
