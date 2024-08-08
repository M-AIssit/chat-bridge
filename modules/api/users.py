from flask import request
from modules.whatsapp.api import send_whatsapp_message
from modules.whatsapp.utils import validate_whatsapp_number, format_whatsapp_number, is_valid_phone_number
from modules.translation.api import detect_language, translate_text
from modules.CSVHandler.CSVHandler import check_phone_number, add_phone_number
import json
import os
from dotenv import load_dotenv

# Cargar el archivo .env
load_dotenv()

# Variable global para almacenar el número de destino actual
current_to_number = None
BUSINESS_OWNER_PHONE_NUMBER = os.getenv("BUSINESS_OWNER_PHONE_NUMBER")

def create_user():
    global current_to_number

    # Extracción de datos del formulario de solicitud
    from_number = request.form.get('From')
    body = request.form.get('Body')

    # Registro de datos de entrada
    print("From Number:", from_number)
    print("Body:", body)

    # Comprobación de la información del teléfono en el CSV
    phone_info = check_phone_number(from_number)
    if not phone_info:
        detected_language_json = detect_language(body)
        try:
            detected_lang_data = json.loads(detected_language_json)
            if 'ISO 639-1' in detected_lang_data:
                add_phone_number(from_number, detected_lang_data['language'], detected_lang_data['ISO 639-1'])
                detected_language = detected_lang_data['language']
                iso_code = detected_lang_data['ISO 639-1']
            else:
                print("No ISO code provided in the language detection response.")
                return "Error handling request"
        except json.JSONDecodeError:
            print("Failed to decode the language detection response.")
            return "Error handling request"
    else:
        detected_language = phone_info['language']
        iso_code = phone_info['ISO 639-1']

    # Traducción del mensaje
    translated_text = translate_text(body, detected_language, iso_code)
    print("Detected Language:", detected_language)
    print("Translated Text:", translated_text)

    # Conversión del texto traducido a JSON y preparación para el envío
    translated_text_json = json.loads(translated_text)
    translated_text_json['from_number'] = from_number

    # Envío del mensaje traducido según la lógica de negocio
    if from_number != BUSINESS_OWNER_PHONE_NUMBER:
        send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)
    else:
        if body.strip().lower() == "exit":
            current_to_number = None
            translated_text_json['output'] = "Sesión terminada."
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
            translated_text_json['output'] = f"Número de destino actualizado a: {current_to_number}"
            send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)
        elif current_to_number:
            send_whatsapp_message(translated_text_json, current_to_number)
        else:
            translated_text_json['output'] = "No hay un número de destino establecido."
            send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)

    return "List of users"
