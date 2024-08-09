import unittest
import os
import sys

# Añadir el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.CSVHandler import CSVHandler

class TestCSVHandler(unittest.TestCase):

    def setUp(self):
        # Crear un archivo CSV temporal para las pruebas
        self.test_file = 'test_data.csv'
        self.csv_handler = CSVHandler.CSVHandler(self.test_file)
        # Asegurarse de que el archivo está inicializado
        self.csv_handler.initialize_csv()

    def tearDown(self):
        # Eliminar el archivo CSV después de las pruebas
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_initialize_csv(self):
        # Verificar que el archivo CSV se crea correctamente
        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file, 'r') as file:
            headers = file.readline().strip()
            self.assertEqual(headers, 'Phone_number,Language,ISO_639-1')

    def test_add_number_language(self):
        # Añadir un número y verificar que se guarde correctamente
        self.csv_handler.add_number_language('whatsapp:+1234567890', 'Spanish', 'es')
        data = self.csv_handler.read_csv()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['Phone_number'], 'whatsapp:+1234567890')
        self.assertEqual(data[0]['Language'], 'Spanish')
        self.assertEqual(data[0]['ISO_639-1'], 'es')

    def test_get_language_for_number(self):
        # Añadir y luego recuperar un número
        self.csv_handler.add_number_language('whatsapp:+1234567890', 'Spanish', 'es')
        language, iso_code = self.csv_handler.get_language_for_number('whatsapp:+1234567890')
        self.assertEqual(language, 'Spanish')
        self.assertEqual(iso_code, 'es')

    def test_update_language_for_number(self):
        # Añadir un número, actualizar su idioma y verificar
        self.csv_handler.add_number_language('whatsapp:+1234567890', 'Spanish', 'es')
        updated = self.csv_handler.update_language_for_number('whatsapp:+1234567890', 'French', 'fr')
        self.assertTrue(updated)
        language, iso_code = self.csv_handler.get_language_for_number('whatsapp:+1234567890')
        self.assertEqual(language, 'French')
        self.assertEqual(iso_code, 'fr')

    def test_cache_invalidation_on_write(self):
        # Verificar que el cache se invalide después de escribir
        self.csv_handler.add_number_language('whatsapp:+1234567890', 'Spanish', 'es')
        self.csv_handler.add_number_language('whatsapp:+0987654321', 'French', 'fr')
        data = self.csv_handler.read_csv()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[1]['Language'], 'French')

if __name__ == '__main__':
    unittest.main()
