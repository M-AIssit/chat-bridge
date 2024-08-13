from transformers import MarianMTModel, MarianTokenizer

class HuggingFaceTranslator:
    def __init__(self):
        # Inicializar con una estructura vacía que llenaremos según demanda.
        self.models = {}

    def _load_model(self, source_lang_code, target_lang_code):
        model_key = f'{source_lang_code}-{target_lang_code}'
        if model_key not in self.models:
            model_name = f'Helsinki-NLP/opus-mt-{source_lang_code}-{target_lang_code}'
            try:
                tokenizer = MarianTokenizer.from_pretrained(model_name)
                model = MarianMTModel.from_pretrained(model_name)
                self.models[model_key] = (model_name, tokenizer, model)
            except Exception as e:
                print(f"Failed to load model {model_name}: {str(e)}")
                return None
        return self.models[model_key]

    def translate(self, text, source_lang_code, target_lang_code):
        # Intentar cargar el modelo para el par de idiomas solicitado.
        model_data = self._load_model(source_lang_code, target_lang_code)
        if model_data:
            _, tokenizer, model = model_data
            # Preparar el texto para la traducción.
            encoded_text = tokenizer(text, return_tensors="pt", padding=True)
            # Generar la traducción.
            translated_tokens = model.generate(**encoded_text)
            # Decodificar los tokens traducidos.
            translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
            # Devolver un diccionario con la traducción en formato JSON
            return {"translated_text": translated_text}
        else:
            return None
