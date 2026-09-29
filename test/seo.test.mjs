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

const membership = readFileSync(join(root, "membership/index.html"), "utf8");
assert.match(header, /https:\/\/square\.link\/u\/Yzxyi16L/);
assert.match(membership, /https:\/\/square\.link\/u\/GUdeODzg/);
assert.match(membership, /https:\/\/square\.link\/u\/KlIhQxsE/);
assert.match(membership, /https:\/\/square\.link\/u\/Yzxyi16L/);

const home = readFileSync(join(root, "index.html"), "utf8");
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
