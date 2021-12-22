from bin_strat.indicators import TradingSignal
import bin_strat.resources.config as config
import pandas as pd
import logging as log
import binance_client
from binance.client import Client
import datetime as dt
import indicators
from decimal import Decimal


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
	df = df[["Time", "Close", "Volume"]]
	df.Close = df.Close.astype(float)

	return df


def _calculate_share_price(klines):
	if not klines:
		raise ValueError('cannot calculate share price without price history, got: %s' % str(klines))
	return klines['Close'][-1]


def _calculate_order_qty(symbol, share_price):
	"""
	Determines how many shares should be purchased given a price history.
	Args:
		klines (pd.DataFrame): the 60 minute price history for a given ticker.
	Returns:
		int: the amount of shares that should be purchased, 0 if none.
	"""
	cfg = config.properties['tickers'][symbol]
	return round(Decimal(cfg['limit']) / Decimal(share_price), cfg['precision'])


def _place_limit_sell(symbol, price_history):
	"""
	Given an order, place a OCO sell order good until cancelled.
	Args:
		order (dict): The binance api order response
	"""
	if price_history.empty:
		log.warn('no price history found for ticker %s: cannot place limit sell'.format(symbol))
		return

	order_quantity = client.get_asset_balance(symbol)['free'] # assets could be locked here?

	share_price = _calculate_share_price(price_history)

	if order_quantity > 0:
		# TODO decide if limit sell or stop loss limit?
		order = client.order_limit_sell(symbol = symbol, quantity = order_quantity, price = share_price)
		log.info('placed a limit sell request for %d shares of %s at $%.2d'.format(order_quantity, symbol, share_price))
		log.info(str(order))


def _handle_order_cancellation(order):
	"""
	Sends an order cancellation request if the order should be cancelled.
	Args:
		order (dict): The binance api order response
	"""
	log.info('attempting to cancel order %d, which has a status of %s'.format(order['orderId'], order['status']))
	result = client.cancel_order(symbol = order['symbol'], orderId = order['orderId'])
	log.info('cancellation result: %s'.format(str(result)))

 
def _place_limit_buy(symbol, price_history):
	"""
	Function to generate a limit buy.
	Args:
		symbol (str): the ticker to place a buy limit for
		price_history (pandas.DataFrame): frame containing historical prices
	"""
	if price_history.empty:
		log.warn('no price history found for ticker %s: cannot place limit buy'.format(symbol))
		return

	order_quantity = _calculate_order_qty(price_history)

	share_price = price_history['Close'].iloc[-1] # last closing price

	if order_quantity > 0:
		order = client.order_limit_buy(symbol = symbol, quantity = order_quantity, price = share_price)
		log.info('placed a buy request for %d shares of %s at $%.2d'.format(order_quantity, symbol, share_price))
		log.info(str(order))


def trading_strategy(symbol, interval, limit):
	"""
	Main trading strategy to execute!
	Args:
		symbol (str): the coin ticker to act on.

		interval (str): the time interval between historic data points. (ex: 1m, 2h, 3d)

		limit (int): the amount of historic price points to retrieve.
	"""
	last_known_order = next(client.get_all_orders(symbol, limit=1), None)

	price_history = _map_klines_to_dataframe(
		client.get_klines(symbol=symbol, interval=interval, limit=limit)
	)

	indicator = indicators.macd_signal(price_history)

	if last_known_order is None:
		_handle_first_order(symbol, price_history, indicator)
		return

	status = last_known_order['status']
	if status in [Client.ORDER_STATUS_FILLED]:
		_handle_completed_order(last_known_order, price_history, indicator)
	elif status in [Client.ORDER_STATUS_NEW, Client.ORDER_STATUS_PARTIALLY_FILLED]:
		_handle_open_order(last_known_order, price_history, indicator)
	elif status in [Client.ORDER_STATUS_CANCELED, Client.ORDER_STATUS_EXPIRED, Client.ORDER_STATUS_REJECTED]:
		_handle_rejected_order(last_known_order, price_history, indicator)


def _handle_first_order(symbol, price_history, indicator):
	if indicator == TradingSignal.BUY:
		_place_limit_buy(symbol, price_history)


def _handle_completed_order(order, price_history, indicator):
	if TradingSignal[order['side']] == indicator:
		raise ValueError('previous indicator cannot be identical to current for completed order')

	if order['side'] == Client.SIDE_SELL and indicator == TradingSignal.BUY:
		_place_limit_buy(order['symbol'], price_history)
	elif order['side'] == Client.SIDE_BUY and indicator == TradingSignal.SELL:
		_place_limit_sell(order['symbol'], price_history)


def _handle_rejected_order():
	pass


def _handle_open_order(order, indicator):
	if TradingSignal[order['side']] == indicator:
		raise ValueError('previous indicator cannot be identical to current for open order')

	if indicator == TradingSignal.BUY and order['side'] == Client.SIDE_SELL:
		_handle_order_cancellation(order)
