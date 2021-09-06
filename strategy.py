from bin import *


#Simple trendfollowing strategy
#If crypto (ADAUSD) is rising by x%, place a buy market order
#Exit when the profit is above 0.15% or loss is less than -0.15%
def strategy(entry, lookback, qty, open_position=False):
	while True:
		df = df.read_sql('ADAUSD', engine)
		lookbackperiod = df.iloc[-lookback:]
		cumret = (lookbackperiod.Price.pct_change() +1).cumprod() -1
		if not open_position:
			if comret[comret.last_valid_index()] > entry:
				order = clinet.create_order(symbol='ADAUSD',
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