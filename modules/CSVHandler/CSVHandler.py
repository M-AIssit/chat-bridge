import csv
import os

def ensure_csv_exists(csv_path='phone_numbers.csv'):
    if not os.path.exists(csv_path):
        with open(csv_path, mode='w', newline='') as csvfile:
            fieldnames = ['telefono', 'idioma', 'ISO 639-1']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

def check_phone_number(phone_number, csv_path='phone_numbers.csv'):
    ensure_csv_exists(csv_path)  # Asegurarse de que el CSV existe antes de intentar leerlo
    if os.path.exists(csv_path):
        with open(csv_path, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['telefono'] == phone_number:
                    return {'language': row['idioma'], 'ISO 639-1': row['ISO 639-1']}
    return None

def add_phone_number(phone_number, language, iso_code, csv_path='phone_numbers.csv'):
    ensure_csv_exists(csv_path)  # Asegurarse de que el CSV existe antes de intentar escribir en él
    with open(csv_path, mode='a', newline='') as csvfile:
        fieldnames = ['telefono', 'idioma', 'ISO 639-1']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'telefono': phone_number, 'idioma': language, 'ISO 639-1': iso_code})
