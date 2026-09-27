# Pages CMS acceptance report

Updated: 2026-09-25  
QA branch: `codex/cms-citation-qa-v1-6`  
Pull request: https://github.com/DavidHMeng/energy-materials-lab-website/pull/1

This report records the V1.6 CMS/citation QA performed against the existing
Framework V1.1 information architecture. Temporary QA entries and test DOI
references were removed after verification.

## Acceptance matrix

| Module | Create | Edit | Hide/display | Order | Image/media | EN/ZH | Citation/build | Result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Site settings / typography | N/A | Caption Size changed and restored to `default` | N/A | N/A | Existing lab/school logo selectors verified | N/A | CI passed after restore | PASS |
| Homepage Introduction / Carousel | N/A | bilingual copy, slide metadata, A/B type, timing and optional related DOI saved and reverted | slide visibility controls verified | slide order verified | Existing media selection verified | both language fields saved | DOI was normalized and later removed during cleanup; final registry is clean | PASS |
| Highlights / News | QA entry created, edited, hidden, then deleted | bilingual summary edit saved | `display: false` rendered as hidden | N/A | existing school logo selected; bilingual alt text saved | both language fields saved | CI passed for each CMS commit | PASS |
| News fresh local upload | N/A | N/A | N/A | N/A | Browser file chooser rejected the automated local-file selection (`Not allowed`) | N/A | Existing media path remains valid | PARTIAL |
| Events | QA entry created, edited, hidden, then deleted | Chinese location edit saved | hidden entry did not remain in normal listing | N/A | N/A | bilingual title/location fields saved | CI passed | PASS |
| Research | N/A | related DOI list entry saved and removed | N/A | N/A | N/A | bilingual record retained | DOI normalization and registry check passed | PASS |
| Publications | DOI entry saved, citation generated, then removed | N/A | N/A | N/A | N/A | publication metadata unchanged | citation workflow run `36114896174` succeeded; final cleanup leaves one placeholder source/citation | PASS |
| Team member/profile | N/A | representative DOI saved and removed; existing profile fields retained | active/display behavior retained | category order unchanged | existing portrait/media references retained | bilingual fields retained | final CI run `36117027301` passed | PASS |
| Opportunities | QA entry created, edited, hidden, then deleted | bilingual content/link edit saved | `display: false` verified | display order `99` saved | N/A | bilingual fields saved | CI passed | PASS |

## Citation QA evidence

The tested DOI `10.1021/jacs.5c22628` was entered through four supported CMS
entry points: Publications, Team representative DOIs, Research DOI list and a
Homepage carousel slide. The citation workflow normalized URL, `doi:` prefix,
case and full-width-colon variants into one canonical registry entry and
generated metadata successfully in run
https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/36114896174.

After the workflow was verified, the test DOI was removed from all content and
the generated citation. The final source tree contains one non-test placeholder
DOI source and one generated citation; `py scripts/citation_registry.py --check`
and content validation both pass.

## Build and staging evidence

- Final branch validation run: https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/36117721593
- Final staging artifact run: https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/36117560928
  produced `github-pages-staging` (3,665,258 bytes), digest
  `sha256:4582d3e7dc7947736ef0a5be712754a76bb21fcacdff0e9610b738fa2b726e42`,
  expiring 2026-10-02.
- Citation synchronization run: https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/36114896174
- QA-branch deployment is intentionally rejected by the `github-pages` branch
  policy, but the merged `main` deployment succeeded in
  https://github.com/DavidHMeng/energy-materials-lab-website/actions/runs/36132330770.
- Public URL: https://davidhmeng.github.io/energy-materials-lab-website/
  returned HTTP 200 after deployment. The CDN advertises `max-age=600`, so a
  previously open browser tab may retain old content for up to about ten minutes.
- The local Windows host has no Ruby/Jekyll installation; GitHub Actions remains
  the authoritative production/staging build environment.

## Known boundaries

1. The fresh local-file upload test could not be completed through the current
   browser automation file chooser. This does not invalidate existing CMS media
   selection or the previously committed official logo assets.
2. No changes were made to `main`, EIT VM, Nginx, DNS or HTTPS configuration.
3. The public staging URL cannot represent this QA branch until a repository
   administrator changes the protected Pages environment or merges deliberately.
