import pandas as pd
import config
import binance_client
from binance.client import Client


USD_amount = config.USD_amount
crypto_ticker = config.crypto_ticker

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


def _calculate_buy_price(klines):
	"""
	Determines what price shares should be purchased at, given a history.
	Comment for brynne: Is this just the last known price?
	Args:
		klines (pd.DataFrame): the 60 minute price history for a given ticker.
	Returns:
		float: the price to purchase the shares at.
	"""
	pass


def _place_limit_buy(symbol, qty, price):
	"""
	Function to generate a limit buy.
	Args:
		symbol (str): the ticker to place a buy limit for
		qty (int): the amount of shares to purchase
		price (float): the price to purchase the shares for
	"""
	order = client.order_limit_buy(
		symbol = symbol,
		quantity = qty,
		price = price
	)


def _place_oco_sell(order):
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


def strategy(symbol, interval, limit):
	"""
	Main trading strategy to execute!
	Args:
		symbol (str): the coin ticker to act on
		interval (int): the time interval between historic data points. (ex: 1m, 2h, 3d)
		limit (int): the amount of historic price points to retrieve.
	"""
	#1. Query Binance API, get trading data for last 60 minutes.
	price_history = client.get_klines(symbol=symbol, interval=interval, limit=limit)
	
	price_history_df = _map_klines_to_dataframe(price_history)

	#2. Query Binance API, get the last known trade for ticker.
	orders: list = client.get_all_orders(symbol, limit=1)

	last_known_order = next(orders, None)
	#4. If the last known trade was a LIMIT buy, we check the order status.
	if last_known_order is not None and last_known_order['side'] == Client.SIDE_BUY:
		status = last_known_order['status']
		#5 If the order is FILLED, that means we have not opened sell positions yet. We should do this immediately.
		if status == Client.ORDER_STATUS_FILLED:
			return _place_oco_sell(last_known_order)
		#5a. Alternatively, we can cancel the order if it was placed longer than n minutes ago.
		elif status == Client.ORDER_STATUS_NEW:
			return _handle_order_cancellation(last_known_order)

	#5. Last order must have been a SELL, cancelled BUY, or never existed, so assess an entrypoint to buy back in.
	shares_to_buy = _calculate_order_qty(price_history_df)
	if shares_to_buy > 0:
		_place_limit_buy(symbol, shares_to_buy, _calculate_buy_price(price_history_df))
