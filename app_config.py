import os

b2c_tenant = "qianims"
signupsignin_user_flow = "B2C_1_nimsdev_signupsignin"
# editprofile_user_flow = "B2C_1_profileediting1"

# resetpassword_user_flow = "B2C_1_passwordreset1"  # Note: Legacy setting.
# If you are using the new
# "Recommended user flow" (https://docs.microsoft.com/en-us/azure/active-directory-b2c/user-flow-versions),
# you can remove the resetpassword_user_flow and the B2C_RESET_PASSWORD_AUTHORITY settings from this file.

authority_template = "https://{tenant}.b2clogin.com/{tenant}.onmicrosoft.com/{user_flow}"

# Application (client) ID of app registration
CLIENT_ID = "7c4ff570-714c-4636-9d25-18afa25ddb74"

# Placeholder - for use ONLY during testing.
CLIENT_SECRET = ".pD8Q~ZrDn5tkE2JOwlagWT75K.Q_iFxXHJGddnf"
# In a production app, we recommend you use a more secure method of storing your secret,
# like Azure Key Vault. Or, use an environment variable as described in Flask's documentation:
# https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# if not CLIENT_SECRET:
#     raise ValueError("Need to define CLIENT_SECRET environment variable")

AUTHORITY = authority_template.format(
    tenant=b2c_tenant, user_flow=signupsignin_user_flow)
# B2C_PROFILE_AUTHORITY = authority_template.format(
#     tenant=b2c_tenant, user_flow=editprofile_user_flow)

# B2C_RESET_PASSWORD_AUTHORITY = authority_template.format(
#     tenant=b2c_tenant, user_flow=resetpassword_user_flow)
# If you are using the new
# "Recommended user flow" (https://docs.microsoft.com/en-us/azure/active-directory-b2c/user-flow-versions),
# you can remove the resetpassword_user_flow and the B2C_RESET_PASSWORD_AUTHORITY settings from this file.

# Used for forming an absolute URL to your redirect URI.
REDIRECT_PATH = "/getAToken"
# The absolute URL must match the redirect URI you set
# in the app's registration in the Azure portal.

# This is the API resource endpoint
# Application ID URI of app registration in Azure portal
ENDPOINT = 'https://graph.microsoft.com/v1.0/'

# These are the scopes you've exposed in the web API app registration in the Azure portal
# Example with two exposed scopes: ["demo.read", "demo.write"]
SCOPE = ['https://graph.microsoft.com/v1.0/.default']

# Specifies the token cache should be stored in server-side session
SESSION_TYPE = "filesystem"
REQUIRE_AUTHENTICATION = True
TENANT_ID = "c6cc9b34-5ccc-40b0-8fd8-8fe707e5bcee"
GRAPH_URL = "https://graph.microsoft.com/v1.0"

SECRET_KEY = 'f12aae45-e150-4499-8dca-e8a9b7f21b13'
