# Friends of Scenic 30A: architecture

Last checked against the code and Cloudflare on Oct 8, 2026.

## What it does

The Friends of Scenic 30A nonprofit site (rebuilt from the earlier Wix site): about, our work, gallery, blog, membership, and contact. A small Worker handles the contact form and a few redirects.

## Domains and Worker

- Worker: `friends30a` (repo name is `friends30A`)
- Custom domains (attached in the Cloudflare dashboard): `friendsofscenic30a.org`, `www.friendsofscenic30a.org`
- workers.dev host is enabled.
- `shop.friendsofscenic30a.org` is a separate storefront (DNS only A record, not this Worker). `/shop` on this site 301s there.

## Data and images

- Pages and images are static files in this repo. Blog posts are written in `content/posts/*.txt`, and `scripts/build.py` generates the HTML, `sitemap.xml`, `robots.txt`, `llms.txt`, and `llms-full.txt`.
- Bindings: `ASSETS` (static assets, directory `.`). No D1, R2, or KV.
- External services: Resend (contact mail), a Google Sheets Apps Script webhook (form rows), Google Analytics 4 tag on pages.

## Secrets and env vars (names only)

Secrets set: `RESEND_API_KEY`, `CONTACT_EMAIL`, `GOOGLE_SHEETS_WEBHOOK_URL`, `GOOGLE_SHEETS_WEBHOOK_TOKEN`.

## Cron and scheduled jobs

None. The Worker has only a fetch handler and no cron trigger.

## How it deploys

- Cloudflare Workers Builds, auto deploy on merge to `main`. Repo `marcongit850/friends30A`, trigger `27edbdd0-1668-46ab-b958-07868de0c461`, build command `npm run build`, deploy command `npx wrangler deploy`, root `/`.
- The build command runs `python3 scripts/build.py` on every deploy.
- If a merge does not deploy: `POST /accounts/f1c59948520f1ec39473238b621c7e24/builds/triggers/27edbdd0-1668-46ab-b958-07868de0c461/builds` with body `{"branch": "main", "commit_hash": "<full 40 character sha>"}`. Check builds with `GET /accounts/f1c59948520f1ec39473238b621c7e24/builds/workers/5a936a41de7c491f9b9d4319e204c602/builds?per_page=2` and match `commit_hash`.

## Known gotchas

- The Worker runs first only for `/api/message`, `/impact`, `/shop`, and `/get-involved` (see `run_worker_first`). `/impact` 301s to `/our-work/#past-accomplishments` and `/shop` 301s to the storefront.
- Contact mail is sent from Resend's onboarding sender (`Friends of Scenic 30A <onboarding@resend.dev>`), hardcoded in the code. That sender only delivers to the email on the Resend account, so `CONTACT_EMAIL` must be that address until a domain is verified in Resend and the From line is changed.
- A Sheets row is appended only after Resend accepts the email. A sheet miss does not change the email result.
- Stale config: `wrangler.jsonc` and `README.md` still say not to attach a custom domain and that DNS is deferred, but `friendsofscenic30a.org` is now attached in the dashboard.

TODO: record which service hosts `shop.friendsofscenic30a.org`.

## Standing rule

Any PR that changes architecture (new secret, cron, storage, binding, or deploy change) must update this file in the same PR.
