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

The citation refresh is also manual-only during staging. Enable its schedule only after
the target repository, branch protections and desired pull-request cadence are confirmed.

## Upstream policy

Record the upstream release in `_data/upstream.yaml`. For future updates, compare the
new release against the retained core folders before merging. Reapply only the custom
layer; never overwrite custom schemas or frozen navigation.

## Acceptance routes

`/`, `/research/`, `/publications/`, `/team/`, `/opportunities/`, `/news/`, `/events/`,
their `/zh/` counterparts, generated English and Chinese team profiles, and `/404.html`.
