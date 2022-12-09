# ToDo-MS-client

![https://github.com/kam193/todo-ms-client/actions](https://github.com/kam193/todo-ms-client/workflows/Test%20and%20build/badge.svg) [![PyPI version](https://badge.fury.io/py/todo-ms-client.svg)](https://pypi.org/project/todo-ms-client/)

> :warning: **This library is on early stage of development.**
> Only selected features are available. See issues for current roadmap.

Unofficial Python library for MS ToDo API

- [Contributing](CONTRIBUTING.md) - development rules
- [Changelog](CHANGELOG.md) - changelog
- [sample.py](examples/sample.py) - simply example of library use

Available from PIP:

    pip install todo-ms-client

To learn more about MS ToDo API look into Microsoft docs on [Microsoft Docs page](https://docs.microsoft.com/en-us/graph/api/resources/todo-overview?view=graph-rest-beta).

## Feature coverage

This is the matrix of main features supported by the official API and this library.

| Feature            | Supported by official API | Supported by ToDo-MS-client | Known limitations                             |
| ------------------ | ------------------------- | --------------------------- | --------------------------------------------- |
| Task lists - CRUD  | :heavy_check_mark:        | :heavy_check_mark:          |                                               |
| My day             | :x:                       | -                           |                                               |
| Tasks - CRUD       | :heavy_check_mark:        | :heavy_check_mark:          | API doesn't support moving task between lists |
| Tasks - recurrence | :heavy_check_mark:        | :large_orange_diamond:      | API is a bit unclear here, need testing       |
| Subtasks - CRUD    | :heavy_check_mark:        | :heavy_check_mark:                         |                                               |
| Reminders - CRUD   | :heavy_check_mark:        | :x:                         |                                               |
| Attachments - CRUD | :heavy_check_mark:        | :x:                         |                                               |
| Linked resources   | :heavy_check_mark:        | :x:                         | Not planned at the moment                     |
| Categories         | :heavy_check_mark:        | :x:                         |                                               |
| Searching          | :heavy_check_mark:        | :large_orange_diamond:      |                                               |
| Delta updates      | :heavy_check_mark:        | :x:                         |                                               |

---

This library is not created nor related in any way with Microsoft.
