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
                 '5e7f84e5-c5d7-4c36-9d34-72d4586e410c': 'PSG Crew',
                 'ca35252d-ec09-4353-9e77-ffc68b9412ae': 'Admin',
                 '1b837f0a-11fb-4f27-9d3a-3b2edc6d10a1': 'Engineering',
                 '4d4e4d3c-b7cc-4fb4-9e1a-546fd8db7e80': 'System Integration Lead'}

        dataenvironments = {'73b01a3f-0cd6-4809-9661-52633b67fd63': 'D5E6801C-6C4E-4DE9-8BD2-829406E455A5',
                            '7fdd3800-5468-4550-af37-f803e667a22c': 'D5E6801C-6C4E-4DE9-8BD2-829406E455A5',
                            '5e7f84e5-c5d7-4c36-9d34-72d4586e410c': 'E19AB550-C121-4958-955C-4253E1673016',
                            'ca35252d-ec09-4353-9e77-ffc68b9412ae': 'D5E6801C-6C4E-4DE9-8BD2-829406E455A5',
                            '1b837f0a-11fb-4f27-9d3a-3b2edc6d10a1': 'D5E6801C-6C4E-4DE9-8BD2-829406E455A5',
                            '4d4e4d3c-b7cc-4fb4-9e1a-546fd8db7e80': 'D5E6801C-6C4E-4DE9-8BD2-829406E455A5'}

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
                self.default_environment = dataenvironments[group['appRoleId']]
