#!/usr/bin/env python3
"""Validate editable collections and cross-record references."""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("PyYAML is required: py -m pip install PyYAML")

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []

SCHEMAS = {
    "_research": ["title_en", "title_zh", "graphical_abstract", "alt_en", "alt_zh", "short_intro_en", "short_intro_zh", "doi_list", "display", "order"],
    "_news": ["category", "title_en", "title_zh", "summary_en", "summary_zh", "date", "display"],
    "_events": ["type", "category", "title_en", "title_zh", "date", "description_en", "description_zh", "display"],
    "_members": ["slug", "role", "name_en", "name_zh", "position_en", "position_zh", "portrait", "portrait_alt_en", "portrait_alt_zh", "research_summary_en", "research_summary_zh", "active", "display", "order"],
    "_opportunities": ["category", "title_en", "title_zh", "content_en", "content_zh", "links", "active_override", "display_order", "display"],
}

NEWS_CATEGORIES = {"Publication", "Award", "Member", "Academic Achievement", "Funding", "Announcement"}
EVENT_TYPES = {"Academic", "Group"}
OPPORTUNITY_CATEGORIES = {"PhD Students", "Research Assistants", "Administrative Assistants", "Assistant Professors", "Postdoctoral Researchers", "Visiting Students", "Other"}


