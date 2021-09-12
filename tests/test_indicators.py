import unittest
import sys
sys.path.insert(0, '/Users/brynne/Python/Documents/GitHub/Crypto_Bin/bin_strat')
import indicators

import pandas as pd 
from pandas._testing import assert_frame_equal
import numpy as np




def test_macd_calc():
	"""
	This is to test that the output DataFrame from _MACD_calc function provides the expected calculation by comparing the output to a stand-alone .csv file 'price_history_macd_test.csv'
	inputs: price_history is a dummy .csv file with made up Time, Close, and Volume
	? Cannot import _macd_calc to test this??
	"""
	price_history = pd.read_csv('csv_test_files/price_history_test.csv')
	expected_results = pd.read_csv('csv_test_files/price_history_macd_test.csv')
	price_history_macd = _MACD_calc(price_history)
	macd_calc_test_result = assert_frame_equal(expected_results, price_history_macd)

	return macd_calc_test_result


class TestIndicator(unittest.TestCase):

	def test_macd_signal_HOLD(self):
		"""
		This function will test the retun of a 0 from macd_signal
		The input is the 'price_history_test.csv' which has an increasing price for the past 49 intervals so expected result is a HOLD (0) trading signal
		"""
		price_history = pd.read_csv('csv_test_files/price_history_test.csv')
		expected_result = 0 
		latest_signal = indicators.macd_signal(price_history)
		self.assertEqual(latest_signal, expected_result)

	def test_macd_signal_SELL(self):
		"""
		This function tests the return of a -1 or SELL from macd_signal
		Input is 'price_history_testSELL.csv' which has the latest price decreased significantly.
		"""
		price_history = pd.read_csv('csv_test_files/price_history_testSELL.csv')
		expected_result = -1
		latest_signal = indicators.macd_signal(price_history)
		self.assertEqual(latest_signal, expected_result)

	def test_macd_signal_BUY(self):
		"""
		This function will test the return of a 1 or BUY from macd_signal
		Input is 'price_history_testBUY.csv' which has the latest price increased.
		"""
		price_history = pd.read_csv('csv_test_files/price_history_testBUY.csv')
		expected_result = 1
		latest_signal = indicators.macd_signal(price_history)
		self.assertEqual(latest_signal, expected_result)

if __name__ == '__main__':
	unittest.main()