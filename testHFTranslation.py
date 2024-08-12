import unittest
from modules.translation.hf_translation import HuggingFaceTranslator

class TestHuggingFaceTranslator(unittest.TestCase):
    def setUp(self):
        # Inicializa el traductor antes de cada prueba.
        self.translator = HuggingFaceTranslator()

    def test_translation_en_es(self):
        # Prueba de traducción del inglés al español.
        text = "Hello, how are you?"
        expected_translation_start = "Hola,"
        translation = self.translator.translate(text, 'en', 'es')
        print(f"Translation from EN to ES: '{translation}'")  # Imprime la traducción obtenida
        self.assertIsNotNone(translation)
        self.assertTrue(translation.startswith(expected_translation_start))

    def test_translation_es_en(self):
        # Prueba de traducción del español al inglés.
        text = "Hola, ¿cómo estás?"
        expected_translation_start = "Hey,"
        translation = self.translator.translate(text, 'es', 'en')
        print(f"Translation from ES to EN: '{translation}'")  # Imprime la traducción obtenida
        self.assertIsNotNone(translation)
        self.assertTrue(translation.startswith(expected_translation_start))

    def test_model_not_available(self):
        # Prueba con un par de idiomas para el cual no hay modelo disponible.
        text = "This is a test."
        translation = self.translator.translate(text, 'en', 'xx')  # 'xx' es un código inventado para la prueba.
        print(f"Translation when model not available: '{translation}'")  # Imprime la respuesta cuando no hay modelo
        self.assertIsNone(translation)

if __name__ == '__main__':
    unittest.main()
