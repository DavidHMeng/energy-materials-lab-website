# Project status

Updated: 2026-09-22

## Production validated

No production build has been validated yet. Local source validation passes, but this
machine has no Ruby/Jekyll or Docker. GitHub Actions is the designated authoritative
build environment and has not run because the repository has no remote.

Local source checks currently pass for 11 collection records, one DOI source, one
citation seed, CMS schema alignment, images/alts, date ordering, navigation and
forbidden routes.

## CMS validated

Not validated. `.pages.yml` is implemented and statically aligned with the content
schema, but there is no confirmed GitHub repository and no evidence that the Pages CMS
GitHub App is authorized.

Planned closed-loop record: `_news/2026-09-15-placeholder-publication.md`. The hosted
test must edit its bilingual title/summary, commit through Pages CMS, run CI, verify the
rendered EN/ZH result, then revert the test edit. `docs/PAGES_CMS_GUIDE.md` and real
screenshots must not be produced until that succeeds.

## Pending content

- Lab and school names, descriptions, address, email and copyright.
- Approved lab logo, school logo and campus header photograph.
- Real members, portraits, roles, bios, contact details and stable member IDs.
- Lab-owned DOI list and confirmed member-to-publication associations.
- Research areas, graphical abstracts and bilingual research statements.
- Confirmed News, Events and Opportunities content, dates and links.
- Approved brand colors only if the Greene defaults are to be replaced.

## Deployment

- Local branch: `main`.
- Git remote: none.
- GitHub CLI: not installed.
- Git Credential Manager 2.7.3 is present, but its read-only GitHub account list is
  empty. No GitHub login or token scopes can therefore be confirmed.
- Git identity or GitHub owner hints: none found in global configuration or safe
  environment variables.
- Remote writes performed: none.
- CI: runs on pull requests and pushes to `main`; read-only except normal Actions logs.
- Staging: manual workflow builds and uploads a seven-day artifact; it does not publish.
- Pages deployment: manual workflow only.
- Citation refresh: manual workflow only until the target repository is confirmed.

An accurate full repository name cannot be inferred from the local Windows username.
The recommended repository basename is `energy-materials-lab-website`, with **Public**
visibility for transparent academic publishing and the simplest Pages/Pages CMS flow.
The final full name must be `<confirmed-owner>/energy-materials-lab-website` after the
owner is supplied. No repository should be created from this placeholder.

## Known issues

- Production Jekyll build, Sass compilation, custom Ruby filters and generated bilingual
  member pages are not yet executed.
- GitHub Actions syntax is parsed locally but not run by GitHub.
- Desktop/mobile, EN/ZH and light/dark browser matrices are not validated.
- HTML/internal-link/asset checks are implemented but require generated `_site` output.
- Pages CMS hosted round trip, authorization and screenshots are pending.
- Absolute site origin, GitHub Pages base path and repository visibility are pending.
- Placeholder application link uses `example.edu` and is intentionally non-production.
