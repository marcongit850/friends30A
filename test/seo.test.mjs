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

const ORIGIN = "https://friendsofscenic30a.org";
const publicPaths = [
  "/",
  "/about/",
  "/our-work/",
  "/impact/",
  "/gallery/",
  "/get-involved/",
  "/membership/",
  "/contact/",
  "/blog/",
  "/blog/protecting-the-natural-character-of-scenic-30a/",
  "/blog/transportation-has-always-been-part-of-friends-of-scenic-30a-s-mission/",
  "/blog/what-makes-scenic-30a-special/",
  "/blog/30a-in-360-degrees/",
  "/blog/the-communities-of-scenic-30a/",
  "/blog/history-heritage-of-scenic-30a/",
  "/blog/explore-scenic-30a/",
  "/blog/the-story-of-30a/",
  "/blog/vision/",
  "/privacy-policy/",
  "/accessibility/",
  "/terms/",
];

function decode(value) {
  return value
    .replaceAll("&amp;", "&")
    .replaceAll("&quot;", '"')
    .replaceAll("&#x27;", "'")
    .replaceAll("&#39;", "'");
}

function attr(html, pattern) {
  const match = html.match(pattern);
  assert.ok(match, pattern.toString());
  return decode(match[1]);
}

function jsonLd(html) {
  const match = html.match(/<script type="application\/ld\+json">\s*([\s\S]*?)\s*<\/script>/);
  assert.ok(match, "json-ld missing");
  return JSON.parse(match[1]);
}

function imageSize(rel) {
  const bytes = readFileSync(join(root, rel));
  if (bytes[0] === 0x89 && bytes[1] === 0x50) {
    return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20), type: "image/png" };
  }
  assert.equal(bytes[0], 0xff);
  assert.equal(bytes[1], 0xd8);
  let i = 2;
  while (i < bytes.length) {
    if (bytes[i] !== 0xff) {
      i += 1;
      continue;
    }
    const marker = bytes[i + 1];
    if (marker === 0xc0 || marker === 0xc1 || marker === 0xc2) {
      return { width: bytes.readUInt16BE(i + 7), height: bytes.readUInt16BE(i + 5), type: "image/jpeg" };
    }
    if (marker === 0xd8 || marker === 0xd9) {
      i += 2;
      continue;
    }
    i += 2 + bytes.readUInt16BE(i + 2);
  }
  assert.fail("jpeg size not found " + rel);
}

const titles = new Set();
const descriptions = new Set();
for (const path of publicPaths) {
  const file = path === "/" ? "index.html" : `${path.slice(1)}index.html`;
  const html = readFileSync(join(root, file), "utf8");
  const url = ORIGIN + path;
  assert.equal(html.includes("workers.dev"), false, file);
  assert.equal(html.includes("noindex"), false, file);
  const title = attr(html, /<title>([^<]+)<\/title>/);
  const description = attr(html, /<meta name="description" content="([^"]+)"/);
  assert.equal(titles.has(title), false, "duplicate title " + title);
  assert.equal(descriptions.has(description), false, "duplicate description " + description);
  titles.add(title);
  descriptions.add(description);
  assert.ok(title.length >= 20 && title.length <= 70, `${file} title length ${title.length}`);
  assert.ok(description.length >= 110 && description.length <= 165, `${file} description length ${description.length}`);
  assert.equal(attr(html, /<link rel="canonical" href="([^"]+)">/), url);
  assert.equal(attr(html, /<meta property="og:title" content="([^"]+)"/), title);
  assert.equal(attr(html, /<meta property="og:description" content="([^"]+)"/), description);
  assert.equal(attr(html, /<meta property="og:url" content="([^"]+)">/), url);
  assert.equal(attr(html, /<meta property="og:site_name" content="([^"]+)"/), "Friends of Scenic 30A");
  assert.equal(attr(html, /<meta property="og:locale" content="([^"]+)"/), "en_US");
  assert.equal(attr(html, /<meta name="twitter:title" content="([^"]+)"/), title);
  assert.equal(attr(html, /<meta name="twitter:description" content="([^"]+)"/), description);
  assert.equal(attr(html, /<meta name="twitter:card" content="([^"]+)"/), "summary_large_image");
  const image = attr(html, /<meta property="og:image" content="([^"]+)">/);
  assert.ok(image.startsWith(`${ORIGIN}/images/`), image);
  assert.equal(attr(html, /<meta name="twitter:image" content="([^"]+)">/), image);
  const imageAlt = attr(html, /<meta property="og:image:alt" content="([^"]+)"/);
  assert.ok(imageAlt.length > 10, file);
  assert.equal(attr(html, /<meta name="twitter:image:alt" content="([^"]+)"/), imageAlt);
  const relImage = image.slice(ORIGIN.length + 1);
  const size = imageSize(relImage);
  assert.equal(attr(html, /<meta property="og:image:width" content="([^"]+)"/), String(size.width), file);
  assert.equal(attr(html, /<meta property="og:image:height" content="([^"]+)"/), String(size.height), file);
  assert.equal(attr(html, /<meta property="og:image:type" content="([^"]+)"/), size.type, file);
  const data = jsonLd(html);
  assert.equal(data["@context"], "https://schema.org");
  const types = data["@graph"].map((node) => node["@type"]);
  assert.deepEqual(types[0], ["NGO", "Organization"], file);
  assert.equal(types[1], "WebSite", file);
  assert.equal(data["@graph"][0].url, `${ORIGIN}/`);
  assert.equal(data["@graph"][0].address.streetAddress, "877 N County Hwy 393");
  assert.equal(data["@graph"][1].publisher["@id"], `${ORIGIN}/#organization`);
  if (path === "/") assert.equal(types.includes("BreadcrumbList"), false);
  else assert.equal(types.includes("BreadcrumbList"), true, file);
  assert.equal((html.match(/<h1[\s>]/g) || []).length, 1, file);
  for (const tag of html.matchAll(/<img\b[^>]*>/g)) {
    const alt = tag[0].match(/\salt="([^"]*)"/);
    assert.ok(alt, "missing alt " + file);
    if (/\ssrc=/.test(tag[0])) assert.ok(alt[1].trim().length > 0, "empty alt " + file + " " + tag[0]);
  }
}

