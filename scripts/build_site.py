#!/usr/bin/env python3
"""Build a minimal GitHub Pages artifact and derive its crawl files from HTML."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.vasanthmohan.com/"
NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"


class PageHead(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonicals: list[str] = []
        self.robots: list[str] = []
        self.titles = 0
        self.descriptions = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag == "title":
            self.titles += 1
        elif tag == "link" and "canonical" in (data.get("rel") or "").split():
            self.canonicals.append(data.get("href") or "")
        elif tag == "meta" and (data.get("name") or "").lower() == "robots":
            self.robots.append(data.get("content") or "")
        elif tag == "meta" and (data.get("name") or "").lower() == "description":
            self.descriptions += 1


def discover_pages(root: Path) -> list[Path]:
    pages = sorted(root.glob("*.html"), key=lambda p: (p.name != "index.html", p.name))
    if not pages or pages[0].name != "index.html":
        raise ValueError("The public index.html page is required")
    for page in pages:
        expected = BASE + ("" if page.name == "index.html" else page.name)
        head = PageHead()
        head.feed(page.read_text(encoding="utf-8"))
        if head.canonicals != [expected] or head.titles != 1 or head.descriptions != 1:
            raise ValueError(f"{page.name} needs one title, description and canonical {expected}")
        if any("noindex" in directive.lower() for directive in head.robots):
            raise ValueError(f"{page.name} requests noindex")
    return pages


def generate_crawl_files(root: Path, output: Path) -> list[str]:
    pages = discover_pages(root)
    urls = [BASE + ("" if page.name == "index.html" else page.name) for page in pages]
    ET.register_namespace("", NAMESPACE)
    urlset = ET.Element(f"{{{NAMESPACE}}}urlset")
    for url in urls:
        ET.SubElement(ET.SubElement(urlset, f"{{{NAMESPACE}}}url"), f"{{{NAMESPACE}}}loc").text = url
    ET.indent(urlset, space="  ")
    ET.ElementTree(urlset).write(output / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    (output / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: " + BASE + "sitemap.xml\n", encoding="utf-8"
    )
    return urls


def build(root: Path, output: Path) -> list[str]:
    root = root.resolve()
    output = output.resolve()
    if output == root or root not in output.parents:
        raise ValueError("Output must be a staging directory inside the repository")
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"Refusing to overwrite nonempty staging directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    pages = discover_pages(root)
    for page in pages:
        shutil.copy2(page, output / page.name)
    for name in ("styles.css", "script.js", "CNAME", ".nojekyll"):
        shutil.copy2(root / name, output / name)
    shutil.copytree(root / "assets", output / "assets")
    if (output / "CNAME").read_text(encoding="utf-8").strip() != "www.vasanthmohan.com":
        raise ValueError("CNAME and canonical host disagree")
    return generate_crawl_files(root, output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    urls = build(ROOT, args.output)
    print(f"Built {len(urls)} canonical pages in {args.output} with sitemap.xml and robots.txt")
