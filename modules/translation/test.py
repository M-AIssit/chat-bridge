import unittest
import json
import google.generativeai as genai
from .api import detect_language, translate_text  # Import the function to be tested

class GeminiAPITest(unittest.TestCase):
    def test_detect_language_french(self):
        # Test detection of French
        response = detect_language("Bonjour, comment ça va ?")
        # Validate the JSON response
        response_json = json.loads(response)
        expected_output = {"language": "French","ISO 639-1": "fr"}
        self.assertEqual(response_json, expected_output)

    def test_detect_language_spanish(self):
        # Test detection of Spanish
        response = detect_language("Hola, ¿cómo estás?")
        # Validate the JSON response
        response_json = json.loads(response)
        expected_output = { "language": "Spanish", "ISO 639-1": "es" }
        self.assertEqual(response_json, expected_output)

    def test_detect_language_english(self):
        # Test detection of English
        response = detect_language("Hello, how are you?")
        # Validate the JSON response
        response_json = json.loads(response)
        expected_output = { "language": "English", "ISO 639-1": "en" }
        self.assertEqual(response_json, expected_output)

    def test_translate_text_integration(self):
        # Example test case: translating "Hello, how are you?" from English to Spanish
        source_text = "Tell me about yourself."
        source_lang = "english"
        target_lang = "spanish"
        
        # Call the function
        response = translate_text(source_text, source_lang, target_lang)
        
        # Since the actual output can vary and we're directly calling the API,
        # we'll check if the response structure is as expected
        self.assertIn("input", response)
        self.assertIn("output", response)
        self.assertIn("src_lang", response)
        self.assertIn("src_lang_code", response)
        self.assertIn("target_lang", response)
        self.assertIn("target_lang_code", response)
        response_dict = json.loads(response)

        # Check if the source and target languages in the response match the request
        self.assertEqual(response_dict["src_lang"], source_lang)
        self.assertEqual(response_dict["target_lang"], target_lang)
        
        # Optionally, check if the translation is not empty or perform more specific checks
        self.assertNotEqual(response_dict["output"].strip(), "")


# Run the tests
if __name__ == '__main__':
    unittest.main()
