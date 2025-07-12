from difflib import SequenceMatcher

MULTI_FIELDS = {"Likes", "Dislikes"}
NUMERIC_FIELDS = {"Height", "Weight"}
IGNORE_FIELDS = {"Aliases"}

def compare_character(guess, target):
    result = {}
    for key in target:
        if key == "Name" or key in IGNORE_FIELDS:
            continue

        guess_val = guess[key]
        target_val = target[key]

        if key in MULTI_FIELDS:
            result[key] = compare_multi_field(guess_val, target_val)

        elif key in NUMERIC_FIELDS:
            # Verify if the values are equal
            if guess_val == target_val or int(guess_val) == int(target_val):
                result[key] = f"{guess_val} ✅"
            
            # Verify if the values are numeric
            elif guess_val.isdigit() and target_val.isdigit():
                if int(guess_val) > int(target_val):
                    result[key] = f"{guess_val} ⬇️"
                elif int(guess_val) < int(target_val):
                    result[key] = f"{guess_val} ⬆️"
            
            # Handle cases where one or both values are not numeric
            elif not target_val.isdigit():
                result[key] = f"{guess_val} ⬇️"
            elif not guess_val.isdigit():
                result[key] = f"{guess_val} ⬆️"
        else:
            if guess_val == target_val:
                result[key] = f"{guess_val} ✅"
            else:
                result[key] = f"{guess_val} ❌"
    return result

def find_similar_name(name_input, characters, used_names, threshold=0.5):
    best_match = None
    best_score = 0

    for char in characters:
        if char["Name"] in used_names:
            continue

        # Lista de nomes possíveis
        all_names = [char["Name"]]
        if "Aliases" in char:
            all_names += [alias.strip() for alias in char["Aliases"].split(",")]

        for alt_name in all_names:
            score = SequenceMatcher(None, name_input.lower(), alt_name.lower()).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_match = char

    return best_match


def compare_multi_field(guess_val, target_val):
    guess_items = set(i.strip() for i in guess_val.split(",") if i.strip())
    target_items = set(i.strip() for i in target_val.split(",") if i.strip())

    if guess_items == target_items:
        return f"{guess_val} ✅"
    elif guess_items & target_items:
        return f"{guess_val} 🟨"
    else:
        return f"{guess_val} ❌"
