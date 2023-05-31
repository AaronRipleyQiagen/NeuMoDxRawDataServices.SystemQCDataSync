import os
from flask import Blueprint, redirect, render_template, request, url_for, request, session
from flask_login import current_user
from werkzeug.urls import url_unparse, url_parse
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient
from app.forms import FileUploadForm
from app.models import User, RawDataFile
import logging
import msal
import app_config
from functools import wraps
from flask import request, redirect, flash
import requests

server_bp = Blueprint('main', __name__)


def login_required(f):
    """
    Decorator for flask endpoints, ensuring that the user is authenticated and redirecting to log-in page if not.
    Example:
    ```
        from flask import current_app as app
        @login_required
        @app.route("/")
        def index():
            return 'route protected'
    ```
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for('main.login'))
        elif session['user'].group_id == None:
            return redirect(url_for('main.access_error'))
        return f(*args, **kwargs)
    return decorated_function


@server_bp.route("/")
def index():
    if not session.get("user"):
        return render_template('index.html', user=None, title='Home')
    return render_template('index.html', user=session["user"], version=msal.__version__, title='Home')


@server_bp.route("/restricted-access")
def access_error():
    return render_template('access_error.html', user=session["user"], version=msal.__version__, title='Restricted Access')


@server_bp.route("/login")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    return redirect(session["flow"]["auth_uri"])


@server_bp.route(app_config.REDIRECT_PATH)
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        user = User(result.get("id_token_claims"))
        user.get_groups()
        print('yes')
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = user
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("main.index"))


@server_bp.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("main.index", _external=True))


@server_bp.route("/graphcall")
def graphcall():
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("main.login"))
    graph_data = requests.get(  # Use token to call downstream service
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
    ).json()
    return render_template('display.html', result=graph_data)


@server_bp.route('/upload/', methods=['GET', 'POST'])
@login_required
def upload_file():
    logging.info("Trying to Upload")
    form = FileUploadForm()
    error = None
    if form.validate_on_submit():
        logging.info('initating upload protocol')
        filename = secure_filename(form.file.data.filename)
        file_content = form.file.data.read()
        logging.info('Establishing connection to raw data file blob storage')
        account_url = "https://prdqianeumodxrdseusst.blob.core.windows.net"
        secret_key = os.environ['NEUMODXSYSTEMQC_RAWDATAFILES_KEY']
        # Create A Blob Service Client Object from account information and key
        blob_service_client = BlobServiceClient(
            account_url=account_url, credential=secret_key)
        logging.info("Connected to Storage Account.")
        raw_data_container = 'neumodxsystemqc-rawdatafiles'
        blob_client = blob_service_client.get_blob_client(
            container=raw_data_container, blob=filename)

        logging.info("Attempting to upload File Data to blob")

        # Upload the file to Azure Blob Storage
        blob_client.upload_blob(
            data=file_content, connection_verify=False, overwrite=True)
        # Add Meta Data for Systems Manufacturing
        meta_data = {'DataEnvironmentId': session['user'].default_environment}
        blob_client.set_blob_metadata(meta_data, connection_verify=False)
        flash(filename + ' Was Uploaded Successfully')
        return redirect(url_for('main.upload_file'))

    return render_template('uploadrawdata.html', form=form, error=error)


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)


def _build_auth_code_flow(authority=None, scopes=None):

    if os.environ['FLASK_ENV'] == 'development':
        return _build_msal_app(authority=authority).initiate_auth_code_flow(app_config.SCOPE,
                                                                            redirect_uri=url_for("main.authorized", _external=True))
    else:
        return _build_msal_app(authority=authority).initiate_auth_code_flow(app_config.SCOPE,
                                                                            redirect_uri=url_for("main.authorized", _external=True, _scheme='https'))


def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        print("trying to get token")
        result = cca.acquire_token_silent(scope, account=accounts[0])
        print(result)
        _save_cache(cache)
        return result
