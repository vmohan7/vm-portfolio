#!/usr/bin/env python3
"""Exercise the Pages artifact and automatic crawl-file generation."""

from pathlib import Path
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_site import BASE, NAMESPACE, build, generate_crawl_files  # noqa: E402


def urls_from(path: Path) -> list[str]:
    tree = ET.parse(path)
    return [node.text or "" for node in tree.findall(f".//{{{NAMESPACE}}}loc")]


with tempfile.TemporaryDirectory(prefix="site-build-", dir=ROOT) as temp:
    stage = Path(temp) / "output"
    urls = build(ROOT, stage)
    assert urls == urls_from(stage / "sitemap.xml")
    assert len(urls) == len(list(ROOT.glob("*.html")))
    assert urls[0] == BASE and len(urls) == len(set(urls))
    assert (stage / "robots.txt").read_text(encoding="utf-8") == (
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE}sitemap.xml\n"
    )
    assert (stage / "CNAME").read_text(encoding="utf-8").strip() == "www.vasanthmohan.com"
    assert all((stage / page.name).read_bytes() == page.read_bytes() for page in ROOT.glob("*.html"))
    assert (stage / "assets/vasanth-mohan.jpg").is_file()
    assert not (stage / ".git").exists() and not (stage / "CONTENT.md").exists()
    assert not (stage / "README.md").exists() and not (stage / "tests").exists()
    print("PASS  generated artifact has current canonical pages, crawl files and public assets only")

with tempfile.TemporaryDirectory(prefix="site-fixture-") as temp:
    fixture = Path(temp)
    for name in ("index.html", "writing.html"):
        shutil.copy2(ROOT / name, fixture / name)
    text = (fixture / "writing.html").read_text(encoding="utf-8")
    (fixture / "notes.html").write_text(text.replace(BASE + "writing.html", BASE + "notes.html"), encoding="utf-8")
    extra_urls = generate_crawl_files(fixture, fixture)
    assert extra_urls == [BASE, BASE + "notes.html", BASE + "writing.html"]
    assert urls_from(fixture / "sitemap.xml") == extra_urls
    print("PASS  adding a canonical HTML page automatically adds it to the sitemap")

print("PASS  artifact builder checks completed")
