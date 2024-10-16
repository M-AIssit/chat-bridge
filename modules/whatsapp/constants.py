import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Twilio API credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
JAVIER_PHONE_NUMBER = os.getenv("JAVIER_PHONE_NUMBER")
CARLOS_PHONE_NUMBER = os.getenv("CARLOS_PHONE_NUMBER")
USA_PHONE_NUMBER = os.getenv("USA_PHONE_NUMBER")
BUSINESS_OWNER_PHONE_NUMBER = os.getenv("BUSINESS_OWNER_PHONE_NUMBER")