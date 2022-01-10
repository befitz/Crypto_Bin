import unittest
import pandas as pd
from parameterized import parameterized
import logging as log
from bin_strat.indicators import macd_signal, TradingSignal


class TestIndicator(unittest.TestCase):

	@parameterized.expand([
		('test the return of 0 (HOLD)', 'tests/csv_test_files/price_history_test.csv', TradingSignal.HOLD),
		('test the return of 1 (BUY)', 'tests/csv_test_files/price_history_testBUY.csv', TradingSignal.BUY),
		('test the return of -1 (SELL)', 'tests/csv_test_files/price_history_testSELL.csv', TradingSignal.SELL)
	])
	def test_macd_signal(self, name, csv, expected_signal):
		log.info('running test case %s'.format(name))
		price_history = pd.read_csv(csv)
		self.assertEqual(expected_signal, macd_signal(price_history))
