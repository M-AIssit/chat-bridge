import json
import os
from flask import request
from dotenv import load_dotenv
from datetime import datetime, timedelta
from modules.whatsapp.api import send_whatsapp_message, send_template
from modules.whatsapp.utils import validate_whatsapp_number, format_whatsapp_number, is_valid_phone_number
from modules.translation.api import detect_language, translate_text
from modules.CSVHandler import CSVHandler

# Load environment variables
load_dotenv()

# Global variables for storing the current destination number and language details
current_to_number = None
current_to_language = None
current_to_iso_code = None

BUSINESS_OWNER_PHONE_NUMBER = os.getenv("BUSINESS_OWNER_PHONE_NUMBER")
BUSINESS_OWNER_LANGUAGE_NAME = os.getenv("BUSINESS_OWNER_LANGUAGE_NAME", "English")
CSV_FILEPATH = os.getenv("CSV_FILEPATH", "data.csv")

# Initialize the CSV handler (using Supabase or similar database)
csv_handler = CSVHandler.CSVHandler(CSV_FILEPATH)

def handle_incoming_message():
    """Main function to handle incoming messages."""
    global current_to_number, current_to_language, current_to_iso_code

    from_number = request.form.get('From')
    body = request.form.get('Body')

    # Check if the message is from a customer or the business owner
    if from_number != BUSINESS_OWNER_PHONE_NUMBER:
        handle_message_from_customer(from_number, body)
    else:
        handle_message_from_owner(body)

    return "Message processed."


### Case 1: Handling messages from the customer

def handle_message_from_customer(from_number, body):
    """
    Handles messages coming from a customer.
    Translates the message and sends it to the business owner.
    """
    # Get the customer's language, ISO code, and last interaction
    language, iso_code, last_interaction = get_or_detect_language(from_number, body)

    # Translate the message to the business owner's language
    translated_message = translate_message(body, language, BUSINESS_OWNER_LANGUAGE_NAME, from_number)

    # Update the last interaction for the customer (only when they send a message)
    csv_handler.update_last_interaction(from_number)

    # Check if more than 24 hours have passed since the last interaction
    if should_send_template(last_interaction):
        # Send the template to the business owner
        send_template(BUSINESS_OWNER_PHONE_NUMBER)
    else:
        # Send the translated message to the business owner
        send_whatsapp_message(translated_message, BUSINESS_OWNER_PHONE_NUMBER)


### Case 2: Handling messages from the business owner

def handle_message_from_owner(body):
    """
    Handles messages coming from the business owner.
    Can execute special commands like 'exit' or 'to:' or send translated messages.
    """
    global current_to_number, current_to_language, current_to_iso_code

    if body.strip().lower() == "exit":
        # Command 'exit': End the current session
        reset_current_user_session()
        send_message_to_owner("Session ended.")
    elif body.startswith("to:"):
        # Command 'to:': Change the current recipient
        update_current_to_number(body[3:].strip())
    elif current_to_number:
        # Send the translated message to the current recipient
        handle_owner_message_to_customer(body)
    else:
        # No recipient set
        send_message_to_owner("No destination number set.")


def handle_owner_message_to_customer(body):
    """
    Translates and sends the business owner's message to the current customer.
    """
    if current_to_language and current_to_iso_code:
        # Check if more than 24 hours have passed since the last interaction
        last_interaction = csv_handler.get_last_interaction(current_to_number)
        if should_send_template(last_interaction):
            # Send the template if more than 24 hours have passed
            send_template(current_to_number)
        else:
            # Send the translated message to the customer (no update to last_interaction here)
            translated_message = translate_message(body, BUSINESS_OWNER_LANGUAGE_NAME, current_to_language, BUSINESS_OWNER_PHONE_NUMBER)
            send_whatsapp_message(translated_message, current_to_number)
    else:
        send_message_to_owner("Could not determine the recipient's language.")


### Helper functions

def get_or_detect_language(from_number, body):
    """
    Retrieves the language of a phone number if it exists in the database.
    If not, detects the language from the message and adds it to the database.
    """
    language, iso_code, last_interaction = csv_handler.get_language_for_number(from_number)

    if not language:
        # Detect the language from the message and add it to the database
        detected_language_json = json.loads(detect_language(body))
        language = detected_language_json.get('language', 'English')
        iso_code = detected_language_json.get('ISO_639-1', 'en')
        csv_handler.add_number_language(from_number, language, iso_code)

    return language, iso_code, last_interaction


def should_send_template(last_interaction):
    """
    Checks if more than 24 hours have passed since the last interaction.
    If no interaction exists, assumes that a template should be sent.
    """
    current_time = datetime.now().astimezone()

    if last_interaction is None:
        return True  # No prior interaction, send template

    if isinstance(last_interaction, str):
        last_interaction = datetime.fromisoformat(last_interaction)

    time_difference = current_time - last_interaction
    return time_difference >= timedelta(hours=24)


def translate_message(body, source_language, target_language, from_number):
    """
    Translates a message from the source language to the target language and returns it as JSON.
    """
    translated_text = translate_text(body, source_language, target_language)
    translated_text_json = json.loads(translated_text)
    translated_text_json['from_number'] = from_number
    return translated_text_json


def send_message_to_owner(output_message):
    """
    Sends a message to the business owner.
    """
    translated_text_json = {"output": output_message}
    send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)


def update_current_to_number(new_number):
    """
    Updates the current destination number.
    """
    global current_to_number, current_to_language, current_to_iso_code

    if not validate_whatsapp_number(new_number):
        if not is_valid_phone_number(new_number):
            raise ValueError("Invalid phone number")
        current_to_number = format_whatsapp_number(new_number)
    else:
        current_to_number = new_number

    current_to_language, current_to_iso_code, _ = csv_handler.get_language_for_number(current_to_number)
    send_message_to_owner(f"Destination number updated to: {current_to_number}")


def reset_current_user_session():
    """
    Resets the current user session.
    """
    global current_to_number, current_to_language, current_to_iso_code
    current_to_number = None
    current_to_language = None
    current_to_iso_code = None
