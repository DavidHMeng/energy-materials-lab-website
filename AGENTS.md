# Website implementation guardrails

This repository implements Framework V1.1 for a bilingual research-group website.

## Frozen information architecture

- Primary navigation is exactly `RESEARCH | PUBLICATIONS | TEAM | OPPORTUNITIES`.
- English is the default route tree (`/`); Chinese uses `/zh/`.
- Do not add Projects, Blog, Alumni, footer navigation, or footer language links.
- News and Events keep archive pages but never enter the primary navigation.
- The home page contains only Highlights and Events beneath the Greene-style header.
- Use `PUBLICATIONS` and `OPPORTUNITIES` consistently, including the plural forms.

## Maintenance rules

- Preserve the Greene Lab v1.4.0 core where practical. Put project-specific work in
  `_includes/custom/`, `_styles/custom.scss`, `_scripts/custom.js`, custom layouts,
  and `_plugins/custom_*.rb`.
- Content editors maintain structured Markdown/YAML through Pages CMS. Do not expose
  Liquid, HTML, SCSS, or JavaScript as normal editorial fields.
- A DOI is the single publication identifier. Do not copy bibliographic metadata into
  Research or member records.
- Real content must replace placeholders field-by-field; do not restructure pages to
  accommodate missing content.
- Empty optional fields must remain hidden. Empty team and opportunity categories must
  remain hidden.
- Departed members use `active: false` or `display: false`; never create an Alumni page.
- Keep images accessible with localized alt text.

## Before merging

Run `py scripts/validate_content.py`, then build with Jekyll and run the generated-site
checks described in `BUILD_SPEC.md`.
