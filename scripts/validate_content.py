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

from citation_registry import CitationRegistryError, normalize_doi

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
WARNINGS: list[str] = []

SCHEMAS = {
    "_research": ["title_zh", "graphical_abstract", "alt_zh", "short_intro_zh", "doi_list", "display", "order"],
    "_news": ["category", "title_zh", "summary_zh", "date", "display"],
    "_events": ["type", "category", "title_zh", "date", "display"],
    "_members": ["slug", "role", "name_zh", "position_zh", "portrait", "portrait_alt_zh", "research_summary_zh", "profile_summary_zh", "active", "display", "order"],
    "_opportunities": ["category", "title_zh", "content_zh", "links", "active_override", "display_order", "display"],
}

CMS_EXPECTED_FIELDS = {
    "_research": ["title_en", "alt_en", "short_intro_en"],
    "_news": ["title_en", "summary_en"],
    "_events": ["title_en", "description_en"],
    "_members": ["name_en", "position_en", "portrait_alt_en", "research_summary_en", "profile_summary_en", "representative_dois"],
    "_opportunities": ["title_en", "content_en"],
}

NEWS_CATEGORIES = {"Publication", "Award", "Member", "Academic Achievement", "Funding", "Announcement"}
EVENT_TYPES = {"Academic", "Group"}
OPPORTUNITY_CATEGORIES = {"PhD Students", "Research Assistants", "Administrative Assistants", "Assistant Professors", "Postdoctoral Researchers", "Visiting Students", "Other"}
TYPOGRAPHY_PRESETS = {
    "heading_font": {"default", "sans-modern", "sans-academic", "serif-editorial"},
    "body_font": {"default", "sans", "serif"},
    "lab_name_size": {"small", "default", "large"},
    "navigation_size": {"small", "default", "large"},
    "page_title_size": {"small", "default", "large"},
    "section_title_size": {"small", "default", "large"},
    "body_text_size": {"small", "default", "large"},
    "caption_size": {"small", "default", "large"},
    "line_height": {"compact", "default", "relaxed"},
}


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


def check_date(value, label: str, *, required: bool = False) -> str:
    """Validate the CMS contract instead of relying on lexical date sorting."""
    text = iso_date(value)
    if not text:
        if required:
            ERRORS.append(f"{label}: date is required and must use YYYY-MM-DD")
        return ""
    try:
        date.fromisoformat(text)
    except ValueError:
        ERRORS.append(f"{label}: use YYYY-MM-DD")
    return text


def checked_doi(value, label: str) -> str | None:
    try:
        return normalize_doi(value)
    except CitationRegistryError as exc:
        ERRORS.append(f"{label}: {exc}")
        return None


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
    check_date(data.get("date"), f"{path.relative_to(ROOT)}: date", required=True)
    check_image(data.get("image", ""), path)
    if data.get("image") and not data.get("alt_zh"):
        ERRORS.append(f"{path.relative_to(ROOT)}: news image requires Chinese alt text")

for path, data in records["_events"]:
    if data.get("type") not in EVENT_TYPES:
        ERRORS.append(f"{path.relative_to(ROOT)}: invalid event type")
    event_date = check_date(data.get("date"), f"{path.relative_to(ROOT)}: date", required=True)
    end_date = check_date(data.get("end_date"), f"{path.relative_to(ROOT)}: end_date")
    check_image(data.get("cover_image", ""), path)
    if data.get("cover_image") and not data.get("alt_zh"):
        ERRORS.append(f"{path.relative_to(ROOT)}: cover image requires Chinese alt text")
    if end_date and event_date and end_date < event_date:
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
    for key in ("label_zh", "order"):
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
    for retired_field in ("office", "phone", "biography_en", "biography_zh"):
        if retired_field in data:
            ERRORS.append(f"{path.relative_to(ROOT)}: retired member field {retired_field} remains in source")
    for doi in data.get("representative_dois", []) or []:
        checked_doi(doi, f"{path.relative_to(ROOT)}: invalid representative DOI")

