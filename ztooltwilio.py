from twilio.rest import Client as TwilioClient

twilio_account_sid = "ACdd5f90bb78f848b59c13ca6f67eea150"
twilio_auth_token = "7dc8625cb72a3b821065d0284f46e3df"

twilio_client = TwilioClient(twilio_account_sid, twilio_auth_token)

phone = twilio_client.lookups.phone_numbers("6572005227").fetch()
print phone.phone_number
