# Implementation audit

Audit date: 2026-09-22
Baseline inspected: `c68202a`
Framework: frozen Framework V1.1 on Greene Lab Website Template v1.4.0

## Status model

- **Implemented**: the required source/configuration exists and static inspection found
  no known specification gap.
- **Partially implemented**: some required source behavior is missing.
- **Not implemented**: no implementation exists.
- **Not validated**: the source exists, but the named execution layer has not run.

These terms are intentionally independent. Source implementation does not prove a
production Jekyll build, browser behavior, deployment, or Pages CMS round trip.

## Feature audit

| Area | Implementation status | Files and implementation | Source validation | Production build | Browser QA | CMS round trip |
| --- | --- | --- | --- | --- | --- | --- |
| Navigation | Implemented | `_includes/header.html`; four fixed primary links only | Validator asserts exact labels and count | Not validated | Not validated | Not applicable |
| Homepage | Implemented | `index.md`, `zh/index.md`; no added hero, only Highlights and Events below header | Front matter/YAML parsed | Not validated | Not validated | Not validated |
| Highlights / News | Implemented | `_news/`, `_includes/custom/news-card.html`, `/news/`, `/zh/news/`; fixed categories and homepage limit | Category, image and bilingual alt checks pass | Not validated | Not validated | Not validated |
| Events | Implemented | `_events/`, `_includes/custom/event-card.html`, archives; homepage summary plus archive description/gallery/date range | Type, dates, cover and bilingual alt checks pass | Not validated | Not validated | Not validated |
| Research | Implemented | `_research/`, bilingual Research pages, alternating custom layout, tokenized image ratio | Required fields and image paths pass | Not validated | Not validated | Not validated |
| Research DOI to citation | Implemented | `doi_list`, `find_citation_by_doi`, compact publication component | DOI must exist in both `sources.yaml` and `citations.yaml` | Not validated | Not validated | Not validated |
| Publications | Implemented | `_data/sources.yaml` is the manual DOI source; Greene `_cite` and citation include retained | Seed DOI metadata corrected against publisher/PubMed; source/citation matching passes | Not validated | Not validated | Not validated |
| Team | Implemented | `_members/`, fixed role groups, empty-group suppression, active/display filtering | Roles, duplicate slugs, portraits and alt text pass | Not validated | Not validated | Not validated |
| Member profiles | Implemented | `_layouts/profile.html`, bilingual page generator, optional-field hiding, `member_ids` publication filter | Python cross-reference checks exist; no fabricated seed member association remains | Not validated | Not validated | Not validated |
| Opportunities | Implemented | `_opportunities/`, group include, custom visibility filter | Category, tri-state value and date-order checks pass | Not validated | Not validated | Not validated |
| Footer | Implemented | `_includes/footer.html`; identity, school/college, address, email, logo, copyright only | Source inspection; generated checker forbids footer nav | Not validated | Not validated | Site settings not validated remotely |
| EN / ZH | Implemented | `/` and `/zh/` pages share collections with bilingual fields; member ZH routes generated | Required field and planned route checks exist | Not validated | Not validated | Not validated |
| Light / Dark | Implemented | `_scripts/dark-mode.js`; system preference on first visit and localStorage override | JavaScript syntax passes | Not validated | Not validated | Not applicable |
| Pages CMS | Implemented | `.pages.yml`; Homepage, News, Events, Research, Publications, Team, Opportunities, Site, Media | YAML and schema/path alignment checks pass | Not applicable | Not validated | Not validated; GitHub App authorization unknown |
| Responsive | Implemented | `_styles/custom.scss`; 900 px and 700 px breakpoints, reduced-motion handling | SCSS structural checks only | Not validated | Not validated on desktop/mobile | Not applicable |
| SEO / 404 | Implemented | `_includes/meta.html`, localized descriptions, canonical/hreflang, sitemap, EN/ZH 404, favicon | Source/YAML checks; generated routes/assets are asserted | Not validated | Not validated | Site URL pending deployment target |
| GitHub Actions | Implemented | CI, manual staging artifact, manual Pages deployment, manual citation refresh | Workflow YAML parses locally | Not validated on GitHub | Not applicable | Not applicable |
| Placeholder data | Implemented | Structured placeholders across every collection and media folder | 11 collection records plus DOI/source/citation checks pass | Not validated | Not validated | One News record selected for future CMS round-trip test |

## Current validation boundary

Validated locally: YAML/front matter, CMS-to-schema alignment, category/role enums,
image existence and localized alt requirements, DOI cross-references, date ordering,
JavaScript/Python/PowerShell syntax, forbidden route directories, and exact navigation
labels.

Not validated locally: Ruby plugin execution, Liquid rendering, Sass compilation,
Jekyll production output, HTML Proofer, generated routes/assets, or browser behavior.
The host has neither Ruby/Jekyll nor Docker.

Not validated remotely: GitHub Actions, GitHub Pages, GitHub permissions, Pages CMS
GitHub App authorization, CMS edit/commit/build round trip, and screenshots.

## Known implementation risks

1. Custom Ruby filters and bilingual page generation have not executed in Jekyll.
2. The first GitHub Actions run may expose lockfile or platform issues not observable
   without Ruby. `BUNDLE_FROZEN=true` prevents a silent dependency rewrite.
3. Absolute canonical URLs remain intentionally unavailable until the Pages origin and
   base path are supplied by `actions/configure-pages`.
4. Placeholder people, branding, dates, links and copy are not production content.
5. The DOI seed is real and its bibliographic metadata is verified, but it is not
   attributed to a placeholder member.
6. The Pages CMS guide and screenshots are intentionally absent until a hosted CMS
   round trip succeeds.

## Browser acceptance checklist pending deployment

- Desktop and mobile: header, four-item navigation, language and theme controls.
- EN and ZH: Homepage, Research, Publications, Team, member profile,
  Opportunities, News archive, Events archive, Footer and 404.
- Light and dark: contrast, images, cards, citation blocks and focus states.
- Layout: no overflow at 320 px; Research alternation; portrait and graphical-abstract
  ratios; footer has no navigation or language entry.
- Behavior: system theme on first visit; persisted user theme; language counterpart
  links; expired and empty opportunity categories hidden.
