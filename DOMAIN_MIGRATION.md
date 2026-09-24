# Custom-domain production migration

Target production origin: `https://jliang.eitech.edu.cn/`  
Jekyll `baseurl`: empty  
Repository: `DavidHMeng/energy-materials-lab-website`  
Deployment source: GitHub Actions

## Current gate status

The repository is prepared for root-domain output, but the public cutover is not yet
safe. The 2026-09-24 DNS audit returned an A record for `jliang.eitech.edu.cn` pointing
to private address `10.38.132.58`. No CNAME to GitHub Pages was present, no AAAA record
was observed, and HTTPS could not connect on port 443.

The manual production workflow therefore fails closed unless `actions/configure-pages`
reports both:

- origin `https://jliang.eitech.edu.cn`;
- an empty base path.

This prevents an accidental project-path build or a premature deployment. The staging
artifact workflow remains available and uses the production root-domain configuration
without publishing it.

## School DNS request

Ask the administrator responsible for the `eitech.edu.cn` DNS zone to:

1. remove the conflicting A record for `jliang.eitech.edu.cn` (`10.38.132.58`);
2. ensure no A, AAAA, ALIAS, ANAME or second CNAME conflicts remain for that host;
3. create exactly this record:

   - type: `CNAME`
   - host/name: `jliang` (or `jliang.eitech.edu.cn`, depending on the DNS console)
   - target/value: `davidhmeng.github.io`

Do not include `https://`, a repository path, or a trailing slash. DNS propagation can
take time. Re-query the authoritative/public DNS before changing the repository Pages
setting.

## GitHub Pages cutover sequence

After the CNAME resolves publicly:

1. Open repository **Settings → Pages**.
2. Confirm the build source is **GitHub Actions**.
3. Enter `jliang.eitech.edu.cn` under **Custom domain** and save.
4. Wait for GitHub's DNS check and certificate provisioning.
5. Enable **Enforce HTTPS** only when GitHub makes it available.
6. Run **Deploy GitHub Pages (manual)**. Its domain gate must pass before build/upload.
7. Verify `/`, `/research/`, `/publications/`, `/team/`, `/opportunities/`, `/news/`,
   `/events/`, `/zh/`, a member profile, `sitemap.xml`, `robots.txt` and an unknown URL.

With a custom Actions Pages workflow, a repository `CNAME` file is not the source of
truth and is intentionally not added.

## Optional GitHub domain verification

For takeover protection, the repository owner can open personal GitHub
**Settings → Pages → Add a domain** and add `jliang.eitech.edu.cn`. GitHub will display
the TXT host and value. Copy those exact values into a school DNS request; never infer
or invent the challenge. Verify only the authorized subdomain, not the parent domain.

## Rollback

The annotated tag `pre-custom-domain-migration` marks the synchronized stable source
before this change and is present on GitHub. Do not use a destructive reset on shared
`main`. If a migration commit must be backed out, revert the migration commit normally,
then run CI and the manual deployment workflow after restoring a safe Pages setting.

## Acceptance boundary

Code migration is complete only after CI and the root-path staging artifact pass.
Production migration is complete only after DNS, GitHub Pages custom domain, HTTPS,
live routes/assets, canonical/hreflang/sitemap/robots, CMS editing and citation links
are verified on `https://jliang.eitech.edu.cn/`. Until then report:

**CODE MIGRATION COMPLETE — DNS/HTTPS PENDING**
