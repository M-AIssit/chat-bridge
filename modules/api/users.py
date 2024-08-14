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

# Variables globales para almacenar el número de destino actual y su idioma
current_to_number = None
current_to_language = None
current_to_iso_code = None

BUSINESS_OWNER_PHONE_NUMBER = os.getenv("BUSINESS_OWNER_PHONE_NUMBER")
BUSINESS_OWNER_LANGUAGE_NAME = os.getenv("BUSINESS_OWNER_LANGUAGE_NAME", "Spanish")
BUSINESS_OWNER_LANGUAGE_CODE = os.getenv("BUSINESS_OWNER_LANGUAGE_CODE", "es")
CSV_FILEPATH = os.getenv("CSV_FILEPATH", "data.csv")

# Inicializar el manejador del CSV
csv_handler = CSVHandler.CSVHandler(CSV_FILEPATH)

def create_user():
    global current_to_number, current_to_language, current_to_iso_code

    from_number = request.form.get('From')
    body = request.form.get('Body')

    if from_number != BUSINESS_OWNER_PHONE_NUMBER:
        # El mensaje viene del cliente, procesar normalmente
        language, iso_code = csv_handler.get_language_for_number(from_number)
        if not language:
            # Si no está, detectar el idioma y agregarlo al CSV
            detected_language_json = json.loads(detect_language(body))
            language = detected_language_json.get('language', 'English')
            iso_code = detected_language_json.get('ISO_639-1', 'en')
            csv_handler.add_number_language(from_number, language, iso_code)
        print("Detected Language:", language, "ISO 639-1:", iso_code)

        # Traducir el cuerpo del mensaje al idioma del propietario del negocio
        translated_text = translate_text(body, language, BUSINESS_OWNER_LANGUAGE_NAME, iso_code, BUSINESS_OWNER_LANGUAGE_CODE)
        print("Translated Text:", translated_text)

        # Convertir el texto traducido a formato JSON
        translated_text_json = json.loads(translated_text)
        translated_text_json['from_number'] = from_number

        translated_text_json['output'] = translated_text_json.get('translated_text', '')  # Asegurarse de que 'output' esté presente
        send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)

    else:
        # El mensaje viene del propietario del negocio
        if body.strip().lower() == "exit":
            current_to_number = None
            current_to_language = None
            current_to_iso_code = None
            translated_text_json = {
                'from_number': BUSINESS_OWNER_PHONE_NUMBER,
                'output': "Sesión terminada."
            }
            send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)
        elif body.startswith("to:"):
            # Asignar nuevo destinatario
            preformatted_current_to_number = body[3:].strip()
            if not validate_whatsapp_number(preformatted_current_to_number):
                if not is_valid_phone_number(preformatted_current_to_number):
                    raise ValueError("Invalid phone number")
                current_to_number = format_whatsapp_number(preformatted_current_to_number)
            else:
                current_to_number = preformatted_current_to_number

            # Recuperar y almacenar el idioma y el código ISO del destinatario
            current_to_language, current_to_iso_code = csv_handler.get_language_for_number(current_to_number)
            if not current_to_language:
                raise ValueError(f"Language for number {current_to_number} not found in CSV.")
            print(f"Nuevo número de destino asignado: {current_to_number}, Idioma: {current_to_language}, ISO: {current_to_iso_code}")

            translated_text_json = {
                'from_number': BUSINESS_OWNER_PHONE_NUMBER,
                'output': f"Número de destino actualizado a: {current_to_number}"
            }
            send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)
        elif current_to_number:
            # Traducir y enviar el mensaje al idioma del destinatario actual
            translated_text = translate_text(body, BUSINESS_OWNER_LANGUAGE_NAME, current_to_language, BUSINESS_OWNER_LANGUAGE_CODE, current_to_iso_code)
            translated_text_json = json.loads(translated_text)
            translated_text_json['from_number'] = BUSINESS_OWNER_PHONE_NUMBER
            translated_text_json['output'] = translated_text_json.get('translated_text', '')  # Asegurarse de que 'output' esté presente
            send_whatsapp_message(translated_text_json, current_to_number)
        else:
            translated_text_json = {
                'from_number': BUSINESS_OWNER_PHONE_NUMBER,
                'output': "No hay un número de destino establecido."
            }
            send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)

    return "List of users"
