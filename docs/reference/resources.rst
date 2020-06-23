Resources
=========

.. module:: todoms.resources

Module `todoms.resources` contains objects represent resource in ToDo API, like
tasks and lists.

----------------
Resource classes
----------------

.. autoclass:: TaskList
    :members:
    :undoc-members:
    :inherited-members:
    :exclude-members: ATTRIBUTES, ENDPOINT


.. autoclass:: Task
    :members:
    :undoc-members:
    :inherited-members:
    :exclude-members: ATTRIBUTES, ENDPOINT


.. autoclass:: Attachment
    :members:
    :undoc-members:
    :inherited-members:
    :exclude-members: ATTRIBUTES, ENDPOINT

----------
Exceptions
----------

.. autoclass:: ResourceAlreadyCreatedError

.. autoclass:: NotSupportedError

.. autoclass:: TaskListNotSpecifiedError
