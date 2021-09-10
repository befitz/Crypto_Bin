from enum import Enum

class TradingSignal(Enum):
    BUY = 1
    SELL = -1
    HOLD = 0

def macd_signal(price_history):
    """
    Calculates the most recent macd signal for a given asset
    Args:
        price_history (pd.DataFrame): the historical price data for a given asset
    Returns:
        TradingSignal: the signal to sell (TradingSignal.SELL), buy (TradingSignal.BUY), or do nothing (TradingSignal.HOLD)
    """
    pass
