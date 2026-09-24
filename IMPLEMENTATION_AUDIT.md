# Implementation audit

Audit updated: 2026-09-24
Latest UI V1.3 baseline: current `main`
Framework: frozen Framework V1.1 on Greene Lab Website Template v1.4.0

## Status model

- **Implemented**: the required source/configuration exists and static inspection found
  no known specification gap.
- **Production validated**: the named behavior passed the production Jekyll/HTML build
  in GitHub Actions.
- **Browser validated**: the named behavior was exercised on the deployed Pages site.
- **CMS validated**: the hosted editor created a real commit which passed CI, deployed
  to EN/ZH pages, and was then cleanly reverted and redeployed.

## Feature audit

| Area | Implementation | Production evidence | Browser evidence | CMS evidence |
| --- | --- | --- | --- | --- |
| Navigation | Implemented: `_includes/header.html`; four fixed primary links only | Generated checker asserts exact labels/count on 20 HTML files | Desktop EN routes show the four required links; language control is separate | Not applicable |
| Homepage | Introduction with bilingual copy and A/B visual carousel above Highlights and Events | V1.3 production Jekyll, route, asset and HTML gates pass | EN/ZH structure, 651 px desktop module, carousel controls and 320 px layout inspected | Introduction copy, slides, types, alt, order and timing exposed |
| Highlights / News | Implemented: `_news/`, custom card and EN/ZH archives | Categories, dates, localized alt fields and empty-link handling pass | Home and archive routes inspected | Real bilingual edit/commit/deploy/revert completed |
| Events | Implemented: `_events/`, custom card, date range, gallery and archives | Types, dates, covers, assets and links pass | Home and archive routes inspected | Collection loaded from live schema |
| Research | Implemented: `_research/`, bilingual alternating layout | Required fields, DOI references and images pass | Hosted EN route inspected; lazy assets exist and generated checks pass | Collection loaded from live schema |
| Publications | DOI is the single identifier in `_data/sources.yaml`; Greene citation pipeline retained | One verified DOI source generated one citation; build passed | Hosted publication route inspected | File editor and DOI refresh action configured |
| Team | CMS-maintained role labels, compact circular portrait grid, active/display filters and empty-group suppression | V1.3 source and production gates pass | Desktop and two-column 320 px grids inspected; mobile width has no horizontal overflow | Members and Team Role Labels exposed as structured editors |
| Member optional fields | Profiles show email/academic links, interests, education and optional plain-text Personal Note; no phone/office/publications | EN/ZH generated profiles pass production checks | EN and ZH Personal Note pages inspected; retired sections are absent | Personal Note is plain text; retired fields are not exposed |
| Opportunities | Categories, tri-state visibility and date logic implemented | Source and generated routes pass | Hosted route inspected | Collection loaded from live schema |
| Footer | Identity/contact only; no navigation or language links | Generated checker rejects footer navigation | Hosted footer visible | Site Settings loaded in CMS |
| EN / ZH | English `/`; Chinese `/zh/`; shared structured collections | Required route/language checks pass | Representative EN/ZH pages have localized titles and correct `lang` | Bilingual CMS edit rendered in both route trees |
| Light / Dark | `_scripts/dark-mode.js`; first-visit system preference plus saved override | Script/assets pass generated checks | Toggle changes colors and survives reload | Not applicable |
| Pages CMS | Root `.pages.yml` exposes structured content/media and workflow actions | YAML and content-schema alignment pass | Hosted editor and repository content loaded | Commit `2c85add`, CI, deploy, EN/ZH render and cleanup validated |
| Motion and responsive UI | Native cross-page transitions, restrained card/link motion, reveal effects, carousel controls and reduced-motion fallback | JavaScript syntax, Sass/Jekyll compilation and generated-site checks pass | Desktop and 320 px layouts inspected; carousel advances and mobile overflow is absent | Carousel interval, order and visibility are editable |
| SEO / 404 | Production canonical/OG/Twitter/JSON-LD/hreflang/sitemap/robots; staging canonical-to-production plus noindex; EN/ZH 404 and favicon | Environment-aware generated checks are implemented; final run evidence is recorded in `PROJECT_STATUS.md` | Existing staging unknown-path behavior was previously checked | Site metadata editor loaded |
| GitHub Actions | CI, staging artifact, manual Pages deploy, citation refresh, gated production build and static-branch publish | Production publish has independent citation, translation and content prerequisites; only publish can write contents | Existing staging preview is public over HTTPS | Existing CMS actions remain configured |
| Placeholder data | Structured placeholders across collections/media | 11 records, one DOI source and one citation pass | Clearly rendered as placeholders | Must be replaced field-by-field |

## Validation evidence

The production workflow ran the following gate sequence on Ubuntu:

1. install locked Ruby and Python dependencies;
2. run `scripts/validate_content.py`;
3. run a production Jekyll build;
4. check required routes, assets, languages, navigation and forbidden routes;
5. run HTML Proofer for images, internal links, fragments and scripts.

The GitHub Pages deployment repeats the gates with the real
`/energy-materials-lab-website` base path and noindex policy before uploading the
staging artifact. Production uses an empty base path, writes a secret-free
`version.json`, and is published as static files at the `server-deploy` branch root.

## Remaining acceptance boundary

The staging website is buildable, deployed, browser-validated and CMS-validated.
GitHub/build migration and EIT VM deployment are tracked separately. The VM is not
considered deployed until the user performs `DEPLOYMENT.md` and verifies the upstream.
Remaining work includes:

1. replace and approve all placeholder institutional and research content;
2. add lab-owned DOI records and verify generated citation pull requests;
3. execute the documented VM/Nginx/systemd setup and request the school edge mapping;
4. monitor upstream action releases for the current Node/runner deprecation warnings.
