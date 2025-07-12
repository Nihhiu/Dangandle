import csv
import os
import sys

def get_resource_path(relative_path):
    """Resolve o caminho do recurso, mesmo dentro de um .exe do PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

def load_characters(relative_path):
    filename = get_resource_path(relative_path)
    
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        characters = list(reader)
    return characters