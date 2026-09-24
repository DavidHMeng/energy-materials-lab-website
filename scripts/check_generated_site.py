#!/usr/bin/env python3
"""Check required routes, internal links, assets, and key rendered invariants."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


class SiteHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references: list[tuple[str, str]] = []
        self.image_alts: list[str | None] = []
        self.html_lang: str | None = None
        self.nav_depth = 0
        self.footer_depth = 0
        self.footer_has_nav = False
        self.current_nav_link = False
        self.nav_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "html":
            self.html_lang = values.get("lang")
        if tag == "nav":
            self.nav_depth += 1
            if self.footer_depth:
                self.footer_has_nav = True
        if tag == "footer":
            self.footer_depth += 1
        if tag == "a" and values.get("href"):
            self.references.append(("link", values["href"]))
            classes = set(values.get("class", "").split())
            self.current_nav_link = self.nav_depth > 0 and "language-toggle" not in classes
        if tag in {"img", "script"} and values.get("src"):
            self.references.append(("asset", values["src"]))
        if tag == "link" and values.get("href"):
            rel = set(values.get("rel", "").split())
            if rel & {"stylesheet", "icon"}:
                self.references.append(("asset", values["href"]))
        if tag == "img":
            self.image_alts.append(values.get("alt"))

    def handle_endtag(self, tag):
        if tag == "a":
            self.current_nav_link = False
        elif tag == "nav":
            self.nav_depth = max(0, self.nav_depth - 1)
        elif tag == "footer":
            self.footer_depth = max(0, self.footer_depth - 1)

    def handle_data(self, data):
        if self.current_nav_link and data.strip():
            self.nav_text.append(data.strip())


def normalize_baseurl(value: str) -> str:
    value = value.strip()
    if not value or value == "/":
        return ""
    return "/" + value.strip("/")


def local_target(site: Path, source: Path, raw: str, baseurl: str) -> Path | None:
    if raw.startswith(("mailto:", "tel:", "#", "javascript:", "data:")):
        return None
    parsed = urlparse(raw)
    if parsed.scheme or parsed.netloc:
        return None
    clean = unquote(parsed.path)
    if not clean:
        return None
    if clean.startswith("/"):
        if baseurl and (clean == baseurl or clean.startswith(baseurl + "/")):
            clean = clean[len(baseurl):] or "/"
        target = site / clean.lstrip("/")
    else:
        target = source.parent / clean
    if clean.endswith("/"):
        target /= "index.html"
    elif target.suffix == "":
        target /= "index.html"
    return target


cli = argparse.ArgumentParser()
cli.add_argument("site", nargs="?", default="_site")
cli.add_argument("--baseurl", default="")
args = cli.parse_args()

site = Path(args.site).resolve()
baseurl = normalize_baseurl(args.baseurl)
required = [
    "index.html", "research/index.html", "publications/index.html", "team/index.html",
    "opportunities/index.html", "news/index.html", "events/index.html", "zh/index.html",
    "zh/research/index.html", "zh/publications/index.html", "zh/team/index.html",
    "zh/opportunities/index.html", "zh/news/index.html", "zh/events/index.html",
    "team/mei-li/index.html", "zh/team/mei-li/index.html", "404.html", "zh/404.html",
    "images/icon.svg", "_styles/custom.css", "_scripts/dark-mode.js", "_scripts/custom.js"
]
errors = [f"missing route or asset: /{path}" for path in required if not (site / path).is_file()]
expected_nav = ["RESEARCH", "PUBLICATIONS", "TEAM", "OPPORTUNITIES"]

home_html = (site / "index.html").read_text(encoding="utf-8", errors="replace") if (site / "index.html").is_file() else ""
zh_home_html = (site / "zh" / "index.html").read_text(encoding="utf-8", errors="replace") if (site / "zh" / "index.html").is_file() else ""
for name, rendered in (("index.html", home_html), ("zh/index.html", zh_home_html)):
    if 'class="home-introduction"' not in rendered or "data-carousel" not in rendered:
        errors.append(f"homepage introduction/carousel missing in {name}")
    if rendered.count("data-carousel-slide") < 1:
        errors.append(f"homepage has no visible carousel slide in {name}")
    page = SiteHTMLParser()
    page.feed(rendered)
    custom_stylesheets = [
        reference
        for kind, reference in page.references
        if kind == "asset" and urlparse(reference).path.endswith("/_styles/custom.css")
    ]
    if len(custom_stylesheets) != 1:
        errors.append(f"project custom stylesheet must load exactly once in {name}")
    for marker in ('data-heading-font=', 'data-body-font=', 'data-lab-name-size=', 'data-line-height='):
        if marker not in rendered:
            errors.append(f"typography setting {marker} missing in {name}")

for profile_path in (site / "team" / "mei-li" / "index.html", site / "zh" / "team" / "mei-li" / "index.html"):
    if profile_path.is_file():
        profile = profile_path.read_text(encoding="utf-8", errors="replace")
        if '<section class="profile-intro"' not in profile:
            errors.append(f"profile hero must use normal-flow section markup in {profile_path.relative_to(site).as_posix()}")
        if '<header class="profile-intro"' in profile:
            errors.append(f"profile hero must not inherit sticky site-header rules in {profile_path.relative_to(site).as_posix()}")
        if 'class="profile-personal-note"' not in profile:
            errors.append(f"personal note missing in {profile_path.relative_to(site).as_posix()}")
        if 'class="profile-summary"' not in profile:
            errors.append(f"profile summary missing in {profile_path.relative_to(site).as_posix()}")
        if 'class="profile-contacts"' not in profile or 'class="profile-portrait"' not in profile:
            errors.append(f"compact profile contact layout missing in {profile_path.relative_to(site).as_posix()}")
        if "Phone" in profile or "Office" in profile:
            errors.append(f"retired phone/office content rendered in {profile_path.relative_to(site).as_posix()}")

custom_css = (site / "_styles" / "custom.css").read_text(encoding="utf-8", errors="replace") if (site / "_styles" / "custom.css").is_file() else ""
for marker in (
    "view-transition-old", ".visual-carousel", ".team-card img", ".profile-intro",
    ".profile-contacts", ".profile-summary", ".representative-publications",
    "aspect-ratio: 1.65 / 1", "--font-lab-name", "body.publications-page"
):
    if marker not in custom_css:
        errors.append(f"compiled custom CSS is missing {marker}")

for publication_path in (site / "publications" / "index.html", site / "zh" / "publications" / "index.html"):
    if publication_path.is_file():
        publication = publication_path.read_text(encoding="utf-8", errors="replace")
        if 'class="publications-page"' not in publication:
            errors.append(f"publication route is missing page-specific sizing class in {publication_path.relative_to(site).as_posix()}")

for html in site.rglob("*.html"):
    page = SiteHTMLParser()
    page.feed(html.read_text(encoding="utf-8", errors="replace"))
    relative = html.relative_to(site).as_posix()
    expected_lang = "zh" if relative.startswith("zh/") else "en"
    if page.html_lang != expected_lang:
        errors.append(f"wrong html lang in {relative}: expected {expected_lang}, got {page.html_lang}")
    if page.nav_text != expected_nav:
        errors.append(f"primary navigation mismatch in {relative}: {page.nav_text}")
    if page.footer_has_nav:
        errors.append(f"footer navigation is forbidden in {relative}")
    if any(alt is None or not alt.strip() for alt in page.image_alts):
        errors.append(f"empty image alt in {relative}")
    for kind, reference in page.references:
        parsed_reference = urlparse(reference)
        reference_path = parsed_reference.path
        is_local = not parsed_reference.scheme and not parsed_reference.netloc
        if is_local and any(f"/{name}/" in reference_path.lower() for name in ("projects", "blog", "alumni")):
            errors.append(f"forbidden route reference in {relative}: {reference}")
        if (
            baseurl
            and is_local
            and reference_path.startswith("/")
            and reference_path != baseurl
            and not reference_path.startswith(baseurl + "/")
        ):
            errors.append(f"root-relative {kind} is missing baseurl in {relative}: {reference}")
        target = local_target(site, html, reference, baseurl)
        if target is not None and not target.exists():
            errors.append(f"broken internal {kind} in {relative}: {reference}")

if errors:
    print("Generated-site checks failed:")
    for error in sorted(set(errors)):
        print(f"- {error}")
    raise SystemExit(1)

print(f"Generated-site checks passed for {len(list(site.rglob('*.html')))} HTML files (baseurl={baseurl or '/'}).")
