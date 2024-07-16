import re
import phonenumbers

def validate_whatsapp_number(number):
    pattern = r'^whatsapp:\+\d+$'
    return re.match(pattern, number) is not None

def format_whatsapp_number(number):
    return f"whatsapp:{number}"

def is_valid_phone_number(number):
    try:
        parsed_number = phonenumbers.parse(number, None)
        return phonenumbers.is_valid_number(parsed_number)
    except phonenumbers.phonenumberutil.NumberParseException:
        return False
    