import mock
import unittest

import nosetimer
from nose_parameterized import parameterized


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

    @parameterized.expand([
        ('1', 1000),  # seconds by default
        ('2s', 2000),  # seconds
        ('500ms', 500),  # miliseconds
    ])
    def test_parse_time(self, value, expected_ms):
        plugin = nosetimer.TimerPlugin()
        self.assertEqual(plugin._parse_time(value), expected_ms)

    def test_parse_time_error(self):
        plugin = nosetimer.TimerPlugin()
        self.assertRaises(ValueError, plugin._parse_time, '5seconds')

    @parameterized.expand([
        'timer_ok',
        'timer_warning',
    ])
    def test_parse_time_called(self, option):
        plugin = nosetimer.TimerPlugin()
        time = '100ms'
        with mock.patch.object(plugin, '_parse_time') as parse:
            parse.return_value = time
            mock_opts = mock.MagicMock(**{option: time})
            plugin.configure(mock_opts, None)
            self.assertEqual(getattr(plugin, option), time)
            parse.assert_any_call(time)
