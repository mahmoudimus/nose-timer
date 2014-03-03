import re
import operator
import os
from time import time
import logging

from nose.plugins.base import Plugin

log = logging.getLogger('nose.plugin.timer')


class TimerPlugin(Plugin):
    """This plugin provides test timings."""

    name = 'timer'
    score = 1

    COLORS = {
        'ok': '\033[92m',
        'warning': '\033[93m',
        'error': '\033[91m',
        'default': '\033[0m'
    }

    time_format = re.compile(r'^(?P<time>\d+)(?P<units>s|ms)?$')

    def _timeTaken(self):
        if hasattr(self, '_timer'):
            taken = time() - self._timer
        else:
            # test died before it ran (probably error in setup())
            # or success/failure added before test started probably
            # due to custom TestResult munging
            taken = 0.0
        return taken

    def _parse_time(self, value):
        """Parse string time representation to get number of milliseconds.
        Raises ValueError for invalid format
        """
        try:
            # Default time unit is second, we should convert it to milliseconds
            return int(value) * 1000
        except ValueError:
            # Try to parse if we are unlucky to cast value into int
            m = self.time_format.match(value)
            if not m:
                raise ValueError("Could not parse time represented by "
                                 "'{t}'".format(t=value))
            time = int(m.group('time'))
            if m.group('units') != 'ms':
                time *= 1000
            return time

    def configure(self, options, config):
        """Configures the test timer plugin."""
        super(TimerPlugin, self).configure(options, config)
        self.config = config
        self.timer_top_n = int(options.timer_top_n)
        self.timer_ok = self._parse_time(options.timer_ok)
        self.timer_warning = self._parse_time(options.timer_warning)
        self.timer_verbose = options.timer_verbose
        self._timed_tests = {}

    def startTest(self, test):
        """Initializes a timer before starting a test."""
        self._timer = time()

    def afterTest(self, test):
        """Called after the test has been run and the result recorded (after
        stopTest)."""
        if self.timer_verbose:
            try:
                log.info(self._timed_tests[test.id()])
            except KeyError:
                pass

    def report(self, stream):
        """Report the test times."""
        if not self.enabled:
            return

        d = sorted(self._timed_tests.items(),
                   key=operator.itemgetter(1),
                   reverse=True)

        for i, (test, time_taken) in enumerate(d):
            if i < self.timer_top_n or self.timer_top_n == -1:
                stream.writeln(self._format_report(test, time_taken))

    def _format_report(self, test, time_taken):
        # Time taken is stores as seconds, we should convert it to milliseconds
        # to be able to compare with timer settings.
        taken_ms = time_taken * 1000
        if taken_ms <= self.timer_ok:
            color = "default"
        elif taken_ms <= self.timer_warning:
            color = "warning"
        else:
            color = "error"
        return "%s%s: %0.4fs%s" % \
            (self.COLORS[color], test, time_taken, self.COLORS["default"])

    def _register_time(self, test):
        self._timed_tests[test.id()] = self._timeTaken()

    def addError(self, test, err, capt=None):
        """Called when a test raises an uncaught exception."""
        self._register_time(test)

    def addFailure(self, test, err, capt=None, tb_info=None):
        """Called when a test fails."""
        self._register_time(test)

    def addSuccess(self, test, capt=None):
        """Called when a test passes."""
        self._register_time(test)

    def addOptions(self, parser, env=os.environ):
        """Called to allow plugin to register command-line options with the
        parser.
        """
        super(TimerPlugin, self).addOptions(parser, env)

        _help = ("When the timer plugin is enabled, only show the N tests "
                 "that consume more time. The default, -1, shows all tests.")

        parser.add_option("--timer-top-n", action="store", default="-1",
                          dest="timer_top_n", help=_help)

        _time_unit_help = "Default time unit is a second, but you can set " \
                          "it explicitly (e.g. 1s, 500ms)."

        _ok_help = ("Normal execution time. Such test will be highlight "
                    "green. {units}".format(units=_time_unit_help))

        parser.add_option("--timer-ok", action="store", default=1,
                          dest="timer_ok",
                          help=_ok_help)

        _warning_help = ("Warning about execution time to highlight slow "
                         "tests in yellow. Tests which take more time will "
                         "be highlighted red. {units}".format(
                             units=_time_unit_help))

        parser.add_option("--timer-warning", action="store", default=3,
                          dest="timer_warning",
                          help=_warning_help)

        _verbose_help = ("Print execution time after each test.")

        parser.add_option("--timer-verbose", action="store_true",
                          dest="timer_verbose", help=_verbose_help)
