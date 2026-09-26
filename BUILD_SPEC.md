# Build and maintenance specification

## Baseline

- Upstream: `greenelab/lab-website-template` release `v1.4.0`.
- Runtime: Ruby 3.3.12, Bundler 2.5.6, Jekyll 4.4.1, GitHub Actions,
  Pages CMS. Versions are pinned by `.ruby-version` and `Gemfile.lock`.
- Deployment: static files only; no database or application server. GitHub Actions
  builds production; the EIT VM never runs Jekyll or content tooling.
- Source control: public GitHub repository at
  `DavidHMeng/energy-materials-lab-website`; `main` is the default branch.
- Staging preview: `https://davidhmeng.github.io/energy-materials-lab-website/`, with
  `baseurl: /energy-materials-lab-website`, deployed by the manual Pages workflow.
- Production origin: `https://jliang.eitech.edu.cn`, with an empty `baseurl`; built
  output is published at the root of the `server-deploy` branch for VM pull deployment.
- Layered configuration: `_config.yml` plus `_config.staging.yml` or
  `_config.production.yml`. Do not copy the site source for either environment.

## Local setup

1. Install Ruby 3.3.12 and Python 3.9+, or Docker Desktop.
2. Run `bash script/setup`.
3. Run `bash script/test` for the production build and acceptance checks. For staging,
   set `JEKYLL_CONFIG=_config.yml,_config.staging.yml`, the staging URL/base path, and
   `SITE_ENVIRONMENT=staging` as shown in the staging workflow.
4. Run `bash script/serve` and open the printed local URL for visual QA.

On Windows, `powershell -ExecutionPolicy Bypass -File scripts/preview.ps1` selects an
available Ruby or Docker route and explains what is missing when neither is installed.

## CI gates

The CI workflow validates content, builds production Jekyll, checks generated routes,
assets, language/navigation invariants, metadata and internal links, and runs HTML
Proofer without external-network checks. The staging artifact and manual Pages deploy
use the staging layer and must retain the repository base path.

CMS collection records are editorial data, not build fixtures. CI must accept an empty
Research, News, Events, Team or Opportunities collection and must never require a
placeholder slug, filename, record count or placeholder image. Records that remain are
still checked for schema completeness, stable identifiers, valid references, dates,
accessible image metadata and existing media paths.

`Publish production static branch` runs only for `main`. Citation freshness,
translation/fallback tests and content validation are independent prerequisites. Only
after all three pass does it run the exact production Jekyll build, add `version.json`,
check root-path output, upload the artifact, and replace `server-deploy`. The publish
job alone has `contents: write`; failed gates leave `server-deploy` unchanged. Because
the workflow listens only to `main`, publishing the generated branch cannot loop.

Generated-site checks also enforce the project typography attributes, a single load of
the project stylesheet, the compact profile contact layout, normal-flow profile hero,
profile summaries, the fixed scientific carousel canvas, and the absence of retired
phone/office output. Python regression tests exercise translation-state transitions
before every Jekyll build. Production checks also enforce production canonical,
OpenGraph, Twitter, JSON-LD, reciprocal hreflang, sitemap and robots values; reject
legacy GitHub Pages base-path leakage; and validate the public build manifest.

## Chinese-primary translation workflow

`Generate optional English content` is an isolated GitHub Actions workflow. It runs
after relevant content pushes or from Pages CMS, and may commit generated English plus
`_translation/state.yml` back to `main`. It never handles publication records. Existing
CI and manual staging/deployment remain independent, so missing credentials or a
translation-provider outage cannot block a valid site build.

Repository configuration:

- Actions secret: `TRANSLATION_API_KEY`.
- Repository variable: `TRANSLATION_PROVIDER`, either `openai-compatible` (default) or
  `deepl`.
- OpenAI-compatible providers require `TRANSLATION_MODEL`; their optional
  `TRANSLATION_API_BASE` defaults to `https://api.openai.com/v1`.
- DeepL does not use `TRANSLATION_MODEL`. Its optional `TRANSLATION_API_BASE` defaults
  to `https://api-free.deepl.com` for legacy `:fx` keys and `https://api.deepl.com`
  otherwise. Set it explicitly when the account endpoint differs.

The key is never exposed to Pages CMS, source YAML, client JavaScript, or the generated
site. `github-actions[bot]` is excluded from the workflow job and the generated commit
uses `[skip translate]`, preventing a translation commit loop. GitHub does not emit new
`push` workflow runs for commits created with the built-in `GITHUB_TOKEN`; after a real
translation commit, the translation workflow therefore dispatches `ci.yml` and
`publish-production.yml` explicitly. Without the required provider credentials, the
workflow records pending state and exits without compromising CI.

The citation refresh is also manual-only during staging. Enable its schedule only after
the target repository, branch protections and desired pull-request cadence are confirmed.

`_translation/registry.yml` is the central coverage source for every Pages CMS
collection. It classifies field stems as machine-translatable, manual-English-only or
collection-excluded. `scripts/check_translation_coverage.py` warns when a new `*_zh`
field has no matching optional `*_en` field or no registry decision. The asynchronous
translator, build-time fallback and QA tests consume the same registry.

Provider errors, missing credentials, empty responses and timeouts are non-blocking.
Affected blank fields remain `pending`; stale automatic English becomes `auto-stale`;
the workflow emits a warning and Jekyll renders Chinese fallback on English routes.
Manual English is never replaced. Names and official role/site identity fields are
manual-only, while all publication records are excluded.

The all-English-empty fixture covers Homepage, Highlights, Events, Research, Team,
Team Role Labels, Opportunities and Site Settings. It verifies CMS optionality,
successful generation, provider-unavailable fallback and registry exclusions. A Ruby
fixture also verifies fallback for missing, rather than merely blank, English keys.

## Homepage scientific carousel

The carousel uses one stable scientific canvas per viewport. Its desktop target is
approximately 1.4:1, with a responsive height capped at 780 px; tablet uses 420–540 px
and mobile uses 280–380 px. Every image uses `object-fit: contain` and
`object-position: center` on a near-white canvas in both themes. Original pixels are
not cropped or stretched.

Each slide always contains the fixed canvas followed by a fixed-height caption region.
Titles are clamped to two lines and the metadata row reserves its height even when no
DOI metadata exists. Pagination remains outside the viewport, keeping the following
Highlights position stable while tall, medium and wide images switch.

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
