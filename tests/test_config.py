import io
import os
import unittest
import logging as log
from unittest.mock import patch

from parameterized import parameterized

from bin_strat.resources.config import load_property_configurations


class ConfigTest(unittest.TestCase):

    @patch('bin_strat.resources.config.exists')
    def test_missing_property_file(self, exists_mock):
        exists_mock.return_value = False
        self.assertRaises(FileNotFoundError, load_property_configurations)

    @parameterized.expand([
        ("No Local Property File, No Environment Interpolation",
         False,
         [io.StringIO('{properties: {run-interval: 2h, candlesticks: 80}}')],
         {'properties': {'run-interval': '2h', 'candlesticks': 80}}),

        ("Local Property File Overrides List, Replaces Strings, Replaces Integers",
         True,
         [io.StringIO('{xx: {yy: {zz: [xxx, yyy, zzz], ww: www, aa: 5}}}'),
          io.StringIO('{xx: {yy: {zz: [aaa, bbb, ccc], ww: abc, aa: 10}}}')],
         {
             'xx': {
                 'yy': {
                     'zz': ['aaa', 'bbb', 'ccc'],
                     'ww': 'abc',
                     'aa': 10
                 }
             }
         }),

        ("Local Property File Does Not Modify Original",
         True,
         [io.StringIO('{properties: {run-interval: 2h, candlesticks: 80}}'),
          io.StringIO('{properties: {}}')],
         {'properties': {'run-interval': '2h', 'candlesticks': 80}}),

        ("Local Property File Cannot Create New Properties",
         True,
         [io.StringIO('{properties: {run-interval: 2h, candlesticks: 80}}'),
          io.StringIO('{properties: {binance-api-key: X-MBX-APIKEY}}')],
         {'properties': {'run-interval': '2h', 'candlesticks': 80}})
    ])
    @patch('bin_strat.resources.config.open')
    @patch('bin_strat.resources.config.exists')
    def test_yaml_loading(self, name, exists_local, open_input, expected, exists_mock, open_mock):
        log.info("running test %s".format(name))

        exists_mock.side_effect = [True, exists_local]
        open_mock.side_effect = open_input

        self.assertEqual(expected, load_property_configurations())

    @parameterized.expand([
        ("Loads Integer and String Value from Environment - Local Overrides Main",
         {'INTERVAL': '2h', 'CANDLESTICKS': '80'},
         [io.StringIO('{properties: {run-interval: $INTERVAL, candlesticks: 200}}'),
          io.StringIO('{properties: {candlesticks: $CANDLESTICKS}}')],
         {'properties': {'run-interval': '2h', 'candlesticks': 80}}),

        ("Loads String and Integer Value from Environment - Local Overrides Main #2",
         {'INTERVAL': '2h', 'CANDLESTICKS': '80'},
         [io.StringIO('{properties: {run-interval: 5h, candlesticks: 200}}'),
          io.StringIO('{properties: {run-interval: $INTERVAL, candlesticks: $CANDLESTICKS}}')],
         {'properties': {'run-interval': '2h', 'candlesticks': 80}}),

        ("Loads Float and String Value from Environment - No Local Properties",
         {'INTERVAL': '2h', 'CANDLESTICKS': '80.2'},
         [io.StringIO('{properties: {run-interval: $INTERVAL, candlesticks: $CANDLESTICKS}}'),
          io.StringIO('{properties: {}}')],
         {'properties': {'run-interval': '2h', 'candlesticks': 80.2}}),
    ])
    @patch('bin_strat.resources.config.open')
    @patch('bin_strat.resources.config.exists')
    def test_environment_interpolation(self, name, env, open_input, expected, exists_mock, open_mock):
        log.info("running test %s".format(name))

        for e in env.keys():
            os.environ[e] = env[e]

        exists_mock.return_value = True
        open_mock.side_effect = open_input

        self.assertEqual(expected, load_property_configurations())
