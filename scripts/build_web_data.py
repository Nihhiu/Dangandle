"""Build the static web game dataset from resources/characters.csv.

Outputs:
  * docs/js/characters.js   -> window.DANGANDLE_CHARACTERS = [...] (used by the site)
  * docs/images/<id>.webp  -> portrait of every character, named after its id
  * resources/image-mapping.csv -> id / name / original file name (so the rename
    is reversible and auditable)

Usage:
    python scripts/build_web_data.py

The script is idempotent: once the portraits have been moved to docs/images it
re-uses them instead of looking for the original file names again.
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "resources" / "characters.csv"
IMG_DIR = ROOT / "resources" / "image"
WEB_DIR = ROOT / "docs"
OUT_IMG_DIR = WEB_DIR / "images"
OUT_JS = WEB_DIR / "js" / "characters.js"
MAPPING_CSV = ROOT / "resources" / "image-mapping.csv"

# ---------------------------------------------------------------------------
# Games (used for the "Debut" attribute and for the partial-match rule)
# ---------------------------------------------------------------------------

GAMES = {
    "Danganronpa 1: Trigger Happy Havoc": {
        "code": "DR1",
        "label": "Danganronpa 1",
        "series": "main",
    },
    "Danganronpa 2: Goodbye Despair": {
        "code": "DR2",
        "label": "Danganronpa 2",
        "series": "main",
    },
    "Danganronpa Another Episode: Ultra Despair Girls": {
        "code": "UDG",
        "label": "Another Episode",
        "series": "spin-off",
    },
    "Danganronpa 3: The End of Hope's Peak High School": {
        "code": "DR3",
        "label": "Danganronpa 3",
        "series": "main",
    },
    "Danganronpa V3: Killing Harmony": {
        "code": "V3",
        "label": "Danganronpa V3",
        "series": "main",
    },
}

GAME_ORDER = {"DR1": 0, "DR2": 1, "UDG": 2, "DR3": 3, "V3": 4}

# ---------------------------------------------------------------------------
# Characters that exist as portraits but are not present in characters.csv.
# Values are best-effort approximations.
# ---------------------------------------------------------------------------

EXTRA_CHARACTERS = [
    {
        "Name": "Miaya Gekkogahara",
        "Aliases": "",
        "Title": "Ultimate Therapist",
        "Gender": "Male",
        "Height": "153",
        "Weight": "41",
        "Status": "Deceased",
        "Talent Category": "Intellectual",
        "Likes": "",
        "Dislikes": "",
        "First Appearance": "Danganronpa 3: The End of Hope's Peak High School",
        "Image": "Miaya_Gekkogahara_DR3_VA_ID.webp",
    },
    {
        "Name": "Monodam",
        "Aliases": "Super High School Level Debate Club President",
        "Title": "Super High School Level Debate Club President",
        "Gender": "Male",
        "Height": "Unknown",
        "Weight": "Unknown",
        "Status": "Inactive",
        "Talent Category": "NAN",
        "Likes": "",
        "Dislikes": "",
        "First Appearance": "Danganronpa Another Episode: Ultra Despair Girls",
        "Image": "Monodam_VA_ID.webp",
    },
    {
        "Name": "Monokid",
        "Aliases": "",
        "Title": "Class Representative Robot",
        "Gender": "Male",
        "Height": "Unknown",
        "Weight": "Unknown",
        "Status": "Inactive",
        "Talent Category": "Special",
        "Likes": "",
        "Dislikes": "",
        "First Appearance": "Danganronpa 2: Goodbye Despair",
        "Image": "Monokid_VA_ID.webp",
    },
    {
        "Name": "Monophanie",
        "Aliases": "",
        "Title": "Homeroom Robot",
        "Gender": "Female",
        "Height": "Unknown",
        "Weight": "Unknown",
        "Status": "Inactive",
        "Talent Category": "Special",
        "Likes": "",
        "Dislikes": "",
        "First Appearance": "Danganronpa 2: Goodbye Despair",
        "Image": "Monophanie_VA_ID.webp",
    },
    {
        "Name": "Monosuke",
        "Aliases": "",
        "Title": "Headmaster's Assistant Robot",
        "Gender": "Male",
        "Height": "Unknown",
        "Weight": "Unknown",
        "Status": "Inactive",
        "Talent Category": "Special",
        "Likes": "",
        "Dislikes": "",
        "First Appearance": "Danganronpa 1: Trigger Happy Havoc",
        "Image": "Monosuke_VA_ID.webp",
    },
    {
        "Name": "Monotaro",
        "Aliases": "Bear mascot",
        "Title": "Ultimate Mascot",
        "Gender": "Male",
        "Height": "Unknown",
        "Weight": "Unknown",
        "Status": "Inactive",
        "Talent Category": "Special",
        "Likes": "",
        "Dislikes": "",
        "First Appearance": "Danganronpa 2: Goodbye Despair",
        "Image": "Monotaro_VA_ID.webp",
    },
]

# Characters that may be the daily answer. The mascot robots are guessable but
# never drawn, because almost every attribute of theirs is unknown.
NOT_IN_DAILY_POOL = {"Monodam", "Monokid", "Monophanie", "Monosuke", "Monotaro"}

# ---------------------------------------------------------------------------
# Manual overrides for names that do not match the portrait file names
# ---------------------------------------------------------------------------

# character display name -> (primary portrait, alternate portrait or None)
IMAGE_OVERRIDES = {
    "Usami": ("Usami_VA_ID.webp", None),
    "Byakuya Togami (Imposter)": ("Ultimate_Imposter_VA_ID.webp", None),
    "Celeste Ludenberg": ("Celestia_Ludenberg_VA_ID.webp", None),
    "Toko Fukawa": ("Toko_Fukawa_VA_ID.webp", None),
    "Genocide Jack": ("Genocide_Jack_DRAE_VA_ID.webp", "Toko_Fukawa_DRAE_VA_ID.webp"),
    "Junko Enoshima": (
        "Guide_Project_Junko_Enoshima_16.webp",
        "Guide_Project_Junko_Disguise_10.webp",
    ),
    "Masaru Daimon": ("Masaru_Daimon_VA_ID.webp", None),
    "K1-B0": ("Ki-Bo_VA_ID.webp", None),
    "Miaya Gekkogahara": ("Miaya_Gekkogahara_DR3_VA_ID.webp", None),
}

# Characters without a portrait in resources/image
NO_IMAGE = {
    "Grand Bois Chéri Ludenberg",
    "Izuru Kamakura",
    "Mukuro Ikusaba",
    "Jin Kirigiri",
}

# Display names that read better than the raw CSV value
DISPLAY_NAMES = {
    "Monomi, Usami": "Usami",
    "Byakuya Togami (DR2)": "Byakuya Togami (Imposter)",
    "Masaru Dalmon": "Masaru Daimon",
    "Celestia Ludenburg": "Celeste Ludenberg",
}

EXTRA_ALIASES = {
    "Usami": ["Monomi"],
    "Byakuya Togami (Imposter)": ["Ultimate Imposter"],
    "Masaru Daimon": [],
    "Grand Bois Chéri Ludenberg": ["Chéri"],
}

# Suffixes used by the portrait file names
FILE_SUFFIXES = {
    "VA",
    "ID",
    "AI",
    "DR",
    "DR1",
    "DR2",
    "DR3",
    "DRAE",
    "V3",
    "V2",
    "SB",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def slug(value: str) -> str:
    """Lowercase, strip accents and keep only alphanumerics."""
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def split_list(value: str) -> list[str]:
    """Split a CSV multi-value cell into a clean list."""
    items = []
    for raw in (value or "").split(","):
        item = raw.strip().rstrip("?").strip()
        if not item:
            continue
        if item.lower() in {"none", "unknown", "nan", "n/a", "-"}:
            continue
        items.append(item)
    # keep order, drop duplicates
    seen = set()
    unique = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def to_number(value: str):
    value = (value or "").strip()
    if value.isdigit():
        return int(value)
    return None


def read_characters() -> list[dict]:
    rows = []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if not row.get("Name"):
                continue
            row = {k: (v if v is not None else "") for k, v in row.items()}
            rows.append(row)
    for extra in EXTRA_CHARACTERS:
        rows.append(dict(extra))
    return rows

def find_game(value: str) -> dict:
    """Look a game up by its full name, ignoring punctuation/case."""
    target = slug(value)
    for name, game in GAMES.items():
        if slug(name) == target:
            return game
    raise SystemExit(f"Unknown game: {value!r}")


def build_dataset(rows: list[dict]) -> list[dict]:
    dataset = []
    for row in rows:
        name = row["Name"].strip()
        display = DISPLAY_NAMES.get(name, name)

        game = find_game(row["First Appearance"].strip())
        if game is None:
            raise SystemExit(f"Unknown game for {name!r}: {row['First Appearance']!r}")

        aliases = split_list(row.get("Aliases", ""))
        aliases.extend(EXTRA_ALIASES.get(display, []))

        dataset.append(
            {
                "name": display,
                "aliases": aliases,
                "title": split_list(row.get("Title", "")),
                "gender": row.get("Gender", "").strip(),
                "height": to_number(row.get("Height", "")),
                "weight": to_number(row.get("Weight", "")),
                "status": row.get("Status", "").strip(),
                "talent": row.get("Talent Category", "").strip(),
                "likes": split_list(row.get("Likes", "")),
                "dislikes": split_list(row.get("Dislikes", "")),
                "appearance": game["code"],
                "appearanceLabel": game["label"],
                "series": game["series"],
                "pool": name not in NOT_IN_DAILY_POOL,
            }
        )

    dataset.sort(key=lambda c: (GAME_ORDER[c["appearance"]], slug(c["name"])))
    for index, character in enumerate(dataset, start=1):
        character["id"] = index
    return dataset


def collect_portraits() -> list[tuple[str, Path]]:
    """Return every portrait as (file name, path).

    On the first run the portraits live in resources/image. After a run they
    have been renamed to web/images/<id>.webp, so the mapping CSV is used to
    find them again. This keeps the script re-runnable.
    """
    portraits: list[tuple[str, Path]] = []
    if IMG_DIR.exists():
        for path in sorted(IMG_DIR.glob("*.webp")):
            portraits.append((path.name, path))

    if MAPPING_CSV.exists():
        with MAPPING_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                original = row.get("original_file", "")
                new_file = row.get("new_file", "")
                if not original or not new_file:
                    continue
                if any(name == original for name, _ in portraits):
                    continue
                candidate = ROOT / new_file
                if candidate.exists():
                    portraits.append((original, candidate))

    return portraits


def portrait_key(file_name: str) -> str:
    """Normalise a portrait file name into a comparable name.

    "Chisa_Yukizome_DR3_VA_ID.webp" -> "chisa yukizome"
    """
    stem = Path(file_name).stem
    tokens = []
    for token in stem.split("_"):
        if not token:
            continue
        if token.upper() in FILE_SUFFIXES or token.isdigit():
            continue
        tokens.append(token)
    return slug(" ".join(tokens))


def match_images(dataset: list[dict], portraits: list[tuple[str, Path]]) -> None:
    """Attach the portrait file names to the dataset entries."""
    by_key: dict[str, str] = {}
    for name, _ in portraits:
        by_key.setdefault(portrait_key(name), name)

    used = set()

    for character in dataset:
        override = IMAGE_OVERRIDES.get(character["name"])
        if override is None and character["name"] in NO_IMAGE:
            override = (None, None)

        if override is not None:
            primary, alt = override
            character["source"] = primary
            character["sourceAlt"] = alt
            if primary:
                used.add(primary)
            if alt:
                used.add(alt)
            continue

        found = None
        for candidate in [character["name"], *character["aliases"]]:
            key = slug(candidate)
            if key in by_key:
                found = by_key[key]
                break

        character["source"] = found
        character["sourceAlt"] = None
        if found:
            used.add(found)

    unused = [name for name, _ in portraits if name not in used]
    if unused:
        print("Warning: portraits without a character:")
        for name in unused:
            print(f"  - {name}")
    missing = [c["name"] for c in dataset if not c.get("source")]
    if missing:
        print(f"Characters without a portrait: {', '.join(missing)}")
    return unused


def copy_images(dataset: list[dict], portraits: list[tuple[str, Path]]) -> None:
    """Move/rename the portraits to web/images/<id>.webp."""
    OUT_IMG_DIR.mkdir(parents=True, exist_ok=True)
    paths = dict(portraits)
    mapping = []

    for character in dataset:
        for key, suffix in (("source", ""), ("sourceAlt", "_alt")):
            source_name = character.get(key)
            if not source_name:
                continue
            target_name = f"{character['id']}{suffix}.webp"
            target_path = OUT_IMG_DIR / target_name
            source_path = paths.get(source_name)
            if source_path and source_path.exists() and source_path != target_path:
                shutil.copy2(source_path, target_path)
            elif not target_path.exists():
                raise SystemExit(f"Missing portrait: {source_name} for {character['name']}")
            character[key.replace("source", "image")] = f"images/{target_name}"
            mapping.append(
                {
                    "id": character["id"],
                    "name": character["name"],
                    "original_file": source_name,
                    "new_file": target_path.relative_to(ROOT).as_posix(),
                    "variant": suffix.lstrip("_") or "primary",
                }
            )
        character.pop("source", None)
        character.pop("sourceAlt", None)

    # portraits that were not linked to anybody are kept with a readable name
    linked = {entry["original_file"] for entry in mapping}
    for name, path in portraits:
        if name in linked:
            continue
        shutil.copy2(path, OUT_IMG_DIR / name)

    with MAPPING_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["id", "name", "original_file", "new_file", "variant"]
        )
        writer.writeheader()
        writer.writerows(sorted(mapping, key=lambda r: (r["id"], r["variant"])))

    # the portraits now live in web/images, the source folder is emptied
    for name, path in portraits:
        if path.parent == IMG_DIR and path.exists():
            path.unlink()


def write_js(dataset: list[dict]) -> None:
    OUT_JS.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(dataset, ensure_ascii=False, indent=2)
    OUT_JS.write_text(
        "// AUTO-GENERATED by scripts/build_web_data.py - do not edit by hand.\n"
        "// Source: resources/characters.csv (+ scripts/build_web_data.py extras)\n"
        "window.DANGANDLE_CHARACTERS = " + payload + ";\n",
        encoding="utf-8",
    )


def main() -> None:
    rows = read_characters()
    dataset = build_dataset(rows)
    portraits = collect_portraits()
    match_images(dataset, portraits)
    copy_images(dataset, portraits)
    write_js(dataset)

    pool = [c for c in dataset if c["pool"]]
    missing = [c["name"] for c in dataset if not c.get("image")]
    print(f"characters : {len(dataset)} ({len(pool)} in the daily pool)")
    print(f"portraits  : {len(list(OUT_IMG_DIR.glob('*.webp')))} in web/images")
    if missing:
        print(f"no portrait: {', '.join(missing)}")
    print(f"dataset    : {OUT_JS.relative_to(ROOT)}")
    print(f"mapping    : {MAPPING_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
