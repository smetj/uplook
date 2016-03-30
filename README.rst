======
Uplook
======

What?
-----

An opinionated Python module which facilitates configuration value storage and
access with support for external value lookups.


Examples
--------

Provided kwargs are accessible as attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>>> from uplook import UpLook
    >>>> u = UpLook(one=1, two=2)
    >>>> u
    UpLook({'two': 2, 'one': 1})
    >>>> u.value.one
    1



Dict argument values are recursively mapped to attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>>> from uplook import UpLook
    >>>> u = UpLook(levels = {"level1":{"level2":{"level3": "hello"}}})
    >>>> u
    UpLook({'levels': {'level1': {'level2': {'level3': 'hello'}}}})
    >>>> u.value.levels.level1.level2.level3
    'hello'



Get the data portion without all helper methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>>> from uplook import UpLook
    >>>> u = UpLook(one=1, two=2)
    >>>> u
    UpLook({'two': 2, 'one': 1})
    >>>> data = u.get()
    >>>> data.one
    1



Get a simple dict representation of the data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>>> from uplook import UpLook
    >>>> u = UpLook(one=1, two=2)
    >>>> u
    UpLook({'two': 2, 'one': 1})
    >>>> data = u.dump()
    {'two': 2, 'one': 1}



Iterate over key/value pairs of a data container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>>> from uplook import UpLook
    >>>> u = UpLook(one=1, two=2)
    >>>> u
    UpLook({'two': 2, 'one': 1})
    >>>> for key, value in u.get():
    ....     print "key: %s, value: %s" % (key, value)
    ....
    key: two, value: 2
    key: one, value: 1



External lookup values
----------------------

Some value lookup function
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from uplook import UpLook
    from uplook.errors import NoSuchValue


    def someLookupFunction(key):
        data = {"value.number.one": "hi",
                "value.number.two": "this",
                "value.number.three": "is",
                "value.number.four": "a",
                "value.number.five": "silly",
                "value.number.six": "demo"
                }

        try:
            return data[key]
        except KeyError:
            raise NoSuchValue("%s is an unknown value." % (key))


    def randomInt(max):
        return random.randint(0, max)




Initialize an Uplook instance with a dynamic and static lookup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> instance = UpLook(static='~fubar("value.number.one", "unknown")',
    >>>                   dynamic='~~random(100)',
    >>>                   normal='hello')




List all user defined lookup functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> for function in instance.listfunctions():
            print function
    fubar
    random
    >>>



Register lookup functions
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> instance.registerLookup("fubar", someLookupFunction)
    >>> instance.registerLookup("random", randomInt)




Access a static lookup value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> print test.value.static
    hi
    >>> print test.value.static
    hi



Access a dynamic lookup value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    >>> print test.value.dynamic
    >>> 81
    >>> print test.value.dynamic
    >>> 16


Each time test.value.dynamic is called, the lookup function is executed
because of the double tilde (~~) in the argument value
