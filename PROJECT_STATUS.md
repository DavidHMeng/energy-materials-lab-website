# Project status

Updated: 2026-09-23
Validated commit: `1371ac4`

## Production validated

The authoritative GitHub Actions build is now passing. Run
[`35818157326`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35818157326)
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
- Latest successful deployment: run
  [`35818208351`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35818208351).
- Staging artifact: run
  [`35818423091`](https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/35818423091)
  produced `github-pages-staging` (114,550 bytes), retained until 2026-09-30.

GitHub CLI was used from an ignored portable directory only; it is not part of the
repository or the deployed site.

## Browser QA

Validated on the hosted Pages site:

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
  CSS was confirmed updated. One final browser screenshot remains pending until the
  previous CSS response leaves the browser's ten-minute cache.

## CMS validation

Not yet complete. `.pages.yml` is present at the repository root and its schema matches
the content files. The hosted Pages CMS sign-in page is reachable, but GitHub sign-in
and installation/authorization of the Pages CMS GitHub App require the repository
owner's account approval.

Planned closed-loop record: `_news/2026-09-15-placeholder-publication.md`.

1. Sign in at <https://app.pagescms.org/> with GitHub.
2. Install/authorize Pages CMS for `DavidHMeng/energy-materials-lab-website`.
3. Edit the record's bilingual title or summary and save it through Pages CMS.
4. Verify the CMS commit, successful CI, and rendered EN/ZH change.
5. Revert the test edit, then verify CI and deployment again.
6. Only after this loop succeeds, finalize `PAGES_CMS_GUIDE.md` with real screenshots.

## Pending real content

- Lab and school names, descriptions, address, email and copyright.
- Approved lab logo, school logo and campus header photograph.
- Real members, portraits, roles, bios, contact details and stable member IDs.
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
