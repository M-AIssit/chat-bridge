
from .constants import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, JAVIER_PHONE_NUMBER, CARLOS_PHONE_NUMBER, USA_PHONE_NUMBER, TWILIO_PHONE_NUMBER
from twilio.rest import Client
from .utils import validate_whatsapp_number, format_whatsapp_number, is_valid_phone_number


def send_whatsapp_message(body, to, from_=TWILIO_PHONE_NUMBER):
    
    if not validate_whatsapp_number(to):    
        print("Invalid phone -> to")
        if not is_valid_phone_number(to):
            raise ValueError("Invalid phone number")
        to = format_whatsapp_number(to)
        print('to after format', to)

    if to.startswith('whatsapp:+52'):
        print('to starts with +52')
        to = 'whatsapp:+521' + to[12:]
        print('to after format', to)

    # Extract 'output' attribute from body_json into a message var
    message = body['output']

    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        from_=from_,    #"whatsapp:+14155238886"
        body=message,
        to=to,          #"whatsapp:+14155238884"
    )
    print(message.body)

            # def is_my_own_number(phone_number):
            #     return phone_number == USA_PHONE_NUMBER

            # def is_javier(from_):
            #     print("is_javier")
            #     print(from_)   
            #     if not validate_whatsapp_number(from_):
            #         print("Invalid phone -> from")
            #         if not is_valid_phone_number(from_):
            #             raise ValueError("Invalid phone number")
            #         from_ = format_whatsapp_number(from_)
            #     print(JAVIER_PHONE_NUMBER)
            #     result = from_ == 'whatsapp:+34645630311'
            #     print(result)
            #     return result

            # def is_carlos(from_):
            #     print("is_carlos")
            #     print(from_)
            #     if not validate_whatsapp_number(from_):
            #         print("Invalid phone -> from")
            #         if not is_valid_phone_number(from_):
            #             raise ValueError("Invalid phone number")
            #         from_ = format_whatsapp_number(from_)
            #     print(CARLOS_PHONE_NUMBER)
            #     result = from_ == CARLOS_PHONE_NUMBER
            #     print(result)
            #     return result


