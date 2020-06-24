Filters
=======

Module `todoms.filters` contains function useful when filtering resources, typically
on `list` method. Using this you can build basic filters without fully understanding
the OData `$filter` parameter.

------
Syntax
------

The general syntax is `field_name=func(value)`. `field_name` should match the original
field name in API, `func` is one of available filters and `value` could be any correct
value for given field. Filters automatically converts boolean, enums from 
:doc:`attributes` and datetime objects.

.. note::

    Support for filtering is now only basic. This part will be changed

-----------------
Available filters
-----------------

.. automodule:: todoms.filters
