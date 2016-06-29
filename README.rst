======
Uplook
======

What?
-----

An opinionated Python module to store and access configuration values with
transparent support to query external resources.

How?
----

The **UpLook** class takes an arbitrary number of key/values. The variables
used to initialize the module can be retrieved as object attributes. Values of
type <<dict>> can be accessed in dotted format.


A value can also be a *lookup function* by using a special syntax.  When a
value starts with a '~' or '~~' it means that accessing the UpLook instance
attribute invokes a funtion in order to retrieve the desired value.


.. code-block:: python

    u = UpLook(servers='~~consul("first", [])')


For this to work you first need to register the function responsible for
retrieving the data:

.. code-block:: python

    def show_members(cluster_name):
        if cluster_name == "first"
            return ["one", "two", "three"]
        else:
            raise Exception("Unknown cluster")

    u.registerLookup("consul", show_members)


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
