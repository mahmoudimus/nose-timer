import logging
import multiprocessing
import operator
import os
import re
import termcolor
import timeit

from nose.plugins import Plugin

log = logging.getLogger('nose.plugin.timer')


class TimerPlugin(Plugin):
    """This plugin provides test timings."""

    name = 'timer'
    score = 1

    time_format = re.compile(r'^(?P<time>\d+)(?P<units>s|ms)?$')

    def __init__(self):
        super(TimerPlugin, self).__init__()
        self._timed_tests = multiprocessing.Manager().dict()

    def _time_taken(self):
        if hasattr(self, '_timer'):
            taken = timeit.default_timer() - self._timer
        else:
            # Test died before it ran (probably error in setup()) or
            # success/failure added before test started probably due to custom
            # `TestResult` munging.
            taken = 0.0
        return taken

    def _parse_time(self, value):
        """Parse string time representation to get number of milliseconds.
        Raises the ``ValueError`` for invalid format.
        """
        try:
            # Default time unit is a second, we should convert it to
            # milliseconds.
            return int(value) * 1000
        except ValueError:
            # Try to parse if we are unlucky to cast value into int.
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
        if self.enabled:
            self.timer_top_n = int(options.timer_top_n)
            self.timer_ok = self._parse_time(options.timer_ok)
            self.timer_warning = self._parse_time(options.timer_warning)
            self.timer_no_color = options.timer_no_color

    def startTest(self, test):
        """Initializes a timer before starting a test."""
        self._timer = timeit.default_timer()

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

    def _colored_time(self, time_taken):
        """Get formatted and colored string for a given time taken."""
        if self.timer_no_color:
            return "{0:0.4f}s".format(time_taken)
        time_taken_ms = time_taken * 1000
        if time_taken_ms <= self.timer_ok:
            color = 'green'
        elif time_taken_ms <= self.timer_warning:
            color = 'yellow'
        else:
            color = 'red'
        return termcolor.colored("{0:0.4f}s".format(time_taken), color)

    def _format_report(self, test, time_taken):
        """Format a single report line."""
        return "{0}: {1}".format(test, self._colored_time(time_taken))

    def _register_time(self, test):
        self._timed_tests[test.id()] = self._time_taken()

    def addError(self, test, err, capt=None):
        """Called when a test raises an uncaught exception."""
        self._register_time(test)

    def addFailure(self, test, err, capt=None, tb_info=None):
        """Called when a test fails."""
        self._register_time(test)

    def addSuccess(self, test, capt=None):
        """Called when a test passes."""
        self._register_time(test)

    def prepareTestResult(self, result):
        """Called before the first test is run."""
        def _add_success(result, test):
            """Called when a test passes."""
            if result.showAll:
                output = 'ok'
                time_taken = self._timed_tests.get(test.id())
                if time_taken is not None:
                    output += ' ({0})'.format(self._colored_time(time_taken))
                result.stream.writeln(output)
            elif result.dots:
                result.stream.write('.')
                result.stream.flush()

        # monkeypatch the result
        result.addSuccess = lambda test: _add_success(result, test)
        result._timed_tests = self._timed_tests

    def options(self, parser, env=os.environ):
        """Register commandline options."""
        super(TimerPlugin, self).options(parser, env)

        _help = ("When the timer plugin is enabled, only show the N tests "
                 "that consume more time. The default, -1, shows all tests.")

        parser.add_option("--timer-top-n", action="store", default="-1",
                          dest="timer_top_n", help=_help)

        _time_units_help = ("Default time unit is a second, but you can set "
                            "it explicitly (e.g. 1s, 500ms).")

        _ok_help = ("Normal execution time. Such tests will be highlighted in "
                    "green. {units_help}".format(units_help=_time_units_help))

        parser.add_option("--timer-ok", action="store", default=1,
                          dest="timer_ok",
                          help=_ok_help)

        _warning_help = ("Warning about execution time to highlight slow "
                         "tests in yellow. Tests which take more time will "
                         "be highlighted in red. {units_help}".format(
                             units_help=_time_units_help))

        parser.add_option("--timer-warning", action="store", default=3,
                          dest="timer_warning",
                          help=_warning_help)

        _no_color_help = "Don't colorize output (useful for non-tty output)."

        parser.add_option("--timer-no-color", action="store_true",
                          default=False, dest="timer_no_color",
                          help=_no_color_help)
