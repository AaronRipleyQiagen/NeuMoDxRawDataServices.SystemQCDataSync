from flask_login import UserMixin
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.extensions import login
import msal
import requests
import app_config


class RawDataFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True, unique=True)
    uri = db.Column(db.String(255))


class User:
    def __init__(self, id_token_claims):
        print("User claims ", id_token_claims)
        self.id = id_token_claims.get("oid")
        self.display_name = id_token_claims.get("name")
        self.first_name = id_token_claims.get("given_name")
        self.surname = id_token_claims.get("family_name")
        self.emails = id_token_claims.get("emails")
        self.job_title = id_token_claims.get("jobTitle")
        self.group_id = None
        self.group_display = None

    def get_groups(self):
        roles = {'73b01a3f-0cd6-4809-9661-52633b67fd63': 'System QC Reviewer',
                 '7fdd3800-5468-4550-af37-f803e667a22c': 'System QC Tech',
                 'ca35252d-ec09-4353-9e77-ffc68b9412ae': 'Admin'}

        authority = "https://login.microsoftonline.com/"+app_config.TENANT_ID
        scope = ['https://graph.microsoft.com/.default']
        client = msal.ConfidentialClientApplication(
            app_config.CLIENT_ID, authority=authority, client_credential=app_config.CLIENT_SECRET)
        token_result = client.acquire_token_silent(scope, account=None)

        # If the token is available in cache, save it to a variable
        if token_result:
            access_token = 'Bearer ' + token_result['access_token']

        # If the token is not available in cache, acquire a new one from Azure AD and save it to a variable
        if not token_result:
            token_result = client.acquire_token_for_client(scopes=scope)
            access_token = 'Bearer ' + token_result['access_token']

        test_endpoint = f"{app_config.GRAPH_URL}/users/{self.id}/appRoleAssignments"

        groups = requests.get(  # Use token to call downstream service
            test_endpoint,
            headers={'Authorization': access_token},
        ).json()

        for group in groups['value']:
            if group['resourceDisplayName'] == 'WebAppTest':
                self.group_id = group['appRoleId']
                self.group_display = roles[group['appRoleId']]
