nose-timer
==========

A timer plugin for nosetests that answers the question: *how much time does every test take?*

.. image:: https://travis-ci.org/mahmoudimus/nose-timer.png?branch=master
   :target: https://travis-ci.org/mahmoudimus/nose-timer


Install
-------

To install the latest release from PyPI::

    pip install nose-timer

Or to install the latest development version from Git::

    pip install git+git://github.com/mahmoudimus/nose-timer.git

Or to install the latest from source::

    git clone https://github.com/mahmoudimus/nose-timer.git
    cd nose-timer
    pip install .

You can also make a developer install if you plan on modifying the
source frequently::

    pip install -e .


Usage
-----

Run nosetests with the ``--with-timer`` flag, and you will see a list of the
tests and the time spent by each one (in seconds)::

    myapp.tests.ABigTestCase.test_the_world_is_running: 56.0010s
    myapp.tests.ABigTestCase.test_the_rest_of_the_galaxy_is_running: 2356.0010s


How do I show only the ``n`` slowest tests?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For example, to show only the **10** slowest tests, run nosetests with the
``--timer-top-n`` flag::

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


How do I filter results by colors?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to filter results by color. To do so, you can use the
``--timer-filter`` flag::

    nosetests --with-timer --timer-filter ok
    nosetests --with-timer --timer-filter warning
    nosetests --with-timer --timer-filter error


Or to apply several filters at once::

    nosetests --with-timer --timer-filter warning,error

How do I cause slow tests to fail?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can cause any tests that exceed a threshold to fail by specifying the
``--timer-fail`` option:

- If you specify ``--timer-fail warning``, slow tests which would be displayed
  as a warning (i.e. that take more time than  ``--timer-ok``) will fail.
- If you specify ``--timer-fail error``, slow tests which would be displayed as
  an error (i.e. that take more time than ``--timer-warning``) will fail.

For example, to fail any tests that take more than 5 seconds::

    nosetests --with-timer --timer-warning 5.0 --timer-fail error


How do I export the results ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``--timer-json-file <myfile.json>`` flag, it will save the result
in the following format::

  {
   'tests':
    {
    '<test key 1>':
      {
        'status': 'success'|'error'|'fail,
        'time': <float in s>
      },
    '<test key 2>':
      {
        'status': 'success'|'error'|'fail,
        'time': <float in s>
      },
     ....
   }


License
-------

``nose-timer`` is MIT Licensed library.


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

- `@acordiner <https://github.com/acordiner>`_
- `@andresriancho <https://github.com/andresriancho>`_
- `@cgoldberg <https://github.com/cgoldberg>`_
- `@DmitrySandalov <https://github.com/DmitrySandalov>`_
- `@e0ne <https://github.com/e0ne>`_
- `@ereOn <https://github.com/ereOn>`_
- `@fisadev <https://github.com/fisadev>`_
- `@garbageek <https://github.com/garbageek>`_
- `@HaraldNordgren <https://github.com/HaraldNordgren>`_
- `@hugovk <https://github.com/hugovk>`_
- `@jakirkham <https://github.com/jakirkham>`_
- `@kevinburke <https://github.com/kevinburke>`_
- `@mahmoudimus <https://github.com/mahmoudimus>`_
- `@satyrius <https://github.com/satyrius>`_
- `@skudriashev <https://github.com/skudriashev>`_
- `@whodafly <https://github.com/whodafly>`_
