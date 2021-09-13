# Crypto_Bin

## Flow

### First Trade
1. For a security **that has not been traded**
2. Program runs at the top of an hour (2hour intervals)
3. Start by fetching historical data.
4. Retreive trading signal from indicator
5. If action is HOLD, exit function
6. If action is SELL, exit function
7. If action is BUY,
	- a. Calculate price to purchase
	- b. Calculate quantiy based on price
	- c. Place limit buy order (time limit?)


### Not First Trade
1. For a security that has been traded previously.
2. Still on a 2 hour interval
3. Pull last known order
4. Order is a buy, not filled
	- a. wait for sell signal to cancel
	- b. get historical data, get trading signal
	- c. if sell, cancel.
	- d. if buy, send alert. Exit on hold
5. Order is a buy and filled
	- a. Get historical data, get signal
	- b. if BUY, send alert
	- c. if SELL, sell
	- d. if HOLD, exit
6. Last order was a sell and filled
	- a. get historical data, signal
	- b. if BUY, buy
	- c. if SELL, alert
	- d. if HOLD, exit
7. Last order was a sell and open (not filled)
	- a. get historical data, signal
	- b. if HOLD, cancel and re-submit limit order
	- c. if BUY, hold onto it and buy more, cancel sell
	- d. if SELL, alert


## Pricing

1. Binance has limitations to precision size of the price.
 - the below code retreives the percisions for both price and quantity
 `def get_percision_size(crypto_ticker):
	"""
	Binance order API requires different percision amounts for each asset
	args: crypto_ticker (string) ex: BTCUSD
	returns:
	base_asset (string) ex: BTC
	asset_percision (int) the max number of values after a decimal point allowed for qty
	quote_percision (int) the max number of values after a decimal point allowed for price
	"""
	symbol_info = client.get_symbol_info(crypto_ticker)
	base_asset = symbol_info['baseAsset']
	asset_percision = symbol_info['baseAssetPrecision']
	quote_percision = symbol_info['quoteAssetPrecision']
	return base_asset, asset_percision, quote_percision
 `
2. Retreiving price using the order book
- Once we have the precision, then we can retreive the bids and asks 
`
def bid_ask_spread(crypto_ticker, ask_percentile = 5, bid_percentile = 95):
	"""
	Function to look at the Binance API order book for the latest bid/asks
	bids are the market buy limit orders, asks are the market sell limit orders. The theory here is to use the (almost) best price from this order-book to choose a limit price
	args: 
	crypto_ticker (string) ex: BTCUSD
	ask_percentile (int) this is the percentile (integer but is read as a percentage) for sell limit price discovery, the lower this percentile, the lower the price but higher likelihood the order will be filled
	bid_percentile (int) this is a percentile (integer but is read as a percentage) for buys, the lower this percentile, the lower the price but the higher the likelihood the order will be filled
	returns: 
	p_asks (float) for sell limit price
	p_bids (float) for buy limit price
	"""
	order_book = client.get_order_book(symbol = crypto_ticker)
	frames = {side: pd.DataFrame(data = order_book[side], columns = ['price', 'quantity'], dtype = float)
	for side in ['bids', 'asks']}
	frames_list = [frames[side].assign(side=side) for side in frames]
	data = pd.concat(frames_list, axis="index", ignore_index=True, sort=True)
	asks = data[data['side'] == 'asks']
	p_asks = np.percentile(asks.price, ask_percentile)
	bids = data[data['side'] == 'bids']
	p_bids = np.percentile(bids.price, bid_percentile)
	return p_asks, p_bids
	`
- This would be the main function to tie it together...
`
def get_limit_price(crypto_ticker, quote_percision, side):
	"""
	Function to get the latest price using the bid ask spread
	args: 
		crypto_ticker (string)
		quote_percision (int) the maximum number of values after the decimal point allowed
		side (string): 'BUY' or 'SELL'
	returns:
		limit_price (string)
	"""
	p_asks, p_bids = bid_ask_spread(crypto_ticker, ask_percentile = 5, bid_percentile = 95)
	if side == 'BUY':
		limit_price = p_bids
	elif side == 'SELL':
		limit_price = p_asks
	else:
		print("side provided not valid")
	context = Context(prec = quote_percision, rounding = ROUND_DOWN)
	limit_price = context.create_decimal_from_float(limit_price)
	limit_price = str(limit_price)
	return limit_price
`