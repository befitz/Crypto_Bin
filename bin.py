import pandas as pd 
import sqlalchemy
import asyncio
from binance.client import Client
from binance import AsyncClient, BinanceSocketManager
import config


client = Client(config.apiKey, config.apiSecurity, tld='us')
print("Logged in!")
engine = sqlalchemy.create_engine('sqlite:///ADAUSDstream.db')

def createframe(msg):
	df = pd.DataFrame([msg])
	df = df.loc[:,['s','E','p']]
	df.columns = ['symbol','Time','Price']
	df.Price = df.Price.astype(float)
	df.Time = pd.to_datetime(df.Time, units='ms')
	return df

while True:
	await socket.__aenter__()
	msg = await socket.recv()
	frame = createframe(msg)
	frame.to_sql('ADAUSD', engine, if_exists='append', index = False)
	print(frame)
