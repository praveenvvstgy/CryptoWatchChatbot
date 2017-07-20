import os
import logging
import time
from coinbase.wallet.client import Client
from coinbase.wallet.model import APIObject
from twilio.rest import Client as TwilioClient
import boto3
from random import randint


api_key = os.environ['api_key']
api_secret = os.environ['api_secret']

twilio_account_sid = os.environ['twilio_account_sid']
twilio_auth_token = os.environ['twilio_auth_token']

sns_access_secret = os.environ['sns_access_secret']
sns_access_key = os.environ['sns_access_key']

sid_sns_access_secret = os.environ['sid_sns_secret']
sid_sns_access_key = os.environ['sid_sns_access_key']

client = Client(api_key, api_secret)

twilio_client = TwilioClient(twilio_account_sid, twilio_auth_token)

sns_client = boto3.client(
	"sns",
	aws_access_key_id=sid_sns_access_key,
	aws_secret_access_key=sid_sns_access_secret,
	region_name="us-east-1"
)

dynamodb = boto3.resource(
	"dynamodb",
	aws_access_key_id=sns_access_key,
	aws_secret_access_key=sns_access_secret,
	region_name="us-east-1"
)

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
	print "slots in elicit: {}".format(slots)
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


def close(session_attributes, fulfillment_state, message, responseCard = None):
	response = {
		'sessionAttributes': session_attributes,
		'dialogAction': {
			'type': 'Close',
			'fulfillmentState': fulfillment_state,
			'message': message,
			'responseCard': responseCard
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


def build_response_card(title, subtitle, options, image = None):
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
			'imageUrl': image,
			'buttons': buttons
		}]
	}

""" --- Helper Functions for Watch --- """

def random_with_N_digits(n):
	range_start = 10**(n-1)
	range_end = (10**n)-1
	return str(randint(range_start, range_end))

""" --- DynamoDB --- """

def get_user_record(user):
	users_table = dynamodb.Table('users')
	user_record = users_table.get_item(Key = {
		'userId': user
		})
	if 'Item' in user_record:
		return user_record['Item']
	else:
		return None

def get_phone_records_for_user(user):
	user_record = get_user_record(user)
	if not user_record:
		return None
	else:
		phone_record_for_user = None
		if user_record:
			if 'phones' in user_record and len(user_record['phones']) > 0:
				return user_record['phones']
		return None

def get_phone_record_for_user(user, phone):
	user_record = get_user_record(user)
	if not user_record:
		return None
	else:
		phone_record_for_user = None
		if user_record:
			if 'phones' in user_record and len(user_record['phones']) > 0:
				for record in user_record['phones']:
					if record['phoneNumber'] == phone:
						return record
		return None

def update_user_phone_record(user, phone_record):
	users_table = dynamodb.Table('users')
	user_record = get_user_record(user)
	if not user_record:
		users_table.put_item(Item = {
			'userId': user,
			'phones': phone_record
			})
	else:
		users_table.update_item(
			Key = {
			'userId': user
			},
			UpdateExpression='SET phones = :val1',
			ExpressionAttributeValues={
				':val1': phone_record
			}
		)

def update_key_value_for_user(key, matchingValue, user, withkey, withValue):
	phone_records = get_phone_records_for_user(user)
	new_records = []
	for record in phone_records:
		if record[key] == matchingValue:
			record[withkey] = withValue
			new_records.append(record)
		else:
			new_records.append(record)
	update_user_phone_record(user, new_records)

def update_token_for_phone_and_user(phone, user, token):
	update_key_value_for_user('phoneNumber', phone, user, 'token', token)

def insert_user_phone_record(user, new_phone_record):
	user_record = get_user_record(user)
	if not user_record:
		update_user_phone_record(user, [new_phone_record])
	else:
		phone_record = get_phone_records_for_user(user)
		if phone_record and len(phone_record) > 0:
			phone_record.append(new_phone_record)
			update_user_phone_record(user, phone_record)
		else:
			update_user_phone_record(user, [new_phone_record])

def is_number_verified_for_user(user, phone):
	user_record = get_user_record
	if not user_record:
		return False
	else:
		phone_record = get_phone_record_for_user(user, phone)
		if phone_record:
			return phone_record['verified']
		else:
			return False

