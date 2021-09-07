import xlwings
import pandas as pd 
from binance.client import Client
import config

client = Client(config.apiKey, config.apiSecurity, tld='us')
print("Logged in, leggo!")


#Function to add latest prices to prices excel sheet
def update_port_prices():
	wb = xlwings.Book('crypto_portfolio.xlsx')
	price_sheet = wb.sheets('prices')

	prices = client.get_all_tickers()

	df = pd.DataFrame(prices)
	price_sheet.range('a1').options(pd.DataFrame, index=False).value = df


#Get Account info
def positions():
	wb = xlwings.Book('crypto_portfolio.xlsx')
	pos_sheet = wb.sheets('positions')

	info = client.get_account()
	df = pd.DataFrame(info['balances'])
	df.columns = ['Coin', 'Available', 'In_order']
	coins_list = df['Coin'].to_list()
	pos_sheet.range('a1').options(pd.DataFrame, index=False).value = df
	return coins_list


#Function to retreive all trades and add it to excel
def update_trades():
	coins_list = positions()
	dfs = []

	for coin in coins_list:
		try:
			trades = client.get_my_trades(symbol = f'{coin}USD')
			df = pd.DataFrame(trades)
			dfs.append(df)
		except:
			pass
	final_df = pd.concat(dfs)
	final_df.time = pd.to_datetime(final_df.time, unit='ms')

	
	wb = xlwings.Book('crypto_portfolio.xlsx')
	trade_sheet = wb.sheets('trades')
	trade_sheet.range('a1').options(pd.DataFrame, index=False).value = final_df



#Main Function
def update_portfolio():
	update_port_prices()
	positions()
	update_trades()


update_portfolio()