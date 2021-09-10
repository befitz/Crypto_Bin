import pandas as pd
import logging as log
import binance_client
from binance.client import Client


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

def _attempt_limit_buy(symbol, price_history):
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


def strategy(symbol, interval, limit):
	"""
	Main trading strategy to execute!
	Args:
		symbol (str): the coin ticker to act on
		interval (int): the time interval between historic data points. (ex: 1m, 2h, 3d)
		limit (int): the amount of historic price points to retrieve.
	"""
	# query Binance API, get trading data for last limit hours.
	price_history = client.get_klines(symbol=symbol, interval=interval, limit=limit)
	
	price_history_df = _map_klines_to_dataframe(price_history)

	# query Binance API, get the last known trade for ticker.
	last_known_order = next(client.get_all_orders(symbol, limit=1), None)

	# if no orders exist for this ticker, we should place a buy order.
	if not last_known_order:
		_attempt_limit_buy(symbol, price_history_df)
		return

	if last_known_order['side'] == Client.SIDE_BUY:
		# if the order is FILLED, that means we have not opened sell positions yet.
		if last_known_order['status'] == Client.STATUS_FILLED:
			_place_limit_sell(last_known_order)
			return
		# alternatively, we can cancel the order if it was placed longer than n minutes ago.
		if last_known_order['status'] == Client.STATUS_NEW:
			_handle_order_cancellation(last_known_order)
			return

	# last order must have been a SELL or cancelled BUY so assess an entrypoint to buy back in.
	_attempt_limit_buy(symbol, price_history_df)
