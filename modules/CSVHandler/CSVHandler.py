import csv
import os

class CSVHandler:
    def __init__(self, filepath):
        self.filepath = filepath
        self.initialize_csv()

    def initialize_csv(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode='w', newline='') as file:
                fieldnames = ['Phone_number', 'Language', 'ISO_639-1']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

    def read_csv(self):
        data = []
        try:
            with open(self.filepath, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
        except FileNotFoundError:
            pass
        return data

    def write_csv(self, data):
        with open(self.filepath, mode='w', newline='') as file:
            fieldnames = ['Phone_number', 'Language', 'ISO_639-1']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    def get_language_for_number(self, phone_number):
        data = self.read_csv()
        for row in data:
            if row['Phone_number'] == phone_number:
                return row['Language'], row['ISO_639-1']
        return None, None

    def add_number_language(self, phone_number, language, iso):
        data = self.read_csv()
        data.append({'Phone_number': phone_number, 'Language': language, 'ISO_639-1': iso})
        self.write_csv(data)
