"""Merge the official Danganronpa Wiki profiles into resources/characters.csv.

The wiki dump lives in resources/wiki-profiles.json (fetched from the
MediaWiki API) and holds, for every character, the official *Likes* and
*Dislikes* plus the profile numbers.

    python scripts/import_wiki_profiles.py

The script rewrites resources/characters.csv in place and prints a report of
every change, so the data can be reviewed in the diff.

Characters without an official profile keep the fan categories that were in the
old CSV, but the emojis are replaced by readable words ("Social media",
"Meals", …) so everybody understands what a clue means.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "resources" / "characters.csv"
WIKI_PATH = ROOT / "resources" / "wiki-profiles.json"

# CSV character name -> Danganronpa Wiki page title
WIKI_PAGES = {
    "Monomi, Usami": "Usami",
    "Byakuya Togami (DR2)": "Ultimate Imposter",
    "Chiaki Nanami": "Chiaki Nanami (Danganronpa 2)",
    "Masaru Dalmon": "Masaru Daimon",
}

# The wiki page of Hajime Hinata also lists the profile of Izuru Kamakura.
HAJIME_PAGE = "Hajime Hinata"
IZURU_PAGE = "Izuru Kamakura"

# Curated corrections for the values the wiki states differently.
FIXES = {
    "Miaya Gekkogahara": {
        "Title": "Ultimate Therapist",
        "Height": "153",
        "Weight": "41",
    },
    "Mukuro Ikusaba": {
        "Weight": "44",
    },
}

# Characters whose portrait/height only makes sense as "unknown"
KEEP_UNKNOWN = {"Monodam", "Monokid", "Monophanie", "Monosuke", "Monotaro"}

# Fan categories of the old CSV, written out in words
EMOJI_CATEGORIES = {
    "\U0001F4F1": "Social media",
    "\U0001F37D\uFE0F": "Meals",
    "\U0001F369": "Snacks",
    "\U0001F4BB": "Computers",
    "\U0001F3AC": "Entertainment",
    "\U0001F3A7": "Music",
    "\U0001F3C3": "Sports",
    "\U0001F4DA": "Books",
    "\U0001F415": "Animals",
    "\U0001F33F": "Plants",
    "\U0001F6CF\uFE0F": "Interiors",
    "\U0001F455": "Clothes",
    "\U0001F379": "Alcohol",
    "\u26C5": "Weather",
    "\U0001F3C1\uFE0F": "Countries",
    "\U0001F467": "Girls",
    "\U0001F466": "Boys",
    "\U0001F3B1": "Billiards",
    "\u26C4": "Weather",
    "\U0001F34E": "Sweets",
    "\U0001F35E": "Bread",
    "\U0001F952": "Sweets",
}

NO_DATA_VALUES = {"none", "unknown", "n/a", "nan", "-"}


def slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9 ]+", "", value)
    return re.sub(r"\s+", " ", value).strip()


def split_list(value: str) -> list[str]:
    items = []
    for raw in (value or "").split(","):
        item = raw.strip().rstrip("?").strip()
        if not item or item.lower() in NO_DATA_VALUES:
            continue
        items.append(item)
    seen = set()
    unique = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def emoji_to_words(value: str) -> list[str]:
    """Turn the old emoji categories into readable words."""
    words = []
    for item in split_list(value):
        word = EMOJI_CATEGORIES.get(item)
        if word is None:
            # keep unknown emoji as-is
            word = item
        if word not in words:
            words.append(word)
    return words


def wiki_likes_dislikes(page: str, profiles: dict) -> tuple[list[str], list[str]]:
    data = profiles.get(page)
    if not data:
        return [], []
    likes = [x for x in (data.get("likes") or []) if x.lower() not in NO_DATA_VALUES]
    dislikes = [x for x in (data.get("dislikes") or []) if x.lower() not in NO_DATA_VALUES]
    if page == HAJIME_PAGE:
        # the page also carries the profile of Izuru Kamakura
        likes = prefixed(data, "Hajime", "likes")
        dislikes = prefixed(data, "Hajime", "dislikes")
    return tidy(likes), tidy(dislikes)


def tidy(items: list[str]) -> list[str]:
    """Drop the (JP)/(EN) markers and the Japanese name when an English one exists."""
    if any(item.endswith("(EN)") for item in items):
        items = [item for item in items if not item.endswith("(JP)")]
    return [re.sub(r"\s*\((?:JP|EN)\)$", "", item).strip() for item in items if item.strip()]


def prefixed(data: dict, prefix: str, key: str) -> list[str]:
    """Pick the entries of a profile that start with a prefix ("Hajime: …")."""
    values = data.get(key) or []
    picked = []
    for value in values:
        if value.lower().startswith(prefix.lower()):
            picked.append(value.split(":", 1)[1].strip())
    return [v for v in picked if v and v.lower() not in NO_DATA_VALUES]


def main() -> None:
    profiles = json.loads(WIKI_PATH.read_text(encoding="utf-8"))
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = [dict(row) for row in reader]

    report = []
    for row in rows:
        name = row["Name"].strip()
        page = WIKI_PAGES.get(name, name)
        likes: list[str] = []
        dislikes: list[str] = []

        if name == IZURU_PAGE:
            data = profiles.get(HAJIME_PAGE) or {}
            likes = prefixed(data, "Izuru", "likes")
            dislikes = prefixed(data, "Izuru", "dislikes")
        else:
            likes, dislikes = wiki_likes_dislikes(page, profiles)

        source = "wiki"
        if not likes and not dislikes:
            # no official profile: keep the fan categories, written in words
            likes = emoji_to_words(row.get("Likes", ""))
            dislikes = emoji_to_words(row.get("Dislikes", ""))
            source = "categories"

        old_likes = row.get("Likes", "")
        old_dislikes = row.get("Dislikes", "")
        row["Likes"] = ", ".join(likes)
        row["Dislikes"] = ", ".join(dislikes)
        if old_likes != row["Likes"] or old_dislikes != row["Dislikes"]:
            report.append(f"{name}: likes/dislikes <- {source}")

        for key, value in FIXES.get(name, {}).items():
            if key in row and row[key] != value:
                report.append(f"{name}: {key} {row[key]!r} -> {value!r}")
                row[key] = value

        if name in KEEP_UNKNOWN:
            row["Height"] = "Unknown"
            row["Weight"] = "Unknown"

    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"updated {CSV_PATH.relative_to(ROOT)} ({len(rows)} characters)")
    for line in report:
        print("  " + line)


if __name__ == "__main__":
    main()