def verify_user_phone(phone, user):
	token = random_with_N_digits(4)
	send_sms(phone, "Your Crypto Watch verification code is: {}".format(token))
	phone_record = get_phone_record_for_user(user, phone)
	if phone_record:
		update_token_for_phone_and_user(phone, user, token)
	else:
		insert_user_phone_record(user, {
				'phoneNumber': phone,
				'token': token,
				'verified': False
				})

def send_sms(phone, message):
	sns_client.publish(
		PhoneNumber=phone,
		Message=message
	)
	print "Sending SMS to {} with {}".format(phone, message)

def verify_user_phone_with_token(user, phone, token):
	if is_number_verified_for_user(phone, user):
		return True
	else:
		phone_record = get_phone_record_for_user(user, phone)
		if phone_record and phone_record['token'] == token:
			update_key_value_for_user('phoneNumber', phone, user, 'verified', True)
			return True
		return False

def start_phone_verification(phone, user):
	if is_number_verified_for_user(user, phone):
		return True
	else:
		verify_user_phone(phone, user)
		return False

def set_alarm(currency, phone, value):
	if currency == "BTC":
		btc_price = bitcoin_spot_price()
		btc_alarms_table = dynamodb.Table('btc-alarms')
		print "Inserting Alarm: {}".format({
			'alarmId': random_with_N_digits(4),
			'phone': phone,
			'value': int(value),
			'seekingHigherPrice': int(value) > float(btc_price)
			})
		btc_alarms_table.put_item(Item = {
			'alarmId': random_with_N_digits(4),
			'phone': phone,
			'value': int(value),
			'seekingHigherPrice': int(value) > float(btc_price)
			})
	if currency == "ETC":
		etc_price = ethereum_spot_price()
		etc_alarms_table = dynamodb.Table('etc-alarms')
		print "Inserting Alarm: {}".format({
			'alarmId': random_with_N_digits(4),
			'phone': phone,
			'value': int(value),
			'seekingHigherPrice': int(value) > float(etc_price)
		})
		etc_alarms_table.put_item(Item = {
			'alarmId': random_with_N_digits(4),
			'phone': phone,
			'value': int(value),
			'seekingHigherPrice': int(value) > float(etc_price)
			})
	if currency == "LTC":
		ltc_price = litecoin_spot_price()
		ltc_alarms_table = dynamodb.Table('ltc-alarms')
		print "Inserting Alarm: {}".format({
			'alarmId': random_with_N_digits(4),
			'phone': phone,
			'value': int(value),
			'seekingHigherPrice': int(value) > float(ltc_price)
			})
		ltc_alarms_table.put_item(Item = {
			'alarmId': random_with_N_digits(4),
			'phone': phone,
			'value': int(value),
			'seekingHigherPrice': int(value) > float(ltc_price)
			})

""" --- Helper Functions --- """

def build_validation_result(is_valid, violated_slot, message_content):
	return {
		'isValid': is_valid,
		'violatedSlot': violated_slot,
		'message': {'contentType': 'PlainText', 'content': message_content}
	}


def validate_watch(slots, user, currency):
	if not slots["price"]:
		return build_validation_result(False, 'price', 'What price should {} reach when you want me to notify'.format(currency))
	price = slots["price"]
	if price < 0:
		return build_validation_result(False, 'price', 'Price cannot be less than zero, please enter the price at which I should alert you')
	if not slots["phone"]:
		return build_validation_result(False, 'phone', "What is your phone number? I will send a text when {} reaches {} USD".format(currency, price))
	phone = slots["phone"]
	try:
		phone_number = twilio_client.lookups.phone_numbers(phone).fetch(type="carrier").phone_number
	except Exception as e:
		return build_validation_result(False, 'phone', "The phone number {} is invalid, retry again".format(phone))

	if not slots["verification"]:
		if not is_number_verified_for_user(user, phone_number):
			try:
				if not start_phone_verification(phone_number, user):
					return build_validation_result(False, 'verification', "Enter the verification code sent to {}".format(phone_number))
			except Exception as e:
				return build_validation_result(False, 'phone', "Sending SMS failed. Enter phone number again")
		else:
			return build_validation_result(True, None, None)

	verification = slots["verification"]

	if not verify_user_phone_with_token(user, phone_number, verification):
		return build_validation_result(False, 'verification', "The verification token is incorrect, try again")
		
	return build_validation_result(True, None, None)

