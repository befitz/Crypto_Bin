from binance.client import Client
import config

#Establish connection to Binance via API key
client = Client(config.apiKey, config.apiSecurity, tld='us')
print("Logged in, leggo!")

crypto_ticker = config.crypto_ticker

orders = client.get_open_orders(symbol=crypto_ticker)
print(orders)