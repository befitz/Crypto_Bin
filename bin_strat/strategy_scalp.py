import pandas as pd
from binance.client import Client
import config

#Establish connection to Binance via API key
client = Client(config.apiKey, config.apiSecurity, tld='us')
print("Logged in, leggo!")

crypto_ticker = config.crypto_ticker
USD_amount = config.USD_amount

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
    return df

def klines_maped(limit):
	price_hist = client.get_klines(symbol=crypto_ticker, interval=Client.KLINE_INTERVAL_1MINUTE, limit = limit)
	df = map_klines_to_dataframe(price_hist)
	return df


df = klines_maped(61)
df = df[["Time","Close","Volume"]]
df.Close = df.Close.astype(float)
df['ret'] = df['Close'].pct_change()
print(df)


#Simple trendfollowing strategy
#If crypto (ADAUSD) is rising by x%, place a buy market order
#Exit when the profit is above 0.15% or loss is less than -0.15%
#entry is the percentage change to initiate the entry
def strategy_scalp(entry, lookback, open_position=False, qty=0):
	while True:
		df = klines_maped(61)
		lookbackperiod = df.iloc[-lookback:]
		cumret = (lookbackperiod.Close.pct_change() +1).cumprod() -1
		if not open_position: 
			if cumret[cumret.last_valid_index()] > entry:
				qty = calculate_order_qty()
				order = client.create_order(
					symbol=crypto_ticker,
					side = 'BUY',
					type = 'MARKET',
					quantity = qty)
				print(order)
				open_position = True
				#return order
				break

#Function to take order ID and query BinanceAPI for the order status
#Query unitl status = 'FILLED'
#Only then can we place a sell
#for multiple tickers: either data storage of the orderIDs or time limit and cancel when exceeds time limit

#order output provies price, status, and order id


#Have this run once the order status = filled
#request status of the order for x amount of time
	if open_position:
		while True:
			df = klines_maped(61)
			sincebuy = df.loc[df.Time > pd.to_datetime(order['transactTime'], unit = 'ms')]
			if len(sincebuy) >1:
				sincebuyret = (sincebuy.Close.pct_change() +1).cumprod() -1
				last_entry = sincebuyret[sincebuyret.last_valid_index()]
				if last_entry > 0.0015 or last_entry <0.0015:
					order = limit_sell_order(qty)
					print(order)
					break



#Fletch the latest price
def get_latest_price():
	df = pd.read_sql(crypto_ticker, engine)
	latest_price = df.iloc[-1].Price
	return latest_price

#calculate the quantity of the crypto to buy based on the USD amount and latest price
def calculate_order_qty():
	latest_price = get_latest_price()
	qty = USD_amount/latest_price
	qty = round(qty,2)
	return qty


#function to generate a limit buy and returns the quantiy and prints order details
def limit_buy_order(qty):
	latest_price = get_latest_price()
	order = client.order_limit_buy(
		symbol = crypto_ticker,
		quantity = qty,
		price = latest_price)
	return order


#function to generate a limit sell
def limit_sell_order(qty):
	latest_price = get_latest_price()
	sell_price = latest_price*1.0015
	sell_price = round(sell_price,3)
	order = client.order_limit_sell(
		symbol = crypto_ticker,
		quantity = qty,
		price = sell_price)
	return order
