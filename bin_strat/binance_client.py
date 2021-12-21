from binance.client import Client
import resources.config as config
import logging as log

_api_key = config.properties['X-MBX-APIKEY']
_api_secret = config.properties['X-MBX-SECURITY']

# Defining this function here lets us re-use the connection code in other modules!
def get_binance_client():
    client = Client(_api_key, _api_secret, tld = 'us')
    if client.ping() == {}:
        log.info('successfully connected binance client')
    return client
