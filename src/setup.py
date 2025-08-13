from src.terminal_presentation import clear_screen
import random
import datetime

def select_target_character(characters, mode="daily"):
    if mode == "daily":
        today = datetime.date.today()
        day_of_year = today.timetuple().tm_yday

        seeded_random = random.Random()
        seeded_random.seed(day_of_year)

        target = seeded_random.choice(characters)
    elif mode == "random":
        target = random.choice(characters)
    else:
        raise ValueError("Invalid mode. Use 'daily' or 'random'.")
    return target

def choose_game_mode():
    while True:
        clear_screen()
        print("Choose game mode:")
        print("  1. Daily Challenge")
        print("  2. Random Character")
        print("\n")
        choice = input("Enter the number of the game mode: ").strip()

        if choice == "1":
            return "daily"
        elif choice == "2":
            return "random"
        else:
            print("Invalid choice. Please try again.")
    

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
