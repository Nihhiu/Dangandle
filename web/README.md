# Dangandle — web game

The browser version of **Dangandle**: a daily Wordle-style deduction puzzle where the
secret is a Danganronpa character and every guess is compared with it attribute by
attribute.

```
web/
├── index.html          # the whole UI
├── css/style.css       # theme
├── js/game.js          # game logic (seeding, comparison, candidates, stats)
├── js/characters.js    # generated dataset — do not edit by hand
├── images/<id>.webp    # one portrait per character, named after its id
├── favicon.svg
└── .nojekyll           # makes GitHub Pages serve the folder as-is
```

## How it works

* **Daily puzzle** — the date (`YYYY-MM-DD`) is hashed into a PRNG seed, so the same
  character is drawn for everybody on the same day. The puzzle uses the player's
  local date; `?d=2026-01-31` opens an archived puzzle.
* **Ten attempts**, then the secret is revealed.
* **Nine attributes** are compared on every guess: title, gender, height, weight,
  status, talent, likes, dislikes and debut game.

| Clue | Meaning |
| --- | --- |
| 🟩 green | the attribute is exactly right |
| 🟨 yellow | partial — same role word, same series, or a number very close to the secret |
| 🟥 red | nothing in common |
| ⬜ grey | the secret has no data for that attribute |
| ↑ ↓ | the secret is taller / shorter, heavier / lighter than your guess |

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
4. Select the branch `main` and the folder `/web`, then **Save**.
5. Wait for the green check — the game is live at
   `https://<your-user>.github.io/<your-repo>/`.

`web/.nojekyll` is already committed so GitHub publishes the folder verbatim.

## Regenerate the dataset

The dataset and the renamed portraits are produced from `resources/characters.csv`:

```bash
python scripts/build_web_data.py
```

The script writes `web/js/characters.js`, copies every portrait to
`web/images/<id>.webp` and records the original file names in
`resources/image-mapping.csv`.
