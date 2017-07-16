import os
from coinbase.wallet.client import Client

api_key = os.environ['api_key']
api_secret = os.environ['api_secret']


client = Client(api_key, api_secret)

def create_pair(crypto, currency):
	# pair = "BTC-USD"
	pair = crypto_currency + "-" + currency
	return pair

def bitcoin_spot_price():
	pair = create_pair("BTC", "USD")
	spot_prices = client.get_spot_price(currency_pair = pair)
	return spot_prices["data"]["amount"]

def bitcoin_sell_price():
	pair = create_pair("BTC", "USD")
	sell_prices = client.get_sell_price(currency_pair = pair)
	return sell_prices

def bitcoin_buy_price():
	pair = create_pair("BTC", "USD")
	buy_prices = client.get_buy_price(currency_pair = pair)
	return buy_prices
