from binance.client import Client
from resources.config import properties
import logging as log

_api_key = properties['security']['binance']['X-MBX-APIKEY']
_api_secret = properties['security']['binance']['X-MBX-SECURITY']


# Defining this function here lets us re-use the connection code in other modules!
def get_binance_client():
    client = Client(_api_key, _api_secret, tld='us')
    if client.ping() == {}:
        log.info('successfully connected binance client')
    return client
