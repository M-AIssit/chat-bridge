
from .constants import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, TWILIO_MESSAGING_SERVICE_ID
from twilio.rest import Client
from .utils import validate_whatsapp_number, format_whatsapp_number, is_valid_phone_number


def send_whatsapp_message(body, to, from_=TWILIO_PHONE_NUMBER):
    # Asegurarse de que el número esté formateado correctamente antes de validar
    formatted_to = format_whatsapp_number(to)

    if not validate_whatsapp_number(formatted_to):
        print("Invalid phone -> to")
        raise ValueError("Invalid phone number")
    
    message = body['output']
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        from_=from_,
        body=message,
        to=formatted_to,  # Utiliza el número formateado
    )
    print(message.body)

