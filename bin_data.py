import pandas as pd 
import sqlalchemy
import asyncio
from binance.client import Client
from binance import AsyncClient, BinanceSocketManager
import config

#Establish connection to Binance via API key
client = Client(config.apiKey, config.apiSecurity, tld='us')
print("Logged in!")
#Set up a SQL database to store timestamps and prices
engine = sqlalchemy.create_engine('sqlite:///ADAUSDstream.db')

#Creates a dataframe of the timestamps and prices by second
def createframe(msg):
	df = pd.DataFrame([msg])
	df = df.loc[:,['s','E','p']]
	df.columns = ['symbol','Time','Price']
	df.Price = df.Price.astype(float)
	df.Time = pd.to_datetime(df.Time, units='ms')
	return df


#Function to call the API for the information, stores it to the SQL database
async def fetch():
	while True:
		await socket.__aenter__()
		msg = await socket.recv()
		frame = createframe(msg)
		frame.to_sql('ADAUSD', engine, if_exists='append', index = False)
		print(frame)


#This will need to remain open and running while the strategy is running until closed.