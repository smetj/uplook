Uplook
========

What?
-----

A Python library and syntax to perform external lookups to retrieve argument
values. What a function exactly does and how it performs the lookup of the
requested value is entirely up to the programmer.


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

    >>> for function in instance.listfunctions():
            print function
    someLookupFunction
    random
    >>>


Register the functions to the object so external lookups can be executed.

.. code-block:: python

    >>> test.registerLookup("fubar", someLookupFunction)
    >>> test.registerLookup("random", randomInt)


Prepare the object and access values.

.. code-block:: python

    >>> test.parseArguments()
    >>> print test.value.static
    >>> hi
    >>> print test.value.dynamic
    >>> 81
    >>> print test.value.dynamic
    >>> 16
    >>> print test.value.normal
    >>> hello

Each time test.value.dynamic is called, the lookup function is executed
because of the double tilde (~~) in the argument value


Example
=======

The current directory contains a JSON file named "uplook_example.json" with following content:

.. code-block:: json

    {"greeting": "hello"}


Consider following script:

.. code-block:: python

    import argparse
    import json
    from time import sleep

    from uplook import UpLook
    from uplook.errors import NoSuchValue


    def getValueFromJSONFile(value):
        with open("uplook_example.json", "r") as i:
            data = json.load(i)

        if value in data:
            return data[value]
        else:
            raise NoSuchValue(value)


    def generateOutput(input, sec):
        while True:
            print input
            sleep(sec)


    def main():

        parser = argparse.ArgumentParser(description='Continuously write the provided word to STDOUT every x second.')
        parser.add_argument('--input', type=str, required=True, help='The value to print to stdout.')
        parser.add_argument('--sec', type=int, default=1, help='The time in seconds to sleep between each write.')

        user_input = UpLook(**vars(parser.parse_args()))
        user_input.registerLookup("json", getValueFromJSONFile)
        user_input.parseArguments()

        print user_input
        generateOutput(**user_input.dump())

    if __name__ == '__main__':
        main()



Use a simple string value
-------------------------


.. code-block: text

    (pypy-2.5.0)[smetj@indigo uplook]$ python example.py --input howdy
    UpLook({'sleep': 1, 'input': 'howdy'})
    howdy
    howdy
    howdy
    howdy
    ...snip...


Lookup once, a variable in the JSON file
----------------------------------------


.. code-block: text

    (pypy-2.5.0)[smetj@indigo uplook]$ python example.py --input '~json("greeting")'
    UpLook({'sleep': 1, 'input': u'hello'})
    hello
    hello
    ...snip...


For each print, lookup the variable in the JSON file
----------------------------------------------------


.. code-block: text

    (pypy-2.5.0)[smetj@indigo uplook]$ python example.py --input '~~json("greeting")'
    UpLook({'sleep': 1, 'input': u'hello'})
    hello
    hello
    -> (edit uplook_example.json and modify the value of "greeting" without interrupting example.py)
    bonjour
    bonjour


Use a default value in case the lookup function raises NoSuchValue
------------------------------------------------------------------


.. code-block: text

    (pypy-2.5.0)[smetj@indigo uplook]$ python example.py --input '~~json("fubar","Guten Tag")'
    UpLook({'sleep': 1, 'input': u'Guten Tag'})
    Guten Tag
    Guten Tag
    ...snip...