const homeLd = jsonLd(readFileSync(join(root, "index.html"), "utf8"));
assert.equal(homeLd["@graph"][2]["@type"], "WebPage");
const aboutLd = jsonLd(readFileSync(join(root, "about/index.html"), "utf8"));
assert.equal(aboutLd["@graph"].some((node) => node["@type"] === "AboutPage"), true);
const contactLd = jsonLd(readFileSync(join(root, "contact/index.html"), "utf8"));
assert.equal(contactLd["@graph"].some((node) => node["@type"] === "ContactPage"), true);
const galleryLd = jsonLd(readFileSync(join(root, "gallery/index.html"), "utf8"));
const galleryPage = galleryLd["@graph"].find((node) => node["@type"] === "ImageGallery");
assert.equal(galleryPage.associatedMedia.length, 14);
const blogLd = jsonLd(readFileSync(join(root, "blog/index.html"), "utf8"));
const blogNode = blogLd["@graph"].find((node) => node["@type"] === "Blog");
assert.equal(blogNode.blogPost.length, 9);
assert.equal(blogNode.blogPost[0].url, `${ORIGIN}/blog/protecting-the-natural-character-of-scenic-30a/`);
const postHtml = readFileSync(join(root, "blog/vision/index.html"), "utf8");
assert.equal(attr(postHtml, /<meta property="og:type" content="([^"]+)"/), "article");
assert.equal(attr(postHtml, /<meta property="article:published_time" content="([^"]+)"/), "2026-09-03");
const posting = jsonLd(postHtml)["@graph"].find((node) => node["@type"] === "BlogPosting");
assert.equal(posting.headline, "A Vision for Scenic 30A");
assert.equal(posting.datePublished, "2026-09-03");
assert.equal(posting.author.name, "Friends of Scenic 30A");
assert.match(postHtml, /<h1>A Vision for Scenic 30A<\/h1>/);
const longPost = readFileSync(join(root, "blog/transportation-has-always-been-part-of-friends-of-scenic-30a-s-mission/index.html"), "utf8");
assert.match(longPost, /Transportation Has Always Been Part of Friends of Scenic 30A/);
assert.equal(attr(longPost, /<title>([^<]+)<\/title>/), "Transportation on Scenic Highway 30A | Friends of Scenic 30A");

const notFound = readFileSync(join(root, "404.html"), "utf8");
assert.match(notFound, /name="robots" content="noindex"/);
assert.match(notFound, new RegExp(`canonical" href="${ORIGIN}/404.html"`));
assert.equal(notFound.includes("workers.dev"), false);

const locs = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) => match[1]);
assert.deepEqual(locs, publicPaths.map((path) => ORIGIN + path));
assert.equal(robots.includes("Disallow"), false);
assert.match(robots, new RegExp(`Sitemap: ${ORIGIN}/sitemap.xml`));
assert.match(robots, new RegExp(`${ORIGIN}/llms.txt`));
assert.match(robots, new RegExp(`${ORIGIN}/llms-full.txt`));
for (const agent of ["Googlebot", "Bingbot", "GPTBot", "ChatGPT-User", "Google-Extended", "ClaudeBot", "anthropic-ai", "PerplexityBot", "Applebot-Extended", "Bytespider", "CCBot", "meta-externalagent", "FacebookBot"]) {
  assert.match(robots, new RegExp(`User-agent: ${agent}\\nAllow: /\\n`), agent);
}

const llms = readFileSync(join(root, "llms.txt"), "utf8");
const llmsFull = readFileSync(join(root, "llms-full.txt"), "utf8");
assert.ok(llmsFull.length > llms.length);
const pageLines = (text) => text.split("## Pages\n")[1].split("## Optional")[0].trim();
assert.equal(pageLines(llms), pageLines(llmsFull));
for (const body of [llms, llmsFull]) {
  assert.equal(body.includes("workers.dev"), false);
  assert.equal(body.includes("<"), false);
  for (const path of publicPaths) assert.ok(body.includes(ORIGIN + path), path);
  assert.ok(body.includes(`${ORIGIN}/sitemap.xml`));
}
assert.ok(llms.includes(`${ORIGIN}/llms-full.txt`));
assert.ok(llmsFull.includes(`${ORIGIN}/llms.txt`));
assert.match(llmsFull, /Florida Scenic Highway designation in 2008/);
assert.match(llmsFull, /National Scenic Byway designation in 2021/);
assert.match(llmsFull, /877 N County Hwy 393/);

const ignore = readFileSync(join(root, ".assetsignore"), "utf8");
for (const name of ["robots.txt", "sitemap.xml", "llms.txt", "llms-full.txt"]) {
  assert.equal(ignore.includes(name), false, name);
}
const headers = readFileSync(join(root, "_headers"), "utf8");
assert.match(headers, /\/llms\.txt\n {2}Content-Type: text\/plain; charset=utf-8/);
assert.match(headers, /\/llms-full\.txt\n {2}Content-Type: text\/plain; charset=utf-8/);

console.log(`seo ok (${pages.length} pages)`);
