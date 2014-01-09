import mock
import unittest

import nosetimer


class TestTimerPlugin(unittest.TestCase):
    def test_addOptions(self):
        plugin = nosetimer.TimerPlugin()
        parser = mock.MagicMock()
        plugin.addOptions(parser)
        self.assertEquals(parser.add_option.call_count, 5)

    def test_configure(self):
        attributes = ['config', 'timer_top_n', 'timer_ok',
                      'timer_warning', '_timed_tests']
        plugin = nosetimer.TimerPlugin()
        for attr in attributes:
            self.assertFalse(hasattr(plugin, attr))

        mock_opts = mock.MagicMock()
        plugin.configure(mock_opts, None)
        for attr in attributes:
            self.assertTrue(hasattr(plugin, attr))

    def test_timeTaken(self):
        plugin = nosetimer.TimerPlugin()
        self.assertFalse(hasattr(plugin, '_timer'))
        self.assertEquals(plugin._timeTaken(), 0.0)

        plugin.startTest(None)
        self.assertTrue(hasattr(plugin, '_timer'))
        self.assertNotEquals(plugin._timeTaken(), 0.0)

    def test_configure_accepts_a_float_for_timer_ok(self):
        plugin = nosetimer.TimerPlugin()
        mock_opts = mock.MagicMock(timer_ok='0.5')
        try:
            plugin.configure(mock_opts, None)
        except ValueError:
            self.fail("configure() raised ValueError unexpectedly!")

    def test_configure_accepts_a_float_for_timer_warning(self):
        plugin = nosetimer.TimerPlugin()
        mock_opts = mock.MagicMock(timer_warning='0.5')
        try:
            plugin.configure(mock_opts, None)
        except ValueError:
            self.fail("configure() raised ValueError unexpectedly!")
