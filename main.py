# Imports
from src.import_csv import load_characters
from src.mechanics import compare_character, find_similar_name
from src.terminal_presentation import clear_screen, print_history
from src.setup import filter_characters_by_appearance, select_target_character, choose_game_mode

GAME_MODE = ""

def play_game(characters, target):
    fields = [key for key in target.keys() if key not in ("Name", "Aliases")]

    history = []
    used_names = []
    clear_screen()

    while True:
        print_history(history, ["Name"] + fields, GAME_MODE)
        if len(history) != 0:
            print("\n--- Try again ---\n")
        guess_name = input("Enter character name: ").strip()
        guess = next((char for char in characters if char["Name"].lower() == guess_name.lower() and char["Name"] not in used_names), None)

        if not guess:
            guess = find_similar_name(guess_name, characters, used_names, threshold=0.5)

        if not guess:
            clear_screen()
            print("Character not found. Try again.\n")
            continue

        if guess["Name"] == target["Name"]:
            clear_screen()
            comparison = compare_character(guess, target)
            entry = {"Name": guess["Name"]}
            entry.update(comparison)
            history.append(entry)
            print_history(history, ["Name"] + fields, GAME_MODE)
            print("\n🎉 Correct! You guessed the character!\n")
            break

        # Comparison
        comparison = compare_character(guess, target)
        entry = {"Name": guess["Name"]}
        entry.update(comparison)
        history.append(entry)
        used_names.append(guess["Name"])

        clear_screen()


if __name__ == "__main__":
    characters = load_characters("../resources/characters.csv")
    GAME_MODE = choose_game_mode()

    if GAME_MODE != "daily":
        characters = filter_characters_by_appearance(characters)

    target = select_target_character(characters, mode=GAME_MODE)

    play_game(characters, target)
    input("Press any key to exit...")