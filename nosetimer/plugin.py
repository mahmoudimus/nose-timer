import json
import logging
import os
import re
import termcolor
import timeit

from nose.plugins import Plugin

try:
    import Queue
except ImportError:
    import queue as Queue

from collections import OrderedDict


# define constants
IS_NT = os.name == 'nt'

# Windows and Python 2.7 multiprocessing don't marry well.
_results_queue = None
if not IS_NT:
    import multiprocessing
    from multiprocessing import queues

    class TimerQueue(queues.Queue):
        """A portable implementation of multiprocessing.Queue.

        Because of multithreading / multiprocessing semantics, Queue.qsize()
        may raise the NotImplementedError exception on Unix platforms like
        Mac OS X where sem_getvalue() is not implemented. This subclass
        addresses this problem by using a synchronized shared counter
        (initialized to zero) and increasing / decreasing its value every time
        the put() and get() methods are called, respectively. This not only
        prevents NotImplementedError from being raised, but also allows us to
        implement a reliable version of both qsize() and empty().
        """

        def __init__(self, *args, **kwargs):
            if hasattr(multiprocessing, 'get_context'):
                kwargs.update(ctx=multiprocessing.get_context())
            super(TimerQueue, self).__init__(*args, **kwargs)
            self.size = multiprocessing.Value('i', 0)

        def put(self, *args, **kwargs):
            with self.size.get_lock():
                self.size.value += 1
            super(TimerQueue, self).put(*args, **kwargs)

        def get(self, *args, **kwargs):
            with self.size.get_lock():
                self.size.value -= 1
            return super(TimerQueue, self).get(*args, **kwargs)

        def qsize(self):
            """Reliable implementation of multiprocessing.Queue.qsize()."""
            return self.size.value

        def empty(self):
            """Reliable implementation of multiprocessing.Queue.empty()."""
            return not self.qsize()

    _results_queue = TimerQueue()


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
            self.json_file = options.json_file

            # Windows + nosetests does not support colors (even with colorama).
            if not IS_NT:
                self.timer_no_color = options.timer_no_color

            # determine if multiprocessing plugin enabled
            self.multiprocessing_enabled = \
                bool(getattr(options, 'multiprocess_workers', False))

    def startTest(self, test):
        """Initializes a timer before starting a test."""
        self._timer = timeit.default_timer()

    def report(self, stream):
        """Report the test times."""
        if not self.enabled:
            return

        # if multiprocessing plugin enabled - get items from results queue
        if self.multiprocessing_enabled:
            for i in range(_results_queue.qsize()):
                try:
                    k, v, s = _results_queue.get(False)
                    self._timed_tests[k] = {'time': v,
                                            'status': s}
                except Queue.Empty:
                    pass

        d = sorted(self._timed_tests.items(),
                   key=lambda item: item[1]['time'],
                   reverse=True)

        if self.json_file:
            dict_type = OrderedDict if self.timer_top_n else dict
            with open(self.json_file, 'w') as f:
                json.dump({'tests': dict_type((k, v) for k, v in d)}, f)

        total_time = sum([vv['time'] for kk, vv in d])

        for i, (test, time_and_status) in enumerate(d):
            time_taken = time_and_status['time']
            status = time_and_status['status']
            if i < self.timer_top_n or self.timer_top_n == -1:
                color = self._get_result_color(time_taken)
                percent = 0 if total_time == 0 else time_taken/total_time*100
                line = self._format_report_line(test,
                                                time_taken,
                                                color,
                                                status,
                                                percent)
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

    def _format_report_line(self, test, time_taken, color, status, percent):
        """Format a single report line."""
        return "[{0}] {3:04.2f}% {1}: {2}".format(
                                      status, test,
                                      self._colored_time(time_taken, color),
                                      percent)

    def _register_time(self, test, status=None):
        if self.multiprocessing_enabled:
            _results_queue.put((test.id(), self._time_taken(), None))

        self._timed_tests[test.id()] = {
                                        'time': self._time_taken(),
                                        'status': status
                                       }

    def addError(self, test, err, capt=None):
        """Called when a test raises an uncaught exception."""
        self._register_time(test, 'error')

    def addFailure(self, test, err, capt=None, tb_info=None):
        """Called when a test fails."""
        self._register_time(test, 'fail')

    def addSuccess(self, test, capt=None):
        """Called when a test passes."""
        self._register_time(test, 'success')

    def prepareTestResult(self, result):
        """Called before the first test is run."""
        def _add_success(result, test):
            """Called when a test passes."""
            if result.showAll:
                output = 'ok'
                time_taken = self._timed_tests.get(test.id())['time']
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

        _help = ("Save the results of the timing and status of each"
                 "tests in said Json file")

        parser.add_option("--timer-json-file", action="store",
                          default=None,
                          dest="json_file",
                          help=_help)

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
        if not IS_NT:
            parser.add_option("--timer-no-color", action="store_true",
                              default=False, dest="timer_no_color",
                              help=_no_color_help)

        # timer filter
        _filter_help = "Show filtered results only (ok,warning,error)"
        parser.add_option("--timer-filter", action="store", default=None,
                          dest="timer_filter", help=_filter_help)
