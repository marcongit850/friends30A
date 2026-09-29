import assert from "node:assert/strict";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const root = new URL("..", import.meta.url).pathname;

function walk(dir, found = []) {
  for (const name of readdirSync(dir)) {
    if (name === "node_modules" || name === ".git" || name === "content" || name === "includes") continue;
    const path = join(dir, name);
    if (statSync(path).isDirectory()) walk(path, found);
    else if (name.endsWith(".html")) found.push(path);
  }
  return found;
}

const pages = walk(root);
assert.ok(pages.length >= 15, `expected the rebuilt site, found ${pages.length} html files`);

for (const page of pages) {
  const html = readFileSync(page, "utf8");
  assert.match(html, /<title>[^<]+<\/title>/, page);
  assert.match(html, /<meta name="description" content="[^"]+"/, page);
  assert.match(html, /<link rel="canonical" href="https?:\/\/[^"]+"/, page);
  assert.match(html, /name="viewport"/, page);
  assert.match(html, /id="site-header"/, page);
  assert.match(html, /id="site-footer"/, page);
  assert.match(html, /src="\/header\.js"/, page);
  assert.match(html, /src="\/footer\.js"/, page);
  assert.doesNotMatch(html, /Mail is also received at P\.O\. Box 1931/, page);
}

const headerJs = readFileSync(join(root, "header.js"), "utf8");
const footerJs = readFileSync(join(root, "footer.js"), "utf8");
assert.match(headerJs, /\/includes\/header\.html/);
assert.match(footerJs, /\/includes\/footer\.html/);

