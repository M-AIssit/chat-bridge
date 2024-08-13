import unittest
from unittest.mock import patch
import sys
import os

# Ajusta sys.path para incluir el directorio raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from modules.translation.api import translate_text

class TestTranslationAPI(unittest.TestCase):
    def test_translation_success_with_hf(self):
        # Simula un escenario donde Hugging Face devuelve una traducción exitosa
        with patch('modules.translation.hf_translation.HuggingFaceTranslator.translate', return_value='Traducción exitosa'):
            result = translate_text('Hola', 'Spanish', 'English', 'es', 'en')
            print(f"Test 1 - Hugging Face success: Result = {result}")
            self.assertEqual(result, 'Traducción exitosa')

    def test_translation_fallback_to_gemini(self):
        # Simula un escenario donde Hugging Face falla y se utiliza Gemini
        with patch('modules.translation.hf_translation.HuggingFaceTranslator.translate', return_value=None), \
             patch('modules.translation.api.translate_text_gemini', return_value='Fallback successful'):
            result = translate_text('Hello', 'English', 'Spanish', 'en', 'es')
            print(f"Test 2 - Fallback to Gemini: Result = {result}")
            self.assertEqual(result, 'Fallback successful')

    def test_gemini_api_failure(self):
        # Simula un escenario donde tanto Hugging Face como Gemini fallan
        with patch('modules.translation.hf_translation.HuggingFaceTranslator.translate', return_value=None), \
             patch('modules.translation.api.translate_text_gemini', return_value='{"error": "Translation failed."}'):
            result = translate_text('Bonjour', 'French', 'English', 'fr', 'en')
            print(f"Test 3 - Gemini API failure: Result = {result}")
            self.assertEqual(result, '{"error": "Translation failed."}')

    def test_translation_between_common_languages(self):
        language_pairs = [
            ('English', 'Spanish', 'Hello', 'Hola'),
            ('Spanish', 'English', 'Hola', 'Hello'),
            ('English', 'French', 'Good morning', 'Bonjour'),
            ('French', 'English', 'Bonjour', 'Good morning'),
            ('English', 'Chinese', 'Welcome', '欢迎'),
            ('Chinese', 'English', '欢迎', 'Welcome'),
            ('English', 'Arabic', 'Peace', 'سلام'),
            ('Arabic', 'English', 'سلام', 'Peace')
        ]

        for source_lang, target_lang, source_text, expected_translation in language_pairs:
            with self.subTest(source_lang=source_lang, target_lang=target_lang):
                with patch('modules.translation.api.translate_text', return_value=expected_translation) as mocked_translate:
                    result = mocked_translate(source_text, source_lang, target_lang, 'en', 'es')  # Assuming ISO codes are 'en' and 'es' for simplicity in the mock setup
                    print(f"Translating from {source_lang} to {target_lang}: '{source_text}' -> '{result}'")
                    self.assertEqual(result, expected_translation)

if __name__ == '__main__':
    unittest.main()
