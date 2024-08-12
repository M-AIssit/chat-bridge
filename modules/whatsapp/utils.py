import re
import phonenumbers

def validate_whatsapp_number(number):
    pattern = r'^whatsapp:\+\d{10,15}$'  # Ajusta la longitud según sea necesario
    return re.match(pattern, number) is not None
def format_whatsapp_number(number):
    # Eliminar el prefijo si ya está presente para manejar el número puro
    if number.startswith('whatsapp:'):
        number = number.split(':', 1)[1]
    
    # Añadir el '1' a los números mexicanos si es necesario
    if number.startswith('+521'):
        return f"whatsapp:{number}"
    elif number.startswith('+52') and not number.startswith('+521'):
        return f"whatsapp:+521{number[3:]}"
    else:
        return f"whatsapp:{number}"
    
def is_valid_phone_number(number):
    try:
        parsed_number = phonenumbers.parse(number, None)
        return phonenumbers.is_valid_number(parsed_number)
    except phonenumbers.phonenumberutil.NumberParseException:
        return False
    