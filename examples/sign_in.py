import os

from todoms.provider import WebBrowserProvider

# Get app details from MS and register "http://localhost:8000" as redirect URI, see:
# https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app

APP_ID = os.environ.get("APP_ID")
APP_SECRET = os.environ.get("APP_SECRET")

provider = WebBrowserProvider(APP_ID, APP_SECRET)
provider.authorize(local_port=8000)

print(provider._token)
