#!/usr/bin/env python3
"""Check routes, links, metadata, assets and release invariants."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
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
        self.canonical_urls: list[str] = []
        self.alternate_urls: dict[str, list[str]] = {}
        self.metadata_urls: dict[str, list[str]] = {"og:url": [], "twitter:url": []}
        self.robots_values: list[str] = []

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
            if "canonical" in rel:
                self.canonical_urls.append(values["href"])
            if "alternate" in rel and values.get("hreflang"):
                self.alternate_urls.setdefault(values["hreflang"], []).append(values["href"])
        if tag == "meta" and values.get("content"):
            key = values.get("property") or values.get("name")
            if key in self.metadata_urls:
                self.metadata_urls[key].append(values["content"])
            if values.get("name") == "robots":
                self.robots_values.append(values["content"])
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


def route_for_html(site: Path, html: Path) -> str:
    relative = html.relative_to(site).as_posix()
    if relative == "index.html":
        return "/"
    if relative.endswith("/index.html"):
        return "/" + relative.removesuffix("index.html")
    return "/" + relative


cli = argparse.ArgumentParser()
cli.add_argument("site", nargs="?", default="_site")
cli.add_argument("--baseurl", default="")
cli.add_argument("--origin", required=True)
cli.add_argument("--canonical-origin", required=True)
cli.add_argument("--environment", choices=("production", "staging"), required=True)
cli.add_argument("--require-version", action="store_true")
args = cli.parse_args()

site = Path(args.site).resolve()
baseurl = normalize_baseurl(args.baseurl)
origin = args.origin.rstrip("/")
canonical_origin = args.canonical_origin.rstrip("/")
production = args.environment == "production"
errors: list[str] = []

if production and (origin != "https://jliang.eitech.edu.cn" or baseurl):
    errors.append(f"production URL must be https://jliang.eitech.edu.cn with empty baseurl, got {origin}{baseurl}")
if canonical_origin != "https://jliang.eitech.edu.cn":
    errors.append(f"canonical origin must be production, got {canonical_origin}")
if not production and (origin != "https://davidhmeng.github.io" or baseurl != "/energy-materials-lab-website"):
    errors.append(f"staging URL/baseurl mismatch: {origin}{baseurl}")

required = [
    "index.html", "research/index.html", "publications/index.html", "team/index.html",
    "opportunities/index.html", "news/index.html", "events/index.html", "zh/index.html",
    "zh/research/index.html", "zh/publications/index.html", "zh/team/index.html",
    "zh/opportunities/index.html", "zh/news/index.html", "zh/events/index.html",
    "404.html", "zh/404.html",
    "images/icon.svg", "_styles/custom.css", "_scripts/dark-mode.js", "_scripts/custom.js",
    "_scripts/search.js", "sitemap.xml", "robots.txt",
]
errors.extend(f"missing route or asset: /{path}" for path in required if not (site / path).is_file())
source_only_paths = (
    "AGENTS.md", "BUILD_SPEC.md", "CONTENT_SCHEMA.md", "DEPLOYMENT.md",
    "IMPLEMENTATION_AUDIT.md", "PAGES_CMS_GUIDE.md", "PROJECT_STATUS.md", "README.md",
    "Gemfile", "Gemfile.lock", "_config.yml", "_config.production.yml", "_config.staging.yml",
    ".github", "ops", "scripts", "script", "_cite", "_translation",
)
errors.extend(f"source-only path leaked into generated site: /{path}" for path in source_only_paths if (site / path).exists())
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
        reference for kind, reference in page.references
        if kind == "asset" and urlparse(reference).path.endswith("/_styles/custom.css")
    ]
    if len(custom_stylesheets) != 1:
        errors.append(f"project custom stylesheet must load exactly once in {name}")
    for marker in ('data-heading-font=', 'data-body-font=', 'data-lab-name-size=', 'data-line-height='):
        if marker not in rendered:
            errors.append(f"typography setting {marker} missing in {name}")

profile_paths = sorted((site / "team").glob("*/index.html")) if (site / "team").is_dir() else []
if not profile_paths:
    errors.append("generated site has no visible member profile route")
for profile_path in profile_paths:
    if profile_path.is_file():
        profile = profile_path.read_text(encoding="utf-8", errors="replace")
        relative = profile_path.relative_to(site).as_posix()
        if '<section class="profile-intro"' not in profile or '<header class="profile-intro"' in profile:
            errors.append(f"profile hero is not normal-flow section markup in {relative}")
        # Personal note and profile summary are optional CMS fields and should
        # disappear cleanly when editors delete them. Contacts and portrait are
        # structural parts of every profile card.
        for marker in ('class="profile-contacts"', 'class="profile-portrait"'):
            if marker not in profile:
                errors.append(f"profile marker {marker} missing in {relative}")
        if re.search(r"<strong>\s*(?:Phone|Office)\s*:\s*</strong>", profile, re.IGNORECASE):
            errors.append(f"retired phone/office content rendered in {relative}")

        route = profile_path.parent.name
        localized_path = site / "zh" / "team" / route / "index.html"
        if not localized_path.is_file():
            errors.append(f"missing localized member profile route: /zh/team/{route}/")
        else:
            localized = localized_path.read_text(encoding="utf-8", errors="replace")
            for marker in ('class="profile-contacts"', 'class="profile-portrait"'):
                if marker not in localized:
                    errors.append(f"profile marker {marker} missing in zh/team/{route}/index.html")

        english_path = site / "team" / route / "index.html"
        if english_path.is_file():
            english = english_path.read_text(encoding="utf-8", errors="replace")
            if f"/zh/team/{route}/" not in english:
                errors.append(f"English profile language link does not match slug in {relative}")
        if localized_path.is_file():
            localized = localized_path.read_text(encoding="utf-8", errors="replace")
            if f"/team/{route}/" not in localized:
                errors.append(f"Chinese profile language link does not match filename in zh/team/{route}/index.html")

custom_css = (site / "_styles" / "custom.css").read_text(encoding="utf-8", errors="replace") if (site / "_styles" / "custom.css").is_file() else ""
compact_custom_css = "".join(custom_css.split())
for marker in (
    "view-transition-old", ".visual-carousel", ".team-card img", ".profile-intro",
    ".profile-contacts", ".profile-summary", ".representative-publications",
    "--font-lab-name", "body.publications-page",
):
    if marker not in custom_css:
        errors.append(f"compiled custom CSS is missing {marker}")
for marker in (
    "--scientific-canvas-height:clamp(560px,69vw,780px)",
    "aspect-ratio:1.4/1",
    ".visual-slide-image",
    "object-fit:contain",
    "object-position:center",
    ".visual-slide-caption",
    "-webkit-line-clamp:2",
):
    if marker not in compact_custom_css:
        errors.append(f"compiled custom CSS is missing fixed scientific canvas marker {marker}")

for publication_path in (site / "publications" / "index.html", site / "zh" / "publications" / "index.html"):
    if publication_path.is_file():
        publication = publication_path.read_text(encoding="utf-8", errors="replace")
        if 'class="publications-page"' not in publication:
            errors.append(f"publication route is missing page-specific sizing class in {publication_path.relative_to(site).as_posix()}")

for archive in (site / "news" / "index.html", site / "events" / "index.html", site / "zh" / "news" / "index.html", site / "zh" / "events" / "index.html"):
    if archive.is_file():
        archive_html = archive.read_text(encoding="utf-8", errors="replace")
        # Empty CMS archives are valid. Require the search marker only when the
        # archive actually contains a rendered card that should be searchable.
        has_card = 'class="news-card"' in archive_html or 'class="event-card"' in archive_html
        if has_card and "data-search=" not in archive_html:
            errors.append(f"search index marker missing in {archive.relative_to(site).as_posix()}")

for html in site.rglob("*.html"):
    rendered = html.read_text(encoding="utf-8", errors="replace")
    page = SiteHTMLParser()
    page.feed(rendered)
    relative = html.relative_to(site).as_posix()
    route = route_for_html(site, html)
    expected_public_url = f"{canonical_origin}{route}"
    expected_lang = "zh" if relative.startswith("zh/") else "en"
    if page.html_lang != expected_lang:
        errors.append(f"wrong html lang in {relative}: expected {expected_lang}, got {page.html_lang}")
    if page.nav_text != expected_nav:
        errors.append(f"primary navigation mismatch in {relative}: {page.nav_text}")
    if page.footer_has_nav:
        errors.append(f"footer navigation is forbidden in {relative}")
    if any(alt is None or not alt.strip() for alt in page.image_alts):
        errors.append(f"empty image alt in {relative}")
    if page.canonical_urls != [expected_public_url]:
        errors.append(f"canonical mismatch in {relative}: {page.canonical_urls}, expected {expected_public_url}")
    for key in ("og:url", "twitter:url"):
        if page.metadata_urls[key] != [expected_public_url]:
            errors.append(f"{key} mismatch in {relative}: {page.metadata_urls[key]}, expected {expected_public_url}")
    if production and page.robots_values:
        errors.append(f"production page unexpectedly has robots noindex in {relative}")
    if not production and page.robots_values != ["noindex, nofollow, noarchive"]:
        errors.append(f"staging robots meta mismatch in {relative}: {page.robots_values}")
    if route.startswith("/zh/"):
        en_route, zh_route = route[3:], route
    else:
        en_route, zh_route = route, "/zh" + route
    expected_alternates = {
        "en": [f"{canonical_origin}{en_route}"],
        "zh-CN": [f"{canonical_origin}{zh_route}"],
        "x-default": [f"{canonical_origin}{en_route}"],
    }
    for language, expected in expected_alternates.items():
        if page.alternate_urls.get(language) != expected:
            errors.append(f"hreflang {language} mismatch in {relative}: {page.alternate_urls.get(language)}, expected {expected}")
    if f'"url": "{expected_public_url}"' not in rendered:
        errors.append(f"JSON-LD URL mismatch in {relative}: expected {expected_public_url}")
    for kind, reference in page.references:
        parsed_reference = urlparse(reference)
        reference_path = parsed_reference.path
        is_local = not parsed_reference.scheme and not parsed_reference.netloc
        if is_local and any(f"/{name}/" in reference_path.lower() for name in ("projects", "blog", "alumni")):
            errors.append(f"forbidden route reference in {relative}: {reference}")
        if baseurl and is_local and reference_path.startswith("/") and reference_path != baseurl and not reference_path.startswith(baseurl + "/"):
            errors.append(f"root-relative {kind} is missing baseurl in {relative}: {reference}")
        target = local_target(site, html, reference, baseurl)
        if target is not None and not target.exists():
            errors.append(f"broken internal {kind} in {relative}: {reference}")
        if kind == "asset" and parsed_reference.scheme == "http":
            errors.append(f"mixed-content asset in {relative}: {reference}")

robots = (site / "robots.txt").read_text(encoding="utf-8", errors="replace") if (site / "robots.txt").is_file() else ""
if production:
    for generated in site.rglob("*"):
        if not generated.is_file() or generated.suffix.lower() not in {".html", ".xml", ".txt", ".css", ".js", ".json"}:
            continue
        contents = generated.read_text(encoding="utf-8", errors="replace")
        for marker in ("davidhmeng.github.io/energy-materials-lab-website", "/energy-materials-lab-website/", "http://jliang.eitech.edu.cn"):
            if marker in contents:
                errors.append(f"legacy or insecure production URL in {generated.relative_to(site).as_posix()}: {marker}")
    sitemap = (site / "sitemap.xml").read_text(encoding="utf-8", errors="replace") if (site / "sitemap.xml").is_file() else ""
    if f"<loc>{canonical_origin}/" not in sitemap:
        errors.append("production sitemap does not contain the production origin")
    if f"Sitemap: {canonical_origin}/sitemap.xml" not in robots or "Disallow: /" in robots:
        errors.append("production robots.txt is not indexable or has the wrong sitemap")
else:
    if "Disallow: /" not in robots:
        errors.append("staging robots.txt must disallow indexing")

if args.require_version:
    version_path = site / "version.json"
    if not version_path.is_file():
        errors.append("production release is missing version.json")
    else:
        try:
            version = json.loads(version_path.read_text(encoding="utf-8"))
            if version.get("environment") != "production":
                errors.append("version.json environment must be production")
            for key in ("source_commit", "build_commit"):
                if not re.fullmatch(r"[0-9a-f]{40}", str(version.get(key, ""))):
                    errors.append(f"version.json {key} is not a full Git SHA")
            datetime.fromisoformat(str(version.get("built_at", "")).replace("Z", "+00:00"))
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            errors.append(f"invalid version.json: {exc}")

if errors:
    print("Generated-site checks failed:")
    for error in sorted(set(errors)):
        print(f"- {error}")
    raise SystemExit(1)

print(
    f"Generated-site checks passed for {len(list(site.rglob('*.html')))} HTML files "
    f"(environment={args.environment}, origin={origin}, baseurl={baseurl or '/'})."
)
