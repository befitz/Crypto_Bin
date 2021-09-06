import sqlalchemy
import pandas as pd
from binance.client import Client
import config

#Establish connection to Binance via API key
client = Client(config.apiKey, config.apiSecurity, tld='us')
print("Logged in!")

engine = sqlalchemy.create_engine('sqlite:///ADAUSDstream.db')

#Simple trendfollowing strategy
#If crypto (ADAUSD) is rising by x%, place a buy market order
#Exit when the profit is above 0.15% or loss is less than -0.15%
def strategy(entry, lookback, qty, open_position=False):
	while True:
		df = pd.read_sql('ADAUSD', engine)
		lookbackperiod = df.iloc[-lookback:]
		cumret = (lookbackperiod.Price.pct_change() +1).cumprod() -1
		if not open_position:
			if cumret[cumret.last_valid_index()] > entry:
				order = client.create_order(symbol='ADAUSD',
					side = 'BUY',
					type = 'MARKET',
					quantity = qty)
				print(order)
				open_position = True
				break

	if open_position:
		while True:
			df = pd.read_sql('ADAUSD', engine)
			sincebuy = df.loc[df.Time > pd.to_datetime(order['transactTime'], unit = 'ms')]
			if len(sincebuy) >1:
				sincebuyret = (sincebuy.Price.pct_change() +1).cumprod() -1
				last_entry = sincebuyret[sincebuyret.last_valid_index()]
				if last_entry > 0.0015 or last_entry <0.0015:
					order = client.create_order(symbol = 'ADAUSD',
						side = 'SELL', 
						type = 'MARKET',
						quantity = qty)
					print(order)
					break

strategy(0.001, 60, 9)