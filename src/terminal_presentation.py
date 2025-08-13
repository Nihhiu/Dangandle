import os
import datetime

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_header(mode):
    if mode == "daily":
        print("Guess today's Danganronpa character! " + datetime.date.today().strftime("%d-%m-%Y"))
    else:
        print("Guess the character from Danganronpa!")
    print("\n")

def print_table_header(fields):
    print(" | ".join(f"{field:^20}" for field in fields))
    print("-" * (23 * len(fields)))

def print_history(history, fields, mode):
    print_header(mode)
    print_table_header(fields)
    for entry in history:
        row = [f"{entry.get(field, ''):^20}" for field in fields]
        print(" | ".join(row))