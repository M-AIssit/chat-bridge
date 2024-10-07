import json
import os
from flask import request
from dotenv import load_dotenv
from datetime import datetime, timedelta
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
BUSINESS_OWNER_LANGUAGE_NAME = os.getenv("BUSINESS_OWNER_LANGUAGE_NAME", "English")
CSV_FILEPATH = os.getenv("CSV_FILEPATH", "data.csv")

# Inicializar el manejador del CSV
csv_handler = CSVHandler.CSVHandler(CSV_FILEPATH)

def create_user():
    global current_to_number, current_to_language, current_to_iso_code

    from_number = request.form.get('From')
    body = request.form.get('Body')

    # Verificar si el número de teléfono ya está en el CSV
    language, iso_code, last_interaction = csv_handler.get_language_for_number(from_number) 
    if not language:
        # Si no está, detectar el idioma y agregarlo al CSV
        detected_language_json = json.loads(detect_language(body))
        language = detected_language_json.get('language', 'English')
        iso_code = detected_language_json.get('ISO_639-1', 'en')
        csv_handler.add_number_language(from_number, language, iso_code)
    print("Detected Language:", language, "ISO 639-1:", iso_code)

    # Traducir el cuerpo del mensaje al idioma del propietario del negocio
    translated_text = translate_text(body, language, BUSINESS_OWNER_LANGUAGE_NAME)
    print("Translated Text:", translated_text)

    # Convertir el texto traducido a formato JSON
    translated_text_json = json.loads(translated_text)
    translated_text_json['from_number'] = from_number

    ##
    if has_24_hours_passed(last_interaction):
        ## Here we send a template or special message
        print("More than 24 hours has passed since the last message from: ", from_number)
    else :
        csv_handler.update_last_interaction(from_number)
    ##

    if from_number != BUSINESS_OWNER_PHONE_NUMBER:
        # Caso 1: El mensaje no es de BUSINESS_OWNER_PHONE_NUMBER
        send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)
    else:
        # Caso 2: El mensaje es de BUSINESS_OWNER_PHONE_NUMBER
        if body.strip().lower() == "exit":
            current_to_number = None
            current_to_language = None
            current_to_iso_code = None
            translated_text_json['output'] = "Sesión terminada."
            send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)
        elif body.startswith("to:"):
            preformatted_current_to_number = body[3:].strip()

            if not validate_whatsapp_number(preformatted_current_to_number):
                if not is_valid_phone_number(preformatted_current_to_number):
                    raise ValueError("Invalid phone number")
                current_to_number = format_whatsapp_number(preformatted_current_to_number)
            else:
                current_to_number = preformatted_current_to_number

            # Recuperar y almacenar el idioma y el código ISO del destinatario
            current_to_language, current_to_iso_code, last_interaction = csv_handler.get_language_for_number(current_to_number)
            print(f"Nuevo número de destino asignado: {current_to_number}, Idioma: {current_to_language}, ISO: {current_to_iso_code}")
            translated_text_json['output'] = f"Número de destino actualizado a: {current_to_number}"
            send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)
        elif current_to_number:
            # Utilizar el idioma y código ISO almacenado para traducir y enviar el mensaje
            if current_to_language and current_to_iso_code:
                translated_text = translate_text(body, BUSINESS_OWNER_LANGUAGE_NAME, current_to_language)
                translated_text_json = json.loads(translated_text)
                translated_text_json['from_number'] = BUSINESS_OWNER_PHONE_NUMBER
                send_whatsapp_message(translated_text_json, current_to_number)
            else:
                translated_text_json['output'] = "No se pudo determinar el idioma del destinatario."
                send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)
        else:
            translated_text_json['output'] = "No hay un número de destino establecido."
            send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)

    return "List of users"


def has_24_hours_passed(last_interaction):
    # Get the current timestamp with timezone
    current_time = datetime.now().astimezone()

    # Calculate the time difference between current time and last interaction
    time_difference = current_time - last_interaction

    # Check if the difference is greater than or equal to 24 hours
    if time_difference >= timedelta(hours=24):
        return True
    return False