import operator
import os
from time import time

from nose.plugins.base import Plugin


class TimerPlugin(Plugin):
    """This plugin provides test timings

    """

    name = 'timer'
    score = 1

    COLORS = {
        'ok': '\033[92m',
        'warning': '\033[93m',
        'error': '\033[91m',
        'default': '\033[0m'
    }

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
        self.timer_top_n = int(options.timer_top_n)
        self.timer_ok = int(options.timer_ok)
        self.timer_warning = int(options.timer_warning)
        self._timed_tests = {}

    def startTest(self, test):
        """Initializes a timer before starting a test."""
        self._timer = time()

    def report(self, stream):
        """Report the test times"""
        if not self.enabled:
            return

        d = sorted(self._timed_tests.iteritems(),
                   key=operator.itemgetter(1),
                   reverse=True)

        for i, (test, time_taken) in enumerate(d):
            if i < self.timer_top_n or self.timer_top_n == -1:
                stream.writeln(self._format_report(test, time_taken))

    def _format_report(self, test, time_taken):
        if time_taken <= self.timer_ok:
            color = "default"
        elif time_taken <= self.timer_warning:
            color = "warning"
        else:
            color = "error"
        return "%s%s: %0.4fs%s" % \
            (self.COLORS[color], test, time_taken, self.COLORS["default"])

    def _register_time(self, test):
        self._timed_tests[test.id()] = self._timeTaken()

    def addError(self, test, err, capt=None):
        self._register_time(test)

    def addFailure(self, test, err, capt=None, tb_info=None):
        self._register_time(test)

    def addSuccess(self, test, capt=None):
        self._register_time(test)

    def addOptions(self, parser, env=os.environ):
        super(TimerPlugin, self).addOptions(parser, env)

        _help = ("When the timer plugin is enabled, only show the N tests"
                 " that consume more time. The default, -1, shows all tests.")

        parser.add_option("--timer-top-n", action="store", default="-1",
                          dest="timer_top_n", help=_help)

        _ok_help = ("Normal execution time in seconds."
                    "Such test will be highlight green")

        parser.add_option("--timer-ok", action="store", default=1,
                          dest="timer_ok",
                          help=_ok_help)

        _warning_help = ("Warning about execution time in seconds to "
                         "highlight slow tests yellow. Tests which takes "
                         "more time will be highlighted red")

        parser.add_option("--timer-warning", action="store", default=3,
                          dest="timer_warning",
                          help=_warning_help)
