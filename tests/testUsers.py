import os
import sys

# Añadir el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, request
import json
from modules.api import users

class TestCreateUser(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)

    @patch('modules.api.users.send_whatsapp_message')
    @patch('modules.api.users.translate_text')
    @patch('modules.api.users.detect_language')
    @patch('modules.api.users.csv_handler.get_language_for_number')
    @patch('modules.api.users.csv_handler.add_number_language')
    def test_create_user_new_number(self, mock_add_number_language, mock_get_language_for_number, mock_detect_language, mock_translate_text, mock_send_whatsapp_message):
        with self.app.test_request_context('/create_user', method='POST', data={
            'From': 'whatsapp:+1234567890',
            'Body': 'Hello'
        }):

            # Configurar los mocks
            mock_get_language_for_number.return_value = (None, None)
            mock_detect_language.return_value = json.dumps({'language': 'Spanish', 'ISO_639-1': 'es'})
            mock_translate_text.return_value = json.dumps({'translated_text': 'Hola'})
            mock_send_whatsapp_message.return_value = None

            # Ejecutar el método
            response = users.create_user()

            # Verificar que se detectó el idioma y se añadió al CSV
            mock_detect_language.assert_called_once_with('Hello')
            mock_add_number_language.assert_called_once_with('whatsapp:+1234567890', 'Spanish', 'es')

            # Verificar la traducción
            mock_translate_text.assert_called_once_with('Hello', 'Spanish', 'English')
            mock_send_whatsapp_message.assert_called_once()
            self.assertEqual(response, "List of users")

    @patch('modules.api.users.send_whatsapp_message')
    @patch('modules.api.users.translate_text')
    @patch('modules.api.users.csv_handler.get_language_for_number')
    def test_create_user_existing_number(self, mock_get_language_for_number, mock_translate_text, mock_send_whatsapp_message):
        with self.app.test_request_context('/create_user', method='POST', data={
            'From': 'whatsapp:+1234567890',
            'Body': 'Hello'
        }):

            # Configurar los mocks
            mock_get_language_for_number.return_value = ('Spanish', 'es')
            mock_translate_text.return_value = json.dumps({'translated_text': 'Hola'})
            mock_send_whatsapp_message.return_value = None

            # Ejecutar el método
            response = users.create_user()

            # Verificar la traducción
            mock_translate_text.assert_called_once_with('Hello', 'Spanish', 'English')
            mock_send_whatsapp_message.assert_called_once()
            self.assertEqual(response, "List of users")

    @patch('modules.api.users.send_whatsapp_message')
    @patch('modules.api.users.csv_handler.get_language_for_number')
    def test_create_user_command_to(self, mock_get_language_for_number, mock_send_whatsapp_message):
        with self.app.test_request_context('/create_user', method='POST', data={
            'From': 'whatsapp:+0987654321',
            'Body': 'to:+1234567890'
        }):

            # Configurar los mocks
            mock_get_language_for_number.side_effect = [
                ('Spanish', 'es'),  # Para el número desde el que se envía
                ('Spanish', 'es')   # Para el número al que se está configurando el `to`
            ]
            mock_send_whatsapp_message.return_value = None

            # Ejecutar el método
            response = users.create_user()

            # Verificar que se estableció el número de destino correctamente
            mock_get_language_for_number.assert_any_call('whatsapp:+1234567890')
            mock_send_whatsapp_message.assert_called_once()
            self.assertEqual(response, "List of users")

    @patch('modules.api.users.send_whatsapp_message')
    @patch('modules.api.users.csv_handler.get_language_for_number')
    def test_create_user_command_exit(self, mock_get_language_for_number, mock_send_whatsapp_message):
        with self.app.test_request_context('/create_user', method='POST', data={
            'From': 'whatsapp:+0987654321',
            'Body': 'exit'
        }):

            # Configurar los mocks
            mock_get_language_for_number.return_value = ('Spanish', 'es')
            mock_send_whatsapp_message.return_value = None

            # Ejecutar el método
            response = users.create_user()

            # Verificar que se reinició el número de destino
            mock_send_whatsapp_message.assert_called_once()
            self.assertEqual(response, "List of users")

    @patch('modules.api.users.send_whatsapp_message')
    @patch('modules.api.users.translate_text')
    @patch('modules.api.users.csv_handler.get_language_for_number')
    def test_create_user_send_message_to_assigned_number(self, mock_get_language_for_number, mock_translate_text, mock_send_whatsapp_message):
        with self.app.test_request_context('/create_user', method='POST', data={
            'From': 'whatsapp:+0987654321',
            'Body': 'Message after to: command'
        }):

            # Configurar los mocks
            mock_get_language_for_number.return_value = ('Spanish', 'es')
            mock_translate_text.return_value = json.dumps({'translated_text': 'Mensaje después del comando to:'})
            mock_send_whatsapp_message.return_value = None

            # Establecer un número de destino simulado
            users.current_to_number = 'whatsapp:+1234567890'
            users.current_to_language = 'Spanish'
            users.current_to_iso_code = 'es'

            # Ejecutar el método
            response = users.create_user()

            # Verificar la traducción y envío del mensaje
            mock_translate_text.assert_called_once_with('Message after to: command', 'English', 'Spanish')
            mock_send_whatsapp_message.assert_called_once()
            self.assertEqual(response, "List of users")

if __name__ == '__main__':
    unittest.main()
