# Build and maintenance specification

## Baseline

- Upstream: `greenelab/lab-website-template` release `v1.4.0`.
- Runtime: Ruby 3.3.12, Bundler 2.5.6, Jekyll 4.4.1, GitHub Actions,
  Pages CMS. Versions are pinned by `.ruby-version` and `Gemfile.lock`.
- Deployment: static files only; no database or application server.
- Source control: public GitHub repository at
  `DavidHMeng/energy-materials-lab-website`; `main` is the default branch.
- Preview: `https://davidhmeng.github.io/energy-materials-lab-website/`, deployed by
  the manual Pages workflow after the same production checks used by CI.

## Local setup

1. Install Ruby 3.3.12 and Python 3.9+, or Docker Desktop.
2. Run `bash script/setup`.
3. Run `bash script/test` for the production build and acceptance checks.
4. Run `bash script/serve` and open the printed local URL for visual QA.

On Windows, `powershell -ExecutionPolicy Bypass -File scripts/preview.ps1` selects an
available Ruby or Docker route and explains what is missing when neither is installed.

## CI gates

The CI workflow validates content, builds Jekyll, checks generated routes, assets,
language/navigation invariants and internal links, and runs HTML Proofer without
external-network checks. Staging produces an Actions artifact only. The deployment
workflow remains manual so a validated commit can be reviewed before publication.

Generated-site checks also enforce the project typography attributes, a single load of
the project stylesheet, the compact profile contact layout, normal-flow profile hero,
profile summaries, the 1.65:1 contained-image carousel, and the absence of retired
phone/office output. Python regression tests exercise translation-state transitions
before every Jekyll build.

## Chinese-primary translation workflow

`Generate optional English content` is an isolated GitHub Actions workflow. It runs
after relevant content pushes or from Pages CMS, and may commit generated English plus
`_translation/state.yml` back to `main`. It never handles publication records. Existing
CI and manual staging/deployment remain independent, so missing credentials or a
translation-provider outage cannot block a valid site build.

Repository configuration:

- Actions secret: `TRANSLATION_API_KEY`.
- Repository variable: `TRANSLATION_MODEL` (required for generation).
- Optional repository variables: `TRANSLATION_PROVIDER=openai-compatible` and
  `TRANSLATION_API_BASE=https://api.openai.com/v1` (or a compatible endpoint).

The key is never exposed to Pages CMS, source YAML, client JavaScript, or the generated
site. `github-actions[bot]` is excluded from the workflow job and the generated commit
uses `[skip translate]`, preventing a translation commit loop. Without the secret/model,
the workflow records pending state and exits without compromising CI.

The citation refresh is also manual-only during staging. Enable its schedule only after
the target repository, branch protections and desired pull-request cadence are confirmed.

## UI and performance policy

- Same-origin multi-page navigation uses the native View Transition API. The root fade
  and 6 px entrance motion complete in about 220 ms and collapse for
  `prefers-reduced-motion`; the site remains a static multi-page Jekyll build.
- Internal navigation is prefetched only after pointer or keyboard intent, with a small
  per-page cap. No router or transition library is included.
- `dark-mode.js` remains synchronous to prevent a wrong-theme first paint. Other local
  scripts use `defer`; third-party scripts are already deferred.
- Google Font CSS is loaded non-blockingly with preconnect hints and `font-display=swap`.
  Typography alternatives use the existing Barlow download or system font stacks; no
  additional font families are fetched.
- The compiled project stylesheet must be linked exactly once. Below-fold team,
  research, event and carousel images use lazy loading where appropriate.
- Placeholder runtime images are sub-kilobyte SVG files. The current 642 KiB PNG in
  `images/uploads/` is not referenced by a page and therefore creates no page request.
  Before real photos are published, prefer optimized WebP/AVIF and avoid oversized
  originals.

## Upstream policy

Record the upstream release in `_data/upstream.yaml`. For future updates, compare the
new release against the retained core folders before merging. Reapply only the custom
layer; never overwrite custom schemas or frozen navigation.

## Acceptance routes

`/`, `/research/`, `/publications/`, `/team/`, `/opportunities/`, `/news/`, `/events/`,
their `/zh/` counterparts, generated English and Chinese team profiles, and `/404.html`.
