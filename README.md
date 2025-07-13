# Dangandle

Dangandle is a terminal-based guessing game inspired by Onepiecedle, but with Danganronpa characters. Your goal is to guess the secret character by entering their name. After each guess, the game will show you which details you got right, which are wrong, and how close you are for certain fields.

---

## Index

- [How to Play](#how-to-play)
- [Data Columns Explained](#data-columns-explained)
- [Likes and Dislikes Guide](#likes-and-dislikes-guide)
- [Emoji Feedback Guide](#emoji-feedback-guide)
- [Running the Game](#running-the-game)

---

## How to Play
1. The game randomly selects a character from the Danganronpa universe.
2. You try to guess the character by typing their name.
3. After each guess, the game compares your guess to the target character and displays feedback for each attribute:
   - **Correct**: You matched the target's attribute.
   - **Wrong**: Your guess does not match the target's attribute.
   - **Close**: For numeric fields (like Height/Weight), you get hints if your guess is higher or lower than the target.
   - **Partial**: For multi-value fields (like Likes/Dislikes), you get hints if you have some overlap.
4. Use the feedback to refine your next guess. The game continues until you guess the correct character.

---

## Data Columns Explained
The game uses a CSV file (`characters.csv`) with the following columns:

- **Name**: The main name of the character.
- **Aliases**: Alternative names or nicknames.
- **Title**: The character's title or role (e.g., "Ultimate Lucky Student").
- **Gender**: Male, Female, or Unknown.
- **Height**: Character's height in centimeters (may be "Unknown").
- **Weight**: Character's weight in kilograms (may be "Unknown").
- **Status**: Whether the character is Alive, Deceased, or Inactive.
- **Talent Category**: The type of talent (e.g., Intellectual, Physical, Creative, Special, NAN).
- **Likes**: Things the character likes (can be multiple, separated by commas).
- **Dislikes**: Things the character dislikes (can be multiple, separated by commas).
- **First Appearance**: The game or media where the character first appeared.

---

## Likes and Dislikes Guide
In the `Likes` and `Dislikes` columns, emojis are used to represent categories or specific interests. Here is a guide to their meanings, grouped by type:

| Emoji | Meaning                      |
|-------|------------------------------|
| 🍽️    | Meal                         |
| 🍩    | Snack                        |
| 📚    | Objects                      |
| 💻    | Intelectual, Tech            |
| 🎧    | Sound                        |
| 🏳️    | Country                      |
| 🐕    | Animal                       |
| 🌿    | Plants                       |
| 🛏️    | Furniture, Rooms             |
| 👕    | Clothes                      |
| 🍹    | Alcohol, Tobacco, Drugs      |
| ⛅    | Weather                      |
| 🎬    | Entertainment                |
| 🏃    | Physical Activity            |
| 👧    | Girl                         |
| 👦    | Boy                          |
| 📱    | Social                       |

---

## Emoji Feedback Guide
After each guess, the game uses emojis to show how close you are:

- **✅**: Correct! Your guess matches the target's attribute.
- **❌**: Wrong. Your guess does not match the target's attribute.
- **⬆️**: For numeric fields, your guess is lower than the target's value (try a higher number).
- **⬇️**: For numeric fields, your guess is higher than the target's value (try a lower number).
- **🟨**: Partial match for multi-value fields (e.g., some Likes/Dislikes overlap).

---

## Running the Game

Install one of the `releases` or download the source code and do the following:

1. Make sure you have Python 3 installed.
2. Run the game:
   ```
   python main.py
   ```
3. Follow the on-screen instructions to play!