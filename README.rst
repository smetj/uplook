======
Uplook
======

What?
-----

An opinionated Python module to store and access configuration values with
transparent support to query key/values from external resources.

How?
----

The **UpLook** class takes an arbitrary number of key/values. These variables
are stored and accessible as regular object attributes. Values of type
<<dict>> can be accessed in dotted format.

A value can also be a *lookup function* by using a special syntax:

.. code-block:: text

        +-> The name of the funtion.  1 tilde means the function is a static lookup.
        |   2 tildes means a lookup is done every time the attribute is accessed.
        |
        |         +------------+------> An optional pair of values.  The first value is the <key>
        |         |         |           to lookup.  The second value is a default value to return
        |         |         |           in case the key lookup fails.
    ~~function("key", "default value")
                         |
                         |
                         +-> The default value can also be JSON.  In that case you should not use
                             quotes around the value.


An actual example would look like:

.. code-block:: python

    >>>> u = UpLook(servers='~~consul("first", [])')


For this to work you first need to register the function responsible for
retrieving the data.  Depending what is required to lookup the desired value
you could feed a <key> value to the function.

An (silly) example lookup function looks like:

.. code-block:: python

    def show_members(cluster_name):
        if cluster_name == "first"
            return ["one", "two", "three"]
        else:
            raise Exception("Unknown cluster")

    >>>> u.registerLookup("consul", show_members)


Accessing value *u.value.server* will then trigger the the registered *lookup*
function and return its value:

.. code-block:: python

    >>>> u.value.servers
    ["one", "two", "three"]


When the registered function return an Exception, the default value is returned:

.. code-block:: python

    >>>> u = UpLook(servers='~~consul("blahblahblah", [])')
    >>>> u.value.servers
    []


Remarks
-------

- When executing the lookup function fails and a default value has been
  defined, no error is raised and the default value is returned.

- When executing the lookup function fails and **no** default value has been
  defined an error is raised.

- When the default value is between single or double quotes, it is returned
  literally.  When the *default value* is **not** between quotes, it is
  considered to be JSON.  When The JSON is invalid, an error is returned.


More examples
-------------

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
