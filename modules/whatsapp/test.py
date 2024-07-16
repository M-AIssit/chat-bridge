import unittest
from .utils import validate_whatsapp_number, format_whatsapp_number, is_valid_phone_number

class TestWhatsAppUtils(unittest.TestCase):
    def test_validate_whatsapp_number_valid(self):
        self.assertTrue(validate_whatsapp_number("whatsapp:+12345678901"))

    def test_validate_whatsapp_number_invalid(self):
        self.assertFalse(validate_whatsapp_number("whatsapp:12345678901"))
        self.assertFalse(validate_whatsapp_number("+12345678901"))
        #self.assertFalse(validate_whatsapp_number("whatsapp:+123"))

    def test_format_whatsapp_number(self):
        formatted_number = format_whatsapp_number("+12345678901")
        self.assertEqual(formatted_number, "whatsapp:+12345678901")

    def test_is_valid_phone_number_valid(self):
        self.assertTrue(is_valid_phone_number("+12345678901"))

    def test_is_valid_phone_number_invalid(self):
        self.assertFalse(is_valid_phone_number("12345678901"))
        self.assertFalse(is_valid_phone_number("+1"))

if __name__ == '__main__':
    unittest.main()