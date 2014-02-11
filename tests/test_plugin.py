import mock
import unittest

import nosetimer


class TestTimerPlugin(unittest.TestCase):

    def setUp(self):
        super(TestTimerPlugin, self).setUp()
        self.plugin = nosetimer.TimerPlugin()
        self.test_mock = mock.MagicMock(name='test')
        self.test_mock.id.return_value = 1
        self.opts_mock = mock.MagicMock(name='opts')

    def test_addOptions(self):
        parser = mock.MagicMock()
        self.plugin.addOptions(parser)
        self.assertEquals(parser.add_option.call_count, 5)

    def test_configure(self):
        attributes = ('config', 'timer_top_n', 'timer_ok',
                      'timer_warning', '_timed_tests')
        for attr in attributes:
            self.assertFalse(hasattr(self.plugin, attr))

        self.plugin.configure(self.opts_mock, None)
        for attr in attributes:
            self.assertTrue(hasattr(self.plugin, attr))

    def test_timeTaken(self):
        self.assertFalse(hasattr(self.plugin, '_timer'))
        self.assertEquals(self.plugin._timeTaken(), 0.0)

        self.plugin.startTest(self.test_mock)
        self.assertTrue(hasattr(self.plugin, '_timer'))
        self.assertNotEquals(self.plugin._timeTaken(), 0.0)

    def test_afterTest(self):
        self.opts_mock.timer_verbose.return_value = True
        self.plugin.configure(self.opts_mock, None)
        # make sure there is no exception if test time result was not found
        self.plugin.afterTest(self.test_mock)
