import mock
import unittest

from nosetimer import plugin
from nose_parameterized import parameterized


class TestTimerPlugin(unittest.TestCase):

    def setUp(self):
        super(TestTimerPlugin, self).setUp()
        self.plugin = plugin.TimerPlugin()
        self.plugin.enabled = True
        self.plugin.timer_ok = 1000
        self.plugin.timer_warning = 2000
        self.plugin.timer_no_color = False
        self.test_mock = mock.MagicMock(name='test')
        self.test_mock.id.return_value = 1
        self.opts_mock = mock.MagicMock(name='opts')

    def test_options(self):
        parser = mock.MagicMock()
        self.plugin.options(parser)
        self.assertEquals(parser.add_option.call_count, 7)

    def test_configure(self):
        attributes = ('config', 'timer_top_n')
        for attr in attributes:
            self.assertFalse(hasattr(self.plugin, attr))

        self.plugin.configure(self.opts_mock, None)
        for attr in attributes:
            self.assertTrue(hasattr(self.plugin, attr))

    def test_time_taken(self):
        self.assertFalse(hasattr(self.plugin, '_timer'))
        self.assertEquals(self.plugin._time_taken(), 0.0)

        self.plugin.startTest(self.test_mock)
        self.assertTrue(hasattr(self.plugin, '_timer'))
        self.assertNotEquals(self.plugin._time_taken(), 0.0)

    @parameterized.expand([
        ('1', 1000),  # seconds by default
        ('2s', 2000),  # seconds
        ('500ms', 500),  # milliseconds
    ])
    def test_parse_time(self, value, expected_ms):
        self.assertEqual(self.plugin._parse_time(value), expected_ms)

    def test_parse_time_error(self):
        self.assertRaises(ValueError, self.plugin._parse_time, '5seconds')

    @parameterized.expand([
        'timer_ok',
        'timer_warning',
    ])
    def test_parse_time_called(self, option):
        time = '100ms'
        with mock.patch.object(self.plugin, '_parse_time') as parse_time:
            parse_time.return_value = time
            mock_opts = mock.MagicMock(**{option: time})
            self.plugin.configure(mock_opts, None)
            self.assertEqual(getattr(mock_opts, option), time)
            parse_time.has_call(time)

    @parameterized.expand([
        (0.0001, '0.0001s', 'green'),
        (1,      '1.0000s', 'green'),
        (1.0001, '1.0001s', 'yellow'),
        (2.00,   '2.0000s', 'yellow'),
        (2.0001, '2.0001s', 'red'),
    ])
    @mock.patch("nosetimer.plugin.termcolor.colored")
    def test_colored_time(self, time_taken, expected, color, colored_mock):
        self.plugin._colored_time(time_taken, color)
        colored_mock.assert_called_once_with(expected, color)

    @mock.patch("nosetimer.plugin.termcolor.colored")
    def test_no_color_option(self, colored_mock):
        self.plugin.timer_no_color = True
        self.assertEqual(self.plugin._colored_time(1), "1.0000s")
        self.assertFalse(colored_mock.called)
