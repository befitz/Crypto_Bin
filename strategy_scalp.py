import sqlalchemy
import pandas as pd
from binance.client import Client
import config

#Establish connection to Binance via API key
client = Client(config.apiKey, config.apiSecurity, tld='us')
print("Logged in, leggo!")

crypto_ticker = 'ALGOUSD'
USD_amount = 50
#Set up a SQL database to fetch timestamps and prices
engine = sqlalchemy.create_engine(f'sqlite:///{crypto_ticker}stream.db')

#Simple trendfollowing strategy
#If crypto (ADAUSD) is rising by x%, place a buy market order
#Exit when the profit is above 0.15% or loss is less than -0.15%
#entry is the percentage change to initiate the entry
def strategy_scalp(entry, lookback, open_position=False):
	while True:
		df = pd.read_sql(crypto_ticker, engine)
		lookbackperiod = df.iloc[-lookback:]
		cumret = (lookbackperiod.Price.pct_change() +1).cumprod() -1
		if not open_position: 
			if cumret[cumret.last_valid_index()] > entry:
				order, qty = limit_buy_order()
				open_position = True
				break

	if open_position:
		while True:
			df = pd.read_sql(crypto_ticker, engine)
			sincebuy = df.loc[df.Time > pd.to_datetime(order['transactTime'], unit = 'ms')]
			if len(sincebuy) >1:
				sincebuyret = (sincebuy.Price.pct_change() +1).cumprod() -1
				last_entry = sincebuyret[sincebuyret.last_valid_index()]
				if last_entry > 0.0015 or last_entry <0.0015:
					order = limit_sell_order()
					break

strategy_scalp(0.001,60)


#function to generate a limit buy and returns the quantiy and prints order details
def limit_buy_order():
	df = pd.read_sql(crypto_ticker, engine)
	latest_price = df.iloc[-1:].Price
	qty = USD_amount/latest_price
	order = client.order_limit_buy(
		symbol = crypto_ticker,
		quantity = qty,
		price = latest_price)
	return qty
	print(order)


#function to generate a limit sell
def limit_sell_order():
	df = pd.read_sql(crypto_ticker, engine)
	latest_price = df.iloc[-1:].Price
	qty = USD_amount/latest_price
	order = client.order_limit_sell(
		symbol = crypto_ticker,
		quantity = qty,
		price = latest_price)
	print(order)