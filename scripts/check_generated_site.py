#!/usr/bin/env python3
"""Check required routes and internal links in a generated Jekyll site."""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
required = ["index.html", "research/index.html", "publications/index.html", "team/index.html", "opportunities/index.html", "news/index.html", "events/index.html", "zh/index.html", "zh/research/index.html", "zh/publications/index.html", "zh/team/index.html", "zh/opportunities/index.html", "zh/news/index.html", "zh/events/index.html", "team/mei-li/index.html", "zh/team/mei-li/index.html", "404.html"]
errors = [f"missing route: /{path}" for path in required if not (site / path).is_file()]

for html in site.rglob("*.html"):
    parser = LinkParser()
    parser.feed(html.read_text(encoding="utf-8", errors="replace"))
    for href in parser.links:
        parsed = urlparse(href)
        if parsed.scheme or parsed.netloc or href.startswith(("mailto:", "tel:", "#", "javascript:")):
            continue
        clean = unquote(parsed.path)
        if not clean:
            continue
        target = (site / clean.lstrip("/")) if clean.startswith("/") else (html.parent / clean)
        if clean.endswith("/"):
            target = target / "index.html"
        elif target.suffix == "":
            target = target / "index.html"
        if not target.exists():
            errors.append(f"broken internal link in {html.relative_to(site)}: {href}")

if errors:
    print("Generated-site checks failed:")
    for error in sorted(set(errors)):
        print(f"- {error}")
    raise SystemExit(1)

print(f"Generated-site checks passed for {len(list(site.rglob('*.html')))} HTML files.")
