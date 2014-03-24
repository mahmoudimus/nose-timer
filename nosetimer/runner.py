from nose import core
from nosetimer import utils


class TimerTestResult(core.TextTestResult):
    """Timer test result."""

    def __init__(self, timed_tests, **kwargs):
        super(TimerTestResult, self).__init__(**kwargs)
        self._timed_tests = timed_tests

    def addSuccess(self, test):
        """Called when a test passes."""
        if self.showAll:
            result = 'ok'
            time_taken = self._timed_tests.get(test.id())
            if time_taken is not None:
                result += ' ({0})'.format(
                    utils.colored_time(time_taken, self.config.options))
            self.stream.writeln(result)
        elif self.dots:
            self.stream.write('.')
            self.stream.flush()


class TimerTestRunner(core.TextTestRunner):
    """Timer test runner."""

    def __init__(self, timed_tests, **kwargs):
        super(TimerTestRunner, self).__init__(**kwargs)
        self._timed_tests = timed_tests

    def _makeResult(self):
        return TimerTestResult(timed_tests=self._timed_tests,
                               stream=self.stream,
                               descriptions=self.descriptions,
                               verbosity=self.verbosity,
                               config=self.config)
