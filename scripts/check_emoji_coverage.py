"""Check that every like / dislike of the dataset gets a specific emoji.

    python scripts/check_emoji_coverage.py

Prints the entries that would fall back to the generic "?" emoji, so the
EMOJI_RULES table in docs/js/game.js can be extended.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
GAME_JS = ROOT / "docs" / "js" / "game.js"
DATASET = ROOT / "docs" / "js" / "characters.js"


def load_rules() -> list[tuple[re.Pattern, str]]:
    text = GAME_JS.read_text(encoding="utf-8")
    block = text[text.index("var EMOJI_RULES"):text.index("function emojiFor")]
    rules = re.findall(r'\[/(.*?)/([a-z]*), "(.+?)"\]', block)
    return [(re.compile(pattern, re.IGNORECASE if "i" in flags else 0), emoji) for pattern, flags, emoji in rules]


def load_items() -> set[str]:
    text = DATASET.read_text(encoding="utf-8")
    data = json.loads(text[text.index("["):text.rindex("]") + 1])
    items: set[str] = set()
    for character in data:
        items.update(character.get("likes") or [])
        items.update(character.get("dislikes") or [])
    return items


def main() -> None:
    rules = load_rules()
    items = load_items()
    missing = sorted(item for item in items if not any(rule.search(item) for rule, _ in rules))
    print(f"{len(items)} distinct entries, {len(rules)} rules, {len(missing)} without a specific emoji")
    for item in missing:
        print(f"  - {item}")


if __name__ == "__main__":
    main()
