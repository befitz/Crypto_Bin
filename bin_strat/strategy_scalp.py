import logging as log
from decimal import Decimal

import pandas as pd
from binance.client import Client

import bin_strat.resources.config as config
import binance_client
import indicators
from bin_strat.indicators import TradingSignal

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
    df.Time = df.Time.dt.tz_localize('UTC')  # To recognize timezones
    df.Time = df.Time.dt.tz_convert('US/Eastern')  # To set the timezone
    df = df[["Time", "Close", "Volume"]]
    df.Close = df.Close.astype(float)

    return df


def _calculate_share_price(symbol, klines):
    if not klines:
        raise ValueError('cannot calculate share price without price history, got: %s'.format(str(klines)))
    cfg = config.properties['tickers'][symbol]
    return round(Decimal(klines['Close'].iloc[-1]), cfg['price_precision'])


def _calculate_order_qty(symbol, share_price):
    """
    Determines how many shares should be purchased given a price history.
    Args:
        symbol (str): The ticker
        share_price (Decimal): the 60-minute price history for a given ticker.
    Returns:
        Decimal: the amount of shares that should be purchased, 0 if none.
    """
    cfg = config.properties['tickers'][symbol]
    return round(Decimal(cfg['limit']) / share_price, cfg['asset_precision'])


def _place_limit_sell(symbol, price_history):
    """
    Given an order, place an OCO sell order good until cancelled.
    Args:
        symbol (str): The ticker
        price_history (list): The price history for the ticker
    """
    if not price_history:
        log.warning('no price history found for ticker %s: cannot place limit sell'.format(symbol))
        return

    order_quantity = client.get_asset_balance(symbol)['free']  # assets could be locked here?

    share_price = _calculate_share_price(symbol, price_history)

    if order_quantity > 0:
        order = client.order_limit_sell(symbol=symbol, quantity=order_quantity, price=share_price)
        log.info('placed a limit sell request for %d shares of %s at $%.2d'.format(order_quantity, symbol, share_price))
        log.info(str(order))


def _handle_order_cancellation(order):
    """
    Sends an order cancellation request if the order should be cancelled.
    Args:
        order (dict): The binance api order response
    """
    log.info('attempting to cancel order %d, which has a status of %s'.format(order['orderId'], order['status']))
    result = client.cancel_order(symbol=order['symbol'], orderId=order['orderId'])
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

    share_price = _calculate_share_price(symbol, price_history)

    order_quantity = _calculate_order_qty(symbol, share_price)

    if order_quantity > 0:
        order = client.order_limit_buy(symbol=symbol, quantity=order_quantity, price=share_price)
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


def _handle_rejected_order(order, price_history, indicator):
    raise RuntimeError('order %s was rejected, canceled or expired. see more: %s'.format(order['orderId'], order))


def _handle_open_order(order, price_history, indicator):
    if TradingSignal[order['side']] == indicator:
        raise ValueError('previous indicator cannot be identical to current for open order')

    if order['side'] == Client.SIDE_BUY:
        if indicator == TradingSignal.SELL:
            _handle_order_cancellation(order)
    else:
        _handle_order_cancellation(order)
        if indicator == TradingSignal.HOLD:
            _place_limit_sell(order['symbol'], price_history)
