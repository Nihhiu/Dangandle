# Imports
from src.import_csv import load_characters
from src.mechanics import compare_character, find_similar_name
from src.terminal_presentation import clear_screen, print_history
import random

def filter_characters_by_appearance(characters):
    appearances = sorted(set(char.get("First Appearance", "") for char in characters))
    exclude_games = set()
    remaining = appearances.copy()
    clear_screen()

    while remaining:
        print("Available games:")
        for idx, app in enumerate(remaining, 1):
            print(f"  {idx}. {app}")
        
        choice = input("Enter the number of a game to EXCLUDE, or press Enter to finish: ").strip()

        if not choice:
            break
        if not choice.isdigit() or not (1 <= int(choice) <= len(remaining)):
            print("Invalid input. Please enter a valid number.")
            continue

        idx = int(choice) - 1

        exclude_games.add(remaining[idx])


        clear_screen()

        print(f"Excluded: {remaining[idx]} \n")
        del remaining[idx]

        if not remaining:
            print("All games excluded.")
            break
    
    filtered_characters = [char for char in characters if char.get("First Appearance", "") not in exclude_games]

    if not filtered_characters:
        print("No characters left after filtering. Exiting game.")
        return []
    
    return filtered_characters

def play_game(characters):
    filtered_characters = filter_characters_by_appearance(characters)
    if not filtered_characters:
        return
    target = random.choice(filtered_characters)
    fields = [key for key in target.keys() if key not in ("Name", "Aliases")]

    history = []
    used_names = []
    clear_screen()
    print("Guess the character from Danganronpa!\n")

    while True:
        guess_name = input("Enter character name: ").strip()
        guess = next((char for char in filtered_characters if char["Name"].lower() == guess_name.lower() and char["Name"] not in used_names), None)

        if not guess:
            guess = find_similar_name(guess_name, filtered_characters, used_names, threshold=0.5)

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
    characters = load_characters("resources/characters.csv")
    play_game(characters)
    input("Press any key to exit...")