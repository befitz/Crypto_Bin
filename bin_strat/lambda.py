from resources.config import properties
from strategy_scalp import trading_strategy
import logging as log

def trading_event_handler(event, context):
    run_interval: str = properties['run-interval']
    candlesticks: int = properties['candlesticks']

    for ticker in properties['tickers'].keys():
        log.info('submitting symbol %s to trading strategy'.format(ticker))
        trading_strategy(ticker, run_interval, candlesticks)
