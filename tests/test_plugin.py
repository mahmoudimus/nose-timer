import mock
import unittest

from parameterized import parameterized

from nosetimer import plugin


class TestTimerPlugin(unittest.TestCase):

    def setUp(self):
        super(TestTimerPlugin, self).setUp()
        self.plugin = plugin.TimerPlugin()
        self.plugin.enabled = True
        self.plugin.timer_ok = 1000
        self.plugin.timer_warning = 2000
        self.plugin.timer_fail = None
        self.plugin.timer_no_color = False
        self.plugin.multiprocessing_enabled = False
        self.plugin._timed_tests = {}
        self.test_mock = mock.MagicMock(name='test')
        self.test_mock.id.return_value = 1
        self.opts_mock = mock.MagicMock(
            name='opts',
            json_file=None,
            timer_filter=None,
            timer_top_n=-1,
        )

    def test_report_enabled_false(self):
        stream_mock = mock.MagicMock(name='stream')
        self.plugin.enabled = False

        self.plugin.report(stream=stream_mock)

        stream_mock.writeln.assert_not_called()

    def test_report(self):
        stream_mock = mock.MagicMock(name='stream')
        self.plugin.configure(self.opts_mock, None)
        self.plugin._timed_tests = {
            'test_1': {'time': 0.1, 'status': 'error'},
            'test_2': {'time': 0.2, 'status': 'fail'},
            'test_3': {'time': 0.3, 'status': 'success'},
        }

        self.plugin.report(stream=stream_mock)

        stream_mock.writeln.assert_has_calls([
            mock.call('[success] 50.00% test_3: 0.3000s'),
            mock.call('[fail] 33.33% test_2: 0.2000s'),
            mock.call('[error] 16.67% test_1: 0.1000s'),
        ])

    def test_report_with_queue(self):
        stream_mock = mock.MagicMock(name='stream')
        self.opts_mock.multiprocess_workers = 4
        self.plugin.configure(self.opts_mock, None)
        for data in (('test_1', 0.1, 'error'),
                     ('test_2', 0.2, 'fail'),
                     ('test_3', 0.3, 'success')):
            plugin._results_queue.put(data)

        self.plugin.report(stream=stream_mock)

        stream_mock.writeln.assert_has_calls([
            mock.call('[success] 50.00% test_3: 0.3000s'),
            mock.call('[fail] 33.33% test_2: 0.2000s'),
            mock.call('[error] 16.67% test_1: 0.1000s'),
        ])

    def test_report_with_queue_empty(self):
        stream_mock = mock.MagicMock(name='stream')
        self.opts_mock.multiprocess_workers = 4
        self.plugin.configure(self.opts_mock, None)

        self.plugin.report(stream=stream_mock)

        stream_mock.writeln.assert_not_called()

    @parameterized.expand([
        (1.00, 'green'),
        (1.01, 'yellow'),
        (2.01, 'red'),
    ])
    def test_get_result_color(self, time_taken, color):
        self.assertEqual(self.plugin._get_result_color(time_taken=time_taken), color)

    @parameterized.expand([
        ('green', '\x1b[32m1.0000s\x1b[0m'),
        ('yellow', '\x1b[33m1.0000s\x1b[0m'),
        ('red', '\x1b[31m1.0000s\x1b[0m'),
    ])
    def test_format_report_line(self, color, expected):
        self.assertEqual(
            self.plugin._format_report_line(self.test_mock, 1, color, 'error', 0.1),
            "[error] 0.10%% %s: %s" % (self.test_mock, expected),
        )

    def test_add_error(self):
        self.plugin.addError(self.test_mock, None)

        self.assertEqual(
            self.plugin._timed_tests,
            {
                1: {
                    'status': 'error',
                    'time': 0.0,
                },
            },
        )

    def test_add_failure(self):
        self.plugin.addFailure(self.test_mock, None)

        self.assertEqual(
            self.plugin._timed_tests,
            {
                1: {
                    'status': 'fail',
                    'time': 0.0,
                },
            },
        )

    def test_add_success(self):
        self.plugin.multiprocessing_enabled = True
        self.plugin.addSuccess(self.test_mock, None)

        self.assertEqual(
            self.plugin._timed_tests,
            {
                1: {
                    'status': 'success',
                    'time': 0.0,
                },
            },
        )
        self.assertEqual(plugin._results_queue.get(), (1, 0.0, 'success'))

    def test_prepare_test_result_show_all(self):
        stream_mock = mock.MagicMock(name='stream')
        result_mock = mock.MagicMock(
            name='result',
            showAll=True,
            dots=False,
            stream=stream_mock,
        )
        self.plugin._timed_tests = {
            1: {'time': 0.3, 'status': 'success'},
        }

        self.plugin.prepareTestResult(result=result_mock)
        result_mock.addSuccess(test=self.test_mock)

        self.assertEqual(self.plugin._timed_tests, result_mock._timed_tests)
        stream_mock.assert_has_calls([
            mock.call.writeln('ok (\x1b[32m0.3000s\x1b[0m)'),
        ])

    def test_prepare_test_result_dots(self):
        stream_mock = mock.MagicMock(name='stream')
        result_mock = mock.MagicMock(
            name='result',
            showAll=False,
            dots=True,
            stream=stream_mock,
        )
        self.plugin._timed_tests = {
            'test': {'time': 0.3, 'status': 'success'},
        }

        self.plugin.prepareTestResult(result=result_mock)
        result_mock.addSuccess(test=self.test_mock)

        self.assertEqual(self.plugin._timed_tests, result_mock._timed_tests)
        stream_mock.assert_has_calls([
            mock.call.write('.'),
            mock.call.flush(),
        ])

    def test_options(self):
        parser = mock.MagicMock()
        self.plugin.options(parser)
        if not plugin.IS_NT:
            self.assertEqual(parser.add_option.call_count, 8)
        else:
            self.assertEqual(parser.add_option.call_count, 7)

    def test_configure(self):
        attributes = ('config', 'timer_top_n')
        for attr in attributes:
            self.assertFalse(hasattr(self.plugin, attr))

        self.plugin.configure(self.opts_mock, None)
        for attr in attributes:
            self.assertTrue(hasattr(self.plugin, attr))

    def test_time_taken(self):
        self.assertFalse(hasattr(self.plugin, '_timer'))
        self.assertEqual(self.plugin._time_taken(), 0.0)

        self.plugin.startTest(self.test_mock)
        self.assertTrue(hasattr(self.plugin, '_timer'))
        self.assertNotEqual(self.plugin._time_taken(), 0.0)

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
    @mock.patch("nosetimer.plugin._colorize")
    def test_colored_time(self, time_taken, expected, color, colored_mock):
        self.plugin._colored_time(time_taken, color)
        colored_mock.assert_called_once_with(expected, color)

    maxDiff = None

    @mock.patch.object(plugin, "colorama")
    @mock.patch.object(plugin, "termcolor", None)
    def test_colored_time_with_colorama(self, colorama_mock):
        plugin.TERMCOLOR2COLORAMA = {'green': colorama_mock.Fore.GREEN}

        res = self.plugin._colored_time(1.0, 'green')

        self.assertEqual(
            res,
            "{}1.0000s{}".format(colorama_mock.Fore.GREEN, colorama_mock.Style.RESET_ALL),
        )

    @mock.patch("nosetimer.plugin._colorize")
    def test_no_color_option(self, colored_mock):
        self.plugin.timer_no_color = True
        self.assertEqual(self.plugin._colored_time(1), "1.0000s")
        self.assertFalse(colored_mock.called)

    @parameterized.expand([
        ('warning', 0.5, False),
        ('warning', 1.5, True),
        ('error', 1.5, False),
        ('error', 2.5, True),
    ])
    def test_timer_fail_option_warning_pass(self, timer_fail_level, time_taken,
                                            fail_expected):
        self.plugin.timer_fail = timer_fail_level
        self.plugin.multiprocessing_enabled = False
        with mock.patch.object(self.plugin, '_time_taken') as _time_taken:
            _time_taken.return_value = time_taken
            self.plugin.startTest(self.test_mock)
            self.plugin.addSuccess(self.test_mock)
            self.assertEqual(self.test_mock.fail.called, fail_expected)
