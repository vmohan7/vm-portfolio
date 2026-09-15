#!/usr/bin/env python3
"""Focused, dependency-free checks for the static portfolio."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "index.html"
CSS_PATH = ROOT / "styles.css"
JS_PATH = ROOT / "script.js"


class PortfolioParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.hrefs: list[tuple[str, dict[str, str]]] = []
        self.images: list[dict[str, str]] = []
        self.heading_levels: list[int] = []
        self.scripts: list[dict[str, str]] = []
        self.stylesheets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        element_id = data.get("id")
        if element_id:
            if element_id in self.ids:
                self.duplicate_ids.add(element_id)
            self.ids.add(element_id)
        if tag == "a":
            self.hrefs.append((data.get("href", ""), data))
        elif tag == "img":
            self.images.append(data)
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.heading_levels.append(int(tag[1]))
        elif tag == "script":
            self.scripts.append(data)
        elif tag == "link" and "stylesheet" in data.get("rel", "").split():
            self.stylesheets.append(data.get("href", ""))


def check(condition: bool, message: str, failures: list[str]) -> None:
    if condition:
        print(f"PASS  {message}")
    else:
        print(f"FAIL  {message}")
        failures.append(message)


def local_target_exists(reference: str) -> bool:
    clean = reference.split("#", 1)[0].split("?", 1)[0]
    return not clean or (ROOT / clean).is_file()


def main() -> int:
    failures: list[str] = []
    required = [
        HTML_PATH,
        CSS_PATH,
        JS_PATH,
        ROOT / "README.md",
        ROOT / "CONTENT.md",
        ROOT / ".nojekyll",
        ROOT / "assets/favicon.svg",
        ROOT / "tests/check_copy.js",
    ]
    check(all(path.exists() for path in required), "all required public files exist", failures)

    html = HTML_PATH.read_text(encoding="utf-8")
    css = CSS_PATH.read_text(encoding="utf-8")
    js = JS_PATH.read_text(encoding="utf-8")
    parser = PortfolioParser()
    parser.feed(html)
    parser.close()

    check(not parser.duplicate_ids, "HTML ids are unique", failures)
    check(parser.heading_levels and parser.heading_levels[0] == 1, "heading outline starts with one h1", failures)
    check(parser.heading_levels.count(1) == 1, "page contains exactly one h1", failures)
    check(all(b - a <= 1 for a, b in zip(parser.heading_levels, parser.heading_levels[1:])), "heading levels do not skip downward", failures)

    fragments = [href[1:] for href, _ in parser.hrefs if href.startswith("#") and len(href) > 1]
    check(all(fragment in parser.ids for fragment in fragments), "all internal navigation fragments resolve", failures)

    local_refs = [
        href for href, _ in parser.hrefs if href and not href.startswith(("#", "http://", "https://", "mailto:", "tel:"))
    ]
    local_refs.extend(parser.stylesheets)
    local_refs.extend(data.get("src", "") for data in parser.scripts if data.get("src"))
    check(all(local_target_exists(ref) for ref in local_refs), "all local HTML assets resolve", failures)

    external_links = [data for href, data in parser.hrefs if href.startswith(("http://", "https://"))]
    check(
        all(data.get("target") == "_blank" and {"noopener", "noreferrer"}.issubset(set(data.get("rel", "").split())) for data in external_links),
        "external content links use safe new-tab attributes",
        failures,
    )
    check(all(data.get("alt", "").strip() for data in parser.images), "all images have non-empty alt text", failures)
    check(len(parser.images) == 2 and all("i.ytimg.com/vi/" in data.get("src", "") for data in parser.images), "only the two verified video previews are present", failures)

    required_sources = [
        "https://sambanova.ai/blog/first-disaggregated-inference-demo-for-ai-agents-live",
        "https://www.youtube.com/watch?v=7klpNFoI6Cs",
        "https://www.youtube.com/watch?v=ekB2HKu8__M",
        "https://www.linkedin.com/in/v-mohan",
        "https://github.com/vmohan7",
    ]
    check(all(source in html for source in required_sources), "all verified public links are present", failures)
    check("June 3, 2026" in html and "AI By the Bay · 2025" in html, "verified dates are present", failures)

    public_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.parts
    )
    sensitive_patterns = [
        r"/(?:root|home)/[^\s<]+",
        r"(?<!\d)-\d{9,}(?!\d)",
        r"(?:api|auth|bot)[_-]?(?:key|token)\s*[:=]",
    ]
    check(not any(re.search(pattern, public_text, re.IGNORECASE) for pattern in sensitive_patterns), "public files exclude path, identifier, and secret-shaped data", failures)

    check("prefers-reduced-motion" in css and ":focus-visible" in css, "CSS includes reduced-motion and visible-focus treatments", failures)
    check("navigator.clipboard" in js and "document.execCommand(\"copy\")" in js, "copy control includes modern and fallback clipboard paths", failures)
    check('role="status"' in html and 'aria-live="polite"' in html, "copy feedback has a polite live region", failures)
    check(not re.search(r"(?:src|href)=[\"']/", html), "asset references are project-path-safe", failures)

    print(f"\n{len(failures)} failure(s); {17 - len(failures)}/17 checks passed.")
    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