for path, data in records["_opportunities"]:
    if data.get("category") not in OPPORTUNITY_CATEGORIES:
        ERRORS.append(f"{path.relative_to(ROOT)}: invalid opportunity category")
    if data.get("active_override") not in {"auto", "force_show", "force_hide"}:
        ERRORS.append(f"{path.relative_to(ROOT)}: active_override must be auto, force_show, or force_hide")
    opening = check_date(data.get("opening_date"), f"{path.relative_to(ROOT)}: opening_date")
    closing = check_date(data.get("closing_date"), f"{path.relative_to(ROOT)}: closing_date")
    if opening and closing and closing < opening:
        ERRORS.append(f"{path.relative_to(ROOT)}: closing_date precedes opening_date")

sources = load_yaml(ROOT / "_data" / "sources.yaml") or []
citations = load_yaml(ROOT / "_data" / "citations.yaml") or []
source_dois = []
for index, source in enumerate(sources):
    source_id = str(source.get("id", ""))
    normalized = checked_doi(source_id, f"_data/sources.yaml item {index + 1}")
    if normalized is None:
        continue
    if normalized in source_dois:
        ERRORS.append(f"_data/sources.yaml: duplicate DOI {normalized}")
    source_dois.append(normalized)
    for member_id in source.get("member_ids", []) or []:
        if member_id not in member_ids:
            ERRORS.append(f"_data/sources.yaml: unknown member_id {member_id}")

citation_dois = set()
for index, item in enumerate(citations, start=1):
    normalized = checked_doi(item.get("id"), f"_data/citations.yaml item {index}")
    if normalized:
        citation_dois.add(normalized)
source_doi_set = set(source_dois)
for doi in source_doi_set - citation_dois:
    WARNINGS.append(f"_data/sources.yaml: DOI {doi} metadata is pending in citations.yaml")
for citation in citations:
    for member_id in citation.get("member_ids", []) or []:
        if member_id not in member_ids:
            ERRORS.append(f"_data/citations.yaml: unknown member_id {member_id}")
for path, data in records["_research"]:
    check_image(data.get("graphical_abstract", ""), path)
    for doi in data.get("doi_list", []) or []:
        normalized = checked_doi(doi, f"{path.relative_to(ROOT)}: invalid related DOI")
        if not normalized:
            continue
        if normalized not in citation_dois:
            WARNINGS.append(f"{path.relative_to(ROOT)}: DOI {normalized} metadata is pending")
        if normalized not in source_doi_set:
            WARNINGS.append(f"{path.relative_to(ROOT)}: DOI {normalized} awaits registry synchronization")

for path, data in records["_members"]:
    for doi in data.get("representative_dois", []) or []:
        normalized = checked_doi(doi, f"{path.relative_to(ROOT)}: invalid representative DOI")
        if not normalized:
            continue
        if normalized not in citation_dois:
            WARNINGS.append(f"{path.relative_to(ROOT)}: representative DOI {normalized} metadata is pending")
        if normalized not in source_doi_set:
            WARNINGS.append(f"{path.relative_to(ROOT)}: representative DOI {normalized} awaits registry synchronization")

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
    missing_fields = (set(SCHEMAS[folder]) | set(CMS_EXPECTED_FIELDS[folder])) - cms_fields
    if missing_fields:
        ERRORS.append(f".pages.yml {collection_name}: missing schema fields {sorted(missing_fields)}")

homepage = load_yaml(ROOT / "_data" / "homepage.yaml") or {}
introduction = homepage.get("introduction") or {}
for key in ("eyebrow_zh", "title_zh", "text_zh"):
    if not introduction.get(key):
        ERRORS.append(f"_data/homepage.yaml introduction: missing {key}")
autoplay = introduction.get("autoplay_seconds")
if not isinstance(autoplay, int) or not 5 <= autoplay <= 12:
    ERRORS.append("_data/homepage.yaml introduction: autoplay_seconds must be an integer from 5 to 12")
