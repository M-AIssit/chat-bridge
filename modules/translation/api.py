from modules.translation.hf_translation import HuggingFaceTranslator
from .constants import GEMINI_API_KEY, MODEL_ID
import google.generativeai as genai
import json

genai.configure(api_key=GEMINI_API_KEY)
hf_translator = HuggingFaceTranslator()

def translate_text(text, source_lang_name, target_lang_name, source_lang_code, target_lang_code):
    try:
        # Intentar traducción usando los modelos de Hugging Face
        translated_text = hf_translator.translate(text, source_lang_code, target_lang_code)
        if translated_text:
            print("Using Hugging Face for translation.")
            return json.dumps(translated_text)  # Devolver directamente el JSON sin anidación
    except Exception as e:
        print(f"Error with Hugging Face translation: {str(e)}")

    try:
        # Usar la API de Gemini como alternativa si la traducción de Hugging Face falla
        print("Falling back to Gemini API for translation.")
        translated_text = translate_text_gemini(text, source_lang_name, target_lang_name)
        if translated_text:
            print("Using Gemini API for translation.")
            return translated_text  # Asegurar que Gemini también devuelve el JSON correcto
    except Exception as e:
        print(f"Error with Gemini API translation: {str(e)}")
        return json.dumps({"error": "Translation failed with both services."})

    # Si se llega a este punto, significa que la traducción de Hugging Face fue None sin lanzar una excepción
    return json.dumps({"error": "No translation available from Hugging Face, and Gemini API not attempted."})


def translate_text_gemini(text, source_lang, target_lang):
    model = genai.GenerativeModel(MODEL_ID, generation_config={"response_mime_type": "application/json"})  # Usando un modelo específico de Gemini
    prompt = f"""
Translate '{text}' from {source_lang} to {target_lang}.

Here are examples:
{{
    "input": "Hello, how are you?",
    "output": "Hola, ¿cómo estás?",
    "src_lang": "english",
    "src_lang_code": "en",
    "target_lang": "spanish",
    "target_lang_code": "es"
}},
{{
    "input": "What is your name?",
    "output": "¿Cómo te llamas?",
    "src_lang": "english",
    "src_lang_code": "en",
    "target_lang": "spanish",
    "target_lang_code": "es"
}},
{{
    "input": "Good morning!",
    "output": "Bonjour!",
    "src_lang": "english",
    "src_lang_code": "en",
    "target_lang": "French",
    "target_lang_code": "fr"
}}
"""
    # Manejo de excepciones alrededor del modelo de generación
    try:
        response = model.generate_content(prompt)
        if response:
            return json.dumps({"translated_text": response.text})  # Asegurar que el resultado esté en formato JSON
        else:
            return '{"error": "Translation failed."}'
    except Exception as e:
        print(f"Error generating content with Gemini: {str(e)}")
        return '{"error": "Translation failed due to an exception."}'

def detect_language(text):
    """
    Detecta el idioma del texto proporcionado usando la API de Gemini, devolviendo el resultado en un formato JSON estructurado, incluyendo el código ISO 639-1.

    Args:
    text (str): El texto para el cual se necesita detectar el idioma.

    Returns:
    str: Cadena en formato JSON que indica el idioma detectado y su código ISO 639-1.
    """

    # Configurar la API con tu clave
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Configuración del modelo
    model = genai.GenerativeModel(MODEL_ID, generation_config={"response_mime_type": "application/json"})

    # Crear el prompt con una instrucción clara y ejemplos
    prompt = (f"Detect the language of the following text and return the result in JSON format "
              f"including the language name and its ISO_639-1 code. Here are examples:\n"
              f"Text: 'Bonjour, comment ça va ?'\n"
              f"Output: {{'language': 'French', 'ISO_639-1': 'fr'}}\n"
              f"Text: 'Hello, how are you?'\n"
              f"Output: {{'language': 'English', 'ISO_639-1': 'en'}}\n\n"
              f"Text: '{text}'\n"
              f"Output:")

    try:
        response = model.generate_content(prompt)
        if response:
            return response.text
        else:
            return '{"error": "Language detection was inconclusive."}'
    except Exception as e:
        print(f"Error detecting language with Gemini: {str(e)}")
        return '{"error": "Language detection failed due to an exception."}'