def build_options(slot):
	"""
	Build a list of potential options for a given slot, to be used in responseCard generation.
	"""
	if slot == 'CryptoHelpIntent':
		options = []
		options.append({'text': "Bitcoin Price", 'value': "What is the price of bitcoin?"})
		options.append({'text': "Ethereum Price", 'value': "What is the price of ethereum?"})
		options.append({'text': "Litecoin Price", 'value': "What is the price of litecoin?"})
		options.append({'text': "Bitcoin Alarm", 'value': "Create a bitcoin alarm"})
		options.append({'text': "Ethereum Alarm", 'value': "Create a ethereum alarm"})
		options.append({'text': "Litecoin Alarm", 'value': "Create a litecoin alarm"})
		return options
	else:
		return None
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
			{},
			'Fulfilled',
			{
				'contentType': 'PlainText',
				'content': 'The price of Bitcoin now is {}'.format(bitcoin_spot_price())
			},
			build_response_card(
					'Bitcoin Price',
					'Bitcoin price history for past 6 hours',
					None,
					'https://s3.amazonaws.com/com.praveengowda.cryptoimages/BTC-USD_data.png'
					)
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
			},
			build_response_card(
					'Ethereum Price',
					'Ethereum price history for past 6 hours',
					None,
					'https://s3.amazonaws.com/com.praveengowda.cryptoimages/ETH-USD_data.png'
					)
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
			},
			build_response_card(
					'Litecoin Price',
					'Litecoin price history for past 6 hours',
					None,
					'https://s3.amazonaws.com/com.praveengowda.cryptoimages/LTC-USD_data.png'
					)
		)

def make_watch(intent_request, currency):
	source = intent_request['invocationSource']
	output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
	userId = intent_request['userId']
	print "slots are: {}".format(intent_request['currentIntent']['slots'])

	if source == 'DialogCodeHook':
		slots = intent_request['currentIntent']['slots']
		if slots["phone"]:
			output_session_attributes["phone"] = slots["phone"]
		else:
			if "phone" in output_session_attributes:
				slots["phone"] = output_session_attributes["phone"]
		validation_result = validate_watch(slots, userId, currency)
		if not validation_result['isValid']:
			slots[validation_result['violatedSlot']] = None
			return elicit_slot(
				output_session_attributes,
				intent_request['currentIntent']['name'],
				slots,
				validation_result['violatedSlot'],
				validation_result['message'],
				None
			)
		if currency == "Bitcoin":
			set_alarm("BTC", slots["phone"], slots["price"])
		elif currency == "Litecoin":
			set_alarm("LTC", slots["phone"], slots["price"])
		elif currency == "Ethereum":
			set_alarm("ETC", slots["phone"], slots["price"])
		return close(
			output_session_attributes,
			'Fulfilled',
			{
				'contentType': 'PlainText',
				'content': "Successfuly set the alarm! I will text you if {} reaches {} USD".format(currency, slots["price"])
			}
		)

def make_help(intent_request):
		return close(
			{},
			'Fulfilled',
			{
				'contentType': 'PlainText',
				'content': "I can fulfill all your crypto currency needs"
			},
			build_response_card(
					"Bitcoin, Ethereum and Litecoin Prices and Price Alerts",
					'Try one of the below options',
					build_options('CryptoHelpIntent')
					)
		)

def make_start(intent_request):
		return close(
			{},
			'Fulfilled',
			{
				'contentType': 'PlainText',
				'content': "Hey! I am crypto watch bot. I can tell you the prices of Crypto currencies and alart you when they reach the prices you want. :)"
			},
			build_response_card(
					"Bitcoin, Ethereum and Litecoin Prices and Price Alerts supported",
					'Try one of the below options',
					build_options('CryptoHelpIntent')
					)
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
	elif intent_name == 'BitcoinWatchIntent':
		return make_watch(intent_request, "Bitcoin")
	elif intent_name == 'EthereumWatchIntent':
		return make_watch(intent_request, "Ethereum")
	elif intent_name == 'LitecoinWatchIntent':
		return make_watch(intent_request, "Litecoin")
	elif intent_name == 'CryptoHelpIntent':
		return make_help(intent_request)
	elif intent_name == 'HelloIntent':
		return make_start(intent_request)
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
