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

# Global variable to store the current destination number
current_to_number = None
BUSINESS_OWNER_PHONE_NUMBER = os.getenv("BUSINESS_OWNER_PHONE_NUMBER")
BUSINESS_OWNER_LANGUAGE_NAME = os.getenv("BUSINESS_OWNER_LANGUAGE_NAME", "English")  # Default language of the business owner
BUSINESS_OWNER_LANGUAGE_CODE = os.getenv("BUSINESS_OWNER_LANGUAGE_CODE", "en")  # ISO code of the business owner's language
CSV_FILEPATH = os.getenv("CSV_FILEPATH", "data.csv")  # Path to the CSV

# Initialize the CSV handler
csv_handler = CSVHandler.CSVHandler(CSV_FILEPATH)

def create_user():
    global current_to_number

    message_sid = request.form.get('MessageSid')
    from_number = request.form.get('From')
    body = request.form.get('Body')
    print("Message SID:", message_sid)
    print("From Number:", from_number)
    print("Body:", body)

    # Ensure number format includes "whatsapp:" prefix
    formatted_from_number = format_whatsapp_number(from_number) if not from_number.startswith('whatsapp:') else from_number

    if formatted_from_number != BUSINESS_OWNER_PHONE_NUMBER:
        # Check if the phone number is already in the CSV
        language, iso_code = csv_handler.get_language_for_number(formatted_from_number)
        if not language:
            detected_language_json = json.loads(detect_language(body))
            language = detected_language_json.get('language', 'English')
            iso_code = detected_language_json.get('ISO 639-1', 'en')
            csv_handler.add_number_language(formatted_from_number, language, iso_code)
        print("Detected Language:", language, "ISO 639-1:", iso_code)

        # Translate the body of the message to the business owner's language
        translated_text = translate_text(body, iso_code, BUSINESS_OWNER_LANGUAGE_CODE)
    else:
        # Handle messages from the business owner
        if body.strip().lower().startswith("to:"):
            potential_new_to_number = format_whatsapp_number(body[3:].strip())
            recipient_language, recipient_iso_code = csv_handler.get_language_for_number(potential_new_to_number)
            if not recipient_language:
                # Default to business owner's language if not found
                recipient_language = BUSINESS_OWNER_LANGUAGE_NAME
                recipient_iso_code = BUSINESS_OWNER_LANGUAGE_CODE
            current_to_number = potential_new_to_number
            print(f"Destination number updated to: {current_to_number} with default language settings.")
        else:
            recipient_language, recipient_iso_code = csv_handler.get_language_for_number(current_to_number)
            if not recipient_language:
                recipient_language = BUSINESS_OWNER_LANGUAGE_NAME
                recipient_iso_code = BUSINESS_OWNER_LANGUAGE_CODE
        translated_text = translate_text(body, BUSINESS_OWNER_LANGUAGE_CODE, recipient_iso_code)

    print("Translated Text:", translated_text)

    # Convert the translated text to JSON format
    translated_text_json = json.loads(translated_text)
    translated_text_json['from_number'] = from_number

    print("Translated Text JSON:", translated_text_json)

    if formatted_from_number != BUSINESS_OWNER_PHONE_NUMBER:
        send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)
    else:
        if body.strip().lower() == "exit":
            current_to_number = None
            translated_text_json['output'] = "Session ended."
            send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)
        elif body.startswith("to:"):
            preformatted_current_to_number = format_whatsapp_number(body[3:].strip())
            if not validate_whatsapp_number(preformatted_current_to_number):
                print("Invalid phone -> to")
                if not is_valid_phone_number(preformatted_current_to_number):
                    raise ValueError("Invalid phone number")
                current_to_number = preformatted_current_to_number
                print('to after format', current_to_number)
            else:
                current_to_number = preformatted_current_to_number
            translated_text_json['output'] = f"Current destination number updated to: {current_to_number}"
            send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)
        elif current_to_number:
            send_whatsapp_message(translated_text_json, current_to_number)
        else:
            translated_text_json['output'] = "No destination number set."
            send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)

    return "List of users"
