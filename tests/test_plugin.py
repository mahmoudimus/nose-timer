import mock
import unittest

from nosetimer import plugin
from nose_parameterized import parameterized


class TestTimerPlugin(unittest.TestCase):

    def setUp(self):
        super(TestTimerPlugin, self).setUp()
        self.plugin = plugin.TimerPlugin()
        self.test_mock = mock.MagicMock(name='test')
        self.test_mock.id.return_value = 1
        self.opts_mock = mock.MagicMock(name='opts')

    def test_options(self):
        parser = mock.MagicMock()
        self.plugin.options(parser)
        self.assertEquals(parser.add_option.call_count, 4)

    def test_configure(self):
        attributes = ('config', 'timer_top_n', '_timed_tests')
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
