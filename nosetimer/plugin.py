import logging
import operator
import os
import re
import termcolor
import timeit

# Windows and Python 2.7 multiprocessing don't marry well.
_results_queue = None
if os.name != 'nt':
    import multiprocessing
    try:
        import Queue
    except ImportError:
        import queue as Queue
    _results_queue = multiprocessing.Queue()

from nose.plugins import Plugin

log = logging.getLogger('nose.plugin.timer')


class TimerPlugin(Plugin):
    """This plugin provides test timings."""

    name = 'timer'
    score = 1

    time_format = re.compile(r'^(?P<time>\d+)(?P<units>s|ms)?$')
    _timed_tests = {}

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

    @staticmethod
    def _parse_filter(value):
        """Parse timer filters."""
        return value.split(',') if value is not None else None

    @staticmethod
    def _parse_inline_only(inline_only, verbosity):
        """Parse and validate inline-only option."""
        inline_only = bool(inline_only)
        if inline_only and (not verbosity or verbosity < 2):
            raise ValueError('inline-only option requires nose verbosity >= 2')
        return inline_only

    def configure(self, options, config):
        """Configures the test timer plugin."""
        super(TimerPlugin, self).configure(options, config)
        self.config = config
        if self.enabled:
            self.timer_top_n = int(options.timer_top_n)
            self.timer_ok = self._parse_time(options.timer_ok)
            self.timer_warning = self._parse_time(options.timer_warning)
            self.timer_filter = self._parse_filter(options.timer_filter)
            self.timer_no_color = True
            self.verbosity = int(options.verbosity)
            self.inline_only = self._parse_inline_only(
                options.inline_only, self.verbosity)

            # Windows + nosetests does not support colors (even with colorama).
            if os.name != 'nt':
                self.timer_no_color = options.timer_no_color

            # determine if multiprocessing plugin enabled
            self.multiprocessing_enabled = \
                bool(getattr(options, 'multiprocess_workers', False))

    def startTest(self, test):
        """Initializes a timer before starting a test."""
        self._timer = timeit.default_timer()

    def report(self, stream):
        """Report the test times."""
        if not self.enabled or self.inline_only:
            return

        # if multiprocessing plugin enabled - get items from results queue
        if self.multiprocessing_enabled:
            for i in range(_results_queue.qsize()):
                try:
                    k, v = _results_queue.get_nowait()
                    self._timed_tests[k] = v
                except Queue.Empty:
                    pass

        d = sorted(self._timed_tests.items(),
                   key=operator.itemgetter(1),
                   reverse=True)

        for i, (test, time_taken) in enumerate(d):
            if i < self.timer_top_n or self.timer_top_n == -1:
                color = self._get_result_color(time_taken)
                line = self._format_report_line(test, time_taken, color)
                _filter = self._color_to_filter(color)
                if (self.timer_filter is None or _filter is None or
                        _filter in self.timer_filter):
                    stream.writeln(line)

    def _color_to_filter(self, color):
        """Get filter name by a given color."""
        return {
            'green': 'ok',
            'yellow': 'warning',
            'red': 'error',
        }.get(color)

    def _get_result_color(self, time_taken):
        """Get time taken result color."""
        time_taken_ms = time_taken * 1000
        if time_taken_ms <= self.timer_ok:
            color = 'green'
        elif time_taken_ms <= self.timer_warning:
            color = 'yellow'
        else:
            color = 'red'

        return color

    def _colored_time(self, time_taken, color=None):
        """Get formatted and colored string for a given time taken."""
        if self.timer_no_color:
            return "{0:0.4f}s".format(time_taken)
        return termcolor.colored("{0:0.4f}s".format(time_taken), color)

    def _format_report_line(self, test, time_taken, color):
        """Format a single report line."""
        return "{0}: {1}".format(test, self._colored_time(time_taken, color))

    def _register_time(self, test):
        if self.multiprocessing_enabled:
            _results_queue.put((test.id(), self._time_taken()))
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
                    color = self._get_result_color(time_taken)
                    output += ' ({0})'.format(self._colored_time(time_taken,
                                                                 color))
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

        # timer top n
        _help = ("When the timer plugin is enabled, only show the N tests "
                 "that consume more time. The default, -1, shows all tests.")
        parser.add_option("--timer-top-n", action="store", default="-1",
                          dest="timer_top_n", help=_help)

        _time_units_help = ("Default time unit is a second, but you can set "
                            "it explicitly (e.g. 1s, 500ms).")

        # timer ok
        _ok_help = ("Normal execution time. Such tests will be highlighted in "
                    "green. {units_help}".format(units_help=_time_units_help))
        parser.add_option("--timer-ok", action="store", default=1,
                          dest="timer_ok", help=_ok_help)

        # time warning
        _warning_help = ("Warning about execution time to highlight slow "
                         "tests in yellow. Tests which take more time will "
                         "be highlighted in red. {units_help}".format(
                             units_help=_time_units_help))
        parser.add_option("--timer-warning", action="store", default=3,
                          dest="timer_warning", help=_warning_help)

        # timer no color
        _no_color_help = "Don't colorize output (useful for non-tty output)."

        # Windows + nosetests does not support colors (even with colorama).
        if os.name != 'nt':
            parser.add_option("--timer-no-color", action="store_true",
                              default=False, dest="timer_no_color",
                              help=_no_color_help)

        # timer filter
        _filter_help = "Show filtered results only (ok,warning,error)"
        parser.add_option("--timer-filter", action="store", default=None,
                          dest="timer_filter", help=_filter_help)

        # inline only
        _inline_only_help = ("Suppress separate test timing lines, instead "
                             " only appending times to nose's own test output "
                             " lines. Requires --verbosity >= 2")
        parser.add_option("--inline-only", action="store_true", default=False,
                          dest="inline_only", help=_inline_only_help)
