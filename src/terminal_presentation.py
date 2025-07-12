import os

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_header(fields):
    print(" | ".join(f"{field:^20}" for field in fields))
    print("-" * (23 * len(fields)))

def print_history(history, fields):
    print_header(fields)
    for entry in history:
        row = [f"{entry.get(field, ''):^20}" for field in fields]
        print(" | ".join(row))