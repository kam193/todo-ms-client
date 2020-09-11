import os
from pprint import pprint

from todoms.client import ToDoClient
from todoms.provider import WebBrowserProvider
from todoms.resources import Task, TaskList

# Get app details from MS and register "http://localhost:8000" as redirect URI, see:
# https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app

APP_ID = os.environ.get("APP_ID")
APP_SECRET = os.environ.get("APP_SECRET")

provider = WebBrowserProvider(APP_ID, APP_SECRET)
provider.authorize(local_port=8000)

client = ToDoClient(provider)
# task_lists = client.list(TaskList, name="name>")
task_lists = client.list(TaskList)


print(task_lists)

list_1 = client.get(TaskList, task_lists[1].id)

print(list_1)
pprint(list_1.get_tasks())

all_tasks = client.list(Task)
pprint(all_tasks)

# Updating task
# first_task = all_tasks[0]
# first_task.body = "changed"
# first_task.update()

# Complete task
# first_task = all_tasks[0]
# first_task.complete()

# Create list
# new_list = TaskList(client, "My new list")
# new_list.create()
