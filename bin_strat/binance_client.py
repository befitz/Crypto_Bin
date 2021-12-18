from binance.client import Client
import resources.config as config

# Defining this function here lets us re-use the connection code in other modules!
def get_binance_client():
    #Establish connection to Binance via API key
    client = Client(config.properties['X-MBX-APIKEY'], config.properties['X-MBX-SECURITY'], tld = 'us')
    if client.ping() == {}:
            print("Logged in, leggo!")
    return client
