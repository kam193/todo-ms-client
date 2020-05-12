import os

from todoms.client import ToDoClient
from todoms.provider import WebBrowserProvider
from todoms.resources import TaskList

# Get app details from MS and register "http://localhost:8000" as redirect URI, see:
# https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app

APP_ID = os.environ.get("APP_ID")
APP_SECRET = os.environ.get("APP_SECRET")

provider = WebBrowserProvider(APP_ID, APP_SECRET)
provider.authorize(local_port=8000)

client = ToDoClient(provider)
task_lists = client.list(TaskList)

print(task_lists)
