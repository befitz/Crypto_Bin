from enum import Enum

class TradingSignal(Enum):
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
    pass


def _MACD_calc(price_history):
    """
    Calculates the MACD line and signal line
    Args:
        price_history (pd.DataFrame): the historical price data for a given asset
    Returns:
        price_history_macd (pd.DataFrame) with  columns ['Close', 'ret_pct_change', 'MACD', 'signal', 'go_long', 'potential_gains']
    """
    k = price_history['Close'].ewm(span=12, adjust=False, min_periods=12).mean() # Get the 26-day EMA of the closing price
    d = price_history['Close'].ewm(span=26, adjust=False, min_periods=26).mean() # Get the 12-day EMA of the closing price
    macd = k - d # Subtract the 26-day EMA from the 12-Day EMA to get the MACD
    macd_s = macd.ewm(span=9, adjust=False, min_periods=9).mean() # Get the 9-Day EMA of the MACD for the Trigger line
    
    price_history_macd = pd.DataFrame()
    price_history_macd['Close'] = price_history['Close']
    price_history_macd['ret_pct_change'] = price_history['Close'].pct_change()
    price_history_macd['MACD'] = macd 
    price_history_macd['signal'] = macd_s
    long = [] #Creating a 'long' list to be converted to pd.Series which will be 0 for short, 1 for long
    for i in range(0,len(price_history_macd)):
        if price_history_macd.MACD[i] > price_history_macd.signal[i]: #Long potental where price is above the 9 day moving average
            long.append(1)
        else:
            long.append(0) #Short where price is not above the 9 day moving average
    price_history_macd['go_long'] = long
    price_history_macd['potential_gains'] = price_history_macd.ret_pct_change * price_history_macd.go_long #Column to provide the potential gains if long on the asset

    return price_history_macd


        flag = 0
    entry_exit = []
    entry_price = []
    exit_price = []
    for i in range(0,len(macddf)):
        if i != 0:
            if macddf.go_long[i] == 1:
                if macddf.go_long[i-1] == 0:
                    entry_exit.append(1)
                    entry_price.append(macddf['Close'][i])
                    exit_price.append(np.NaN)
                else:
                    entry_exit.append(0)
                    entry_price.append(np.NaN)
                    exit_price.append(np.NaN)
            elif macddf.go_long[i] == 0:
                if macddf.go_long[i-1] == 1:
                    entry_exit.append(-1)
                    exit_price.append(macddf['Close'][i])
                    entry_price.append(np.NaN)
                else:
                    entry_exit.append(0)
                    entry_price.append(np.NaN)
                    exit_price.append(np.NaN)
        else:
            entry_exit.append(0)
            exit_price.append(np.NaN)
            entry_price.append(np.NaN)

    macddf['entry_exit_signal'] = entry_exit
    macddf['entry_price'] = entry_price
    macddf['exit_price'] = exit_price

    return macd_signal