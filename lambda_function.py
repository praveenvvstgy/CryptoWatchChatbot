import os
import logging
import time
from coinbase.wallet.client import Client
from coinbase.wallet.model import APIObject

api_key = os.environ['api_key']
api_secret = os.environ['api_secret']

client = Client(api_key, api_secret)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

""" --- Coinbase Client ---- """
def create_pair(crypto, currency):
	pair = crypto + "-" + currency
	return pair
	
def get_prices(price_type, currency_pair):
	return client._make_api_object(client._get('v2', 'prices', currency_pair, price_type), APIObject)

def bitcoin_spot_price():
	pair = create_pair("BTC", "USD")
	spot_prices = get_prices("spot", pair)
	return spot_prices["amount"]

def bitcoin_sell_price():
	pair = create_pair("BTC", "USD")
	sell_prices = get_prices("sell", pair)
	return sell_prices["amount"]

def bitcoin_buy_price():
	pair = create_pair("BTC", "USD")
	buy_prices = get_prices("buy", pair)
	return buy_prices["amount"]

def ethereum_spot_price():
	pair = create_pair("ETH", "USD")
	spot_prices = get_prices("spot", pair)
	return spot_prices["amount"]

def ethereum_sell_price():
	pair = create_pair("ETH", "USD")
	sell_prices = get_prices("sell", pair)
	return sell_prices["amount"]

def ethereum_buy_price():
	pair = create_pair("ETH", "USD")
	buy_prices = get_prices("buy", pair)
	return buy_prices["amount"]

def litecoin_spot_price():
	pair = create_pair("LTC", "USD")
	spot_prices = get_prices("spot", pair)
	return spot_prices["amount"]

def litecoin_sell_price():
	pair = create_pair("LTC", "USD")
	sell_prices = get_prices("sell", pair)
	return sell_prices["amount"]

def litecoin_buy_price():
	pair = create_pair("LTC", "USD")
	buy_prices = get_prices("buy", pair)
	return buy_prices["amount"]

""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message, response_card):
	return {
		'sessionAttributes': session_attributes,
		'dialogAction': {
			'type': 'ElicitSlot',
			'intentName': intent_name,
			'slots': slots,
			'slotToElicit': slot_to_elicit,
			'message': message,
			'responseCard': response_card
		}
	}


def confirm_intent(session_attributes, intent_name, slots, message, response_card):
	return {
		'sessionAttributes': session_attributes,
		'dialogAction': {
			'type': 'ConfirmIntent',
			'intentName': intent_name,
			'slots': slots,
			'message': message,
			'responseCard': response_card
		}
	}


def close(session_attributes, fulfillment_state, message):
	response = {
		'sessionAttributes': session_attributes,
		'dialogAction': {
			'type': 'Close',
			'fulfillmentState': fulfillment_state,
			'message': message
		}
	}
	logger.debug("closing with response: {}".format(response))
	return response


def delegate(session_attributes, slots):
	return {
		'sessionAttributes': session_attributes,
		'dialogAction': {
			'type': 'Delegate',
			'slots': slots
		}
	}


def build_response_card(title, subtitle, options):
	"""
	Build a responseCard with a title, subtitle, and an optional set of options which should be displayed as buttons.
	"""
	buttons = None
	if options is not None:
		buttons = []
		for i in range(min(5, len(options))):
			buttons.append(options[i])

	return {
		'contentType': 'application/vnd.amazonaws.card.generic',
		'version': 1,
		'genericAttachments': [{
			'title': title,
			'subTitle': subtitle,
			'buttons': buttons
		}]
	}


""" --- Helper Functions --- """

def build_validation_result(is_valid, violated_slot, message_content):
	return {
		'isValid': is_valid,
		'violatedSlot': violated_slot,
		'message': {'contentType': 'PlainText', 'content': message_content}
	}


def validate_user_form_details(name):
	if len(name) < 3:
		return build_validation_result(False, 'NameType', 'That name is invalid, can you please enter your name again!')

	return build_validation_result(True, None, None)

def build_options(slot):
	"""
	Build a list of potential options for a given slot, to be used in responseCard generation.
	"""
	if slot == 'NameType':
		return None
	elif slot == 'Date':
		# Return the next five weekdays.
		options = []
		potential_date = datetime.date.today()
		while len(options) < 5:
			potential_date = potential_date + datetime.timedelta(days=1)
			if potential_date.weekday() < 5:
				options.append({'text': '{}-{} ({})'.format((potential_date.month), potential_date.day, day_strings[potential_date.weekday()]),
								'value': potential_date.strftime('%A, %B %d, %Y')})
		return options
	elif slot == 'Time':
		# Return the availabilities on the given date.
		if not appointment_type or not date:
			return None

		availabilities = try_ex(lambda: booking_map[date])
		if not availabilities:
			return None

		availabilities = get_availabilities_for_duration(get_duration(appointment_type), availabilities)
		if len(availabilities) == 0:
			return None

		options = []
		for i in range(min(len(availabilities), 5)):
			options.append({'text': build_time_output_string(availabilities[i]), 'value': build_time_output_string(availabilities[i])})

		return options

""" --- Functions that control the bot's behavior --- """

def make_bitcoin_spot_price(intent_request):
	"""
	Performs dialog management and fulfillment for filling a w9 form.

	Beyond fulfillment, the implementation for this intent demonstrates the following:
	1) Use of elicitSlot in slot validation and re-prompting
	2) Use of confirmIntent to support the confirmation of inferred slot values, when confirmation is required
	on the bot model and the inferred slot values fully specify the intent.
	"""
	source = intent_request['invocationSource']
	output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

	if source == 'DialogCodeHook':
		return close(
			output_session_attributes,
			'Fulfilled',
			{
				'contentType': 'PlainText',
				'content': 'The price of Bitcoin now is {}'.format(bitcoin_spot_price())
			}
		)

def make_ethereum_spot_price(intent_request):
	source = intent_request['invocationSource']
	output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

	if source == 'DialogCodeHook':
		return close(
			output_session_attributes,
			'Fulfilled',
			{
				'contentType': 'PlainText',
				'content': 'The price of Ethereum now is {}'.format(ethereum_spot_price())
			}
		)

def make_litecoin_spot_price(intent_request):
	source = intent_request['invocationSource']
	output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

	if source == 'DialogCodeHook':
		return close(
			output_session_attributes,
			'Fulfilled',
			{
				'contentType': 'PlainText',
				'content': 'The price of Litecoin now is {}'.format(litecoin_spot_price())
			}
		)

""" --- Intents --- """


def dispatch(intent_request):
	"""
	Called when the user specifies an intent for this bot.
	"""

	logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

	intent_name = intent_request['currentIntent']['name']

	# Dispatch to your bot's intent handlers
	if intent_name == 'BitcoinSpotPriceIntent':
		return make_bitcoin_spot_price(intent_request)
	elif intent_name == 'EthereumSpotPriceIntent':
		return make_ethereum_spot_price(intent_request)
	elif intent_name == 'LitecoinSpotPriceIntent':
		return make_litecoin_spot_price(intent_request)
	raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def crypto_watch_handler(event, context):
	"""
	Route the incoming request based on intent.
	The JSON body of the request is provided in the event slot.
	"""
	# By default, treat the user request as coming from the America/New_York time zone.
	os.environ['TZ'] = 'America/New_York'
	time.tzset()
	logger.debug('event.bot.name={}'.format(event['bot']['name']))

	return dispatch(event)
