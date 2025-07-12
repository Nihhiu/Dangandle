import csv

def load_characters(filename):
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        characters = list(reader)
    return characters