Resources
=========

.. module:: todoms.resources

Module `todoms.resources` contains objects represent resource in ToDo API, like
tasks and lists.

----------------
Resource classes
----------------

.. autoclass:: TaskList
    :exclude-members: ATTRIBUTES, ENDPOINT


.. autoclass:: Task
    :exclude-members: ATTRIBUTES, ENDPOINT


.. autoclass:: Attachment
    :exclude-members: ATTRIBUTES, ENDPOINT

----------
Exceptions
----------

.. autoclass:: ResourceAlreadyCreatedError
    :no-inherited-members:

.. autoclass:: NotSupportedError
    :no-inherited-members:

.. autoclass:: TaskListNotSpecifiedError
    :no-inherited-members:
