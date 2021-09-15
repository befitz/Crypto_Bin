import unittest
import sys

from bin_strat.indicators import macd_signal

import pandas as pd 
import numpy as np

class TestIndicator(unittest.TestCase):

	def test_macd_signal_HOLD(self):
		"""
		This function will test the retun of a 0 from macd_signal
		The input is the 'price_history_test.csv' which has an increasing price for the past 49 intervals so expected result is a HOLD (0) trading signal
		"""
		price_history = pd.read_csv('tests/csv_test_files/price_history_test.csv')
		expected_result = 0 
		latest_signal = macd_signal(price_history)
		self.assertEqual(latest_signal, expected_result)

	def test_macd_signal_SELL(self):
		"""
		This function tests the return of a -1 or SELL from macd_signal
		Input is 'price_history_testSELL.csv' which has the latest price decreased significantly.
		"""
		price_history = pd.read_csv('tests/csv_test_files/price_history_testSELL.csv')
		expected_result = -1
		latest_signal = macd_signal(price_history)
		self.assertEqual(latest_signal, expected_result)

	def test_macd_signal_BUY(self):
		"""
		This function will test the return of a 1 or BUY from macd_signal
		Input is 'price_history_testBUY.csv' which has the latest price increased.
		"""
		price_history = pd.read_csv('tests/csv_test_files/price_history_testBUY.csv')
		expected_result = 1
		latest_signal = macd_signal(price_history)
		self.assertEqual(latest_signal, expected_result)

if __name__ == '__main__':
	unittest.main()