slides = introduction.get("slides") or []
visible_slides = 0
orders = set()
for index, slide in enumerate(slides):
    for key in ("image", "alt_zh", "visual_type", "order"):
        if slide.get(key) in (None, ""):
            ERRORS.append(f"_data/homepage.yaml introduction slide {index + 1}: missing {key}")
    if slide.get("visual_type") not in {"graphical-abstract", "lab-photo"}:
        ERRORS.append(f"_data/homepage.yaml introduction slide {index + 1}: invalid visual_type")
    if slide.get("order") in orders:
        ERRORS.append(f"_data/homepage.yaml introduction: duplicate slide order {slide.get('order')}")
    orders.add(slide.get("order"))
    check_image(slide.get("image", ""), ROOT / "_data" / "homepage.yaml")
    if slide.get("related_doi"):
        normalized = checked_doi(
            slide["related_doi"],
            f"_data/homepage.yaml introduction slide {index + 1}: invalid related_doi",
        )
        if normalized and (normalized not in citation_dois or normalized not in source_doi_set):
            WARNINGS.append(
                f"_data/homepage.yaml introduction slide {index + 1}: DOI {normalized} awaits citation synchronization"
            )
    if slide.get("display") is True:
        visible_slides += 1
if not slides or visible_slides < 1:
    ERRORS.append("_data/homepage.yaml introduction: at least one visible slide is required")

for key in ("highlights_heading_zh", "events_heading_zh"):
    if not homepage.get(key):
        ERRORS.append(f"_data/homepage.yaml: missing {key}")
for key in ("news_limit", "events_limit"):
    if not isinstance(homepage.get(key), int) or homepage[key] < 1:
        ERRORS.append(f"_data/homepage.yaml: {key} must be a positive integer")

site_data = load_yaml(ROOT / "_data" / "site.yaml") or {}
site_required = {
    "lab_name_zh", "school_zh", "college_zh", "address_zh", "email", "header_image",
    "lab_logo", "school_logo", "copyright_zh", "description_zh"
}
site_optional_english = {"lab_name_en", "school_en", "college_en", "address_en", "copyright_en", "description_en"}
for key in site_required:
    if not site_data.get(key):
        ERRORS.append(f"_data/site.yaml: missing {key}")
for key in ("header_image", "lab_logo", "school_logo"):
    check_image(site_data.get(key, ""), ROOT / "_data" / "site.yaml")
typography = site_data.get("typography") or {}
for key, allowed in TYPOGRAPHY_PRESETS.items():
    if typography.get(key) not in allowed:
        ERRORS.append(f"_data/site.yaml typography.{key}: expected one of {sorted(allowed)}")
site_cms_fields = {field.get("name") for field in cms_entries.get("site", {}).get("fields", [])}
missing_site_fields = (site_required | site_optional_english) - site_cms_fields
if missing_site_fields:
    ERRORS.append(f".pages.yml site: missing schema fields {sorted(missing_site_fields)}")
if "typography" not in site_cms_fields:
    ERRORS.append(".pages.yml site: missing Typography settings")
else:
    typography_field = next(field for field in cms_entries["site"]["fields"] if field.get("name") == "typography")
    typography_cms_fields = {field.get("name") for field in typography_field.get("fields", [])}
    missing_typography = set(TYPOGRAPHY_PRESETS) - typography_cms_fields
    if missing_typography:
        ERRORS.append(f".pages.yml site typography: missing fields {sorted(missing_typography)}")

homepage_cms_fields = {field.get("name") for field in cms_entries.get("homepage", {}).get("fields", [])}
if "introduction" not in homepage_cms_fields:
    ERRORS.append(".pages.yml homepage: missing introduction fields")

team_roles_cms_fields = {field.get("name") for field in cms_entries.get("team-roles", {}).get("fields", [])}
missing_role_fields = {"id", "label_en", "label_zh", "display", "order"} - team_roles_cms_fields
if missing_role_fields:
    ERRORS.append(f".pages.yml team-roles: missing fields {sorted(missing_role_fields)}")

member_cms_fields = {field.get("name") for field in cms_entries.get("team", {}).get("fields", [])}
for field in (
    "personal_note_en", "personal_note_zh", "email", "address_en", "address_zh",
    "affiliation_en", "affiliation_zh", "research_summary_en", "research_summary_zh",
    "profile_summary_en", "profile_summary_zh", "representative_dois",
    "google_scholar", "orcid", "github", "personal_website"
):
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
for marker in ('class="profile-portrait"', 'class="profile-contacts"', 'class="profile-affiliation"'):
    if marker not in profile_layout:
        ERRORS.append(f"_layouts/profile.html: missing profile marker {marker}")
