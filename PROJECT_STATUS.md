# Project status

Updated: 2026-09-23
Current release line: UI V1.4 on `main`

## Production validated

The authoritative GitHub Actions build is now passing. Run
[`35851579896`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35851579896)
validated the content, installed the locked Ruby dependencies, completed a production
Jekyll build, checked all required EN/ZH routes and assets, and passed HTML Proofer.

Validated runtime:

- Ruby 3.3.12 and Bundler 2.5.6.
- Jekyll 4.4.1 and `sass-embedded` 1.104.1.
- 11 collection records, one DOI source and one generated citation.
- 20 generated HTML files for the root-path CI build.
- Empty optional links are hidden rather than emitted as anchors without targets.
- GitHub Pages base-path builds strip `/energy-materials-lab-website` only for local
  HTML-Proofer resolution; deployed URLs retain the required prefix.

The local Windows host still has no system Ruby/Jekyll or Docker. This is no longer a
release blocker because the pinned GitHub Actions runner is the authoritative build
environment.

## Deployment

- Repository: <https://github.com/DavidHMeng/energy-materials-lab-website>
- Visibility: Public.
- Default branch: `main`.
- GitHub Pages build type: GitHub Actions.
- Preview URL: <https://davidhmeng.github.io/energy-materials-lab-website/>
- HTTPS enforcement: enabled.
- Latest UI V1.4 deployment: run
  [`35851790760`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35851790760)
  from commit [`810503f`](https://github.com/DavidHMeng/energy-materials-lab-website/commit/810503f0d34cec949fa9c65ef4d9646696434a94).
- Staging artifact: run
  [`35851721856`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35851721856)
  produced the final `github-pages-staging` artifact for commit `810503f`.

GitHub CLI was used from an ignored portable directory only; it is not part of the
repository or the deployed site.

## UI V1.4 refinement

The current release preserves Framework V1.1, the frozen navigation and the Pages CMS
schema. It changes only presentation, responsive behavior and generated-site guards.

- Secondary-page headers are compact and tighten again after scrolling. The homepage
  retains its larger Greene-style header. Tablet and mobile rules keep the logo,
  hamburger, language switch and theme control usable; the non-essential school
  subtitle is hidden below 900 px so the tablet header is not forced taller by wrapping.
- Homepage primary navigation renders at 16 px and weight 500 at the inspected desktop
  viewport. Highlights use a one-pixel editorial lift, light tint, restrained shadow and
  title underline instead of the previous heavy rectangular elevation.
- Publications use a 1180 px desktop content width, a roughly 215 px visual column and
  24 px by 30 px citation padding while returning to a non-overflowing mobile column.
- Team keeps the existing CMS category order and data. The inspected desktop grid uses
  five columns, tablet uses three and mobile uses two, with centered circular portraits
  and two-line summaries.
- Member profiles use a compact 390.6 px desktop hero with a 260 by 325 px portrait.
  The profile hero is now a semantic `section` in normal document flow, not a global
  `header` affected by the Greene core sticky-header selector.

The overlap root cause was structural: `_styles/header.scss` intentionally applies
`position: sticky !important` to every `header`, while the member hero had also been
implemented as a `header`. Replacing the member hero with a `section` and enforcing
`position: relative` removes the sticky/fixed behavior rather than masking it with
z-index or overflow changes. Generated-site and source validators now reject a profile
hero that regresses to a global `header`.

Files changed for this release:

- `_layouts/default.html`, `_layouts/profile.html`
- `_includes/custom/team-grid.html`
- `_scripts/custom.js`, `_styles/custom.scss`
- `publications/index.md`, `zh/publications/index.md`
- `scripts/validate_content.py`, `scripts/check_generated_site.py`

## Browser QA

Validated on the hosted Pages site:

- Desktop (1280 px): homepage header remains about 432 px; secondary header is 136 px
  at the top and 124 px after scrolling. No tested page has horizontal overflow.
- Tablet (820 px): Publications remains a horizontal citation layout, Team renders three
  columns, and the profile portrait is 240 by 300 px. The final deployed CSS contains
  the 72/64 px compact-header rules, a non-shrinking logo and the tablet subtitle-hide
  rule; these rules were confirmed directly in the production asset after deployment.
- Mobile (390 px): secondary header is 64 px and tightens to 56 px; Publications is a
  single column, Team is two columns, and the profile portrait is 190 by 237.5 px.
- Profile scroll regression passed at 1280, 820 and 390 px in EN/ZH. It also passed in
  current Chrome and Edge at 1440 by 700: the hero is `position: relative`, moves out of
  the viewport, and does not overlap Education or Personal Note.
- A native Safari runtime was not available on the Windows validation host. Safari was
  therefore covered by the standards-based CSS/HTML build checks, not misreported as a
  live Safari browser run.
- Light and dark themes both render successfully; toggling changes the computed page and
  card colors. Reduced-motion handling remains in place for transitions and reveal
  effects.

- Homepage Introduction is present above Highlights in both language trees. Its desktop
  module measures about 651 px at the inspected viewport, the scientific image remains
  uncropped at 300 px, and the three-slide carousel advances automatically while
  retaining arrows, dots, pause behavior and reduced-motion handling.
- Team uses CMS-maintained bilingual role labels, compact circular portraits and
  two-line member summaries. A 320 px viewport renders two columns with centered text;
  final `scrollWidth` equals `clientWidth` (305 px), so no horizontal overflow remains.
- EN/ZH member profiles show Email, Research Interests, Education and Personal Note.
  Biography, phone/office display and member-specific publication sections are absent.

- Desktop homepage: exact primary navigation, EN language metadata, live assets, no
  empty anchors and no horizontal overflow.
- Representative EN routes: Research, Publications, Team, member profile,
  Opportunities, News and Events.
- Representative ZH routes: Homepage, Team and member profile, with localized titles
  and `lang="zh"`.
- The deployed custom 404 page is returned for an unknown path.
- Light/dark switching changes the rendered colors and the selected theme persists
  across a reload.
- A 320 px test exposed a horizontal overflow caused by `body { min-width: 320px; }`.
  Commit `1371ac4` removes that constraint, CI and Pages deployment pass, and the live
  CSS was confirmed updated. The final uncached 320 px test reports a 305 px layout
  viewport, 305 px document width, no horizontal overflow, and all navigation links
  visible.

## CMS validation

Validated. The hosted Pages CMS GitHub App is authorized for the repository and
`.pages.yml` exposes Homepage, News, Events, Research, Publications, Team,
Team Role Labels, Opportunities, Site Settings and Media.

The closed loop used `_news/2026-09-15-placeholder-publication.md`:

1. Pages CMS created commit [`2c85add`](https://github.com/DavidHMeng/energy-materials-lab-website/commit/2c85addf9cc163132b0090fcd0b05d7d4b98e861).
2. CI run [`35822457262`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35822457262) passed.
3. Pages run [`35822539380`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35822539380) deployed the change.
4. English and Chinese pages displayed the distinct CMS validation markers.
5. Revert commit [`4205075`](https://github.com/DavidHMeng/energy-materials-lab-website/commit/4205075dea98e9f9943c8561de0278b1b9ca8c73) restored the original content.
6. The cleanup CI and deployment passed, and both languages were verified marker-free.

The final maintenance guide is `PAGES_CMS_GUIDE.md`. Pages CMS actions are configured
for production deployment, staging artifact builds and DOI citation refresh.

## Pending real content

- Lab and school names, descriptions, address, email and copyright.
- Approved lab logo, school logo and campus header photograph.
- Real members, portraits, role assignments, short research summaries, personal notes,
  contact details and stable member IDs.
- Approved Homepage Introduction slogan, bilingual copy and a curated mix of graphical
  abstracts and laboratory/group photographs.
- Lab-owned DOI list and confirmed member-to-publication associations.
- Research areas, graphical abstracts and bilingual research statements.
- Confirmed News, Events and Opportunities content, dates and links.
- Approved brand colors only if the Greene defaults are to be replaced.

## Known operational notes

- Actions currently warns that the runner image will move to Ubuntu 26 and that an
  `upload-artifact` dependency still targets Node.js 20. GitHub forced that dependency
  to Node.js 24 and all workflows succeeded; monitor upstream action releases rather
  than weakening the validation gates.
- Pages deployment and citation refresh remain manual by design.
- Placeholder `example.edu` contact/application links are intentionally not production
  data and are excluded only from external-network validation, not internal checks.
