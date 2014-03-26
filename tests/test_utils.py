import mock
import unittest

from nosetimer import utils
from nose_parameterized import parameterized


class TestUtils(unittest.TestCase):

    @parameterized.expand([
        (0.0001, '0.0001s', 'green'),
        (1,      '1.0000s', 'green'),
        (1.0001, '1.0001s', 'yellow'),
        (2.00,   '2.0000s', 'yellow'),
        (2.0001, '2.0001s', 'red'),
    ])
    @mock.patch("nosetimer.utils.termcolor.colored")
    def test_colored_time(self, time_taken, expected, color, colored_mock):
        opts_mock = mock.MagicMock(**{
            'timer_ok': 1000,
            'timer_warning': 2000
        })
        utils.colored_time(time_taken, opts_mock)
        colored_mock.assert_called_once_with(expected, color)
