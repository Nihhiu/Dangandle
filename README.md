# Dangandle

Dangandle is a guessing game inspired by Onepiecedle and Wordle, but with Danganronpa characters. Your goal is to guess the secret character by entering their name. After each guess, the game will show you which details you got right, which are wrong, and how close you are for certain fields.

There are **two versions** in this repository:

| Version | Where | What it is |
| --- | --- | --- |
| 🌐 **Web game** | [`docs/`](docs/) | The daily puzzle, playable in the browser and deployable to GitHub Pages |
| 💻 **Terminal game** | [`main.py`](main.py) | The original command-line version |

---

## 🌐 Play it online (GitHub Pages)

The web game lives in the [`docs/`](docs/) folder and has no build step — it is plain
HTML, CSS and JavaScript, so GitHub Pages can serve it as-is.

### 1. Publish the site

1. Make sure everything is pushed to GitHub:

   ```bash
   git add .
   git commit -m "Add Dangandle web game"
   git push origin main
   ```

2. On GitHub, open the repository → **Settings → Pages**.
3. In *Build and deployment* choose **Deploy from a branch**.
4. Pick the branch **`main`** and the folder **`/docs`** (or **`/ (root)`** if you
   prefer to serve the site from the repository root), then press **Save**.
5. Wait for the green check mark. The game is now live at:

   ```
   https://<your-user>.github.io/<your-repo>/
   ```

   For this repository that is **https://nihhiu.github.io/Dangandle/**

> `docs/.nojekyll` is committed on purpose, so GitHub publishes the folder exactly
> as it is on disk.

### 2. Test it locally before publishing

```bash
python scripts/serve_web.py        # http://127.0.0.1:8765/
```

### How the daily puzzle works

* The date (`YYYY-MM-DD`) is hashed into a seed, so **everybody plays the same
  character on the same day** — a new puzzle is generated every midnight.
* You have **10 attempts**. Every guess is written as a single row:
  `image | name | title | gender | height | weight | status | talent type | likes | dislikes | debut`.
  The newest row is always on top.
* Each of the nine clue cells is coloured:
  * 🟩 **green** (`#7DFF5E`) — exact match
  * 🟨 **yellow** (`#FFD400`) — partial match (same role word, same game series, a
    number close to the secret…)
  * 🩷 **pink** (`#FF6FA5`) — nothing in common
  * ⬛ **dark** — the secret has no data for that attribute
  * **↑ ↓** — the secret is taller/shorter or heavier/lighter than your guess
* The **likes** and **dislikes** are the ones written on the official profile of
  each character on the [Danganronpa Wiki](https://danganronpa.fandom.com/wiki/Game_Characters)
  (curry and trendy things for Makoto, hair braids for Kyoko, fresh towels for
  Nekomaru…). Characters without an official profile use the fan categories
  listed in *How to play*.
* A live **candidate counter** shows how many characters are still consistent with
  every clue you have seen.
* `?d=2026-01-31` opens an archived puzzle.
* Progress and statistics are stored in the browser (`localStorage`).

Full details: [`docs/README.md`](docs/README.md).

---

## Index

### Web game

- [Play it online (GitHub Pages)](#-play-it-online-github-pages)
- [How the daily puzzle works](#how-the-daily-puzzle-works)

### Terminal game

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
The `Likes` and `Dislikes` columns hold the official profile of every character,
taken from the [Danganronpa Wiki](https://danganronpa.fandom.com/wiki/Game_Characters)
(the same lists that appear in the game menus and in the official artbook), for
example:

| Character | Likes | Dislikes |
|-----------|-------|----------|
| Makoto Naegi | Curry, Trendy things | Dried mackerel, Dried bean curd |
| Kyoko Kirigiri | Hair braids | Goya, Coriander |
| Aoi Asahina | Donuts | Calculating |
| Nekomaru Nidai | Freshly washed towels | Lazy people |
| Sonia Nevermind | Occult, Japan | Sour plums |

The characters without an official profile (Monokuma, Chihiro, Leon, Sayaka…) use
the fan categories below, written in words so they are easy to understand:

| Category | Meaning |
|----------|---------|
| Meals | home cooking, restaurants, food in general |
| Snacks / Sweets / Bread | sweets, cakes, little bites, bakery products |
| Social media | phones, chats, networks |
| Computers | gadgets, programming, the web |
| Entertainment | films, series, games, shows |
| Music | songs, concerts, sound |
| Sports | training, running, competitions |
| Books | reading, study, novels |
| Animals | pets, wildlife |
| Plants | flowers, gardens, greenery |
| Interiors | rooms, furniture, decoration |
| Clothes | fashion, outfits |
| Alcohol | drinks, tobacco, party |
| Weather | sun, rain, climate |
| Countries | travel abroad, flags, cultures |
| Girls / Boys | the company of girls / boys |
| Billiards | pool, snooker, cues |

The data is refreshed with:

```bash
python scripts/fetch_wiki_profiles.py    # downloads the wiki profiles
python scripts/import_wiki_profiles.py   # merges them into characters.csv
```

---

## Emoji Feedback Guide
After each guess, the game uses emojis to show how close you are:

- **✅**: Correct! Your guess matches the target's attribute.
- **❌**: Wrong. Your guess does not match the target's attribute.
- **⬆️**: For numeric fields, your guess is lower than the target's value (try a higher number).
- **⬇️**: For numeric fields, your guess is higher than the target's value (try a lower number).
- **🟨**: Partial match for multi-value fields (e.g., some Likes/Dislikes overlap).

---

### Running from Source

1. Make sure you have Python 3 installed.
2. Run the game:
   ```
   python main.py
   ```
3. Follow the on-screen instructions to play!

---

### Creating an Executable (Step-by-Step)

1. Open your terminal and run:
   ```
   pip install pyinstaller
   ```

2. In `main.py`, change the line:
   ```python
   characters = load_characters("../resources/characters.csv")
   ```
   to:
   ```python
   characters = load_characters("resources/characters.csv")
   ```

3. Run the following command in your terminal:
   ```
   python dist_creation.py
   ```
   This will use PyInstaller to build the executable.

4. After the process completes, look for your game executable in the `dist` folder.

5. Double-click the executable or run it from the terminal to play!

---

## Development

```bash
# rebuild the web dataset (docs/js/characters.js + docs/images/<id>.webp)
python scripts/build_web_data.py

# refresh the official likes/dislikes from the Danganronpa Wiki
python scripts/fetch_wiki_profiles.py
python scripts/import_wiki_profiles.py

# serve the web game locally with no-cache headers
python scripts/serve_web.py
```

| Path | Purpose |
| --- | --- |
| `resources/characters.csv` | source of truth for every character attribute |
| `resources/wiki-profiles.json` | the official profiles downloaded from the Danganronpa Wiki |
| `resources/image-mapping.csv` | which portrait file became which id |
| `scripts/build_web_data.py` | regenerates the dataset and renames the portraits |
| `scripts/fetch_wiki_profiles.py` | downloads the official character profiles |
| `scripts/import_wiki_profiles.py` | merges them into `characters.csv` |
| `scripts/serve_web.py` | tiny local static server for the web game |
| `docs/` | the browser game (this is what GitHub Pages publishes) |

---