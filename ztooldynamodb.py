import boto3
from random import randint

sns_access_key = "AKIAIJF4VTPQVCSIIURQ"
sns_access_secret = "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"
dynamodb = boto3.resource(
	"dynamodb",
	aws_access_key_id=sns_access_key,
	aws_secret_access_key=sns_access_secret,
	region_name="us-east-1"
)
phone_number = "+13235401789"

def random_with_N_digits(n):
	range_start = 10**(n-1)
	range_end = (10**n)-1
	return str(randint(range_start, range_end))

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
	token = random_with_N_digits(5)
	send_sms(phone, "Token is {}".format(token))
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

print verify_user_phone_with_token('John', '+13235401789', '12345')
print verify_user_phone_with_token('JohnO', '+13235401789', '12345')
print verify_user_phone_with_token('John', '+132354017890', '12345')
print verify_user_phone_with_token('John', '+13235401789', '54443')

# start_phone_verification("+13235401789", "John")