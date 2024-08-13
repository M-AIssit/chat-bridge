import unittest
from unittest.mock import patch
import sys
import os
import json

# Ajusta sys.path para incluir el directorio raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from modules.translation.api import translate_text, translate_text_gemini

class TestTranslationAPI(unittest.TestCase):
    def test_translation_success_with_hf(self):
        # Simula un escenario donde Hugging Face devuelve una traducción exitosa
        with patch('modules.translation.hf_translation.HuggingFaceTranslator.translate', return_value={'translated_text': 'Traducción exitosa'}):
            result = translate_text('Hola', 'Spanish', 'English', 'es', 'en')
            print(f"Test 1 - Hugging Face success: Result = {result}")
            self.assertEqual(json.loads(result), {"translated_text": "Traducción exitosa"})

    def test_translation_fallback_to_gemini(self):
        # Simula un escenario donde Hugging Face falla y se utiliza Gemini
        with patch('modules.translation.hf_translation.HuggingFaceTranslator.translate', return_value=None), \
             patch('modules.translation.api.translate_text_gemini', return_value='{"translated_text": "Fallback successful"}'):
            result = translate_text('Hello', 'English', 'Spanish', 'en', 'es')
            print(f"Test 2 - Fallback to Gemini: Result = {result}")
            self.assertEqual(json.loads(result), {"translated_text": "Fallback successful"})

    def test_gemini_api_failure(self):
        # Simula un escenario donde tanto Hugging Face como Gemini fallan
        with patch('modules.translation.hf_translation.HuggingFaceTranslator.translate', return_value=None), \
             patch('modules.translation.api.translate_text_gemini', return_value='{"error": "Translation failed."}'):
            result = translate_text('Bonjour', 'French', 'English', 'fr', 'en')
            print(f"Test 3 - Gemini API failure: Result = {result}")
            self.assertEqual(json.loads(result), {"error": "Translation failed."})

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
                with patch('modules.translation.api.translate_text', return_value=f'{{"translated_text": "{expected_translation}"}}') as mocked_translate:
                    result = mocked_translate(source_text, source_lang, target_lang, 'en', 'es')  # Assuming ISO codes are 'en' and 'es' for simplicity in the mock setup
                    print(f"Translating from {source_lang} to {target_lang}: '{source_text}' -> '{result}'")
                    self.assertEqual(json.loads(result), {"translated_text": expected_translation})

    def test_compare_hf_and_gemini(self):
        # Comparación directa entre Hugging Face y Gemini usando la misma frase
        phrase = "This is a test sentence."
        source_lang_name = "English"
        target_lang_name = "Spanish"

        hf_result = translate_text(phrase, source_lang_name, target_lang_name, 'en', 'es')
        gemini_result = translate_text_gemini(phrase, source_lang_name, target_lang_name)

        print(f"Hugging Face Translation: {hf_result}")
        print(f"Gemini Translation: {gemini_result}")

        self.assertTrue(hf_result)
        self.assertTrue(gemini_result)

        hf_translation = json.loads(hf_result).get("translated_text", "")
        gemini_translation = json.loads(gemini_result).get("translated_text", "")

        print(f"Hugging Face: {hf_translation}")
        print(f"Gemini: {gemini_translation}")

        self.assertIsInstance(hf_translation, str)
        self.assertIsInstance(gemini_translation, str)

if __name__ == '__main__':
    unittest.main()
