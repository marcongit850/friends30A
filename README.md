# Friends of Scenic 30A

Preview hosting is the Cloudflare Worker named `friends30a`. This workspace has no Cloudflare API token, so the workers.dev address is created when Workers Builds runs `npx wrangler deploy`. Do not attach a custom domain. Vanity DNS stays deferred.

A static rebuild of the Friends of Scenic 30A website. The pages follow the public copy and structure of [the previous Wix site](https://marc12345678.wixsite.com/friends30a): home, about, our work, impact, gallery, blog, get involved, membership, and contact, plus privacy, accessibility, and terms.

The Worker name is **`friends30a`**. Leave that name in `wrangler.jsonc`. Do not attach a custom domain. A public vanity name and its DNS are deferred until someone chooses a domain later.

## Preview

From the repository root:

```bash
python3 -m http.server 8080
```

Open `http://localhost:8080/`. That server only shows the static pages. Form delivery is the Worker in `src/worker.js`.

```bash
npm test
```

`scripts/build.py` regenerates the HTML, `sitemap.xml`, `robots.txt`, `llms.txt`, and `llms-full.txt` from `content/posts/`. Canonical URLs, Open Graph, Twitter, JSON-LD, the sitemap, and `llms.txt` use `https://friendsofscenic30a.org`. A preview on workers.dev may still exist; do not point those SEO URLs at it. Do not add a custom domain or route in `wrangler.jsonc`.

## Deploy

Cloudflare Workers Builds deploys this repository with `npx wrangler deploy`, using `wrangler.jsonc`.

- `"name"` must stay `friends30a`.
- `assets.directory` is `.`, so `index.html` at the repository root is the site home page.
- `main` is `src/worker.js`. `assets.run_worker_first` is only `/api/message` and `/api/message/`. Every other path is a static asset.
- Do not add a custom domain, route pattern, or vanity DNS record for this Worker.

`CONTACT_EMAIL` and `RESEND_API_KEY` are Worker variables or secrets. Do not commit them. Mail goes out through the Resend HTTP API. The From address is Resend's free onboarding sender, `Friends of Scenic 30A <onboarding@resend.dev>`, which can deliver only to the email address on the Resend account until a domain is verified. Keep `CONTACT_EMAIL` set to that same address. After a domain is verified, change `FROM` in `src/message.js`.

Until those values are set, `POST /api/message` returns HTTP 503 and the form explains that messages can be mailed to Friends of Scenic 30A, 877 N County Hwy 393, Santa Rosa Beach, FL 32459. The pages still display.

## Pages

- `/` is the mission, four pillars, impact, why 30A matters, and ways to give or join
- `/about/` and `/our-work/`
- `/impact/`
- `/gallery/`
- `/blog/` and the posts from the Wix site
- `/get-involved/` for membership, volunteering, updates, and donations
- `/membership/` with the live Square payment links
- `/contact/`
- `/privacy-policy/`, `/accessibility/`, and `/terms/`

Donate: https://square.link/u/Yzxyi16L

Individual membership ($25/year): https://square.link/u/GUdeODzg

Business membership ($100/year): https://square.link/u/KlIhQxsE

The Wix terms page was an unfilled template about how to write terms. `/terms/` is a short terms page for this site instead. The privacy page keeps the September 3, 2026 policy and names Square, which hosts the live donation and membership payments.

Shared chrome lives in `includes/header.html` and `includes/footer.html`. Every page mounts those partials with `header.js` and `footer.js`, and `site.js` binds the menu after the header loads. The footer address is Friends of Scenic 30A, 877 N County Hwy 393, Santa Rosa Beach, FL 32459.
