from bin_strat.indicators import TradingSignal
import pandas as pd
import logging as log
import binance_client
from binance.client import Client
import datetime as dt
import indicators


# Moved client definition to another module (so we can reuse it in bin_data.py)
client = binance_client.get_binance_client()


def _map_klines_to_dataframe(klines):
	"""
	Price information comes back as a list of raw values, which is not intuitive.
	This function converts those values to a readable dataframe, with column titles for easy access.
	Args:
		klines (list): 2d matrix containing Kline/Candlestick price information.
	Returns:
		pd.DataFrame: A dataframe containing price information, with appropriate column titles.
	"""
	converted_klines = []
	for k in klines:
		converted_klines.append({
			"Time": k[0],
			"Open": k[1],
			"High": k[2],
			"Low": k[3],
			"Close": k[4],
			"Volume": k[5],
			"Close Time": k[6],
			"Quote Asset Volume": k[7],
			"Number of Trades": k[8],
			"Taker Buy Base Asset Volume": k[9],
			"Taker Buy Quote Asset Volume": k[10]
		})
	df = pd.DataFrame(converted_klines)
	df.Time = pd.to_datetime(df.Time, unit='ms')
	df.Time = df.Time.dt.tz_localize('UTC') #To recognize timezones
	df.Time = df.Time.dt.tz_convert('US/Eastern') #To set the timezone
	df = df[["Time","Close","Volume"]]
	df.Close = df.Close.astype(float)

	return df


def _calculate_order_qty(klines):
	"""
	Determines how many shares should be purchased given a price history.
	Args:
		klines (pd.DataFrame): the 60 minute price history for a given ticker.
	Returns:
		int: the amount of shares that should be purchased, 0 if none.
	"""
	pass


def _place_limit_sell(order):
	"""
	Given an order, place a OCO sell order good until cancelled.
	Args:
		order (dict): The binance api order response
	"""
	pass


def _handle_order_cancellation(order):
	"""
	Sends an order cancellation request if the order should be cancelled.
	Args:
		order (dict): The binance api order response
	"""
	pass

def _place_limit_buy(symbol, price_history):
	"""
	Function to generate a limit buy.
	Args:
		symbol (str): the ticker to place a buy limit for
		price_history (pandas.DataFrame): frame containing historical prices
	"""
	if price_history.empty:
		return

	order_quantity = _calculate_order_qty(price_history)

	share_price = price_history['Close'].iloc[-1] # last closing price?

	if order_quantity > 0:
		# TODO place a limit buy here!
		log.info('placed a buy request for %d shares of %s at $%.2d', order_quantity, symbol, share_price)


def trading_strategy(symbol, interval, limit):
	"""
	Main trading strategy to execute!
	Args:
		symbol (str): the coin ticker to act on
		interval (int): the time interval between historic data points. (ex: 1m, 2h, 3d)
		limit (int): the amount of historic price points to retrieve.
	"""
	last_known_order = next(client.get_all_orders(symbol, limit=1), None)

	price_history = _map_klines_to_dataframe(
		client.get_klines(symbol=symbol, interval=interval, limit=limit)
	)

	indicator = indicators.macd_signal(price_history)

	if last_known_order is None:
		pass

	status = last_known_order['status']
	if status == Client.ORDER_STATUS_FILLED:
		_handle_completed_order()
	elif status in [Client.ORDER_STATUS_NEW, Client.ORDER_STATUS_PARTIALLY_FILLED]:
		_handle_open_order(last_known_order, indicator, )
	elif status in [Client.ORDER_STATUS_CANCELED, Client.ORDER_STATUS_EXPIRED, Client.ORDER_STATUS_REJECTED]:
		_handle_rejected_order()


def _handle_completed_order(order, indicator):
	last_indicator = TradingSignal.BUY if order['side'] == Client.SIDE_BUY else TradingSignal.SELL
	if last_indicator == indicator:
		pass # send an error here

	if order['side'] == Client.SIDE_SELL and indicator == TradingSignal.BUY:
		_place_limit_buy()
	elif order['side'] == Client.SIDE_BUY and indicator == TradingSignal.SELL:
		_place_limit_sell()


def _handle_rejected_order():
	pass


def _handle_open_order(order, indicator):
	last_indicator = TradingSignal.BUY if order['side'] == Client.SIDE_BUY else TradingSignal.SELL
	if last_indicator == indicator:
		pass # send an error here

	if indicator == TradingSignal.BUY and order['side'] == Client.SIDE_SELL:
		_handle_order_cancellation()
