# Crypto_Bin

## Flow

### First Trade
1. For a security *that has not been traded*
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
	4. a. wait for sell signal to cancel
	4. b. get historical data, get trading signal
	4. c. if sell, cancel.
	4. d. if buy, send alert. Exit on hold
5. Order is a buy and filled
	5. a. Get historical data, get signal
	5. b. if BUY, send alert
	5. c. if SELL, sell
	5. d. if HOLD, exit
6. Last order was a sell and filled
	6. a. get historical data, signal
	6. b. if BUY, buy
	6. c. if SELL, alert
	6. d. if HOLD, exit
7. Last order was a sell and open (not filled)
	7. a. get historical data, signal
	7. b. if HOLD, cancel and re-submit limit order
	7. c. if BUY, hold onto it and buy more, cancel sell
	7. d. if SELL, alert

