import boto3
sns_access_key = "AKIAIJF4VTPQVCSIIURQ"
sns_access_secret = "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"
sns_client = boto3.client(
	"sns",
	aws_access_key_id=sns_access_key,
	aws_secret_access_key=sns_access_secret,
	region_name="us-east-1"
)
phone_number = "+13235401789"

sns_client.publish(PhoneNumber = phone_number, Message = "Testing Sending SMS")