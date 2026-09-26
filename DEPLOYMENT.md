# EIT production deployment

Status boundary: **GITHUB/BUILD MIGRATION COMPLETE / EIT VM DEPLOYMENT PENDING USER EXECUTION**
only after the GitHub workflow and `server-deploy` branch have passed. No repository
automation logs in to or probes the VM.

## Architecture and ownership

```text
Pages CMS -> GitHub main -> citation / translation fallback / validation
          -> GitHub Actions production Jekyll build
          -> server-deploy (generated static files only)
          -> EIT Ubuntu VM pull -> releases/<commit> -> current symlink -> Nginx
          -> EIT reverse proxy / DNS / TLS -> https://jliang.eitech.edu.cn
```

`main` is the sole source of truth. Pages CMS continues editing `main`. The VM checks
out only `server-deploy`; it never uses `main` as a web root and never runs Ruby,
Jekyll, Node, translation, citation, Pages CMS, or a GitHub Actions runner.

GitHub Pages remains staging at
`https://davidhmeng.github.io/energy-materials-lab-website/`. Staging has its project
base path and noindex policy. Production has an empty base path, production canonical
metadata, indexable robots policy, and a `version.json` provenance record.

## GitHub release contract

The workflow `.github/workflows/publish-production.yml` listens only to pushes on
`main`. Translation/fallback tests and structured content validation run first. The
build job then normalizes the current workspace's DOI references, regenerates citation
metadata, checks the result, and only then runs the production build. This makes a CMS
commit containing a new valid DOI self-contained; it does not wait for the separate
citation-schedule commit. The build command is:

```bash
bundle _2.5.6_ exec jekyll build \
  --config _config.yml,_config.production.yml \
  --destination _site --trace
```

The publish job alone receives `contents: write`. It replaces `server-deploy` only
after route, asset, canonical, hreflang, sitemap, robots, search marker, root-path and
HTML/link checks pass. The generated branch root directly contains `index.html`,
`assets` or compiled asset directories, route directories, `zh/`, `sitemap.xml`,
`robots.txt` and `version.json`; it contains no Jekyll source tree.

## Manual VM procedure

Use `ops/README.md` and the checked-in templates. The required directory model is:

- `/opt/jliang-deploy/repo`
- `/var/www/jliang/releases/<server-deploy-commit>`
- `/var/www/jliang/current` -> one release directory

Use a non-root deployment user with write access to the first two directory trees and
group `www-data`. Directories are `755`, files are `644`; Nginx is read-only. The
current public repository should use an HTTPS read-only clone. If it becomes private,
use a repository-scoped read-only deploy key. Never put a PAT, password, token or key
in a clone URL, shell history, repository, Actions log, or generated site.

Install the Nginx template without TLS. It listens on VM-side HTTP, serves
`/var/www/jliang/current`, supports pretty URLs, UTF-8 and gzip, adds basic security
headers, and returns `200 ok` at `/healthz`. HSTS is intentionally absent because the
school edge is expected to terminate HTTPS.

The oneshot service and timer run after boot and approximately every five minutes. The
sync script uses `flock`, fetches `origin/server-deploy`, resets only its dedicated
checkout, creates a SHA-named release, verifies required pages, atomically replaces
`current`, then checks the homepage through Nginx with `Host: jliang.eitech.edu.cn`.
Failure restores the previous symlink. Nginx is never reloaded by the script. Ten
releases are retained by default, and the active release is never removed.

## EIT network administrator request

Please configure the school edge/reverse proxy with:

- public hostname: `jliang.eitech.edu.cn`;
- internal upstream: `<VM_PRIVATE_IP>:80`;
- upstream protocol: HTTP;
- health check: `/healthz`, expecting HTTP 200 and body `ok`;
- preserve the original `Host` header;
- forward `X-Forwarded-Proto`, `X-Forwarded-For`, and `X-Real-IP`;
- terminate TLS at the EIT edge and perform HTTP-to-HTTPS redirection there.

Do not insert a real private address in this repository. If EIT requires the VM to
terminate TLS instead, treat that as a separate reviewed configuration; do not add a
certificate path or HSTS speculatively.

## Acceptance and rollback

After the user completes VM setup, verify locally on the VM with the production Host
header, then through the school edge: Homepage, Research, Publications, Team,
Opportunities, News, Events, `/zh/`, one member profile, carousel assets,
`sitemap.xml`, `robots.txt`, `version.json`, CSS, JavaScript and images. Confirm the
production output contains no `/energy-materials-lab-website/` dependency.

Rollback never rebuilds the site. Select a known-good directory under `releases/` and
atomically replace `current` as documented in `ops/README.md`, then repeat the Host
header homepage check. Repository history and the generated branch remain untouched.
