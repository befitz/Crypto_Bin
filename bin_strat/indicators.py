from enum import IntFlag

class TradingSignal(IntFlag):
    BUY = 1
    SELL = -1
    HOLD = 0

def macd_signal(price_history):
    """
    Calculates the most recent macd signal for a given asset
    - Calculate the MACD and signal lines
    - Generate the trading signal based off the lines crossing

    For when we can do multiple orders/tickers:
    - Screener itteration through multiple tickers to compare the Weighted Success Rate
    - Checking the Binance API account balance for the current balance of the asset
    Args:
        price_history (pd.DataFrame): the historical price data for a given asset
    Returns:
        TradingSignal: the signal to sell (TradingSignal.SELL), buy (TradingSignal.BUY), or do nothing (TradingSignal.HOLD)
    """
    price_history_macd = _MACD_calc(price_history)
    macd_signal = _MACD_strat(price_history_macd)
    latest_signal = macd_signal['buy_sell_signal'].iloc[-1]

    return latest_signal


def _MACD_calc(price_history):
    """
    Calculates the MACD line and signal line
    Args: price_history (pd.DataFrame): the historical price data for a given asset
    Returns: price_history_macd (pd.DataFrame) with  columns ['Close', 'ret_pct_change', 'MACD', 'signal', 'go_long', 'potential_gains']
    """
    k = price_history['Close'].ewm(span=10, adjust=False, min_periods=12).mean() # Get the 26-day EMA of the closing price
    d = price_history['Close'].ewm(span=19, adjust=False, min_periods=26).mean() # Get the 12-day EMA of the closing price
    macd = k - d # Subtract the 26-day EMA from the 12-Day EMA to get the MACD
    macd_s = macd.ewm(span=6, adjust=False, min_periods=9).mean() # Get the 9-Day EMA of the MACD for the Trigger line
    price_history_macd = price_history
    price_history_macd['MACD'] = macd
    price_history_macd['signal'] = macd_s

    return price_history_macd


def _MACD_strat(price_history_macd):
    """
    Function to create the buy_sell_signal: 0 for hold, 1 for buy, -1 for sell. Will use TradingSignal
    Logic: if MACD > signal then buy, if MACD < signal then sell
    args: price_history_macd (pd.DataFrame)
    returns: macd_signal (pd.DataFrame) and latest_signal 
    """
    flag = 0 
    buy_sell_signal = []
    entry_price = []
    exit_price = []
    for i in range(0,len(price_history_macd)):
        if price_history_macd.MACD[i] > price_history_macd.signal[i]: #buy if previous indicator is hold(0)
            if flag != 1:
                buy_sell_signal.append(TradingSignal.BUY)
                entry_price.append(price_history_macd['Close'][i])
                exit_price.append(np.NaN)
                flag = 1
            else:
                buy_sell_signal.append(TradingSignal.HOLD)
                entry_price.append(np.NaN)
                exit_price.append(np.NaN)
                TS = TradingSignal.HOLD
                flag = 1
        elif price_history_macd.MACD[i] < price_history_macd.signal[i]:
            if flag != 0:
                buy_sell_signal.append(TradingSignal.SELL)
                entry_price.append(np.NAN)
                exit_price.append(price_history_macd['Close'][i])
                flag = 0
            else:
                buy_sell_signal.append(TradingSignal.HOLD)
                entry_price.append(np.NaN)
                exit_price.append(np.NaN)
                flag = 0
        else: #handle nan values
            buy_sell_signal.append(TradingSignal.HOLD)
            entry_price.append(np.NaN)
            exit_price.append(np.NaN)

    macd_signal = pd.DataFrame(price_history_macd[['Time','Close']])
    macd_signal['buy_sell_signal'] = buy_sell_signal
    macd_signal['entry_price'] = entry_price
    macd_signal['exit_price'] = exit_price


    return macd_signal