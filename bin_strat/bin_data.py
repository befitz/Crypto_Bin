import pandas as pd 
import sqlalchemy
import binance_client
import asyncio
from binance.client import Client
from binance import AsyncClient, BinanceSocketManager
import config

#Set this as the crypto to get prices for
crypto_ticker = config.crypto_ticker

#Establish connection to Binance via API key
client = binance_client.get_binance_client()

#Set up a SQL database to store timestamps and prices
engine = sqlalchemy.create_engine(f'sqlite:///{crypto_ticker}stream.db')

#Creates a dataframe of the timestamps and prices by second
def createframe(msg):
	df = pd.DataFrame([msg])
	df = df.loc[:,['s','E','p']]
	df.columns = ['symbol','Time','Price']
	df.Price = df.Price.astype(float)
	df.Time = pd.to_datetime(df.Time, unit='ms')
	return df


#Function to call the API for the information, stores it to the SQL database
async def main():
	while True:
		client = await AsyncClient.create(tld='us')
		bm = BinanceSocketManager(client)
		socket = bm.trade_socket(crypto_ticker)
		await socket.__aenter__()
		msg = await socket.recv()
		frame = createframe(msg)
		frame.to_sql(crypto_ticker, engine, if_exists='append', index = False)
		print(frame)

		await client.close_connection()

if __name__ =="__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())


#This will need to remain open and running while the strategy is running until closed.