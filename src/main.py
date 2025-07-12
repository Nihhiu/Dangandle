# Imports
from import_csv import load_characters
from mechanics import compare_character, find_similar_name
from terminal_presentation import clear_screen, print_history
import random

def play_game(characters):
    target = random.choice(characters)
    fields = [key for key in target.keys() if key not in ("Name", "Aliases")]


    history = []
    used_names = []
    clear_screen()
    print("Guess the character from Danganronpa!\n")

    while True:
        guess_name = input("Enter character name: ").strip()
        guess = next((char for char in characters if char["Name"].lower() == guess_name.lower() and char["Name"] not in used_names), None)

        if not guess:
            guess = find_similar_name(guess_name, characters, used_names, threshold=0.5)


        if not guess:
            clear_screen()
            print("Character not found. Try again.\n")
            print_history(history, ["Name"] + fields)
            continue

        if guess["Name"] == target["Name"]:
            clear_screen()
            comparison = compare_character(guess, target)
            entry = {"Name": guess["Name"]}
            entry.update(comparison)
            history.append(entry)
            print_history(history, ["Name"] + fields)
            print("\n🎉 Correct! You guessed the character!\n")
            break

        # Comparação
        comparison = compare_character(guess, target)
        entry = {"Name": guess["Name"]}
        entry.update(comparison)
        history.append(entry)
        used_names.append(guess["Name"])


        clear_screen()
        print_history(history, ["Name"] + fields)
        print("\n--- Try again ---\n")


if __name__ == "__main__":
    characters = load_characters("../resources/characters.csv")
    play_game(characters)