if "member.phone" in profile_layout or "member.office" in profile_layout:
    ERRORS.append("_layouts/profile.html: phone/office must not render")
for marker in ("profile-summary", "representative_dois", "Representative Publications"):
    if marker not in profile_layout:
        ERRORS.append(f"_layouts/profile.html: missing V1.5 profile marker {marker}")

translation_script = (ROOT / "scripts" / "translate_content.py").read_text(encoding="utf-8")
for forbidden in ("_data/sources.yaml", "_data/citations.yaml"):
    if forbidden in translation_script:
        ERRORS.append(f"scripts/translate_content.py: publication data must remain excluded ({forbidden})")
if not (ROOT / "_translation" / "state.yml").is_file():
    ERRORS.append("translation state sidecar is missing")


def walk_cms_fields(fields):
    for field in fields or []:
        yield field
        yield from walk_cms_fields(field.get("fields"))


for entry in cms.get("content", []):
    if entry.get("name") == "publications":
        continue
    for field in walk_cms_fields(entry.get("fields")):
        name = str(field.get("name", ""))
        if name.endswith("_en") and field.get("required") is True:
            ERRORS.append(f".pages.yml {entry.get('name')}.{name}: English must be optional")

production_config = load_yaml(ROOT / "_config.production.yml") or {}
staging_config = load_yaml(ROOT / "_config.staging.yml") or {}
if production_config.get("url") != "https://jliang.eitech.edu.cn" or production_config.get("baseurl") != "":
    ERRORS.append("_config.production.yml: production URL/baseurl contract is invalid")
if production_config.get("robots_noindex") is not False:
    ERRORS.append("_config.production.yml: production must remain indexable")
if staging_config.get("url") != "https://davidhmeng.github.io" or staging_config.get("baseurl") != "/energy-materials-lab-website":
    ERRORS.append("_config.staging.yml: staging URL/baseurl contract is invalid")
if staging_config.get("canonical_url") != "https://jliang.eitech.edu.cn" or staging_config.get("robots_noindex") is not True:
    ERRORS.append("_config.staging.yml: staging canonical/noindex contract is invalid")

deployment_files = (
    "DEPLOYMENT.md",
    "ops/nginx/jliang.conf",
    "ops/scripts/jliang-sync",
    "ops/systemd/jliang-sync.service",
    "ops/systemd/jliang-sync.timer",
    "ops/README.md",
    ".github/workflows/publish-production.yml",
)
for relative in deployment_files:
    if not (ROOT / relative).is_file():
        ERRORS.append(f"deployment contract file is missing: {relative}")

production_workflow = (ROOT / ".github" / "workflows" / "publish-production.yml").read_text(encoding="utf-8")
for marker in (
    "branches: [main]", "needs: [citations, translation, content]", "contents: write",
    "_config.yml,_config.production.yml", "HEAD:server-deploy", "--require-version",
):
    if marker not in production_workflow:
        ERRORS.append(f"production workflow is missing required marker: {marker}")

sync_script = (ROOT / "ops" / "scripts" / "jliang-sync").read_text(encoding="utf-8")
for marker in (
    "set -Eeuo pipefail", "flock -n", "refs/heads/server-deploy:refs/remotes/origin/server-deploy",
    "reset --hard origin/server-deploy", "mv -Tf", "Host: $HEALTH_HOST", "Rollback complete",
):
    if marker not in sync_script:
        ERRORS.append(f"sync script is missing safety marker: {marker}")

try:
    for workflow in (ROOT / ".github" / "workflows").glob("*.y*ml"):
        yaml.safe_load(workflow.read_text(encoding="utf-8"))
except Exception as exc:
    ERRORS.append(f"GitHub Actions workflow YAML is invalid: {exc}")

if ERRORS:
    print("Content validation failed:")
    for error in ERRORS:
        print(f"- {error}")
    sys.exit(1)

if WARNINGS:
    print("Content validation warnings:")
    for warning in sorted(set(WARNINGS)):
        print(f"- {warning}")

print(f"Content validation passed: {sum(len(items) for items in records.values())} collection records, {len(sources)} DOI source(s), {len(citations)} citation(s).")
