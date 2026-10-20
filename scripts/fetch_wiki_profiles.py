"""Fetch the official character profiles from the Danganronpa Wiki.

    python scripts/fetch_wiki_profiles.py

Reads the Danganronpa Wiki through its MediaWiki API and stores the profile of
every character in resources/wiki-profiles.json. The file is then merged into
resources/characters.csv by scripts/import_wiki_profiles.py.

Only the official *Likes* / *Dislikes* (and the profile numbers) are used, so
the clues of the game are the ones written by the official artbook / game menus.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "resources" / "wiki-profiles.json"
API = "https://danganronpa.fandom.com/api.php"

# Danganronpa Wiki page of every character used by the game
PAGES = [
    "Monokuma", "Makoto Naegi", "Aoi Asahina", "Byakuya Togami", "Celestia Ludenberg",
    "Chihiro Fujisaki", "Hifumi Yamada", "Junko Enoshima", "Kiyotaka Ishimaru",
    "Kyoko Kirigiri", "Leon Kuwata", "Mondo Owada", "Mukuro Ikusaba", "Sakura Ogami",
    "Sayaka Maizono", "Toko Fukawa", "Genocide Jack", "Yasuhiro Hagakure", "Usami",
    "Jin Kirigiri", "Hajime Hinata", "Akane Owari", "Ultimate Imposter",
    "Chiaki Nanami (Danganronpa 2)", "Fuyuhiko Kuzuryu", "Gundham Tanaka",
    "Hiyoko Saionji", "Ibuki Mioda", "Kazuichi Soda", "Mahiru Koizumi", "Mikan Tsumiki",
    "Nagito Komaeda", "Nekomaru Nidai", "Peko Pekoyama", "Sonia Nevermind",
    "Teruteru Hanamura", "Komaru Naegi", "Yuta Asahina", "Taichi Fujisaki",
    "Hiroko Hagakure", "Shirokuma", "Kurokuma", "Jataro Kemuri", "Kotoko Utsugi",
    "Masaru Daimon", "Monaca Towa", "Nagisa Shingetsu", "Haiji Towa", "Kaede Akamatsu",
    "Angie Yonaga", "Gonta Gokuhara", "Himiko Yumeno", "K1-B0", "Kaito Momota",
    "Kirumi Tojo", "Kokichi Oma", "Korekiyo Shinguji", "Maki Harukawa", "Miu Iruma",
    "Rantaro Amami", "Ryoma Hoshi", "Shuichi Saihara", "Tenko Chabashira",
    "Tsumugi Shirogane", "Chisa Yukizome", "Daisaku Bandai", "Great Gozu",
    "Juzo Sakakura", "Kazuo Tengan", "Koichi Kizakura", "Kyosuke Munakata",
    "Ruruka Ando", "Ryota Mitarai", "Sonosuke Izayoi", "Seiko Kimura",
    "Miaya Gekkogahara", "Monodam", "Monokid", "Monophanie", "Monosuke", "Monotaro",
]

USER_AGENT = "Dangandle/1.0 (https://github.com/Nihhiu/Dangandle)"


class InfoboxParser(HTMLParser):
    """Pulls the values of the portable infobox out of a wiki page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.values: dict[str, str] = {}
        self._source: str | None = None
        self._in_value = False
        self._in_item = False
        self._buffer: list[str] = []
        self._items: list[str] = []
        self._skip = 0
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "")
        if tag == "div" and "pi-data-value" in classes:
            if self._source is not None:
                self._in_value = True
                self._depth = 1
                self._buffer = []
                self._items = []
            return
        if tag == "div" and "pi-data" in classes:
            self._source = attributes.get("data-source")
            self._buffer = []
            self._items = []
            self._in_value = False
            self._depth = 0
            return
        if self._in_value and tag == "div":
            self._depth += 1
            return
        if self._in_value:
            if tag == "li":
                self._in_item = True
                self._buffer = []
            elif tag == "sup":
                self._skip += 1

    def handle_endtag(self, tag):
        if self._source is None:
            return
        if tag == "sup" and self._skip:
            self._skip -= 1
        elif tag == "li" and self._in_item:
            self._in_item = False
            self._items.append(clean_text("".join(self._buffer)))
            self._buffer = []
        elif tag == "div" and self._in_value:
            self._depth -= 1
            if self._depth > 0:
                return
            self._in_value = False
            text = clean_text("".join(self._buffer))
            if text and not self._items:
                self._items = [text]
            if self._source in ("likes", "dislikes"):
                self.values[self._source] = self._items
            else:
                self.values[self._source] = text
            self._source = None
        elif tag == "div" and self._source:
            self._source = None

    def handle_data(self, data):
        if self._source is not None and self._in_value and not self._skip:
            self._buffer.append(data)


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def strip_tags(html: str) -> str:
    html = re.sub(r"<sup[^>]*>.*?</sup>", " ", html, flags=re.S)
    html = re.sub(r"<[^>]+>", " ", html)
    html = html.replace(">", " ")  # the wiki uses ">" to separate the values
    return clean_text(html)


def raw_value(html: str, source: str) -> str | None:
    """Fallback for the values the wiki renders with a converter template."""
    match = re.search(
        r'data-source="%s".*?class="pi-data-value[^"]*"(.*?)</div>' % re.escape(source),
        html,
        flags=re.S,
    )
    if not match:
        return None
    text = strip_tags(match.group(1))
    return text or None


def fetch(page: str) -> str:
    query = urllib.parse.urlencode(
        {"action": "parse", "page": page, "prop": "text", "format": "json", "origin": "*"}
    )
    request = urllib.request.Request(f"{API}?{query}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload["parse"]["text"]["*"]


def main() -> None:
    profiles: dict[str, dict] = {}
    for page in PAGES:
        try:
            html = fetch(page)
        except Exception as error:  # noqa: BLE001 - keep going, report at the end
            print(f"! {page}: {error}")
            continue
        parser = InfoboxParser()
        parser.feed(html)
        values = parser.values
        for source in ("height", "weight"):
            if not values.get(source):
                fallback = raw_value(html, source)
                if fallback:
                    values[source] = fallback
        profiles[page] = {
            "likes": values.get("likes") or None,
            "dislikes": values.get("dislikes") or None,
            "height": values.get("height") or None,
            "weight": values.get("weight") or None,
            "gender": values.get("gender") or None,
            "status": values.get("status") or None,
            "talent": values.get("english talent") or None,
            "debut": values.get("game debut") or None,
        }
        likes = len(profiles[page]["likes"] or [])
        print(f"  {page}: {likes} likes")
        time.sleep(0.2)

    OUT.write_text(json.dumps(profiles, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"saved {len(profiles)} profiles -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
