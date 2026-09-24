# EIT VM deployment templates

These files are inert templates. GitHub builds the site; the VM only fetches the
`server-deploy` branch and serves static files. Nothing in this directory logs in to,
connects to, scans, or configures the VM automatically.

## Required software

Install only `nginx`, `git`, `rsync`, `curl`, `ca-certificates`, `systemd`, and the
`flock` command supplied by `util-linux`. Ruby, Bundler, Jekyll, Node, Pages CMS,
translation providers, citation tooling, GitHub Actions runners, and build secrets do
not belong on the VM.

## Directory and account model

- Git checkout: `/opt/jliang-deploy/repo`
- Immutable releases: `/var/www/jliang/releases/<server-deploy-commit>`
- Active site: `/var/www/jliang/current` (atomic symlink)
- Owner/group: `<DEPLOYMENT_USER>:www-data`
- Directories: mode `755`; files: mode `644`

The deployment user may write the checkout and website directories. `www-data` only
reads and traverses them; it must not fetch Git, execute the sync script, or edit files.
Replace the literal `__DEPLOYMENT_USER__` in the service template before installing it.

## First-time manual installation

Run these commands manually on the VM after replacing `<DEPLOYMENT_USER>` and the
repository URL. The current repository is public, so an HTTPS read-only clone is the
preferred path.

```bash
sudo apt update
sudo apt install -y nginx git rsync curl ca-certificates util-linux
sudo install -d -o <DEPLOYMENT_USER> -g www-data -m 755 /opt/jliang-deploy
sudo install -d -o <DEPLOYMENT_USER> -g www-data -m 755 /var/www/jliang/releases
sudo -u <DEPLOYMENT_USER> git clone --branch server-deploy --single-branch \
  https://github.com/DavidHMeng/energy-materials-lab-website.git \
  /opt/jliang-deploy/repo
sudo install -o root -g root -m 755 ops/scripts/jliang-sync /usr/local/sbin/jliang-sync
sudo install -o root -g root -m 644 ops/nginx/jliang.conf /etc/nginx/sites-available/jliang.conf
sudo ln -s /etc/nginx/sites-available/jliang.conf /etc/nginx/sites-enabled/jliang.conf
```

Copy the two systemd templates, replace `__DEPLOYMENT_USER__` in the copied service,
then validate before enabling anything:

```bash
sudo install -o root -g root -m 644 ops/systemd/jliang-sync.service /etc/systemd/system/jliang-sync.service
sudo install -o root -g root -m 644 ops/systemd/jliang-sync.timer /etc/systemd/system/jliang-sync.timer
sudo sed -i 's/__DEPLOYMENT_USER__/<DEPLOYMENT_USER>/g' /etc/systemd/system/jliang-sync.service
sudo nginx -t
sudo systemctl daemon-reload
sudo systemctl enable --now nginx
sudo systemctl start jliang-sync.service
curl -i -H 'Host: jliang.eitech.edu.cn' http://127.0.0.1/healthz
sudo systemctl enable --now jliang-sync.timer
```

The sync script validates the release before switching, performs an atomic symlink
replacement, checks the homepage with the production Host header, and restores the
previous target on failure. It never reloads Nginx and never builds the site.

## Private-repository alternative

If repository visibility changes to private, create a dedicated read-only GitHub deploy
key for this repository and install its private half with restrictive permissions under
the deployment user's SSH directory. Do not use a personal access token in a clone URL,
do not paste a token/password into a command that will remain in shell history, and do
not grant write access to the deploy key.

## Manual rollback

List release directories and inspect `version.json`, then atomically point `current` to
the selected known-good SHA. This does not rebuild anything:

```bash
readlink -f /var/www/jliang/current
ls -lt /var/www/jliang/releases
ln -s /var/www/jliang/releases/<KNOWN_GOOD_SHA> /var/www/jliang/.current.rollback
mv -Tf /var/www/jliang/.current.rollback /var/www/jliang/current
curl -f -H 'Host: jliang.eitech.edu.cn' http://127.0.0.1/
```

By default the sync script retains the current release plus up to nine other newest
SHA-named releases (ten total when the current release is among the newest). Cleanup
only considers direct child directories whose names are full Git SHAs, and it never
removes the directory currently targeted by `current`.
