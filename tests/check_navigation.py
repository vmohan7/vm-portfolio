#!/usr/bin/env python3
"""Focused contract test for the five-page portfolio navigation."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "index.html": "Home",
    "writing.html": "Writing",
    "talks.html": "Talks",
    "gallery.html": "Gallery",
    "about.html": "About",
}


class NavigationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_primary_nav = False
        self.nav_depth = 0
        self.links: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "nav" and data.get("aria-label") == "Primary navigation":
            self.in_primary_nav = True
            self.nav_depth = 1
            return
        if self.in_primary_nav:
            if tag == "nav":
                self.nav_depth += 1
            elif tag == "a":
                self.links.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.in_primary_nav and tag == "nav":
            self.nav_depth -= 1
            if self.nav_depth == 0:
                self.in_primary_nav = False


def main() -> int:
    failures: list[str] = []
    expected_hrefs = list(PAGES)

    for filename in PAGES:
        path = ROOT / filename
        if not path.is_file():
            failures.append(f"{filename}: page is missing")
            continue

        parser = NavigationParser()
        parser.feed(path.read_text(encoding="utf-8"))
        parser.close()
        hrefs = [link.get("href", "") for link in parser.links]
        current = [link.get("href", "") for link in parser.links if link.get("aria-current") == "page"]

        if hrefs != expected_hrefs:
            failures.append(f"{filename}: primary navigation must link to {expected_hrefs}, got {hrefs}")
        if current != [filename]:
            failures.append(f"{filename}: aria-current must identify only {filename}, got {current}")

    if failures:
        for failure in failures:
            print(f"FAIL  {failure}")
        print(f"\n{len(failures)} navigation failure(s).")
        return 1

    print("PASS  all five root pages expose the shared page navigation")
    print("PASS  each page identifies its current navigation link")
    return 0


if __name__ == "__main__":
    sys.exit(main())
