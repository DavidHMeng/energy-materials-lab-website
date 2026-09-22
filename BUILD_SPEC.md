# Build and maintenance specification

## Baseline

- Upstream: `greenelab/lab-website-template` release `v1.4.0`.
- Runtime: Jekyll 4.3, Bundler, GitHub Actions, Pages CMS.
- Deployment: static files only; no database or application server.
- Source control: local Git repository. A remote and deployment target must be supplied
  by the site owner before any push.

## Local setup

1. Install Ruby 3.1+ and Bundler, or Docker Desktop.
2. Run `bundle install`.
3. Run `py -m pip install PyYAML` once for schema checks.
4. Run `py scripts/validate_content.py`.
5. Run `bundle exec jekyll serve --livereload` and open the printed local URL.

On Windows, `powershell -ExecutionPolicy Bypass -File scripts/preview.ps1` selects an
available Ruby or Docker route and explains what is missing when neither is installed.

## CI gates

The CI workflow validates content, builds Jekyll, checks generated routes/internal
links, and runs HTML Proofer without external-network checks. The deployment workflow
publishes the same built artifact to GitHub Pages only after a repository owner enables
GitHub Pages and pushes to `main`.

## Upstream policy

Record the upstream release in `_data/upstream.yaml`. For future updates, compare the
new release against the retained core folders before merging. Reapply only the custom
layer; never overwrite custom schemas or frozen navigation.

## Acceptance routes

`/`, `/research/`, `/publications/`, `/team/`, `/opportunities/`, `/news/`, `/events/`,
their `/zh/` counterparts, generated English and Chinese team profiles, and `/404.html`.
