import csv
import os

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
        data = self.read_csv()
        for row in data:
            if row['Phone_number'] == phone_number:
                return row['Language'], row['ISO_639-1']
        return None, None

    def add_number_language(self, phone_number, language, iso):
        # Verificar si ya está en el caché antes de añadir
        if self.get_language_for_number(phone_number) == (None, None):
            new_entry = {'Phone_number': phone_number, 'Language': language, 'ISO_639-1': iso}
            if self.data_cache is not None:
                self.data_cache.append(new_entry)  # Añadir a la caché
            self.write_csv([new_entry])  # Añadir solo la nueva entrada al archivo

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
