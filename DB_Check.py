import sqlalchemy
import pandas as pd



def check_database(lookback, crypto_ticker, USD_amount):
	lookback = 60
	crypto_ticker = crypto_ticker
	engine = sqlalchemy.create_engine(f'sqlite:///{crypto_ticker}stream.db')
	df = pd.read_sql(crypto_ticker, engine)
	lookbackperiod = df.iloc[-lookback:]
	latest_price = df.iloc[-1].Price
	qty = USD_amount/latest_price
	qty = round(qty,3)
	print("Quantity:",qty)
	print("Price:", latest_price)


check_database(60, 'ALGOUSD', 50)