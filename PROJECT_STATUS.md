# Project status

Updated: 2026-09-25
Current release line: UI / CMS Workflow V1.6 on `main`

## CMS placeholder independence correction (2026-09-25)

CMS collection records are no longer treated as production build fixtures. The eight
temporary PhD density records were removed through Pages CMS, exposing a validator bug
that required all eight records even though the documented maintenance contract said
they were removable. The content validator no longer checks a placeholder prefix or
minimum placeholder count.

The corrected contract is:

- Research, News, Events, Team and Opportunities may contain zero or more records;
- no placeholder slug, filename, record count, text value or placeholder image is a
  production requirement;
- records may be deleted, hidden or replaced through Pages CMS;
- retained records still require valid schema fields, unique identifiers, configured
  role references, dates, DOI references, existing image paths and localized alt text;
- deleted editorial files are pruned from `_translation/state.yml` by the translation
  workflow so stale per-record state does not accumulate;
- Homepage Introduction and Site Settings remain structural file records and retain
  their essential carousel, identity, accessibility and typography checks.

CI now runs `scripts/test_cms_record_independence.py`, which removes all editable
collection records in an isolated copy and requires `validate_content.py` to pass.
Remote `main`, production publishing and Pages CMS deployment evidence is recorded
after the corresponding GitHub Actions runs complete.

## CMS / Citation QA V1.6 (2026-09-25)

The existing Framework V1.1 information architecture and Pages CMS model were
kept unchanged. The QA branch exercised the CMS create/edit/hide/delete paths
for News, Events and Opportunities, bilingual Homepage/Research/Publications/
Team fields, typography settings, media selection and the DOI citation action.
Temporary QA entries and the test DOI were removed after the workflow was
verified. The final tree contains no `cms-qa-test` records and no
`10.1021/jacs.5c22628` content/citation reference.

Evidence:

- Final branch validation: [GitHub Actions run 36117027301](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/36117027301)
  passed after the CMS cleanup. The final documentation commit was then
  revalidated by [run 36117721593](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/36117721593).
- Final staging artifact: [run 36117560928](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/36117560928)
  produced `github-pages-staging` (3,665,258 bytes), digest
  `sha256:4582d3e7dc7947736ef0a5be712754a76bb21fcacdff0e9610b738fa2b726e42`,
  expiring 2026-10-02.
- Citation synchronization: [GitHub Actions run 36114896174](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/36114896174)
  normalized mixed DOI forms and generated one citation for the test entry
  before it was deliberately removed.
- Local checks passed: citation-registry unit tests, CMS-schema tests,
  translation tests, content validation, translation dry-run, citation-registry
  synchronization check and `git diff --check`.
- The complete module-by-module record is in
  [`CMS_ACCEPTANCE_REPORT.md`](CMS_ACCEPTANCE_REPORT.md).

Known limits: a new local-file upload could not be completed through the current
browser automation file chooser, while existing official logo/media selection
and committed assets were verified. The QA branch remains intentionally blocked
by the `github-pages` environment policy, while the merged `main` deployment is
now successful.

Main deployment after merge:

- Merge commit: `d58d4e2` (followed by the translation-state bookkeeping commit
  `9cce312`).
- GitHub Pages deployment: [run 36132330770](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/36132330770)
  succeeded on `main`.
- Public staging URL: <https://davidhmeng.github.io/energy-materials-lab-website/>
- Live checks returned HTTP 200 for the English home page, Chinese `/zh/` route
  and canonical uploaded image. The public HTML references the unique
  `/images/uploads/4156020251853fig1.jpg` path and does not reference the removed
  `-1.jpg` duplicate.
- CDN response cache is `max-age=600`; allow up to about ten minutes for an
  already-open browser tab or edge cache to refresh.


## EIT Production Server Migration V1.0 (2026-09-24)

Target architecture is now the approved pull-deployment model: Pages CMS edits `main`;
GitHub Actions gates citation freshness, translation/fallback and content validation;
the production Jekyll build publishes generated files to `server-deploy`; the EIT VM
will later fetch that branch into SHA-named releases and serve the atomic `current`
symlink through Nginx.

Implemented in this migration:

