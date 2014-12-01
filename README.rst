nose-timer
==========

A timer plugin for nosetests that answers the question: *how much time does every test take?*

.. image:: https://travis-ci.org/mahmoudimus/nose-timer.png?branch=master
   :target: https://travis-ci.org/mahmoudimus/nose-timer


Install
-------

.. code::

   pip install nose-timer

Or to install the latest development version from Git:

.. code::

    pip install git+git://github.com/mahmoudimus/nose-timer.git

Or to install the latest from source:

.. code::

    git clone https://github.com/mahmoudimus/nose-timer.git
    cd nose-timer
    python setup.py install


Usage
-----

Run nosetests with the ``--with-timer`` flag, and you will see a list of the
tests and the time spent by each one (in seconds):

.. code:: bash

   myapp.tests.ABigTestCase.test_the_world_is_running: 56.0010s
   myapp.tests.ABigTestCase.test_the_rest_of_the_galaxy_is_running: 2356.0010s


How do I show only the ``n`` slowest tests?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For example, to show only the **10** slowest tests, run nosetests with the
``--timer-top-n`` flag.

.. code:: bash

   nosetests --with-timer --timer-top-n 10


How do I color the output and have pretty colors?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can highlight slower tests using ``--timer-ok`` and ``--timer-warning`` flags.
Default time unit is the second, but you can specify it explicitly, e.g. 1s, 100ms.

- Tests which take less time than ``--timer-ok`` will be highlighted in green.
- Tests which take less time than ``--timer-warning`` will be highlighted in yellow.
- All other tests will be highlighted in red.


How do I turn off pretty colors?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In some cases, you may want to disable colors completely. This is done by using the
``--timer-no-color`` flag. This is useful when running tests in a headless console.


License
-------

``nose-timer`` is an MIT/BSD dual-Licensed library.


Contribute
----------

- Check for open issues or open a fresh issue to start a discussion around a
  feature idea or a bug.
- Fork the repository on GitHub to start making your changes to the master
  branch (or branch off of it).
- Write a test which shows that the bug was fixed or that the feature
  works as expected.
- Send a pull request and bug the maintainer until it gets merged and
  published.
- Make sure to add yourself to the author's file in ``setup.py`` and the
  ``Contributors`` section below :)


Contributors
------------

- `@mahmoudimus <https://github.com/mahmoudimus>`_
- `@fisadev <https://github.com/fisadev>`_
- `@andresriancho <https://github.com/andresriancho>`_
- `@e0ne <https://github.com/e0ne>`_
- `@kevinburke <https://github.com/kevinburke>`_
- `@DmitrySandalov <https://github.com/DmitrySandalov>`_
- `@satyrius <https://github.com/satyrius>`_
- `@skudriashev <https://github.com/skudriashev>`_
- `@whodafly <https://github.com/whodafly>`_
