nose-timer
==========

A timer plugin for nosetests (how much time does every test takes?)

(based on `this gist <https://gist.github.com/848183>`_ from @mahmoudimus)

Install
-------

    pip install nose-timer

Usage
-----

Run nosetests with the ``--with-timer`` flag, and you will see a list of the tests and the time spent by each one (in seconds):

    myapp.tests.ABigTestCase.test_the_world_is_running: 56.0010
    myapp.tests.ABigTestCase.test_the_rest_of_the_galaxy_is_running: 2356.0010

