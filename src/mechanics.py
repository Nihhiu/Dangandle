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
            # Non Numeric values are handled separately
            if not target_val.isdigit():
                if target_val == guess_val:
                    result[key] = f"{guess_val} ✅"
                else:
                    result[key] = f"{guess_val} ⬇️"
            
            elif not guess_val.isdigit():
                if target_val == guess_val:
                    result[key] = f"{guess_val} ✅"
                else:
                    result[key] = f"{guess_val} ⬆️"
            
            # Handle cases where both are numeric
            elif guess_val == target_val or int(guess_val) == int(target_val):
                result[key] = f"{guess_val} ✅"
            elif guess_val < target_val:
                result[key] = f"{guess_val} ⬆️"
            elif guess_val > target_val:
                result[key] = f"{guess_val} ⬇️"
        else:
            if guess_val == target_val:
                result[key] = f"{guess_val} ✅"
            else:
                result[key] = f"{guess_val} ❌"
    return result

from difflib import SequenceMatcher

def find_similar_name(name_input, characters, used_names, threshold=0.6):
    best_match = None
    best_score = 0

    # Normalize
    name_input = name_input.lower().strip()
    input_tokens = name_input.split()

    for char in characters:
        if char["Name"] in used_names:
            continue

        # Possible names
        all_names = [char["Name"]]
        if "Aliases" in char:
            all_names += [alias.strip() for alias in char["Aliases"].split(",")]

        for alt_name in all_names:
            alt_name_norm = alt_name.lower().strip()

            # Check if all tokens appear in the name
            token_hits = sum(1 for tok in input_tokens if tok in alt_name_norm)

            if token_hits == len(input_tokens):
                # If all tokens appear, give maximum priority
                score = 2.0 + token_hits
            else:
                # Otherwise, use normal similarity
                score = SequenceMatcher(None, name_input, alt_name_norm).ratio() + token_hits * 0.3

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
