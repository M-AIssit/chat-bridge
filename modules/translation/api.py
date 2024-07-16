#This file interacts directly with the Gemini API, handling all communications related to text translation and language detection.

from .constants import GEMINI_API_KEY, MODEL_ID
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)

def translate_text(text, source_lang, target_lang):
    model = genai.GenerativeModel(MODEL_ID, generation_config= {"response_mime_type": "application/json"})  # Using a specific Gemini model
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
    ## TO DO: 
    ## Wrap between try and except

    response = model.generate_content(prompt)
    if response:
        return response.text
    else:
        return '{"error": "Translation failed."}'
    

def detect_language(text):
    """
    Detects the language of the provided text using the Gemini API by asking the model
    to return the language in a structured JSON format, including the ISO 639-1 code.
    
    Args:
    text (str): The text for which the language needs to be detected.
    
    Returns:
    str: JSON formatted string indicating the detected language and its ISO 639-1 code.
    """

    

    # Configure the API with your API key
    genai.configure(api_key=GEMINI_API_KEY)

    
    # Setup the model
    model = genai.GenerativeModel(MODEL_ID, generation_config= {"response_mime_type": "application/json"})

    # Create the prompt with a clear instruction and example
    prompt = (f"Detect the language of the following text and return the result in JSON format "
              f"including the language name and its ISO 639-1 code. Here are examples:\n"
              f"Text: 'Bonjour, comment ça va ?'\n"
              f"Output: {{'language': 'French', 'ISO 639-1': 'fr'}}\n"
              f"Text: 'Hello, how are you?'\n"
              f"Output: {{'language': 'English', 'ISO 639-1': 'en'}}\n\n"
              f"Text: '{text}'\n"
              f"Output:")

    ##TO DO: Wrap between try and except
    ## Generate content from the model
    response = model.generate_content(prompt)
  
    # Interpret the response to extract JSON formatted language information
    if response:
        return response.text
    else:
        return '{"error": "Language detection was inconclusive."}'
