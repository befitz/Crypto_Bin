from binance.client import Client
import config

_client = None

# Defining this function here lets us re-use the connection code in other modules!
def get_binance_client():
    global _client
    #Establish connection to Binance via API key
    if _client is None:
        client = Client(config.apiKey, config.apiSecurity, tld='us')
        if client.ping() == {}:
             print("Logged in, leggo!")
    return _client
