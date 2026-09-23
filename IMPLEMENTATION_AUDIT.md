# Implementation audit

Audit updated: 2026-09-23
Validated commit: `1371ac4`
Framework: frozen Framework V1.1 on Greene Lab Website Template v1.4.0

## Status model

- **Implemented**: the required source/configuration exists and static inspection found
  no known specification gap.
- **Production validated**: the named behavior passed the production Jekyll/HTML build
  in GitHub Actions.
- **Browser validated**: the named behavior was exercised on the deployed Pages site.
- **CMS pending**: the source schema exists, but the hosted edit/commit/build/revert
  round trip still requires owner authorization.

## Feature audit

| Area | Implementation | Production evidence | Browser evidence | CMS evidence |
| --- | --- | --- | --- | --- |
| Navigation | Implemented: `_includes/header.html`; four fixed primary links only | Generated checker asserts exact labels/count on 20 HTML files | Desktop EN routes show the four required links; language control is separate | Not applicable |
| Homepage | Implemented: `index.md`, `zh/index.md`; only Highlights and Events below header | EN/ZH routes built and link-checked | EN/ZH hosted pages load; desktop and 320 px layouts inspected | CMS pending |
| Highlights / News | Implemented: `_news/`, custom card and EN/ZH archives | Categories, dates, localized alt fields and empty-link handling pass | Home and archive routes inspected | CMS pending; selected round-trip record identified |
| Events | Implemented: `_events/`, custom card, date range, gallery and archives | Types, dates, covers, assets and links pass | Home and archive routes inspected | CMS pending |
| Research | Implemented: `_research/`, bilingual alternating layout | Required fields, DOI references and images pass | Hosted EN route inspected; lazy assets exist and generated checks pass | CMS pending |
| Publications | DOI is the single identifier in `_data/sources.yaml`; Greene citation pipeline retained | One verified DOI source generated one citation; build passed | Hosted publication route inspected | CMS pending |
| Team | Fixed role groups, active/display filters, empty-group suppression | Roles, slugs, portraits, alts and bilingual routes pass | EN/ZH Team and member profiles inspected | CMS pending |
| Member optional fields | Empty optional values are suppressed in `_layouts/profile.html` | HTML Proofer found no empty anchors | Profile pages inspected | CMS pending |
| Opportunities | Categories, tri-state visibility and date logic implemented | Source and generated routes pass | Hosted route inspected | CMS pending |
| Footer | Identity/contact only; no navigation or language links | Generated checker rejects footer navigation | Hosted footer visible | Site settings CMS pending |
| EN / ZH | English `/`; Chinese `/zh/`; shared structured collections | Required route/language checks pass | Representative EN/ZH pages have localized titles and correct `lang` | CMS pending |
| Light / Dark | `_scripts/dark-mode.js`; first-visit system preference plus saved override | Script/assets pass generated checks | Toggle changes colors and survives reload | Not applicable |
| Pages CMS | Root `.pages.yml` exposes structured content/media only | YAML and content-schema alignment pass | Hosted sign-in page reachable | GitHub App authorization and round trip pending |
| Responsive | Custom 900 px and 700 px breakpoints; reduced-motion handling | Sass compiles in production | Desktop passed; 320 px overflow found and fixed in `1371ac4`; final uncached screenshot pending | Not applicable |
| SEO / 404 | Localized meta, canonical/hreflang, sitemap, EN/ZH 404 and favicon | Routes and assets pass | Unknown hosted path renders custom 404 | Site metadata CMS pending |
| GitHub Actions | CI, staging artifact, manual Pages deploy and citation refresh | CI `35818157326`, deploy `35818208351`, staging `35818423091` succeeded | Preview is public over HTTPS | Not applicable |
| Placeholder data | Structured placeholders across collections/media | 11 records, one DOI source and one citation pass | Clearly rendered as placeholders | Must be replaced field-by-field |

## Validation evidence

The production workflow ran the following gate sequence on Ubuntu:

1. install locked Ruby and Python dependencies;
2. run `scripts/validate_content.py`;
3. run a production Jekyll build;
4. check required routes, assets, languages, navigation and forbidden routes;
5. run HTML Proofer for images, internal links, fragments and scripts.

The GitHub Pages deployment repeats the same gates with the real
`/energy-materials-lab-website` base path before uploading the Pages artifact.

## Remaining acceptance boundary

The website is now buildable, deployed and substantially browser-validated. It is not
content-complete and the editorial workflow is not yet proven. Remaining gates are:

1. owner authorization of the Pages CMS GitHub App;
2. CMS edit -> commit -> CI -> deployed EN/ZH verification -> revert loop;
3. final Pages CMS guide with screenshots from that verified loop;
4. final uncached 320 px screenshot after the prior CSS cache expires;
5. replacement and approval of all placeholder institutional and research content.
