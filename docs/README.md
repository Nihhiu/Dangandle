# Dangandle — web game

The browser version of **Dangandle**: a daily Wordle-style deduction puzzle where the
secret is a Danganronpa character and every guess is compared with it attribute by
attribute.

```
docs/
├── index.html          # the whole UI
├── css/style.css       # black & white theme with coloured clue cells
├── js/game.js          # game logic (seeding, comparison, candidates, stats)
├── js/characters.js    # generated dataset — do not edit by hand
├── images/<id>.webp    # one portrait per character, named after its id
├── Dangandle icon.ico  # page icon
└── .nojekyll           # makes GitHub Pages serve the folder as-is
```

## How it works

* **Daily puzzle** — the date (`YYYY-MM-DD`) is hashed into a PRNG seed, so the same
  character is drawn for everybody on the same day. The puzzle uses the player's
  local date; `?d=2026-01-31` opens an archived puzzle.
* **Ten attempts**, then the secret is revealed.
* **Nine attributes** are compared on every guess: title, gender, height, weight,
  status, talent type, likes, dislikes and debut game.
* Every guess is a single row —
  `image | name | title | gender | height | weight | status | talent type | likes | dislikes | debut`
  — and the newest row sits on top.

| Clue | Colour | Meaning |
| --- | --- | --- |
| exact | 🟩 `#7DFF5E` | the attribute is exactly right |
| partial | 🟨 `#FFD400` | partial — same role word, same series, or a number very close to the secret |
| none | 🩷 `#FF6FA5` | nothing in common |
| unknown | ⬛ | the secret has no data for that attribute |
| ↑ ↓ | — | the secret is taller / shorter, heavier / lighter than your guess |

* **Likes and dislikes** are the official profiles from the
  [Danganronpa Wiki](https://danganronpa.fandom.com/wiki/Game_Characters) — *Curry,
  Trendy things* for Makoto, *Hair braids* for Kyoko, *Freshly washed towels* for
  Nekomaru. Characters without an official profile use the fan categories that are
  listed in *How to play*.
* **Candidate counter** — after every guess the game filters the whole cast with the
  clues seen so far and shows how many characters are still possible.
* **Progress** (guesses, statistics, streaks) is stored in `localStorage`.

## Run it locally

```bash
python scripts/serve_web.py          # http://127.0.0.1:8765/
```

Any static server works; the game has no build step and no runtime dependency.

## Publish it on GitHub Pages

1. Push this repository to GitHub.
2. Open **Settings → Pages**.
3. Under *Build and deployment* choose **Deploy from a branch**.
4. Select the branch `main` and the folder `/docs` (or `/ (root)` to serve it from
   the repository root), then **Save**.
5. Wait for the green check — the game is live at
   `https://<your-user>.github.io/<your-repo>/`.

`docs/.nojekyll` is already committed so GitHub publishes the folder verbatim.

## Regenerate the dataset

The dataset and the renamed portraits are produced from `resources/characters.csv`:

```bash
python scripts/build_web_data.py
```

The script writes `docs/js/characters.js`, copies every portrait to
`docs/images/<id>.webp` and records the original file names in
`resources/image-mapping.csv`.

The official likes/dislikes come from the Danganronpa Wiki and can be refreshed with:

```bash
python scripts/fetch_wiki_profiles.py    # downloads resources/wiki-profiles.json
python scripts/import_wiki_profiles.py   # merges them into resources/characters.csv
```
