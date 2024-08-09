import json
import os
from flask import request
from dotenv import load_dotenv
from modules.whatsapp.api import send_whatsapp_message
from modules.whatsapp.utils import validate_whatsapp_number, format_whatsapp_number, is_valid_phone_number
from modules.translation.api import detect_language, translate_text
from modules.CSVHandler import CSVHandler

# Load the .env file
load_dotenv()

# Global variables to store the current destination number and language details
current_to_number = None
current_to_language = None
current_to_iso_code = None

BUSINESS_OWNER_PHONE_NUMBER = os.getenv("BUSINESS_OWNER_PHONE_NUMBER")
BUSINESS_OWNER_LANGUAGE_NAME = os.getenv("BUSINESS_OWNER_LANGUAGE_NAME", "English")  # Default language of the business owner
BUSINESS_OWNER_LANGUAGE_CODE = os.getenv("BUSINESS_OWNER_LANGUAGE_CODE", "en")  # ISO code of the business owner's language
CSV_FILEPATH = os.getenv("CSV_FILEPATH", "data.csv")  # Path to the CSV

# Initialize the CSV handler
csv_handler = CSVHandler.CSVHandler(CSV_FILEPATH)

def create_user():
    global current_to_number, current_to_language, current_to_iso_code

    from_number = request.form.get('From')
    body = request.form.get('Body')
    print("From Number:", from_number)
    print("Body:", body)

    # Ensure number format includes "whatsapp:" prefix
    formatted_from_number = format_whatsapp_number(from_number) if not from_number.startswith('whatsapp:') else from_number

    if formatted_from_number != BUSINESS_OWNER_PHONE_NUMBER:
        # Check if the phone number is already in the CSV
        language, iso_code = csv_handler.get_language_for_number(formatted_from_number)
        if not language:
            # Detect language and save to CSV if not present
            detected_language_json = json.loads(detect_language(body))
            language = detected_language_json.get('language', 'English')
            iso_code = detected_language_json.get('ISO 639-1', 'en')
            csv_handler.add_number_language(formatted_from_number, language, iso_code)
        print("Detected Language:", language, "ISO 639-1:", iso_code)

        # Translate the body of the message to the business owner's language
        translated_text = translate_text(body, iso_code, BUSINESS_OWNER_LANGUAGE_CODE)
        send_whatsapp_message(translated_text, BUSINESS_OWNER_PHONE_NUMBER)
    else:
        # Handle messages from the business owner
        if body.strip().lower().startswith("to:"):
            potential_new_to_number = format_whatsapp_number(body[3:].strip())
            recipient_language, recipient_iso_code = csv_handler.get_language_for_number(potential_new_to_number)
            if recipient_language:
                current_to_number = potential_new_to_number
                current_to_language = recipient_language
                current_to_iso_code = recipient_iso_code
                print(f"Destination number updated to: {current_to_number} with language settings: {recipient_language}")
            else:
                print("No language data found for the number.")
                return "No language data found for the number."
        elif current_to_number:
            # Translate and send the owner's message to the current destination number
            translated_text = translate_text(body, BUSINESS_OWNER_LANGUAGE_CODE, current_to_iso_code)
            send_whatsapp_message(translated_text, current_to_number)
        else:
            print("No destination number set.")
            return "No destination number set."

    return "Operation completed successfully."
