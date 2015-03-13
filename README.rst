Uplook
========

What?
-----

A Python library to handle user supplied external variable lookups.

Example
-------

2 functions which will be used as an 'external lookup function'.

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



Initialize an Uplook instance:

.. code-block:: python

    >>> instance = UpLook(static='~fubar("value.number.one", "unknown")',
    >>>                   dynamic='~~random(100)',
    >>>                   normal='hello')


List all used functions.  This information can be used to know which functions you should register.

.. code-block:: python

    for function in instance.listfunctions():
        print function

    >>> ['someLookupFunction', 'random']


Register the functions to the object so external lookups can be executed and parse the arguments.

.. code-block:: python

    >>> test.registerLookup("fubar", someLookupFunction)
    >>> test.registerLookup("random", randomInt)


Prepare the object and access values.

.. code-block:: python

    >>> test.parseArguments()
    >>> >>> print test.value.static
    >>> hi
    >>> print test.value.dynamic
    >>> 81
    >>> print test.value.dynamic
    >>> 16
    >>> print test.value.normal
    >>> hello

Each time test.value.dynamic is called, the lookup function is executed
because of the double tilde (~~) in the argument value