from bin import *

def strategy(entry, lookback, qty, open_position=False):
	while True:
		df = df.read_sql('BTCUSD', engine)
		lookbackperiod = df.iloc[-lookback:]
		cumret = (lookbackperiod.Price.pct_change() +1).cumprod() -1
		if not open_position:
			if comret[comret.last_valid_index()] > entry:
				order = clinet.create_order(symbol='BTCUSD',
					side = 'BUY',
					type = 'MARKET',
					quantity = qty)
				print(order)
				open_position = True
				break
	if open_position:
		while True:
			df = pd.read_sql('BTCUSD', engine)
			sincebuy = df.loc[df.Time > pd.to_datetime(order['transactTime'], unit = 'ms')]
			if len(sincebuy) >1:
				sincebuyret = (sincebuy.Price.pct_change() +1).cumprod() -1
				last_entry = sincebuyret[sincebuyret.last_valid_index()]
				if last_entry > 0.0015 or last_entry <0.0015:
					order = client.create_order(symbol = 'BTCUSD',
						side = 'SELL', 
						type = 'MARKET',
						quantity = qty)
					print(order)
					break