def load_yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        ERRORS.append(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")
        return None


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", text, re.S)
    if not match:
        ERRORS.append(f"{path.relative_to(ROOT)}: missing YAML front matter")
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except Exception as exc:
        ERRORS.append(f"{path.relative_to(ROOT)}: invalid front matter: {exc}")
        return {}


def check_image(path_value: str, source: Path):
    if not path_value or path_value.startswith(("http://", "https://")):
        return
    target = ROOT / path_value.lstrip("/")
    if not target.is_file():
        ERRORS.append(f"{source.relative_to(ROOT)}: missing image {path_value}")


def iso_date(value) -> str:
    if isinstance(value, date):
        return value.isoformat()
    return str(value or "")


records: dict[str, list[tuple[Path, dict]]] = {}
for folder, required in SCHEMAS.items():
    records[folder] = []
    for path in sorted((ROOT / folder).glob("*.md")):
        data = frontmatter(path)
        records[folder].append((path, data))
        for key in required:
            if key not in data:
                ERRORS.append(f"{path.relative_to(ROOT)}: missing field {key}")

for path, data in records["_news"]:
    if data.get("category") not in NEWS_CATEGORIES:
        ERRORS.append(f"{path.relative_to(ROOT)}: invalid news category")
    check_image(data.get("image", ""), path)
    if data.get("image") and not (data.get("alt_en") and data.get("alt_zh")):
        ERRORS.append(f"{path.relative_to(ROOT)}: news image requires EN/ZH alt")

for path, data in records["_events"]:
    if data.get("type") not in EVENT_TYPES:
        ERRORS.append(f"{path.relative_to(ROOT)}: invalid event type")
    check_image(data.get("cover_image", ""), path)
    if data.get("cover_image") and not (data.get("alt_en") and data.get("alt_zh")):
        ERRORS.append(f"{path.relative_to(ROOT)}: cover image requires EN/ZH alt")
    if data.get("end_date") and iso_date(data.get("end_date")) < iso_date(data.get("date")):
        ERRORS.append(f"{path.relative_to(ROOT)}: end_date precedes date")

team_roles = load_yaml(ROOT / "_data" / "team_roles.yaml") or []
role_ids = []
for index, role in enumerate(team_roles):
    role_id = str(role.get("id", ""))
    if not re.match(r"^[a-z0-9-]+$", role_id):
        ERRORS.append(f"_data/team_roles.yaml item {index + 1}: invalid role id")
    if role_id in role_ids:
        ERRORS.append(f"_data/team_roles.yaml: duplicate role id {role_id}")
    role_ids.append(role_id)
    for key in ("label_en", "label_zh", "order"):
        if role.get(key) in (None, ""):
            ERRORS.append(f"_data/team_roles.yaml item {index + 1}: missing {key}")

if not role_ids:
    ERRORS.append("_data/team_roles.yaml: at least one team role is required")

member_ids = set()
for path, data in records["_members"]:
    member_id = data.get("slug")
    if member_id in member_ids:
        ERRORS.append(f"{path.relative_to(ROOT)}: duplicate member slug {member_id}")
    member_ids.add(member_id)
    if data.get("role") not in role_ids:
        ERRORS.append(f"{path.relative_to(ROOT)}: invalid role {data.get('role')}")
    check_image(data.get("portrait", ""), path)

for path, data in records["_opportunities"]:
    if data.get("category") not in OPPORTUNITY_CATEGORIES:
        ERRORS.append(f"{path.relative_to(ROOT)}: invalid opportunity category")
    if data.get("active_override") not in {"auto", "force_show", "force_hide"}:
        ERRORS.append(f"{path.relative_to(ROOT)}: active_override must be auto, force_show, or force_hide")
    opening = iso_date(data.get("opening_date"))
    closing = iso_date(data.get("closing_date"))
    if opening and closing and closing < opening:
        ERRORS.append(f"{path.relative_to(ROOT)}: closing_date precedes opening_date")

sources = load_yaml(ROOT / "_data" / "sources.yaml") or []
citations = load_yaml(ROOT / "_data" / "citations.yaml") or []
source_dois = []
for index, source in enumerate(sources):
    source_id = str(source.get("id", ""))
    if not re.match(r"^doi:10\..+/.+$", source_id, re.I):
        ERRORS.append(f"_data/sources.yaml item {index + 1}: id must use doi:10.x/... format")
    normalized = source_id.lower().removeprefix("doi:")
    if normalized in source_dois:
        ERRORS.append(f"_data/sources.yaml: duplicate DOI {normalized}")
    source_dois.append(normalized)
    for member_id in source.get("member_ids", []) or []:
        if member_id not in member_ids:
            ERRORS.append(f"_data/sources.yaml: unknown member_id {member_id}")

citation_dois = {str(item.get("id", "")).lower().removeprefix("doi:") for item in citations}
source_doi_set = set(source_dois)
for doi in source_doi_set - citation_dois:
    ERRORS.append(f"_data/sources.yaml: DOI {doi} has not been resolved into citations.yaml")
for citation in citations:
    for member_id in citation.get("member_ids", []) or []:
        if member_id not in member_ids:
            ERRORS.append(f"_data/citations.yaml: unknown member_id {member_id}")
for path, data in records["_research"]:
    check_image(data.get("graphical_abstract", ""), path)
    for doi in data.get("doi_list", []) or []:
        normalized = str(doi).lower().removeprefix("doi:")
        if normalized not in citation_dois:
            ERRORS.append(f"{path.relative_to(ROOT)}: DOI {doi} is absent from citations.yaml")
        if normalized not in source_doi_set:
            ERRORS.append(f"{path.relative_to(ROOT)}: DOI {doi} is absent from sources.yaml")

cms = load_yaml(ROOT / ".pages.yml") or {}
cms_names = {entry.get("name") for entry in cms.get("content", [])}
required_cms = {"homepage", "news", "events", "research", "publications", "team", "team-roles", "opportunities", "site"}
missing = required_cms - cms_names
if missing:
    ERRORS.append(f".pages.yml: missing CMS sections {sorted(missing)}")
if not cms.get("media"):
    ERRORS.append(".pages.yml: media library is not configured")
else:
    media = cms["media"][0]
    if media.get("input") != "images/uploads" or media.get("output") != "/images/uploads":
        ERRORS.append(".pages.yml: Media must map images/uploads to /images/uploads")

cms_entries = {entry.get("name"): entry for entry in cms.get("content", [])}
for collection_name, folder in {"news": "_news", "events": "_events", "research": "_research", "team": "_members", "opportunities": "_opportunities"}.items():
    cms_fields = {field.get("name") for field in cms_entries.get(collection_name, {}).get("fields", [])}
    missing_fields = set(SCHEMAS[folder]) - cms_fields
    if missing_fields:
        ERRORS.append(f".pages.yml {collection_name}: missing schema fields {sorted(missing_fields)}")

homepage = load_yaml(ROOT / "_data" / "homepage.yaml") or {}
introduction = homepage.get("introduction") or {}
for key in ("eyebrow_en", "eyebrow_zh", "title_en", "title_zh", "text_en", "text_zh"):
    if not introduction.get(key):
        ERRORS.append(f"_data/homepage.yaml introduction: missing {key}")
autoplay = introduction.get("autoplay_seconds")
if not isinstance(autoplay, int) or not 5 <= autoplay <= 12:
    ERRORS.append("_data/homepage.yaml introduction: autoplay_seconds must be an integer from 5 to 12")
slides = introduction.get("slides") or []
visible_slides = 0
orders = set()
for index, slide in enumerate(slides):
    for key in ("image", "alt_en", "alt_zh", "visual_type", "order"):
        if slide.get(key) in (None, ""):
            ERRORS.append(f"_data/homepage.yaml introduction slide {index + 1}: missing {key}")
    if slide.get("visual_type") not in {"graphical-abstract", "lab-photo"}:
        ERRORS.append(f"_data/homepage.yaml introduction slide {index + 1}: invalid visual_type")
    if slide.get("order") in orders:
        ERRORS.append(f"_data/homepage.yaml introduction: duplicate slide order {slide.get('order')}")
    orders.add(slide.get("order"))
    check_image(slide.get("image", ""), ROOT / "_data" / "homepage.yaml")
    if slide.get("display") is True:
        visible_slides += 1
if not slides or visible_slides < 1:
    ERRORS.append("_data/homepage.yaml introduction: at least one visible slide is required")

for key in ("highlights_heading_en", "highlights_heading_zh", "events_heading_en", "events_heading_zh"):
    if not homepage.get(key):
        ERRORS.append(f"_data/homepage.yaml: missing {key}")
for key in ("news_limit", "events_limit"):
    if not isinstance(homepage.get(key), int) or homepage[key] < 1:
        ERRORS.append(f"_data/homepage.yaml: {key} must be a positive integer")

site_data = load_yaml(ROOT / "_data" / "site.yaml") or {}
site_required = {
    "lab_name_en", "lab_name_zh", "school_en", "school_zh", "college_en", "college_zh",
    "address_en", "address_zh", "email", "header_image", "lab_logo", "school_logo",
    "copyright_en", "copyright_zh", "description_en", "description_zh"
}
for key in site_required:
    if not site_data.get(key):
        ERRORS.append(f"_data/site.yaml: missing {key}")
for key in ("header_image", "lab_logo", "school_logo"):
    check_image(site_data.get(key, ""), ROOT / "_data" / "site.yaml")
site_cms_fields = {field.get("name") for field in cms_entries.get("site", {}).get("fields", [])}
missing_site_fields = site_required - site_cms_fields
if missing_site_fields:
    ERRORS.append(f".pages.yml site: missing schema fields {sorted(missing_site_fields)}")

homepage_cms_fields = {field.get("name") for field in cms_entries.get("homepage", {}).get("fields", [])}
if "introduction" not in homepage_cms_fields:
    ERRORS.append(".pages.yml homepage: missing introduction fields")

team_roles_cms_fields = {field.get("name") for field in cms_entries.get("team-roles", {}).get("fields", [])}
missing_role_fields = {"id", "label_en", "label_zh", "display", "order"} - team_roles_cms_fields
if missing_role_fields:
    ERRORS.append(f".pages.yml team-roles: missing fields {sorted(missing_role_fields)}")

member_cms_fields = {field.get("name") for field in cms_entries.get("team", {}).get("fields", [])}
for field in ("personal_note_en", "personal_note_zh", "email"):
    if field not in member_cms_fields:
        ERRORS.append(f".pages.yml team: missing profile field {field}")
for retired_field in ("biography_en", "biography_zh", "office", "phone"):
    if retired_field in member_cms_fields:
        ERRORS.append(f".pages.yml team: retired field {retired_field} remains exposed")

for forbidden in ("projects", "blog", "alumni"):
    if (ROOT / forbidden).exists():
        ERRORS.append(f"forbidden route directory exists: {forbidden}")

nav = (ROOT / "_includes" / "header.html").read_text(encoding="utf-8")
expected_nav = [
    ("/research/", "RESEARCH"),
    ("/publications/", "PUBLICATIONS"),
    ("/team/", "TEAM"),
    ("/opportunities/", "OPPORTUNITIES"),
]
primary_nav = re.findall(
    r'<a href="\{\{ prefix \| append: \'([^\']+)\' \| relative_url \}\}">([A-Z]+)</a>',
    nav,
)
if primary_nav != expected_nav:
    ERRORS.append(f"header primary navigation mismatch: expected {expected_nav}, got {primary_nav}")

profile_layout = (ROOT / "_layouts" / "profile.html").read_text(encoding="utf-8")
if '<header class="profile-intro"' in profile_layout:
    ERRORS.append("_layouts/profile.html: profile hero must not use the globally sticky header element")
if '<section class="profile-intro"' not in profile_layout:
    ERRORS.append("_layouts/profile.html: normal-flow profile-intro section is missing")

if ERRORS:
    print("Content validation failed:")
    for error in ERRORS:
        print(f"- {error}")
    sys.exit(1)

print(f"Content validation passed: {sum(len(items) for items in records.values())} collection records, {len(sources)} DOI source(s), {len(citations)} citation(s).")
