import json
import os
from flask import request
from dotenv import load_dotenv
from datetime import datetime, timedelta
from modules.whatsapp.api import send_whatsapp_message, send_template
from modules.whatsapp.utils import validate_whatsapp_number, format_whatsapp_number, is_valid_phone_number
from modules.translation.api import detect_language, translate_text
from modules.CSVHandler import CSVHandler

# Cargar las variables de entorno
load_dotenv()

# Variables globales
current_to_number = None
current_to_language = None
current_to_iso_code = None

BUSINESS_OWNER_PHONE_NUMBER = os.getenv("BUSINESS_OWNER_PHONE_NUMBER")
BUSINESS_OWNER_LANGUAGE_NAME = os.getenv("BUSINESS_OWNER_LANGUAGE_NAME", "English")
CSV_FILEPATH = os.getenv("CSV_FILEPATH", "data.csv")

# Inicializar el manejador del CSV
csv_handler = CSVHandler.CSVHandler(CSV_FILEPATH)

def handle_incoming_message():
    """Función principal que maneja los mensajes entrantes."""
    global current_to_number, current_to_language, current_to_iso_code

    from_number = request.form.get('From')
    body = request.form.get('Body')

    # Verificar si el mensaje proviene del cliente o del propietario del negocio
    if from_number != BUSINESS_OWNER_PHONE_NUMBER:
        # Caso cliente: manejar mensajes de clientes
        handle_message(from_number, body, BUSINESS_OWNER_LANGUAGE_NAME, BUSINESS_OWNER_PHONE_NUMBER)
    else:
        # Caso propietario: manejar comandos y mensajes del propietario del negocio
        handle_owner_message(body)

    return "Message processed."


### Manejo de Mensajes del Propietario del Negocio (comandos especiales)

def handle_owner_message(body):
    """
    Maneja los mensajes enviados por el propietario del negocio.
    Solo el propietario puede ejecutar comandos como 'exit' o 'to:'.
    """
    global current_to_number, current_to_language, current_to_iso_code

    if body.strip().lower() == "exit":
        # Comando 'exit': Termina la sesión actual
        reset_current_user_session()
        send_message_to_owner("Session ended.")
    elif body.startswith("to:"):
        # Comando 'to:': Cambiar el destinatario actual
        update_current_to_number(body[3:].strip())
    elif current_to_number:
        # Si se ha establecido un destinatario, enviar el mensaje traducido al destinatario actual

        handle_message(BUSINESS_OWNER_PHONE_NUMBER, body, current_to_language, current_to_number)
    else:
        # No se ha establecido un destinatario
        send_message_to_owner("No destination number set.")


### Manejo de Mensajes Común

def handle_message(from_number, body, target_language, to_number):
    """
    Maneja los mensajes provenientes de un cliente o del propietario.
    Traduce el mensaje y lo envía al destinatario adecuado.
    """
    # Obtener el idioma del remitente y la última interacción
    language, iso_code, last_interaction = get_or_detect_language(from_number, body)

    # Actualizar la última interacción si es un cliente    
    csv_handler.update_last_interaction(from_number)

    # Verificar si han pasado más de 24 horas
    if should_send_template(last_interaction):
        send_template(to_number)
    else:
        # Enviar el mensaje traducido
        send_translated_message(body, language, target_language, from_number, to_number)


### Funciones comunes

def send_translated_message(body, source_language, target_language, from_number, to_number):
    """
    Traduce y envía un mensaje a través de WhatsApp.
    """
    translated_message = translate_message(body, source_language, target_language, from_number)
    send_whatsapp_message(translated_message, to_number)


def get_or_detect_language(from_number, body):
    """
    Recupera el idioma de un número de teléfono si existe en la base de datos.
    Si no, detecta el idioma del mensaje y lo agrega a la base de datos.
    """
    language, iso_code, last_interaction = csv_handler.get_language_for_number(from_number)

    if not language:
        detected_language_json = json.loads(detect_language(body))
        language = detected_language_json.get('language', 'English')
        iso_code = detected_language_json.get('ISO_639-1', 'en')
        csv_handler.add_number_language(from_number, language, iso_code)

    return language, iso_code, last_interaction


def should_send_template(last_interaction):
    """
    Verifica si han pasado más de 24 horas desde la última interacción.
    Si no existe interacción, asume que debe enviarse un template.
    """
    current_time = datetime.now().astimezone()

    if last_interaction is None:
        return True

    # Convertir last_interaction de cadena a objeto datetime
    try:
        if isinstance(last_interaction, str):
            # Usa fromisoformat para convertir el string ISO a datetime con zona horaria
            last_interaction = datetime.fromisoformat(last_interaction)
    except ValueError:
        # Si hay un error en la conversión, consideramos que deben pasar más de 24 horas
        return True

    # Calcula la diferencia de tiempo entre la hora actual y la última interacción
    time_difference = current_time - last_interaction

    # Verifica si han pasado más de 24 horas
    return time_difference >= timedelta(hours=24)


def translate_message(body, source_language, target_language, from_number):
    """
    Traduce un mensaje del idioma de origen al idioma de destino y lo devuelve como JSON.
    """
    translated_text = translate_text(body, source_language, target_language)
    translated_text_json = json.loads(translated_text)
    translated_text_json['from_number'] = from_number
    return translated_text_json


def send_message_to_owner(output_message):
    """
    Envía un mensaje al propietario del negocio.
    """
    translated_text_json = {"output": output_message}
    send_whatsapp_message(translated_text_json, BUSINESS_OWNER_PHONE_NUMBER)


def update_current_to_number(new_number):
    """
    Actualiza el número de destino actual.
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
    Reinicia la sesión de usuario actual.
    """
    global current_to_number, current_to_language, current_to_iso_code
    current_to_number = None
    current_to_language = None
    current_to_iso_code = None
