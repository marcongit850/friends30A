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

function isImpactRedirect(html) {
  return /http-equiv="refresh"/.test(html) && /\/our-work\/#past-accomplishments/.test(html);
}

function isShopRedirect(html) {
  return /http-equiv="refresh"/.test(html) && /https:\/\/shop\.friendsofscenic30a\.org\//.test(html);
}

function isGetInvolvedRedirect(html) {
  return /http-equiv="refresh"/.test(html) && /url=\/membership\//.test(html);
}

for (const page of pages) {
  const html = readFileSync(page, "utf8");
  if (isImpactRedirect(html)) {
    assert.match(html, /<title>[^<]+<\/title>/, page);
    assert.match(html, /name="robots" content="noindex"/, page);
    assert.match(html, /canonical" href="https:\/\/friendsofscenic30a.org\/our-work\/"/, page);
    assert.match(html, /location\.replace\("\/our-work\/#past-accomplishments"\)/, page);
    continue;
  }
  if (isShopRedirect(html)) {
    assert.match(html, /<title>[^<]+<\/title>/, page);
    assert.match(html, /name="robots" content="noindex"/, page);
    assert.match(html, /canonical" href="https:\/\/shop\.friendsofscenic30a\.org\/"/, page);
    assert.match(html, /location\.replace\("https:\/\/shop\.friendsofscenic30a\.org\/"\)/, page);
    continue;
  }
  if (isGetInvolvedRedirect(html)) {
    assert.match(html, /<title>[^<]+<\/title>/, page);
    assert.match(html, /name="robots" content="noindex"/, page);
    assert.match(html, /canonical" href="https:\/\/friendsofscenic30a\.org\/membership\/"/, page);
    assert.match(html, /location\.replace\("\/membership\/"\)/, page);
    continue;
  }
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
assert.doesNotMatch(headerJs, /shop\.friendsofscenic30a\.org/);
assert.doesNotMatch(headerJs, /\/shop\//);
assert.match(footerJs, /\/includes\/footer\.html/);

const header = readFileSync(join(root, "includes/header.html"), "utf8");
assert.match(header, /<a class="brand" href="\/"/);
assert.match(header, /<a href="https:\/\/shop\.friendsofscenic30a\.org\/" target="_blank" rel="noopener noreferrer">Shop<\/a>/);
assert.doesNotMatch(header, /href="\/shop\/"/);
assert.doesNotMatch(header, /<a class="brand" href="https:\/\/shop\.friendsofscenic30a\.org\//);
assert.match(header, /aria-label="Friends of Scenic 30A"/);
assert.match(header, /alt="Friends of Scenic 30A"/);
assert.doesNotMatch(header, /brand-kicker|brand-name/);
const footer = readFileSync(join(root, "includes/footer.html"), "utf8");
assert.match(footer, /Friends of Scenic 30A/);
assert.match(footer, /class="footer-brand"/);
assert.match(footer, /alt="Friends of Scenic 30A"/);
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
assert.match(footer, /class="footer-badges"/);
assert.match(footer, /https:\/\/waltondunelakes\.com\//);
assert.match(footer, /logo-walton-dune-lakes\.png/);
assert.match(footer, /alt="Walton Dune Lakes"/);
assert.match(footer, /<h2>Explore<\/h2>/);
assert.match(footer, /<h2>Get Involved<\/h2>/);
assert.match(footer, /href="\/membership\/#volunteer">Volunteer</);
assert.doesNotMatch(footer, /href="\/get-involved\/"/);
assert.match(footer, /<a href="https:\/\/shop\.friendsofscenic30a\.org\/" target="_blank" rel="noopener noreferrer">Shop<\/a>/);
assert.doesNotMatch(footer, /href="\/shop\/"/);
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
const impactHtml = readFileSync(join(root, "impact.html"), "utf8");
const memberPage = readFileSync(join(root, "membership/index.html"), "utf8");
const involved = readFileSync(join(root, "get-involved/index.html"), "utf8");
for (const [name, page] of [["about", about], ["membership", memberPage]]) {
  assert.match(page, /class="page-photos[\s"]/, name);
  assert.ok((page.match(/<figure>/g) || []).length >= 1, name);
}
assert.equal(isImpactRedirect(impact), true);
assert.equal(isImpactRedirect(impactHtml), true);
assert.doesNotMatch(header, /href="\/impact\/"/);
assert.doesNotMatch(footer, /href="\/impact\/"/);
assert.doesNotMatch(header, /href="\/get-involved\/"/);
assert.doesNotMatch(header, />Get Involved</);
assert.match(header, /href="\/membership\/">Membership</);
assert.match(header, /href="\/our-work\/">Our Work</);
assert.match(work, /<figcaption>Photo: Walton County Tourism<\/figcaption>/);
assert.match(work, /id="current-projects"/);
assert.match(work, /id="our-priorities"/);
assert.match(work, /id="past-accomplishments"/);
assert.match(work, /href="#current-projects">Current Projects</);
assert.match(work, /href="#our-priorities">Our Priorities</);
assert.match(work, /href="#past-accomplishments">Past Accomplishments</);
assert.match(work, /West 30A Gateway Landscaping/);
assert.match(work, /Scenic 30A Entry Signage/);
assert.match(work, /Active — Planning &amp; Funding/);
assert.match(work, /Active — In Development/);
assert.match(work, /https:\/\/walton\.civicweb\.net\/document\/529193\//);
assert.match(work, /https:\/\/www\.scenic\.org\/2026\/07\/10\/scenic-walton-celebrates-progress-in-walton-county\//);
assert.doesNotMatch(work, /utm_/);
assert.doesNotMatch(work, /under construction|construction has started|construction is underway/i);
assert.match(work, /additional steps remain before construction begins/);
assert.match(work, /Protecting Our Natural Landscape/);
assert.match(work, /Safer Walking, Biking &amp; Connectivity/);
assert.match(work, /Keeping Scenic 30A Scenic/);
assert.match(work, /Education &amp; Community Stewardship/);
assert.match(work, /Florida Scenic Highway Designation/);
assert.match(work, /class="accomplish-year">2008</);
assert.match(work, /National Scenic Byway Designation/);
assert.match(work, /class="accomplish-year">2021</);
assert.match(work, /class="corner-feature"/);
assert.match(work, /Friends’ Corner at Eastern Lake/);
assert.match(work, /Completed May 2024/);
assert.match(work, /\$50,000/);
assert.match(work, /Kimley-Horn/);
assert.match(work, /Dewberry Engineering/);
assert.match(work, /Irrigation/);
assert.match(work, /images\/friends-corner-eastern-lake\.jpg/);
assert.match(work, /https:\/\/www\.waltoncountyfltourism\.com\/press\/ribbon-cutting-marks-completion-pedestrian-rest-area-on-30a\//);
assert.match(work, /https:\/\/www\.waltoncountyfltourism\.com\/walton-county-line\/new-pedestrian-and-bike-rest-area-enhances-scenic-highway-30a\//);
assert.match(work, /class="accomplish-card"/);
assert.equal((work.match(/class="accomplish-card/g) || []).length, 4);
assert.match(work, /Wayfinding &amp; Signage Improvements/);
assert.match(work, /30A Gateway Improvements/);
assert.match(work, /alt="Aerial view of the Gulf, beach, and a dune lake beside 30A"/);
assert.match(work, /alt="Gulf shoreline and sea oats along Scenic 30A"/);
assert.doesNotMatch(work, /A Voice for Scenic 30A|Bringing Our Community Together|Planning for 30A/);
assert.doesNotMatch(about, /<figcaption>/);
assert.match(about, /page-hero-tall/);
assert.match(about, /feature-row/);
assert.match(about, /topic-grid/);
assert.match(about, /Protect\. Preserve\. Enhance\./);
assert.match(about, /alt="People riding the paved Timpoochee Trail"/);
assert.match(about, /alt="Coastal dune lake edged by pines"/);
assert.match(about, /alt="Sea oats on the dunes"/);
assert.match(memberPage, /<figcaption>/);
assert.match(memberPage, /Step 1\. Pay through Square/);
assert.match(memberPage, /Step 2\. Submit your member details/);
assert.match(memberPage, /id="volunteer"/);
assert.match(memberPage, /data-form="volunteer"/);
assert.match(memberPage, /id="stay-informed"/);
assert.match(memberPage, /data-form="updates"/);
assert.match(memberPage, /There’s a Place for You in Our Mission/);
assert.match(memberPage, /Find Friends of Scenic 30A merchandise in the official shop/);
assert.equal(isGetInvolvedRedirect(involved), true);
assert.doesNotMatch(memberPage, /\$25 annually/);
assert.doesNotMatch(memberPage, /Join as an Individual/);
const contact = readFileSync(join(root, "contact/index.html"), "utf8");
assert.match(contact, /877 N County Hwy 393/);
assert.match(contact, /Say Hello/);
assert.doesNotMatch(contact, /Mail is also received at P\.O\. Box 1931/);
assert.doesNotMatch(contact, /P\.O\. Box 1931/);
const css = readFileSync(join(root, "styles.css"), "utf8");
assert.match(css, /images\/hero\.jpg/);
assert.match(css, /\.brand img \{[^}]*width: 196px/);
assert.match(css, /\.brand img \{[^}]*width: 228px/);
assert.match(css, /\.brand img \{[^}]*height: auto/);
assert.match(css, /\.brand img \{[^}]*object-fit: contain/);
assert.doesNotMatch(css, /\.brand img \{[^}]*height: 104px/);
assert.match(css, /\.header-inner \{[^}]*padding: 0\.35rem 1\.25rem/);
assert.match(css, /\.page-hero \{[^}]*min-height: clamp\(22rem, 52vh, 36rem\)/);
assert.match(css, /\.photo-mosaic/);
assert.match(css, /\.priority-list/);
assert.match(work, /family=Source\+Sans\+3/);
assert.doesNotMatch(work, /Fraunces|Outfit|page-our-work/);
assert.match(css, /--serif: "Source Sans 3"/);
assert.match(css, /--sans: "Source Sans 3"/);
assert.doesNotMatch(css, /Fraunces|Outfit|page-our-work/);
assert.match(css, /\.page-hero h1 \{[^}]*clamp\(2\.2rem, 4\.5vw, 3\.45rem\)/);
assert.match(css, /\.page-hero \.eyebrow \{[^}]*font-weight: 600/);
assert.match(css, /\.lead-split h2, \.work-block h2 \{[^}]*clamp\(1\.85rem, 2\.8vw, 2\.3rem\)/);
assert.match(css, /\.quote \{[^}]*clamp\(1\.6rem, 2\.5vw, 2\.15rem\)/);
assert.match(css, /h1, h2, h3, h4 \{[^}]*font-weight: 600/);

const membership = readFileSync(join(root, "membership/index.html"), "utf8");
assert.match(header, /href="\/our-work\/">Our Work<\/a>\s*<a href="\/how-projects-get-funded\/">How Projects Get Funded<\/a>\s*<a href="\/gallery\/">Gallery<\/a>/);
assert.match(header, /<a href="\/how-projects-get-funded\/">How Projects Get Funded<\/a>/);
assert.match(header, /https:\/\/square\.link\/u\/Yzxyi16L/);
assert.match(membership, /https:\/\/square\.link\/u\/GUdeODzg/);
assert.match(membership, /https:\/\/square\.link\/u\/KlIhQxsE/);
assert.match(membership, /https:\/\/checkout\.square\.site\/merchant\/MLC659T9BQY4F\/checkout\/Y6NHRE2EMR2YOKJIDEGOB3I7/);
assert.match(membership, /<h3>Corporate<\/h3>[\s\S]*\$1,000 \/ year/);
assert.match(membership, /Corporate Membership – \$1,000\/year/);
const funded = readFileSync(join(root, "how-projects-get-funded/index.html"), "utf8");
assert.match(funded, /<h1>How Projects Get Funded<\/h1>/);
assert.match(funded, /<title>How Projects Get Funded \| Friends of Scenic 30A<\/title>/);
for (const sentence of [
  "Improving and protecting Scenic Highway 30A takes more than good ideas. It takes community involvement, partnerships, and the right funding sources.",
  "Friends of Scenic 30A works to identify projects that can improve, preserve, or enhance the Scenic 30A corridor. Depending on the size and type of the project, funding may come from several different sources.",
  "Friends of Scenic 30A is led by a 100% volunteer board. We have no paid staff and no administrative or operating expenses, allowing our efforts to remain focused on projects and initiatives that benefit Scenic Highway 30A and the surrounding community.",
  "Individuals and businesses can help support Friends of Scenic 30A and the projects we pursue. Smaller improvements may be funded directly through donations, while larger projects may use community contributions to help with planning, design, matching funds, or other project-related expenses.",
  "We believe in transparency and want donors to understand how funds are being used and what they are helping accomplish.",
  "Many community, environmental, beautification, transportation, and preservation projects may qualify for grants from foundations, government agencies, and other organizations.",
  "Friends of Scenic 30A can help identify grant opportunities and work with community partners to pursue funding for projects along the corridor.",
  "Many improvements along Scenic 30A involve public property, transportation infrastructure, landscaping, pedestrian facilities, or other community assets.",
  "For these projects, Friends of Scenic 30A can work with Walton County, the Walton County Tourism Department, and other public agencies to advocate for projects and help identify potential funding.",
  "Larger transportation, environmental, safety, and infrastructure projects may qualify for state or federal funding.",
  "Friends of Scenic 30A can help bring attention to these opportunities and work with local officials and community partners to move worthy projects forward.",
  "Local businesses, property owners, civic organizations, homeowners associations, and other community groups can also play an important role.",
  "A project might include private sponsorships, donated materials or services, volunteer participation, or partnerships between several organizations.",
  "There is no single funding source for every project.",
  "A small landscaping project may be funded by community donations and local sponsors. A pedestrian improvement could involve Walton County or the Tourism Department. An environmental project might qualify for a grant. A major infrastructure improvement could involve county, state, and federal funding.",
  "Our role is to help bring the right people, organizations, and funding sources together, while keeping Friends of Scenic 30A volunteer-driven and focused on improving and preserving the Scenic 30A corridor.",
]) {
  assert.ok(funded.includes(sentence), sentence);
}
assert.doesNotMatch(funded, /[—–]/);
const priceGrid = (html) => {
  const match = html.match(/<div class="price-grid">[\s\S]*?<\/div>/);
  assert.ok(match, "price grid");
  return match[0];
};
assert.equal(priceGrid(funded), priceGrid(membership));
const fundedOrder = funded.indexOf("Community Donations");
assert.ok(fundedOrder < funded.indexOf(">Grants<"));
assert.ok(funded.indexOf(">Grants<") < funded.indexOf("Walton County and TDC Partnerships"));
assert.ok(funded.indexOf("Walton County and TDC Partnerships") < funded.indexOf("State and Federal Funding"));
assert.ok(funded.indexOf("State and Federal Funding") < funded.indexOf("Business and Community Partnerships"));
assert.ok(funded.indexOf("Business and Community Partnerships") < funded.indexOf("A Project-by-Project Approach"));
assert.ok(funded.indexOf("A Project-by-Project Approach") < funded.indexOf("Become a Member"));
assert.match(membership, /https:\/\/square\.link\/u\/Yzxyi16L/);
assert.match(membership, /href="https:\/\/shop\.friendsofscenic30a\.org\/" target="_blank" rel="noopener noreferrer">Shop/);

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
assert.match(home, /Organizations connected to the corridor/);
assert.doesNotMatch(home, /Sponsors of Friends of Scenic 30A/);
assert.doesNotMatch(home, /sponsor-logos/);
assert.doesNotMatch(home, /your-brand-here/);
assert.match(footer, /class="section section-sand footer-sponsors"/);
assert.match(footer, /Sponsors of Friends of Scenic 30A/);
const sponsors = footer.match(/<ul class="partner-logos sponsor-logos">[\s\S]*?<\/ul>/);
assert.ok(sponsors, "sponsors list");
assert.equal((sponsors[0].match(/\/images\/sponsors\/your-brand-here\.png/g) || []).length, 3);
assert.equal((sponsors[0].match(/alt="Your brand here"/g) || []).length, 3);
assert.doesNotMatch(sponsors[0], /<a\b/);
assert.match(home, /class="partner-logos"><li><a href="https:\/\/30a\.com\//);
const avatar = home.match(/<div class="hero-avatar">[\s\S]*?<\/div>/);
assert.ok(avatar, "hero avatar");
assert.match(avatar[0], /alt="Video"/);
assert.match(avatar[0], /aria-label="Play video"/);
assert.match(avatar[0], /poster="\/images\/hero-avatar-poster\.jpg"/);
assert.match(avatar[0], /src="\/images\/hero-avatar\.mp4"/);
assert.doesNotMatch(avatar[0], /autoplay|loop|figcaption|caption/);
for (const pagePath of pages) {
  if (pagePath === join(root, "index.html")) continue;
  assert.equal(readFileSync(pagePath, "utf8").includes("hero-avatar"), false, pagePath);
}
assert.match(css, /\.partner-logos\.sponsor-logos img \{[^}]*filter: none/);
assert.match(css, /\.footer-sponsors \{ color: var\(--ink\)/);
assert.match(css, /\.site-footer \.footer-sponsors h2 \{[^}]*text-transform: none/);
assert.match(css, /\.strip-nav/);
assert.match(css, /\.strip-prev \{ left:/);
assert.match(css, /\.strip-next \{ right:/);
const siteJs = readFileSync(join(root, "site.js"), "utf8");
assert.match(siteJs, /bindHeroAvatar/);
assert.match(siteJs, /Play video/);
assert.match(siteJs, /Stop video/);
assert.match(siteJs, /strip-prev/);
assert.match(siteJs, /strip-next/);
assert.match(siteJs, /ArrowLeft/);
assert.match(siteJs, /ArrowRight/);
const build = readFileSync(join(root, "scripts/build.py"), "utf8");
assert.doesNotMatch(build, /sponsor-logos|your-brand-here|Sponsors of Friends of Scenic 30A/);
assert.match(build, /Source\+Sans\+3/);
assert.doesNotMatch(build, /Fraunces|Outfit|page-our-work/);
for (const pagePath of pages) {
  const html = readFileSync(pagePath, "utf8");
  if (isImpactRedirect(html) || isShopRedirect(html) || isGetInvolvedRedirect(html)) continue;
  assert.match(html, /Source\+Sans\+3/, pagePath);
  assert.doesNotMatch(html, /Fraunces|Outfit|page-our-work/, pagePath);
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
for (const path of ["/", "/about/", "/our-work/", "/how-projects-get-funded/", "/gallery/", "/membership/", "/contact/", "/blog/", "/privacy-policy/", "/accessibility/", "/terms/"]) {
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
  "/how-projects-get-funded/",
  "/gallery/",
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
assert.equal(sitemap.includes("/impact/"), false);
assert.equal(llms.includes("/impact/"), false);
assert.equal(sitemap.includes("/shop/"), false);
assert.equal(llms.includes("/shop/"), false);
assert.equal(llmsFull.includes("/shop/"), false);
assert.equal(sitemap.includes("/get-involved/"), false);
assert.equal(llms.includes("/get-involved/"), false);
assert.equal(llmsFull.includes("/get-involved/"), false);

const shopPage = readFileSync(join(root, "shop/index.html"), "utf8");
assert.equal(isShopRedirect(shopPage), true);
assert.match(home, /href="https:\/\/shop\.friendsofscenic30a\.org\/" target="_blank" rel="noopener noreferrer">Shop/);
assert.doesNotMatch(home, /href="\/shop\/"/);
assert.doesNotMatch(membership, /href="\/shop\/"/);

const redirects = readFileSync(join(root, "_redirects"), "utf8");
for (const path of ["/impact", "/impact/", "/impact/index.html", "/impact.html"]) {
  assert.match(redirects, new RegExp(`${path.replaceAll("/", "\\/")} /our-work/#past-accomplishments 301`));
}
for (const path of ["/shop", "/shop/", "/shop/index.html"]) {
  assert.match(redirects, new RegExp(`${path.replaceAll("/", "\\/")} https://shop\\.friendsofscenic30a\\.org/ 301`));
}
for (const path of ["/get-involved", "/get-involved/", "/get-involved/index.html"]) {
  assert.match(redirects, new RegExp(`${path.replaceAll("/", "\\/")} /membership/ 301`));
}
assert.match(wrangler, /\/impact\/index\.html/);
assert.match(wrangler, /\/shop\/index\.html/);
assert.match(wrangler, /\/get-involved\/index\.html/);

const worker = await import("../src/worker.js");
for (const path of ["/impact", "/impact/", "/impact/index.html", "/impact.html"]) {
  const response = await worker.default.fetch(new Request(`https://friendsofscenic30a.org${path}`), {});
  assert.equal(response.status, 301, path);
  assert.match(response.headers.get("location") || "", /\/our-work\/#past-accomplishments$/, path);
}
for (const path of ["/shop", "/shop/", "/shop/index.html"]) {
  const response = await worker.default.fetch(new Request(`https://friendsofscenic30a.org${path}`), {});
  assert.equal(response.status, 301, path);
  assert.equal(response.headers.get("location"), "https://shop.friendsofscenic30a.org/", path);
}
for (const path of ["/get-involved", "/get-involved/", "/get-involved/index.html"]) {
  const response = await worker.default.fetch(new Request(`https://friendsofscenic30a.org${path}`), {});
  assert.equal(response.status, 301, path);
  assert.equal(response.headers.get("location"), "/membership/", path);
}
const homeResponse = await worker.default.fetch(new Request("https://friendsofscenic30a.org/"), {});
assert.equal(homeResponse.status, 404);

const ignore = readFileSync(join(root, ".assetsignore"), "utf8");
for (const name of ["robots.txt", "sitemap.xml", "llms.txt", "llms-full.txt"]) {
  assert.equal(ignore.includes(name), false, name);
}
const headers = readFileSync(join(root, "_headers"), "utf8");
assert.match(headers, /\/llms\.txt\n {2}Content-Type: text\/plain; charset=utf-8/);
assert.match(headers, /\/llms-full\.txt\n {2}Content-Type: text\/plain; charset=utf-8/);
assert.match(headers, /X-Content-Type-Options: nosniff/);
assert.match(headers, /Referrer-Policy: strict-origin-when-cross-origin/);
assert.match(headers, /X-Frame-Options: SAMEORIGIN/);
assert.match(headers, /Permissions-Policy: camera=\(\), microphone=\(\), geolocation=\(\)/);
assert.match(headers, /Strict-Transport-Security: max-age=31536000; includeSubDomains/);
assert.match(headers, /Content-Security-Policy:.*default-src 'self'/);
assert.match(headers, /script-src 'self'/);
assert.match(headers, /style-src 'self' 'unsafe-inline' https:\/\/fonts\.googleapis\.com/);
assert.match(headers, /font-src 'self' https:\/\/fonts\.gstatic\.com/);
assert.match(headers, /frame-src https:\/\/www\.youtube-nocookie\.com https:\/\/www\.youtube\.com/);
assert.match(headers, /connect-src 'self' https:\/\/fonts\.googleapis\.com https:\/\/fonts\.gstatic\.com/);

console.log(`seo ok (${pages.length} pages)`);
