from flask import request
from modules.whatsapp.api import send_whatsapp_message
from modules.whatsapp.utils import validate_whatsapp_number, format_whatsapp_number, is_valid_phone_number
from modules.translation.api import detect_language, translate_text
import json

import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Variable global para almacenar el número de destino actual
current_to_number = None
BUSINESS_OWNER_PHONE_NUMBER = os.getenv("BUSINESS_OWNER_PHONE_NUMBER")

def create_user():
    global current_to_number

    message_sid = request.form.get('MessageSid')
    sms_sid = request.form.get('SmsSid')
    sms_message_sid = request.form.get('SmsMessageSid')
    account_sid = request.form.get('AccountSid')
    messaging_service_sid = request.form.get('MessagingServiceSid')
    from_number = request.form.get('From')
    to_number = request.form.get('To')
    body = request.form.get('Body')
    num_media = request.form.get('NumMedia')
    num_segments = request.form.get('NumSegments')
    print("Message SID:", message_sid)
    print("SMS SID:", sms_sid)
    print("SMS Message SID:", sms_message_sid)
    print("Account SID:", account_sid)
    print("Messaging Service SID:", messaging_service_sid)
    print("From Number:", from_number)
    print("To Number:", to_number)
    print("Body:", body)
    print("Number of Media:", num_media)
    print("Number of Segments:", num_segments)

    # Call the detect_language function here
    detected_language = detect_language(body)
    print("Detected Language:", detected_language)

    # Translate the body of the message to a different language
    translated_text = translate_text(body, detected_language, 'en')
    print("Translated Text:", translated_text)

    # Convert the translated text to JSON format
    translated_text_json = json.loads(translated_text)
    # Add the 'from_number' to the translated text JSON
    translated_text_json['from_number'] = from_number

    # Print the translated text JSON
    print("Translated Text JSON:", translated_text_json)


    if from_number != BUSINESS_OWNER_PHONE_NUMBER:
        # Caso 1: El mensaje no es de BUSINESS_OWNER_PHONE_NUMBER
        send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)
    else:
        # Caso 2: El mensaje es de PRIMARY_NUMBER
        if body.strip().lower() == "exit":
            current_to_number = None
            translated_text_json ['output'] = "Sesión terminada."
            send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)
        elif body.startswith("to:"):
            preformatted_current_to_number = body[3:].strip()

            if not validate_whatsapp_number(preformatted_current_to_number):    
                print("Invalid phone -> to")
                if not is_valid_phone_number(preformatted_current_to_number):
                    raise ValueError("Invalid phone number")
                current_to_number = format_whatsapp_number(preformatted_current_to_number)
                print('to after format', current_to_number)
            else:
                current_to_number = preformatted_current_to_number

            translated_text_json ['output'] = f"Número de destino actualizado a: {current_to_number}"
            send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)
        elif current_to_number:
            
            send_whatsapp_message(translated_text_json, current_to_number)
        else:
            translated_text_json ['output'] = "No hay un número de destino establecido."
            send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)
         

    return "List of users"
