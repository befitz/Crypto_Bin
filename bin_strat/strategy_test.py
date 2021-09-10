import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from binance.client import Client
import binance_client
import datetime as dt
import resources.config as config

#Establish connection to Binance via API key
client = binance_client.get_binance_client()

#crypto_ticker = config.crypto_ticker
#USD_amount = config.USD_amount
lookback = 200

def map_klines_to_dataframe(klines):
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
    return df

def klines_maped(lookback, crypto_ticker):
    price_hist = client.get_klines(symbol=crypto_ticker, interval=Client.KLINE_INTERVAL_2HOUR, limit = lookback)
    df = map_klines_to_dataframe(price_hist)
    return df


def prep_df(crypto_ticker):
    crypto_ticker = crypto_ticker
    df = klines_maped(lookback, crypto_ticker)
    df = df[["Time","Close","Volume"]]
    df.Close = df.Close.astype(float)
    df['ret_pct_change'] = df['Close'].pct_change()

    return df

#MACD
def MACD_calc(df):
    # Get the 26-day EMA of the closing price
    k = df['Close'].ewm(span=12, adjust=False, min_periods=12).mean()
    # Get the 12-day EMA of the closing price
    d = df['Close'].ewm(span=26, adjust=False, min_periods=26).mean()
    # Subtract the 26-day EMA from the 12-Day EMA to get the MACD
    macd = k - d
    # Get the 9-Day EMA of the MACD for the Trigger line
    macd_s = macd.ewm(span=9, adjust=False, min_periods=9).mean()
    # Calculate the difference between the MACD - Trigger for the Convergence/Divergence value
    macd_h = macd - macd_s

    df['MACD'] = macd_h
    df['signal'] = macd_s
    long = []
    for i in range(0,len(df)):
        if df.MACD[i] > df.signal[i]: #Long potental where price is above the 9 day moving average
            long.append(1)
        else:
            long.append(0)
    df['go_long'] = long
    df['potential_gains'] = df.ret_pct_change * df.go_long

    return df

def MACD_strat(df):
    macddf = MACD_calc(df)
    #Identify entry and exit positions
    #1 will be entry, -1 will be exit, 0 will be leave alone
    entry_exit = []
    entry_price = []
    exit_price = []
    for i in range(0,len(macddf)):
        if i != 0:
            #identify entry point which will be where go_long i-1 is 0 and i = 1
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

    return macddf


def plot_results(macddf):
    fig = plt.figure(figsize = (24,8))
    plt.plot(macddf['Close'])
    plt.scatter(macddf.index,macddf['entry_price'], color = 'green', label='Buy Signal', marker='^')
    plt.scatter(macddf.index,macddf['exit_price'], color = 'red', label='Sell Signal', marker='v')
    plt.xlabel('Lookback Interval')
    plt.ylabel('Price($)')
    plt.title('MACD Strategy Results')
    plt.show()

def strat_test_results(crypto_ticker):
    df = prep_df(crypto_ticker)
    macddf = MACD_strat(df)
    num_trades_executed = len(macddf[macddf['entry_exit_signal'] !=0])
    potential_gains = df['potential_gains'].sum()
    potential_gains = potential_gains *100
    print("Coin:", crypto_ticker)
    print("Number of executed trades:", num_trades_executed)
    print("Profit: %0.2f percent" %potential_gains)
    print("Lookback period:", lookback)
    plot_results(macddf)

strat_test_results('ALGOUSD')
