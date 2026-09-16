#!/usr/bin/env python3
"""Dependency-free structure, content, and provenance checks for the portfolio."""

from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PAGE_NAMES = ("index.html", "writing.html", "talks.html", "gallery.html", "about.html")
CSS_PATH = ROOT / "styles.css"
JS_PATH = ROOT / "script.js"
EXPECTED_IMAGES = {
    "index.html": ["assets/vasanth-mohan.jpg"],
    "writing.html": [],
    "talks.html": [
        "https://i.ytimg.com/vi/7klpNFoI6Cs/maxresdefault.jpg",
        "https://i.ytimg.com/vi/ekB2HKu8__M/maxresdefault.jpg",
        "assets/presentations/awe-2021.jpg",
        "assets/presentations/entervr-2019.jpg",
    ],
    "gallery.html": [
        "assets/gallery/raise-summit.jpg",
        "assets/gallery/ai-infra-summit.jpg",
        "assets/gallery/gtc-community.jpg",
        "assets/gallery/sambahouse-germany.jpg",
        "assets/gallery/crewai-signals.jpg",
        "assets/gallery/step-sf.jpg",
        "assets/gallery/llamacon.jpg",
        "assets/gallery/hackutd.jpg",
        "assets/gallery/austin-meetup.jpg",
    ],
    "about.html": ["assets/vasanth-mohan.jpg"],
}
EXPECTED_DECLARED_DIMENSIONS = {
    "assets/vasanth-mohan.jpg": ("800", "800"),
    "assets/presentations/awe-2021.jpg": ("1280", "720"),
    "assets/presentations/entervr-2019.jpg": ("328", "328"),
    "assets/gallery/raise-summit.jpg": ("800", "600"),
    "assets/gallery/ai-infra-summit.jpg": ("800", "600"),
    "assets/gallery/gtc-community.jpg": ("800", "600"),
    "assets/gallery/sambahouse-germany.jpg": ("800", "600"),
    "assets/gallery/crewai-signals.jpg": ("800", "600"),
    "assets/gallery/step-sf.jpg": ("800", "533"),
    "assets/gallery/llamacon.jpg": ("800", "600"),
    "assets/gallery/hackutd.jpg": ("800", "600"),
    "assets/gallery/austin-meetup.jpg": ("800", "600"),
}
ADDITIONAL_GALLERY_SOURCES = {
    "sambahouse-germany": "7426775333942566912",
    "crewai-signals": "7397782776374202369",
    "step-sf": "7365762381819400194",
    "llamacon": "7323033654866169856",
    "hackutd": "7264755844301352960",
    "austin-meetup": "7247411762680004610",
}
REQUIRED_SOURCES = {
    "https://sambanova.ai/blog/first-disaggregated-inference-demo-for-ai-agents-live",
    "https://www.youtube.com/watch?v=7klpNFoI6Cs",
    "https://www.youtube.com/watch?v=ekB2HKu8__M",
    "https://www.youtube.com/watch?v=CXUXfpjjcPQ",
    "https://www.linkedin.com/in/v-mohan",
    "https://github.com/vmohan7",
    "https://www.linkedin.com/feed/update/urn:li:activity:7480532691969536000/",
    "https://www.linkedin.com/feed/update/urn:li:activity:7456100760976789504/",
    "https://www.linkedin.com/feed/update/urn:li:activity:7440461672286240768/",
    "https://www.awexr.com/usa-2021/agenda/2443-5g-edge-compute-essential-infrastructure-to-scale-",
    "https://www.iheart.com/podcast/256-entervr-30992177/episode/exploring-the-current-landscape-of-the-metaverse-with-vasanth-mohan-from-fused-vr-54189932",
    "https://www.oreilly.com/library/view/creating-augmented-and/9781492044185/cover.html",
    "https://medium.com/fusedvr/implementing-vr-scene-transitions-c27861a9ac77",
    "https://www.youtube.com/c/FusedVR",
}
VOID_ELEMENTS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
REQUIRED_SOURCES.update(
    f"https://www.linkedin.com/feed/update/urn:li:activity:{activity}/"
    for activity in ADDITIONAL_GALLERY_SOURCES.values()
)


class PortfolioParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.hrefs: list[tuple[str, dict[str, str]]] = []
        self.images: list[dict[str, str]] = []
        self.heading_levels: list[int] = []
        self.scripts: list[dict[str, str]] = []
        self.link_elements: list[dict[str, str]] = []
        self.copy_targets: list[str] = []
        self.live_regions: list[dict[str, str]] = []
        self.bio_h4_count = 0
        self.stack: list[tuple[str, set[str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        classes = set(data.get("class", "").split())
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
            if tag == "h4" and any("bio-block" in ancestor_classes for _, ancestor_classes in self.stack):
                self.bio_h4_count += 1
        elif tag == "script":
            self.scripts.append(data)
        elif tag == "link":
            self.link_elements.append(data)
        if data.get("data-copy-target"):
            self.copy_targets.append(data["data-copy-target"])
        if data.get("role") == "status":
            self.live_regions.append(data)
        if tag not in VOID_ELEMENTS:
            self.stack.append((tag, classes))

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return


class Checks:
    def __init__(self) -> None:
        self.total = 0
        self.failures: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        self.total += 1
        if condition:
            print(f"PASS  {message}")
        else:
            print(f"FAIL  {message}")
            self.failures.append(message)


def is_external(reference: str) -> bool:
    return reference.startswith(("http://", "https://", "mailto:", "tel:"))


def resolve_local(reference: str, source_path: Path) -> Path | None:
    clean = reference.split("#", 1)[0].split("?", 1)[0]
    if not clean:
        return source_path
    if clean.startswith("/"):
        return None
    target = (source_path.parent / clean).resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return target


def main() -> int:
    checks = Checks()
    page_paths = {name: ROOT / name for name in PAGE_NAMES}
    required = [
        *page_paths.values(),
        CSS_PATH,
        JS_PATH,
        ROOT / "README.md",
        ROOT / "CONTENT.md",
        ROOT / ".nojekyll",
        ROOT / "assets/favicon.svg",
        ROOT / "tests/check_navigation.py",
        ROOT / "tests/check_copy.js",
    ]
    checks.check(all(path.is_file() for path in required), "all five pages and required public files exist")

    html_by_page = {name: path.read_text(encoding="utf-8") for name, path in page_paths.items()}
    parsers: dict[str, PortfolioParser] = {}
    for name, markup in html_by_page.items():
        parser = PortfolioParser()
        parser.feed(markup)
        parser.close()
        parsers[name] = parser

    checks.check(all(not parser.duplicate_ids for parser in parsers.values()), "HTML ids are unique within every page")
    checks.check(
        all(parser.heading_levels and parser.heading_levels[0] == 1 and parser.heading_levels.count(1) == 1 for parser in parsers.values()),
        "every page starts its outline with exactly one h1",
    )
    checks.check(
        all(all(next_level - level <= 1 for level, next_level in zip(parser.heading_levels, parser.heading_levels[1:])) for parser in parsers.values()),
        "heading levels do not skip downward on any page",
    )

    unresolved_fragments: list[str] = []
    missing_local_refs: list[str] = []
    for name, parser in parsers.items():
        source_path = page_paths[name]
        refs = [href for href, _ in parser.hrefs]
        refs.extend(data.get("src", "") for data in parser.images)
        refs.extend(data.get("src", "") for data in parser.scripts if data.get("src"))
        refs.extend(data.get("href", "") for data in parser.link_elements if data.get("href"))
        for reference in refs:
            if not reference or is_external(reference):
                continue
            target = resolve_local(reference, source_path)
            if target is None or not target.is_file():
                missing_local_refs.append(f"{name}: {reference}")

        for href, _ in parser.hrefs:
            if is_external(href) or "#" not in href:
                continue
            path_part, fragment = href.split("#", 1)
            if not fragment:
                continue
            target = resolve_local(path_part, source_path)
            target_name = target.name if target else ""
            if target_name not in parsers or fragment not in parsers[target_name].ids:
                unresolved_fragments.append(f"{name}: {href}")

    checks.check(not missing_local_refs, "all local page, stylesheet, script, icon, and image references resolve")
    checks.check(not unresolved_fragments, "same-page and cross-page fragments resolve")
    checks.check(
        all(
            [data.get("href", "") for data in parser.link_elements if "stylesheet" in data.get("rel", "").split()] == ["styles.css?v=4"]
            for parser in parsers.values()
        ),
        "all five pages use the versioned shared stylesheet",
    )

    external_links = [data for parser in parsers.values() for href, data in parser.hrefs if href.startswith(("http://", "https://"))]
    checks.check(
        all(data.get("target") == "_blank" and {"noopener", "noreferrer"}.issubset(set(data.get("rel", "").split())) for data in external_links),
        "external content links use safe new-tab attributes",
    )

    actual_images = {name: [data.get("src", "") for data in parser.images] for name, parser in parsers.items()}
    checks.check(actual_images == EXPECTED_IMAGES, "images match the source-backed per-page inventory")
    archive_previews = re.findall(
        r'<li class="archive-item talk-entry"[^>]*>.*?</li>', html_by_page["talks.html"], re.DOTALL
    )
    checks.check(
        len(archive_previews) == 2 and all(
            f'assets/presentations/{name}.jpg' in item
            and f'href="{source}"' in item
            and 'class="video-preview' in item
            and 'loading="lazy"' in item
            for name, source, item in zip(
                ("awe-2021", "entervr-2019"),
                ("https://www.youtube.com/watch?v=CXUXfpjjcPQ",
                 "https://www.iheart.com/podcast/256-entervr-30992177/episode/exploring-the-current-landscape-of-the-metaverse-with-vasanth-mohan-from-fused-vr-54189932"),
                archive_previews,
            )
        ),
        "both earlier presentations have lazy-loaded source-linked previews in the shared talk layout",
    )
    gallery_figures = re.findall(r"<figure\b[^>]*>.*?</figure>", html_by_page["gallery.html"], re.DOTALL)
    checks.check(
        len(gallery_figures) == 9 and all(
            sum(
                f'src="assets/gallery/{name}.jpg"' in figure
                and f'https://www.linkedin.com/feed/update/urn:li:activity:{activity}/' in figure
                and 'loading="lazy"' in figure
                for figure in gallery_figures
            ) == 1
            for name, activity in ADDITIONAL_GALLERY_SOURCES.items()
        ),
        "nine gallery photographs retain their own source links and new images load lazily",
    )
    checks.check(
        all(
            len(data.get("alt", "").strip()) >= 12 and data.get("alt", "").strip().lower() not in {"image", "photo", "portrait", "thumbnail"}
            for parser in parsers.values()
            for data in parser.images
        ),
        "all images have meaningful alt text",
    )
    checks.check(
        all(
            (data.get("width", ""), data.get("height", "")) == EXPECTED_DECLARED_DIMENSIONS[data["src"]]
            for parser in parsers.values()
            for data in parser.images
            if data.get("src") in EXPECTED_DECLARED_DIMENSIONS
        ),
        "local image dimensions match the supplied JPEG files",
    )

    local_image_paths = {
        resolve_local(data["src"], page_paths[name])
        for name, parser in parsers.items()
        for data in parser.images
        if data.get("src") and not is_external(data["src"])
    }
    checks.check(
        all(path and path.stat().st_size > 1024 and path.read_bytes().startswith(b"\xff\xd8\xff") for path in local_image_paths),
        "local portfolio photographs are non-empty JPEG files",
    )

    combined_html = "\n".join(html_by_page.values())
    content_ledger = (ROOT / "CONTENT.md").read_text(encoding="utf-8")
    checks.check(all(source in combined_html for source in REQUIRED_SOURCES), "all verified public sources remain linked from the appropriate pages")
    checks.check(all(source in content_ledger for source in REQUIRED_SOURCES), "CONTENT.md retains every published source")
    checks.check(
        {"earlier-work", "awe-2021", "entervr-2019"}.issubset(parsers["talks.html"].ids)
        and {"earlier-work", "ar-vr-book-2019", "vr-transitions-2017"}.issubset(parsers["writing.html"].ids)
        and all(f'datetime="{date}"' in html_by_page[page] for page, date in (
            ("talks.html", "2021-11-11"), ("talks.html", "2019-12-17"),
            ("writing.html", "2019-04"), ("writing.html", "2017-06-08"),
        )),
        "four verified earlier selections are grouped and explicitly dated",
    )
    checks.check(
        all("https://www.linkedin.com/in/v-mohan" in markup and "https://github.com/vmohan7" in markup for markup in html_by_page.values()),
        "every page retains the verified profile links",
    )
    checks.check("June 3, 2026" in html_by_page["writing.html"] and "AI By the Bay · 2025" in html_by_page["talks.html"], "verified publication and event dates remain attached to their sources")
    checks.check(not re.search(r"\b20\d{2}\b", html_by_page["gallery.html"]), "gallery copy does not infer event dates")
    checks.check(
        all(caption in html_by_page["gallery.html"] for caption in ("RAISE Summit, Paris", "AI Infra Summit", "Developer gatherings around GTC")),
        "gallery retains the original conservative event captions",
    )
    checks.check(
        "Head of Dev Rel &amp; Product Marketing" in combined_html and "San Jose, California" in combined_html,
        "profile role and location match the verified LinkedIn wording",
    )
    linkedin_headline = "Head of Dev Rel & Product Marketing @ SambaNova | Agentic AI, Fast & Energy-Efficient Inference, Sovereign AI"
    short_versions = [
        re.search(pattern, html_by_page[page])
        for page, pattern in (
            ("index.html", r'<p class="page-lede">([^<]+)</p>'),
            ("about.html", r'<p class="about-lead">([^<]+)</p>'),
            ("about.html", r'<p id="short-bio">([^<]+)</p>'),
        )
    ]
    checks.check(
        all(match and unescape(match.group(1)).strip() == linkedin_headline for match in short_versions),
        "the short bio and page introductions use the LinkedIn headline verbatim",
    )
    full_bio_match = re.search(r'<p id="full-bio">(.*?)</p>', html_by_page["about.html"], re.DOTALL)
    full_bio_text = unescape(re.sub(r"<[^>]+>", "", full_bio_match.group(1))).strip() if full_bio_match else ""
    checks.check(
        200 <= len(full_bio_text.split()) <= 350
        and len(full_bio_text.split("\n\n")) == 4
        and all(topic in full_bio_text for topic in (
            "SambaNova", "MobiledgeX", "FusedVR", "Unity", "SteamVR",
            "Creating Augmented and Virtual Realities", "Erin Pangilinan", "Steve Lukas",
            "AI By the Bay", "Hacking Agents", "AWE USA", "EnterVR",
        )),
        "the full bio covers the verified career in four copyable paragraphs",
    )

    prohibited_copy = ("forthcoming", "credits will appear", "no stock", "official gtc", "main-stage", "main stage")
    checks.check(not any(phrase in combined_html.lower() for phrase in prohibited_copy), "public pages contain no placeholder or inflated event copy")
    checks.check("production credits" not in combined_html.lower(), "unverified production credits remain documentation-only")

    about = parsers["about.html"]
    checks.check(
        about.copy_targets == ["short-bio", "full-bio"] and all(not parsers[name].copy_targets for name in PAGE_NAMES if name != "about.html"),
        "copy controls are present only for the two About-page bios",
    )
    checks.check(set(about.copy_targets).issubset(about.ids) and about.bio_h4_count == 2, "each copy control targets a bio-block with its h4 label")
    checks.check(
        len(about.live_regions) == 1 and about.live_regions[0].get("aria-live") == "polite",
        "copy feedback has one polite live region on About",
    )
    checks.check(
        [data.get("src", "") for data in about.scripts if data.get("src")] == ["script.js"]
        and all(not [data.get("src", "") for data in parsers[name].scripts if data.get("src")] for name in PAGE_NAMES if name != "about.html"),
        "the copy script loads only where the controls exist",
    )

    text_suffixes = {".html", ".css", ".js", ".md", ".py", ".svg"}
    text_names = {".gitignore", ".nojekyll"}
    public_text_parts: list[str] = []
    text_decode_ok = True
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in text_suffixes and path.name not in text_names:
            continue
        try:
            public_text_parts.append(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            text_decode_ok = False
    public_text = "\n".join(public_text_parts)
    checks.check(text_decode_ok, "declared text files decode as UTF-8 while binary assets are skipped")
    sensitive_patterns = [
        r"/(?:root|home)/[^\s<]+",
        r"(?<!\d)-\d{9,}(?!\d)",
        r"(?:api|auth|bot)[_-]?(?:key|token)\s*[:=]",
    ]
    checks.check(not any(re.search(pattern, public_text, re.IGNORECASE) for pattern in sensitive_patterns), "public text excludes path, identifier, and secret-shaped data")

    css = CSS_PATH.read_text(encoding="utf-8")
    js = JS_PATH.read_text(encoding="utf-8")
    checks.check("prefers-reduced-motion" in css and ":focus-visible" in css, "CSS includes reduced-motion and visible-focus treatments")
    checks.check(
        bool(re.search(r"\.cover-preview img\s*\{[^}]*object-fit:\s*contain\b", css))
        and bool(re.search(r"\.cover-preview img\s*\{[^}]*object-position:\s*center\b", css)),
        "podcast artwork is centered without cropping inside the shared preview frame",
    )
    mobile_css = css.split("@media (max-width: 760px)", 1)[-1].split("@media", 1)[0]
    checks.check(
        bool(re.search(r"\.portrait-frame\s*\{[^}]*justify-self:\s*center\b", mobile_css)),
        "Home and About portraits are centered in the single-column mobile layout",
    )
    checks.check(
        "font-size: clamp(2.15rem, 5vw, 3rem)" in css and "font-size: clamp(1.55rem, 3vw, 1.875rem)" in css,
        "type scale caps page titles at 48px and section titles at 30px",
    )
    checks.check("text-transform: uppercase" not in css and "calc(100vh" not in css, "CSS avoids heavy all-caps and viewport-filling sections")
    checks.check("navigator.clipboard" in js and 'document.execCommand("copy")' in js, "copy control includes modern and fallback clipboard paths")
    checks.check(not re.search(r"(?:src|href)=[\"']/", combined_html), "asset references are project-path-safe")

    passed = checks.total - len(checks.failures)
    print(f"\n{len(checks.failures)} failure(s); {passed}/{checks.total} checks passed.")
    if checks.failures:
        print("Failures:")
        for failure in checks.failures:
            print(f"- {failure}")
        if missing_local_refs:
            print("Missing local references:")
            for reference in missing_local_refs:
                print(f"- {reference}")
        if unresolved_fragments:
            print("Unresolved fragments:")
            for reference in unresolved_fragments:
                print(f"- {reference}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
