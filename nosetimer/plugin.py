import operator
from time import time

from nose.plugins.base import Plugin


class TimerPlugin(Plugin):
    """This plugin provides test timings

    """

    name = 'timer'
    score = 1

    def _timeTaken(self):
        if hasattr(self, '_timer'):
            taken = time() - self._timer
        else:
            # test died before it ran (probably error in setup())
            # or success/failure added before test started probably
            # due to custom TestResult munging
            taken = 0.0
        return taken

    def configure(self, options, config):
        """Configures the test timer plugin."""
        super(TimerPlugin, self).configure(options, config)
        self.config = config
        self._timed_tests = {}

    def startTest(self, test):
        """Initializes a timer before starting a test."""
        self._timer = time()

    def report(self, stream):
        """Report the test times"""
        if not self.enabled:
            return
        d = sorted(self._timed_tests.iteritems(), key=operator.itemgetter(1))
        for test, time_taken in d:
            stream.writeln("%s: %0.4fs" % (test, time_taken))

    def _register_time(self, test):
        self._timed_tests[test.id()] = self._timeTaken()

    def addError(self, test, err, capt=None):
        self._register_time(test)

    def addFailure(self, test, err, capt=None, tb_info=None):
        self._register_time(test)

    def addSuccess(self, test, capt=None):
        self._register_time(test)

