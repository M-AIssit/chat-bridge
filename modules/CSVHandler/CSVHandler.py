import csv
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")


class CSVHandler:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data_cache = None  # Añadimos un caché en memoria
        self.initialize_csv()

    def initialize_csv(self):
        # Inicializar el archivo CSV solo si no existe
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode='w', newline='') as file:
                fieldnames = ['Phone_number', 'Language', 'ISO_639-1']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

    def read_csv(self):
        # Usar caché para evitar lecturas repetidas
        if self.data_cache is not None:
            return self.data_cache
        data = []
        try:
            with open(self.filepath, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
            self.data_cache = data  # Actualizar el caché después de leer
        except FileNotFoundError:
            pass
        return data

    def write_csv(self, data):
        # Escribir el CSV solo si es necesario
        with open(self.filepath, mode='a', newline='') as file:  # Cambio a modo 'a' para añadir al final
            fieldnames = ['Phone_number', 'Language', 'ISO_639-1']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file.tell():  # Si el archivo está vacío, escribir el encabezado
                writer.writeheader()
            writer.writerows(data)
        self.data_cache = None  # Invalidar el caché después de escribir

    def write_full_csv(self, data):
        # Escribir todo el CSV de nuevo, usado para actualizaciones
        with open(self.filepath, mode='w', newline='') as file:
            fieldnames = ['Phone_number', 'Language', 'ISO_639-1']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        self.data_cache = None  # Invalidar el caché después de escribir

    def get_language_for_number(self, phone_number):
        supabase: Client = create_client(url, key)
        
        # Modify the query to include last_interaction
        result = supabase.table('phone_numbers') \
            .select("language, ISO_639, last_interaction") \
            .eq('phone_number', phone_number) \
            .execute()

        # Parse the result from Supabase
        if result.data:
            language = result.data[0]['language']
            iso_code = result.data[0]['ISO_639']
            last_interaction = result.data[0]['last_interaction']
            return language, iso_code, last_interaction

        return None, None, None
    

    def add_number_language(self, phone_number, language, iso):
        # Insert data into the database
        supabase: Client = create_client(url, key)

        # Generate current timestamp with time zone
        current_timestamp = datetime.now().astimezone()

        data, error = supabase.table('phone_numbers').insert({
            "phone_number": phone_number,
            "language": language,
            "ISO_639": iso,
            "last_interaction": current_timestamp
        }).execute()

    def get_last_interaction(self, phone_number):
        # Create the supabase client
        supabase: Client = create_client(url, key)

        # Retrieve the last_interaction value based on the phone number
        response = supabase.table('phone_numbers').select('last_interaction').eq('phone_number', phone_number).single().execute()

        # Check if there was an error or if the record exists
        if response['data']:
            last_interaction = response['data']['last_interaction']
            return last_interaction
        else:
            return f"No record found for phone number: {phone_number}"
        
    def update_last_interaction(self, phone_number):
        # Create the supabase client
        supabase: Client = create_client(url, key)

        # Generate current timestamp with time zone
        current_timestamp = datetime.now().astimezone()

        # Update the last_interaction field for the given phone number
        data, error = supabase.table('phone_numbers').update({
            "last_interaction": current_timestamp
        }).eq('phone_number', phone_number).execute()

        # Check if there was an error
        if error:
            return f"Error updating last interaction: {error}"
        
        return f"Last interaction updated successfully for phone number: {phone_number}"


    def update_language_for_number(self, phone_number, language, iso):
        data = self.read_csv()
        updated = False
        for row in data:
            if row['Phone_number'] == phone_number:
                row['Language'] = language
                row['ISO_639-1'] = iso
                updated = True
        if updated:
            self.write_full_csv(data)
        return updated