- layered `_config.yml`, `_config.staging.yml` and `_config.production.yml`;
- GitHub Pages preserved as noindex staging with its repository base path;
- production root-path metadata, sitemap, robots and legacy-base-path validation;
- main-only `.github/workflows/publish-production.yml`, with write permission limited
  to the final publish job and a secret-free production `version.json`;
- `ops/` Nginx, pull-sync, systemd service/timer templates and manual VM runbook;
- `DEPLOYMENT.md` architecture, EIT network-admin request, acceptance and rollback.

Verified GitHub/build migration evidence for implementation commit
[`7674579`](https://github.com/DavidHMeng/energy-materials-lab-website/commit/767457992c868aeb1e4b2111e2fddcea19fd8c72):

- CI run [`35982387060`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35982387060)
  passed the production Jekyll build, generated-route/SEO/root-path checks and HTML
  Proofer.
- Production run [`35982387259`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35982387259)
  passed Citation, Translation/fallback, content, build and publish jobs.
- That run built source/build SHA `767457992c868aeb1e4b2111e2fddcea19fd8c72`
  and published generated branch SHA `14a76d15691499c101b0b015b2075f7f1f1e02e9`.
- The generated branch root contains only deployable website output; source-only docs,
  workflows, configs and build tooling are absent. Its production files contain no
  `/energy-materials-lab-website/` dependency.
- Staging artifact run [`35982547245`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35982547245)
  passed the real GitHub Pages base-path, noindex, canonical, route, asset and link
  checks. The existing public staging URL remained reachable.

This evidence record is excluded from Jekyll output and does not change the production
page set. Until the user executes the VM runbook, the correct boundary remains:
**GITHUB/BUILD MIGRATION COMPLETE / EIT VM DEPLOYMENT PENDING USER EXECUTION**.

## UI / CMS Workflow V1.5 extension (2026-09-24)

This extension keeps Framework V1.1, the frozen navigation and the existing Pages
CMS collections. It adds the approved Homepage Introduction, profile and bilingual
editorial-workflow refinements without changing the site's information architecture.

Production evidence:

- Final source commit:
  [`7f04a6d`](https://github.com/DavidHMeng/energy-materials-lab-website/commit/7f04a6dca37001f12dc5af52851e8dc19cdde677).
  The feature implementation is in `8ecee69`; follow-up commits `a4c9bb2`, `7d6614f`
  and `7f04a6d` correct generated-style assertions, clip the full-width transition's
  scrollbar remainder and add a build-specific version to `custom.css` so browsers do
  not retain an obsolete project stylesheet after deployment.
- Final CI run
  [`35952350699`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35952350699)
  passed source validation, the locked Jekyll production build, generated-route and
  HTML checks for commit `7f04a6d`.
- Staging run
  [`35951169031`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35951169031)
  produced the `github-pages-staging` artifact for the feature implementation.
- Translation workflow run
  [`35951192707`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35951192707)
  passed the complete production build in fallback mode and explicitly reported that
  translation credentials are not configured.
- Final production deployment run
  [`35952411226`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35952411226)
  successfully published commit `7f04a6d` to
  <https://davidhmeng.github.io/energy-materials-lab-website/>.

Implemented behavior:

- Homepage Header-to-Introduction spacing now uses a restrained full-width tonal
  transition. The graphical-abstract carousel is capped at 1120 px with a 1.65:1
  scientific-image region, `object-fit: contain`, centered positioning, manual controls,
  autoplay pause behavior and reduced-motion handling. Real publisher graphical
  abstracts were not copied without confirmed reuse rights; the structured placeholders
  remain until lab-owned or licensed images are supplied.
- Homepage carousel records may optionally reference a publication DOI. Journal and
  year are resolved from the existing citation source instead of duplicating metadata.
- Member profiles use a compact portrait/contact column and a top-aligned identity area
  with an editable bilingual Profile Summary. Representative publication DOI lists use
  the existing citation renderer and remain hidden when empty. Placeholder members have
  no fabricated publication associations.
- Pages CMS now treats suitable Chinese fields as required and their English counterparts
  as optional. Names and other official English text remain manual. Publication records
  and citation metadata are excluded from translation.
- `scripts/translate_content.py` provides a provider-neutral, academic-English workflow
  with sidecar hash/status tracking. Manual English is never overwritten automatically;
  changed Chinese marks manual English for review, while previously auto-generated
  English may be refreshed. Jekyll provides an in-memory Chinese fallback when English
  is still blank, so builds do not depend on an external translation service.
- The Pages CMS entry action `Generate pending English` is present. To activate actual
  persisted machine translation, repository secret `TRANSLATION_API_KEY` and repository
  variable `TRANSLATION_MODEL` still need to be configured; optional provider/base-URL
  variables are documented in `PAGES_CMS_GUIDE.md`.

Live browser QA on the final deployment:

- Desktop, 1280 by 720: the homepage carousel is 1120 px wide; graphical abstracts
  resolve to `object-fit: contain`; the Publications content and citation row use the
  full 1180 px content width. The member hero is 1180 by about 447 px with a 190 by
  238 px portrait.
- Tablet, 820 by 900: the homepage carousel is 722 px wide with no navigation overlap;
  the member hero is about 773 by 418 px with a 170 by 213 px portrait. After scrolling
  to Research interests, the portrait is above the viewport and the measured overlap is
  zero.
- Mobile, 426 by 687: English and Chinese pages render without horizontal interaction
  leakage; the 345 px carousel keeps images uncropped. The Chinese Team page has the
  existing category order, ten fixture cards, centered wrapping, two columns and 128 px
  circular portraits. The Chinese member hero stacks to about 378 px wide with a
  170 by 213 px portrait.
- EN/ZH document language metadata and localized Introduction/Profile Summary content
  passed. Light and dark themes passed; dark mode resolves to an `rgb(24, 24, 24)` body,
  white primary text and a distinct bordered carousel surface.
- Profile regression passed on desktop, tablet and mobile. Portraits are `position:
  static` inside a `position: relative` hero; after a 708 px desktop scroll the portrait
  bottom was -198 px and overlap with Research interests was zero. Research interests,
  Education and Personal Note remain in normal flow.

Local pre-push checks also passed: 19 collection records, one DOI source, one citation,
four translation state-machine tests and a no-change translation dry run. Native Safari
is unavailable on this Windows host and is not reported as a live Safari test.

## Production validated

The authoritative GitHub Actions build is now passing. Run
[`35874347716`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35874347716)
validated the content, installed the locked Ruby dependencies, completed a production
Jekyll build, checked all required EN/ZH routes and assets, and passed HTML Proofer.

Validated runtime:

- Ruby 3.3.12 and Bundler 2.5.6.
- Jekyll 4.4.1 and `sass-embedded` 1.104.1.
- 19 collection records, one DOI source and one generated citation.
- 38 generated HTML files for the root-path CI build, including the expanded
  placeholder-member routes in both languages.
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
- Latest UI V1.5 deployment: run
  [`35874778117`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35874778117)
  from commit [`0c5b075`](https://github.com/DavidHMeng/energy-materials-lab-website/commit/0c5b0754506611a732bfa38c3cc9a6477e34af5e).
- Staging artifact: run
  [`35874588397`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35874588397)
  produced the final `github-pages-staging` artifact for commit `0c5b075`.

GitHub CLI was used from an ignored portable directory only; it is not part of the
repository or the deployed site.

## UI V1.5 refinement

This release preserves Framework V1.1 and the frozen information architecture while
refining the homepage identity, dense-team presentation, member profiles, transitions,
performance and editor-safe typography controls.

- The homepage lab name is the primary text identity at a measured 37.6 px on the
  1280 px viewport. Primary navigation measures 18.56 px and retains medium weight;
  the university line remains visually secondary.
- Team collections use a centered wrapping layout. The expanded fixture now contains
  eight additional PhD Student placeholders maintained through the normal Team CMS
  collection. The 1280 px layout is five columns with a centered four-card final row,
  the 820 px layout is three columns, and the 390 px layout is two columns with a
  centered single-card final row.
- Member profile heroes now use a compact 4:5 portrait, left-side contact stack and a
  right-side identity block. Email, localized address and Google Scholar are present
  for the representative fixture; empty optional ORCID, website, GitHub and
  ResearchGate fields remain hidden.
- Pages CMS exposes controlled heading/body families, lab/navigation/page/section/body/
  caption size presets and line-height presets under Site Settings. Editors choose
  semantic presets; arbitrary CSS values are not exposed.
- Cross-document transitions use the native View Transition API with restrained
  opacity and six-pixel movement, preserve reduced-motion behavior and degrade to
  ordinary navigation when unsupported. Intent-based prefetching is capped and only
  applies to same-origin primary content links.
- The project stylesheet now loads exactly once. Local scripts other than the
  synchronous theme initializer are deferred, Google font loading is non-blocking, and
  team images use lazy loading with asynchronous decoding.

Files changed for this release:

- `_layouts/default.html`, `_layouts/profile.html`
- `_includes/custom/team-grid.html`, `_includes/fonts.html`, `_includes/scripts.html`,
  `_includes/styles.html`
- `_styles/custom.scss`, `_scripts/custom.js`, `_data/site.yaml`, `.pages.yml`
- `_members/alex-chen.md`, `_members/jianwen-liang.md`, `_members/phd-student-01.md` through
  `_members/phd-student-08.md`
- `scripts/validate_content.py`, `scripts/check_generated_site.py`
- `CONTENT_SCHEMA.md`, `BUILD_SPEC.md`, `PAGES_CMS_GUIDE.md`, `PROJECT_STATUS.md`

## CMS slug/routing correction (2026-09-25)

The Pages CMS commit `83ccd8f` changed the member data slug to `jianwen-liang`
while the source file remained `_members/mei-li.md`. Before this correction,
English member routes used the collection filename while the localized generator
used the front-matter slug. The resulting CI failure reported broken
`/zh/team/mei-li/` and `/team/jianwen-liang/` links and a missing localized
profile route.

The custom member generator, language toggle and alternate-link metadata now all
use the editable front-matter slug for both language trees. Existing CMS entries
can therefore change slug without a manual filesystem rename; new entries still
use the `{slug}.md` creation template. `check_generated_site.py` discovers all
visible member profiles dynamically instead of hard-coding one placeholder name.
The complete input contract and format matrix is documented in
`CMS_INPUT_FORMATS.md`; `scripts/test_cms_input_contract.py` is part of the CI test
suite.

## Previous UI V1.4 baseline (historical)

That release preserved Framework V1.1, the frozen navigation and the Pages CMS schema.
It changed only presentation, responsive behavior and generated-site guards.

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

Current UI V1.5 validation on the deployed Pages site:

- Desktop Edge at 1280 by 900: homepage lab name 37.6 px, primary navigation
  18.56 px, exactly one project stylesheet, and no horizontal overflow. Team renders
  five columns; the incomplete four-card PhD row is centered.
- Tablet Edge at 820 by 900: the compact secondary header is 72 px, Team renders three
  columns, theme switching changes the computed body palette, and no horizontal
  overflow occurs.
- Mobile Edge at 390 by 844: the Chinese secondary header is 64 px, Team renders two
  columns with the final member centered, the profile portrait is 170 by 213 px, and
  Publications remains a single non-overflowing column. English and Chinese routes
  report the correct `lang` metadata.
- The representative desktop profile hero is 403 px high with a 190 by 238 px
  portrait. Its hero is `position: relative` and its portrait is `position: static`.
  After scrolling to Personal Note, the desktop portrait bottom is -39 px and the
  mobile portrait bottom is -515 px, so it has left the viewport and cannot cover
  Research Interests, Education or Personal Note.
- Light and dark modes were visually and computationally checked after transition
  completion. In dark mode the body resolves to `rgb(24, 24, 24)` with white primary
  text and muted profile contacts; returning to light mode resolves to white.
- Native Safari is unavailable on this Windows host and was not misreported as a live
  Safari run. Standards-based production build, HTML checks and progressive fallback
  cover unsupported View Transition implementations.

The following bullets retain the earlier UI V1.4 regression record:

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

UI V1.5 extends those existing collections without changing their identity: Team now
exposes bilingual affiliation/address plus standard academic-profile links, while Site
Settings exposes controlled Typography presets. Source validation confirms the nested
CMS schema and rejects retired phone, office, biography and member-publication fields.
The eight additional PhD fixtures are ordinary Team records and can be replaced or
removed through Pages CMS without a template edit.
The live Pages CMS Site Settings editor was opened read-only after deployment and
rendered Typography plus all nine controlled fields (Heading Font, Body Font, six size
presets and Line Height). No CMS value was changed or saved during this verification.

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