const header = readFileSync(join(root, "includes/header.html"), "utf8");
assert.match(header, /aria-label="Friends of Scenic 30A"/);
assert.doesNotMatch(header, /brand-kicker|brand-name/);
const footer = readFileSync(join(root, "includes/footer.html"), "utf8");
assert.match(footer, /Friends of Scenic 30A/);
assert.match(footer, /877 N County Hwy 393/);
assert.match(footer, /Santa Rosa Beach, FL 32459/);
assert.match(footer, /aria-label="Facebook"/);
assert.match(footer, /aria-label="Nextdoor"/);
assert.match(footer, /https:\/\/www\.facebook\.com\/fof30a/);
assert.match(footer, /https:\/\/nextdoor\.com\/page\/friends-of-scenic-30a-santa-rosa-beach-fl\//);
assert.match(footer, /<svg[\s\S]*visually-hidden">Facebook/);
assert.match(footer, /<svg[\s\S]*visually-hidden">Nextdoor/);
assert.match(footer, /florida-scenic-highway\.png/);
assert.match(footer, /alt="Florida Scenic Highway"/);
assert.match(footer, /<h2>Explore<\/h2>/);
assert.match(footer, /<h2>Get Involved<\/h2>/);
assert.doesNotMatch(footer, /Scenic 30A Resources/);
assert.doesNotMatch(footer, /https:\/\/30a\.com\//);
assert.doesNotMatch(footer, /https:\/\/www\.byways\.org\//);
assert.doesNotMatch(footer, /https:\/\/www\.visitsouthwalton\.com\//);
assert.doesNotMatch(footer, /https:\/\/www\.visitflorida\.com\//);
assert.doesNotMatch(footer, /https:\/\/www\.waltonareachamber\.com\//);
assert.doesNotMatch(footer, /https:\/\/sowal\.com\//);

const about = readFileSync(join(root, "about/index.html"), "utf8");
const work = readFileSync(join(root, "our-work/index.html"), "utf8");
const impact = readFileSync(join(root, "impact/index.html"), "utf8");
const memberPage = readFileSync(join(root, "membership/index.html"), "utf8");
const involved = readFileSync(join(root, "get-involved/index.html"), "utf8");
for (const [name, page] of [["about", about], ["work", work], ["impact", impact], ["membership", memberPage]]) {
  assert.match(page, /class="page-photos[\s"]/, name);
  assert.ok((page.match(/<figure>/g) || []).length >= 1, name);
}
assert.doesNotMatch(impact, /<figcaption>/);
assert.match(impact, /alt="Aerial view of the Gulf, beach, and a dune lake beside 30A"/);
assert.match(impact, /alt="People riding the paved Timpoochee Trail"/);
assert.match(impact, /alt="Gulf shoreline and sea oats along Scenic 30A"/);
assert.doesNotMatch(work, /<figcaption>/);
assert.match(work, /alt="Trail through the Scenic 30A corridor"/);
assert.match(work, /alt="People riding the paved Timpoochee Trail"/);
assert.match(work, /alt="Path beside the Gulf with sea oats and pines"/);
assert.doesNotMatch(about, /<figcaption>/);
assert.match(about, /page-hero-tall/);
assert.match(about, /feature-row/);
assert.match(impact, /page-hero-tall/);
assert.match(impact, /photo-collage/);
assert.match(impact, /accomplish-split/);
assert.doesNotMatch(impact, /<figcaption>/);
assert.match(about, /topic-grid/);
assert.match(about, /Protect\. Preserve\. Enhance\./);
assert.match(about, /alt="People riding the paved Timpoochee Trail"/);
assert.match(about, /alt="Coastal dune lake edged by pines"/);
assert.match(about, /alt="Sea oats on the dunes"/);
assert.match(memberPage, /<figcaption>/);
assert.match(memberPage, /Step 1\. Pay through Square/);
assert.match(memberPage, /Step 2\. Submit your member details/);
assert.match(involved, /30A’s Future Is Something We All Share[\s\S]*Become a Member[\s\S]*Donate/);
const contact = readFileSync(join(root, "contact/index.html"), "utf8");
assert.match(contact, /877 N County Hwy 393/);
assert.match(contact, /Say Hello/);
assert.doesNotMatch(contact, /Mail is also received at P\.O\. Box 1931/);
assert.doesNotMatch(contact, /P\.O\. Box 1931/);
const css = readFileSync(join(root, "styles.css"), "utf8");
assert.match(css, /images\/hero\.jpg/);
assert.match(css, /\.brand img \{[^}]*width: 125px/);
assert.doesNotMatch(css, /\.brand img \{[^}]*height: 104px/);
assert.match(css, /\.header-inner \{[^}]*padding: 0\.35rem 1\.25rem/);
assert.match(css, /\.page-hero \{[^}]*min-height: clamp\(22rem, 52vh, 36rem\)/);
assert.match(css, /\.photo-mosaic/);
assert.match(css, /\.priority-list/);
assert.match(work, /class="page-our-work"/);
assert.match(work, /family=Source\+Sans\+3/);
assert.doesNotMatch(work, /Fraunces|Outfit/);
assert.match(css, /body\.page-our-work[\s\S]*Source Sans 3/);
assert.match(css, /body\.page-our-work \.work-block h2/);
assert.match(css, /body\.page-our-work \.lead-split h2/);
assert.match(css, /body\.page-our-work \.quote/);

const membership = readFileSync(join(root, "membership/index.html"), "utf8");
assert.match(header, /https:\/\/square\.link\/u\/Yzxyi16L/);
assert.match(membership, /https:\/\/square\.link\/u\/GUdeODzg/);
assert.match(membership, /https:\/\/square\.link\/u\/KlIhQxsE/);
assert.match(membership, /https:\/\/square\.link\/u\/Yzxyi16L/);

const home = readFileSync(join(root, "index.html"), "utf8");
const strip = home.match(/<div class="strip"[\s\S]*?<\/div>/)[0];
assert.equal((strip.match(/<img /g) || []).length, 6);
assert.doesNotMatch(strip, /<span>|<figcaption>/);
assert.doesNotMatch(strip, /strip-nav/);
assert.match(strip, /alt="Boardwalk through sea oats toward the Gulf"/);
assert.match(strip, /alt="Aerial view of the Gulf, beach, and a dune lake beside 30A"/);
assert.match(home, /class="strip-scroller"/);
assert.match(home, /aria-label="Previous photos" disabled/);
assert.match(home, /aria-label="Next photos"/);
assert.match(home, /id="corridor-strip"/);
assert.match(css, /\.strip-nav/);
assert.match(css, /\.strip-prev \{ left:/);
assert.match(css, /\.strip-next \{ right:/);
const siteJs = readFileSync(join(root, "site.js"), "utf8");
assert.match(siteJs, /strip-prev/);
assert.match(siteJs, /strip-next/);
assert.match(siteJs, /ArrowLeft/);
assert.match(siteJs, /ArrowRight/);
for (const pagePath of pages) {
  const html = readFileSync(pagePath, "utf8");
  const isOurWork = pagePath.endsWith(`${join("our-work", "index.html")}`);
  if (isOurWork) {
    assert.match(html, /class="page-our-work"/, pagePath);
    assert.match(html, /Source\+Sans\+3/, pagePath);
    assert.doesNotMatch(html, /Fraunces|Outfit/, pagePath);
  } else {
    assert.match(html, /Fraunces/, pagePath);
    assert.match(html, /Outfit/, pagePath);
    assert.doesNotMatch(html, /page-our-work|Source\+Sans\+3/, pagePath);
  }
}
for (const phrase of [
  "Protecting Natural Resources",
  "Preserving Scenic 30A",
  "Improving Trails",
  "Educating",
  "Florida Scenic Highway",
  "National Scenic Byway",
  "Friends' Corner",
  "Why 30A matters",
]) {
  assert.match(home, new RegExp(phrase));
}

const robots = readFileSync(join(root, "robots.txt"), "utf8");
const sitemap = readFileSync(join(root, "sitemap.xml"), "utf8");
assert.match(robots, /^User-agent: \*/m);
assert.match(robots, /Sitemap: https?:\/\/\S+\/sitemap\.xml/);
for (const path of ["/", "/about/", "/our-work/", "/impact/", "/gallery/", "/get-involved/", "/membership/", "/contact/", "/blog/", "/privacy-policy/", "/accessibility/", "/terms/"]) {
  assert.match(sitemap, new RegExp(path.replaceAll("/", "\\/") ));
}

const wrangler = readFileSync(join(root, "wrangler.jsonc"), "utf8");
assert.match(wrangler, /"name": "friends30a"/);
assert.doesNotMatch(wrangler, /routes|custom_domain|pattern":/);

console.log(`seo ok (${pages.length} pages)`);
