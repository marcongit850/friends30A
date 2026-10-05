#!/usr/bin/env python3
"""Generate the static Friends of Scenic 30A pages."""

import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = os.environ.get("SITE_ORIGIN", "https://friendsofscenic30a.org").rstrip("/")
BRAND = "Friends of Scenic 30A"
TITLE_LIMIT = 70
DESCRIPTION_MIN = 110
DESCRIPTION_MAX = 165
DONATE = "https://square.link/u/Yzxyi16L"
MEMBER_INDIVIDUAL = "https://square.link/u/GUdeODzg"
MEMBER_BUSINESS = "https://square.link/u/KlIhQxsE"
MEMBER_CORPORATE = "https://checkout.square.site/merchant/MLC659T9BQY4F/checkout/Y6NHRE2EMR2YOKJIDEGOB3I7"
MEMBERSHIP_DESCRIPTION = (
    "Join Friends of Scenic 30A. Individual membership is $25 a year, business is $100, "
    "and corporate is $1,000, paid securely through Square."
)
SHOP_STOREFRONT = "https://shop.friendsofscenic30a.org/"
PAGES = []
FONT = "https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&display=swap"
GA_MEASUREMENT_ID = "G-98P1HEEQLJ"
GA_INLINE_SCRIPT = (
    "window.dataLayer = window.dataLayer || [];\n"
    "function gtag(){dataLayer.push(arguments);}\n"
    "gtag('js', new Date());\n"
    f"gtag('config', '{GA_MEASUREMENT_ID}');"
)
GA_SNIPPET = (
    f'  <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>\n'
    "  <script>\n"
    + "".join(f"    {line}\n" for line in GA_INLINE_SCRIPT.split("\n"))
    + "  </script>\n"
)

GALLERY = [
    ("/images/gallery/01-boardwalk-sea-oats.jpg", "Boardwalk through sea oats toward the Gulf"),
    ("/images/gallery/02-gulf-sea-oats.jpg", "Gulf shoreline and sea oats along Scenic 30A"),
    ("/images/gallery/03-dune-lake-pines.jpg", "Coastal dune lake edged by pines"),
    ("/images/gallery/04-boardwalk-beach.jpg", "Beach boardwalk opening onto the Gulf"),
    ("/images/gallery/05-dune-lake-shore.jpg", "Grassy shore of a coastal dune lake"),
    ("/images/gallery/06-aerial-gulf-and-lake.jpg", "Aerial view of the Gulf, beach, and a dune lake beside 30A"),
    ("/images/gallery/07-timpoochee-riders.jpg", "People riding the paved Timpoochee Trail"),
    ("/images/gallery/08-gulf-sunset.jpg", "Sunset over the Gulf of Mexico"),
    ("/images/gallery/09-aerial-lake-beach.jpg", "Aerial view of beach, dunes, and a coastal dune lake"),
    ("/images/gallery/10-sandy-scrub-path.jpg", "Sandy path through coastal scrub"),
    ("/images/gallery/11-gulf-path.jpg", "Path beside the Gulf with sea oats and pines"),
    ("/images/gallery/12-beach-chairs.jpg", "Beach chairs on sugar-white sand"),
    ("/images/gallery/13-palm-path.jpg", "Palm-lined path in a 30A beach community"),
    ("/images/gallery/14-dune-sea-oats.jpg", "Sea oats on the dunes"),
]

IMAGE_ALTS = {src: alt for src, alt in GALLERY}
IMAGE_ALTS.update({
    "/images/hero.jpg": "Beach boardwalk opening onto the Gulf",
    "/images/blog/native-landscape.jpg": "Boardwalk through sea oats toward the Gulf of Mexico",
    "/images/blog/corridor-beach.jpg": "Gulf shoreline and sea oats along Scenic Highway 30A",
    "/images/blog/communities.jpg": "Palm-lined path in a Scenic 30A beach community",
    "/images/blog/heritage.jpg": "Sandy path through coastal scrub and pines",
    "/images/blog/dunes.jpg": "Sea oats and a wooden boardwalk on the dunes",
    "/images/blog/story.jpg": "Beach path through sea oats and dunes toward the Gulf",
    "/images/blog/vision.jpg": "Boardwalk through sea oats opening onto the Gulf",
    "/images/blog/trails.jpg": "Trail through the Scenic 30A corridor",
})
HOME_DESCRIPTION = (
    "Scenic Highway 30A preservation starts with community. Join us in protecting its natural beauty, "
    "scenic character, neighborhoods, and quality of life."
)

HEADINGS = {
    "Facilities",
    "State Parks",
    "Trails",
    "Other trails located on state lands include:",
    "Ecology",
    "Natural Resources",
    "Archeological",
    "Native American Burial Grounds",
    "Recreational",
    "Natural",
    "Scenic",
    "Historical Town Stories",
    "Great South Walton Historical Touring Trek",
    "Abandoned Town of Santa Rosa",
    "Grayton",
    "Point Washington",
    "Historic Resources",
    "Historic Point Washington",
    "Bay Elementary School",
    "Seagrove Beach",
    "Seaside",
    "Cultural Resources",
    "Native Vegetation Matters",
    "Protecting Heritage Trees and Scenic Character",
    "Our Coastal Dune Lakes",
    "State Lands and Trails",
    "Preservation Requires Participation",
    "Protecting What Makes 30A Different",
    "A Longstanding Role in Transportation Planning",
    "Making 30A Safer for People Walking and Biking",
    "Connectivity Matters",
    "Growth Makes the Conversation More Important",
    "Planning for the Future",
    "A Collection of Distinct Communities",
    "An Extraordinary Natural Environment",
    "A Corridor Meant to Be Experienced",
    "More Than a Scenic Road",
}


def esc(value):
    return html.escape(value, quote=True)


LINK_TOKEN = re.compile(r"\[(https?://[^\]]+)\]\s*")
CAP_WORDS = re.compile(r"((?:[A-Z0-9][\w’'.-]*\s*){1,6})")


def linkify(text):
    text = re.sub(r"(\d+)\s+(st|nd|rd|th)\b", r"\1\2", text)
    text = re.sub(r"(\d+(?:st|nd|rd|th))\s+,", r"\1,", text)
    pieces = []
    pos = 0
    for match in LINK_TOKEN.finditer(text):
        pieces.append(esc(text[pos:match.start()]))
        url = match.group(1)
        rest = text[match.end():]
        label = ""
        consumed = 0
        labeled = CAP_WORDS.match(rest)
        if labeled:
            words = labeled.group(1).split()
            if words and all(word[:1].isupper() or word[:1].isdigit() for word in words):
                label = labeled.group(1).strip().rstrip(".")
                consumed = len(label)
        if not label:
            label = re.sub(r"^https?://(?:www\.)?", "", url).split("/")[0]
        pos = match.end() + consumed
        spacer = " " if pos < len(text) and text[pos].isalnum() else ""
        pieces.append(
            f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>{spacer}'
        )
    pieces.append(esc(text[pos:]))
    return "".join(pieces)


def article_html(text):
    blocks = []
    items = []

    def flush_items():
        if items:
            blocks.append("<ul>" + "".join(f"<li>{linkify(item)}</li>" for item in items) + "</ul>")
            items.clear()

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        linked = re.match(r"^\[(https?://[^\]]+)\]\s*(.+)$", line)
        if line in HEADINGS or line.endswith("include:"):
            flush_items()
            blocks.append(f"<h2>{linkify(line)}</h2>")
            continue
        if linked and len(linked.group(2)) < 80 and "." not in linked.group(2):
            flush_items()
            blocks.append(
                f'<h2><a href="{esc(linked.group(1))}" target="_blank" rel="noopener noreferrer">{esc(linked.group(2).strip())}</a></h2>'
            )
            continue
        dash = line.split(" – ", 1)[0] if " – " in line else ""
        catalog = bool(dash) and len(dash) <= 64 and dash.count(" ") <= 8 and line.count(".") <= 1
        short = len(line) <= 140 and not re.search(r"[.!?]$", line) and line.count(" ") <= 18
        if catalog or short:
            items.append(line)
            continue
        flush_items()
        blocks.append(f"<p>{linkify(line)}</p>")
    flush_items()
    return "\n".join(blocks)


def document_title(title):
    full = title if title.endswith(BRAND) else f"{title} | {BRAND}"
    if len(full) > TITLE_LIMIT:
        raise SystemExit(f"title too long ({len(full)}): {full}")
    return full


def jpeg_size(data):
    index = 2
    while index < len(data) - 8:
        if data[index] != 0xFF:
            index += 1
            continue
        marker = data[index + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height = int.from_bytes(data[index + 5:index + 7], "big")
            width = int.from_bytes(data[index + 7:index + 9], "big")
            return width, height
        if marker in (0xD8, 0xD9):
            index += 2
            continue
        index += 2 + int.from_bytes(data[index + 2:index + 4], "big")
    raise SystemExit("jpeg size not found")


def image_info(path):
    data = (ROOT / path.lstrip("/")).read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return {
            "width": int.from_bytes(data[16:20], "big"),
            "height": int.from_bytes(data[20:24], "big"),
            "mime": "image/png",
        }
    if data.startswith(b"\xff\xd8"):
        width, height = jpeg_size(data)
        return {"width": width, "height": height, "mime": "image/jpeg"}
    raise SystemExit(f"unsupported image {path}")


def organization_node():
    return {
        "@type": ["NGO", "Organization"],
        "@id": f"{ORIGIN}/#organization",
        "name": BRAND,
        "url": f"{ORIGIN}/",
        "description": "Designated Byway Organization for Scenic Highway 30A.",
        "logo": {
            "@type": "ImageObject",
            "url": f"{ORIGIN}/images/logo.png",
            "width": 512,
            "height": 341,
        },
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "877 N County Hwy 393",
            "addressLocality": "Santa Rosa Beach",
            "addressRegion": "FL",
            "postalCode": "32459",
            "addressCountry": "US",
        },
        "areaServed": {
            "@type": "AdministrativeArea",
            "name": "Scenic Highway 30A, Walton County, Florida",
        },
        "sameAs": [
            "https://www.facebook.com/fof30a",
            "https://nextdoor.com/page/friends-of-scenic-30a-santa-rosa-beach-fl/",
        ],
    }


def website_node():
    return {
        "@type": "WebSite",
        "@id": f"{ORIGIN}/#website",
        "url": f"{ORIGIN}/",
        "name": BRAND,
        "description": HOME_DESCRIPTION,
        "inLanguage": "en",
        "publisher": {"@id": f"{ORIGIN}/#organization"},
    }


def image_node(url, info, alt):
    return {
        "@type": "ImageObject",
        "url": url,
        "width": info["width"],
        "height": info["height"],
        "caption": alt,
    }


def breadcrumb_node(url, crumbs):
    return {
        "@type": "BreadcrumbList",
        "@id": url + "#breadcrumb",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index,
                "name": name,
                "item": ORIGIN + path,
            }
            for index, (name, path) in enumerate(crumbs, start=1)
        ],
    }


def json_ld(graph):
    payload = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)
    payload = payload.replace("<", "\\u003c")
    indented = "\n".join("  " + line for line in payload.splitlines())
    return f'<script type="application/ld+json">\n{indented}\n  </script>'


def layout(title, description, path, body, image="/images/hero.jpg", image_alt=None, kind="WebPage", crumbs=None, article=None, blog_posts=None, media=None, robots=None):
    canonical = ORIGIN + path
    full_title = document_title(title)
    alt = image_alt or IMAGE_ALTS.get(image, "Scenic Highway 30A along the Gulf of Mexico")
    info = image_info(image)
    image_url = ORIGIN + image
    og_type = "article" if article else "website"
    page = {
        "@type": "WebPage" if kind == "BlogPosting" else kind,
        "@id": canonical + "#webpage",
        "url": canonical,
        "name": full_title,
        "description": description,
        "isPartOf": {"@id": f"{ORIGIN}/#website"},
        "inLanguage": "en",
        "primaryImageOfPage": image_node(image_url, info, alt),
    }
    graph = [organization_node(), website_node(), page]
    if article:
        page["mainEntity"] = {"@id": canonical + "#article"}
        graph.append({
            "@type": "BlogPosting",
            "@id": canonical + "#article",
            "headline": article["headline"],
            "description": description,
            "datePublished": article["published"],
            "image": image_url,
            "author": {"@type": "Organization", "name": BRAND, "@id": f"{ORIGIN}/#organization"},
            "publisher": {"@id": f"{ORIGIN}/#organization"},
            "mainEntityOfPage": {"@id": canonical + "#webpage"},
            "url": canonical,
            "inLanguage": "en",
        })
    if blog_posts is not None:
        graph.append({
            "@type": "Blog",
            "@id": canonical + "#blog",
            "url": canonical,
            "name": full_title,
            "description": description,
            "publisher": {"@id": f"{ORIGIN}/#organization"},
            "blogPost": blog_posts,
        })
    if media:
        page["associatedMedia"] = media
    if crumbs:
        page["breadcrumb"] = {"@id": canonical + "#breadcrumb"}
        graph.append(breadcrumb_node(canonical, crumbs))
    robots_tag = f'\n  <meta name="robots" content="{esc(robots)}">' if robots else ""
    article_tag = ""
    if article:
        article_tag = f'\n  <meta property="article:published_time" content="{esc(article["published"])}">'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{GA_SNIPPET}  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(full_title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">{robots_tag}
  <meta property="og:title" content="{esc(full_title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:site_name" content="{BRAND}">
  <meta property="og:locale" content="en_US">
  <meta property="og:type" content="{og_type}">
  <meta property="og:image" content="{esc(image_url)}">
  <meta property="og:image:alt" content="{esc(alt)}">
  <meta property="og:image:width" content="{info["width"]}">
  <meta property="og:image:height" content="{info["height"]}">
  <meta property="og:image:type" content="{info["mime"]}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(full_title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{esc(image_url)}">
  <meta name="twitter:image:alt" content="{esc(alt)}">{article_tag}
  {json_ld(graph)}
  <link rel="icon" href="/favicon.png" type="image/png">
  <link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{FONT}" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <div id="site-header"></div>
  <main id="main">
{body}
  </main>
  <div id="site-footer"></div>
  <noscript><p>Friends of Scenic 30A, 877 N County Hwy 393, Santa Rosa Beach, FL 32459</p></noscript>
  <script src="/header.js"></script>
  <script src="/footer.js"></script>
  <script src="/site.js"></script>
</body>
</html>
"""


def write_page(path, title, description, body, image="/images/hero.jpg", image_alt=None, kind="WebPage", crumbs=None, article=None, blog_posts=None, media=None, robots=None):
    if robots != "noindex" and not DESCRIPTION_MIN <= len(description) <= DESCRIPTION_MAX:
        raise SystemExit(f"description length {len(description)} for {path}: {description}")
    full_title = document_title(title)
    PAGES.append({"path": path, "title": full_title, "description": description, "kind": kind})
    target = ROOT / "index.html" if path == "/" else ROOT / path.strip("/") / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(layout(
        title, description, path, body, image,
        image_alt=image_alt, kind=kind, crumbs=crumbs, article=article,
        blog_posts=blog_posts, media=media, robots=robots,
    ))
    print(path)


def page_hero(kicker, title, lede, image="/images/hero.jpg", extra_class=""):
    classes = "page-hero" + (f" {extra_class}" if extra_class else "")
    return f"""
    <header class="{classes}" style="--hero:url('{image}')">
      <div class="wrap">
        <p class="eyebrow">{esc(kicker)}</p>
        <h1>{title}</h1>
        <p>{lede}</p>
      </div>
    </header>
    """


def photos(items, captions=True, extra_class=""):
    figures = "\n".join(
        f'<figure><img src="{src}" alt="{esc(alt)}">'
        + (f"<figcaption>{esc(alt)}</figcaption>" if captions else "")
        + "</figure>"
        for src, alt in items
    )
    classes = "page-photos" + (f" {extra_class}" if extra_class else "")
    return f'<div class="{classes}">{figures}</div>'


ICON = {
    "leaf": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="currentColor" d="M5 19s7-1 11-8 3-9 3-9-6 1-9 6-5 11-5 11z"/><path fill="none" stroke="currentColor" stroke-width="1.6" d="M8 16c2-2 5-5 8-7"/></svg>',
    "road": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.7" d="M7 21 10 3M17 21 14 3M4 8h16M5 14h14"/></svg>',
    "trail": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><circle cx="7" cy="6" r="2" fill="currentColor"/><path fill="none" stroke="currentColor" stroke-width="1.7" d="M6 9l2 3-2 2 3 6M14 7l3 2-1 4 3 6M11 14h5"/></svg>',
    "people": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><circle cx="8" cy="8" r="2.2" fill="currentColor"/><circle cx="16" cy="9" r="1.8" fill="currentColor"/><path fill="none" stroke="currentColor" stroke-width="1.7" d="M3.5 19c.6-3 2.4-4.5 4.5-4.5S12 16 12.6 19M13 19c.3-2.2 1.6-3.4 3.2-3.4 1.7 0 3 1.2 3.4 3.4"/></svg>',
    "book": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.7" d="M12 6.5c-1.6-1-3.4-1.5-6-1.5v13c2.6 0 4.4.5 6 1.5 1.6-1 3.4-1.5 6-1.5v-13c-2.6 0-4.4.5-6 1.5z"/><path fill="none" stroke="currentColor" stroke-width="1.7" d="M12 6.5v13"/></svg>',
}


def home():
    pillars = [
        ("leaf", "Protecting Natural Resources", "We work to preserve Scenic 30A's coastal dune lakes, native vegetation, forests, dunes, beaches, and other natural resources that make this corridor unlike anywhere else."),
        ("road", "Preserving Scenic 30A", "We advocate for thoughtful planning, landscaping, infrastructure, and maintenance that protect the beauty and distinctive character of the Scenic 30A corridor."),
        ("trail", "Improving Trails &amp; Safety", "We work to improve walking, biking and transportation safety throughout the Scenic 30A corridor through trail and pedestrian improvements, signage, connectivity and thoughtful transportation planning."),
        ("people", "Educating &amp; Engaging", "We bring residents, businesses, visitors, and local government together to understand, appreciate, and help protect Scenic 30A's natural, historic, and cultural resources."),
    ]
    cards = "\n".join(
        f'<article class="pillar"><div class="mark">{ICON[key]}</div><h3>{title}</h3><p>{copy}</p></article>'
        for key, title, copy in pillars
    )
    strip = "\n".join(
        f'<a href="/gallery/"><img src="{src}" alt="{esc(alt)}"></a>'
        for src, alt in GALLERY[:6]
    )
    strip_prev = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" d="M14.5 5 8 12l6.5 7"/></svg>'
    strip_next = '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" d="m9.5 5 6.5 7-6.5 7"/></svg>'
    resources = [
        ("30A", "https://30a.com/", "/images/partners/30a.png", 512, 512),
        ("America's Byways", "https://www.byways.org/", "/images/partners/americas-byways.png", 454, 111),
        ("Beaches of South Walton", "https://www.visitsouthwalton.com/", "/images/partners/beaches-of-south-walton.svg", 459, 244),
        ("Florida Scenic Highways Program", "https://floridascenichighways.com/", "/images/partners/florida-scenic-highways.svg", 171, 110),
        ("Visit Florida", "https://www.visitflorida.com/", "/images/partners/visit-florida.svg", 178, 27),
        ("Walton Area Chamber of Commerce", "https://www.waltonareachamber.com/", "/images/partners/walton-area-chamber.png", 250, 79),
        ("South Walton", "https://sowal.com/", "/images/partners/south-walton.png", 177, 81),
        ("Scenic Walton", "https://www.scenic.org/scenic-walton/", "/images/partners/scenic-walton.png", 535, 215),
        ("Scenic America", "https://www.scenic.org/", "/images/partners/scenic-america.svg", 672, 262),
    ]
    resource_html = "\n".join(
        f'<li><a href="{url}" target="_blank" rel="noopener noreferrer">'
        f'<img src="{src}" alt="{esc(name)}" width="{width}" height="{height}"></a></li>'
        for name, url, src, width, height in resources
    )
    body = f"""
    <section class="hero">
      <div class="hero-inner">
        <p class="eyebrow">Scenic Highway 30A</p>
        <h1>Preserving What Makes 30A Special</h1>
        <p class="lede">Friends of Scenic 30A serves as the designated Byway Organization for Scenic Highway 30A, working to protect and enhance its natural beauty, scenic character, distinctive communities and quality of life.</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="/membership/">Become a Member</a>
          <a class="btn btn-ghost" href="{DONATE}" target="_blank" rel="noopener noreferrer">Donate</a>
          <a class="btn btn-ghost" href="/our-work/">Our Work</a>
        </div>
      </div>
      <img class="hero-scenic-logo" src="/images/hero-florida-scenic-highway.png" alt="Florida Scenic Highway, South Walton's Scenic 30-A" width="1065" height="1009">
      <div class="hero-avatar">
        <video class="hero-avatar-video" poster="/images/hero-avatar-poster.jpg" playsinline preload="none" aria-hidden="true">
          <source src="/images/hero-avatar.mp4" type="video/mp4">
        </video>
        <img class="hero-avatar-poster" src="/images/hero-avatar-poster.jpg" alt="Video">
        <button type="button" class="hero-avatar-toggle" aria-label="Play video">
          <svg class="hero-avatar-icon hero-avatar-icon-play" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="currentColor" d="M9 6.2v11.6L18.5 12z"/></svg>
          <svg class="hero-avatar-icon hero-avatar-icon-stop" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><rect x="6.5" y="6.5" width="11" height="11" rx="1.2" fill="currentColor"/></svg>
        </button>
      </div>
    </section>
    <section class="section section-sand">
      <div class="wrap">
        <p class="eyebrow">Our mission</p>
        <h2>A corridor unlike anywhere else</h2>
        <p class="subhead">Scenic 30A is a designated Florida Scenic Highway and National Scenic Byway, recognitions Friends of Scenic 30A helped make possible.</p>
        <p>To learn more about this designation, please visit the <a href="https://floridascenichighways.com/" target="_blank" rel="noopener noreferrer">Florida Scenic Highways Program</a> website.</p>
        <div class="pillars">{cards}</div>
      </div>
    </section>
    <section class="section section-gulf">
      <div class="wrap">
        <p class="eyebrow">More than 20 years of impact</p>
        <h2>What Friends has helped make possible</h2>
        <div class="impact-grid">
          <article class="stat"><h3>Florida Scenic Highway</h3><p>Helped secure Scenic 30A's designation as a Florida Scenic Highway.</p></article>
          <article class="stat"><h3>National Scenic Byway</h3><p>Helped prepare and advance the successful National Scenic Byway application.</p></article>
          <article class="stat"><h3>Friends' Corner</h3><p>Spearheaded the pedestrian and bicycle rest area at 30A and Eastern Lake Road.</p></article>
        </div>
        <p><a href="/our-work/#past-accomplishments">See past accomplishments →</a></p>
      </div>
    </section>
    <section class="section section-white">
      <div class="wrap">
        <p class="eyebrow">Why 30A matters</p>
        <h2>More than a road</h2>
        <div class="matter">
          <article>
            <h3>More Than a Road</h3>
            <p>Scenic 30A connects a remarkable collection of beaches, coastal dune lakes, state parks, forests, trails, and distinctive communities. Together, these natural and cultural resources create a sense of place unlike anywhere else in Florida.</p>
          </article>
          <article>
            <h3>Worth Protecting for Generations</h3>
            <p>What makes 30A special can easily be taken for granted. Protecting its natural landscapes, scenic character, trails, and community heritage ensures that future generations can experience the same extraordinary place that residents and visitors treasure today.</p>
          </article>
        </div>
      </div>
    </section>
    <section class="section section-foam">
      <div class="wrap">
        <p class="eyebrow">Get involved</p>
        <h2>You can help protect the future of Scenic 30A</h2>
        <div class="involve-grid">
          <article class="involve">
            <h3>Donate</h3>
            <p>Help protect and enhance Scenic 30A.</p>
            <a class="btn btn-gulf" href="{DONATE}" target="_blank" rel="noopener noreferrer">Donate →</a>
          </article>
          <article class="involve">
            <h3>Become a Member</h3>
            <p>Join the community working to preserve what makes 30A special.</p>
            <a class="btn btn-line" href="/membership/">Join Us →</a>
          </article>
          <article class="involve">
            <h3>Shop</h3>
            <p>Find Friends of Scenic 30A merchandise in the official shop.</p>
            <a class="btn btn-line" href="https://shop.friendsofscenic30a.org/" target="_blank" rel="noopener noreferrer">Shop →</a>
          </article>
        </div>
      </div>
    </section>
    <section class="section section-sand">
      <div class="wrap">
        <p class="eyebrow">Along Scenic 30A</p>
        <h2>The corridor, up close</h2>
        <div class="strip-scroller">
          <button type="button" class="strip-nav strip-prev" aria-controls="corridor-strip" aria-label="Previous photos" disabled>{strip_prev}</button>
          <div class="strip" id="corridor-strip" tabindex="0" role="group" aria-label="Corridor photos">{strip}</div>
          <button type="button" class="strip-nav strip-next" aria-controls="corridor-strip" aria-label="Next photos">{strip_next}</button>
        </div>
        <p><a class="btn btn-line" href="/gallery/">Open the gallery</a></p>
      </div>
    </section>
    <section class="section section-white">
      <div class="wrap">
        <p class="eyebrow">Scenic 30A resources</p>
        <h2>Organizations connected to the corridor</h2>
        <p class="subhead">Explore organizations and resources connected to Scenic 30A, South Walton and Florida's scenic highway community.</p>
        <ul class="partner-logos">{resource_html}</ul>
      </div>
    </section>
    """
    write_page(
        "/",
        "Scenic Highway 30A Preservation | Friends of Scenic 30A",
        HOME_DESCRIPTION,
        body,
    )


def about():
    topics = [
        ("leaf", "Protecting Natural Resources", "We support the preservation of the coastal dune lakes, native vegetation, forests, dunes, beaches, and natural landscapes that are fundamental to the identity of Scenic 30A."),
        ("road", "Preserving Scenic 30A", "We advocate for thoughtful planning, landscaping, infrastructure, and maintenance that respect the beauty and distinctive character of the scenic corridor."),
        ("trail", "Trails, Walking &amp; Biking", "The Timpoochee Trail is an important part of the 30A experience. We support improvements to trails, pedestrian connections, crossings, signage, and transportation infrastructure that enhance safety and connectivity."),
        ("people", "Community &amp; Heritage", "Scenic 30A is defined not only by its natural environment but also by its distinctive communities and history. We support efforts that celebrate and preserve the places, stories, and character that make the corridor unique."),
        ("book", "Education &amp; Stewardship", "Preservation begins with understanding. We work to educate and engage residents, visitors, businesses, and community leaders about Scenic 30A's resources and the importance of protecting them."),
    ]
    topic_cards = "\n".join(
        f'<article class="pillar"><div class="mark">{ICON[key]}</div><h3>{title}</h3><p>{copy}</p></article>'
        for key, title, copy in topics
    )
    heritage = photos([
        ("/images/gallery/14-dune-sea-oats.jpg", "Sea oats on the dunes"),
    ], captions=False, extra_class="wide")
    body = page_hero(
        "About Friends of Scenic 30A",
        "Preserving What Makes 30A Special",
        "We are a community-led organization dedicated to maintaining the unique character, natural beauty, and environmental health of the Scenic Highway 30A corridor for all who live here and visit.",
        "/images/blog/story.jpg",
        "page-hero-tall",
    ) + f"""
    <section class="section section-white">
      <div class="wrap feature-row">
        <div>
          <h2>Our Story</h2>
          <div class="prose">
            <p>Friends of Scenic 30A serves as the designated Byway Organization for Scenic Highway 30A. Since Scenic 30A received its Florida Scenic Highway designation in 2008, Friends has helped carry forward a community vision centered on preserving the corridor's extraordinary natural, scenic, historic, recreational and cultural resources.</p>
            <p>That role extends well beyond preservation. Friends works with residents, businesses, Walton County, the Tourist Development Council and other community and regional partners on transportation and trail safety, signage and wayfinding, beautification, public education, community engagement and thoughtful improvements throughout the Scenic 30A corridor.</p>
            <p>In 2021, Scenic 30A received National Scenic Byway designation, further recognizing the national significance of the corridor and its remarkable natural resources. Today, Friends continues working to protect what makes Scenic 30A special while helping prepare the corridor for the challenges and opportunities ahead.</p>
          </div>
        </div>
        <figure class="feature-photo portrait"><img src="/images/gallery/07-timpoochee-riders.jpg" alt="People riding the paved Timpoochee Trail"></figure>
      </div>
    </section>
    <section class="section section-sand">
      <div class="wrap">
        <p class="eyebrow">Our Mission</p>
        <h2 class="display">Protect. Preserve. Enhance.</h2>
        <p class="lede">Our mission is to help preserve and enhance the natural, scenic, recreational, historic, and community resources that define Scenic Highway 30A. Our efforts focus on protecting the character of the corridor while supporting improvements that make 30A safer, more beautiful, accessible, and enjoyable for residents and visitors alike.</p>
        <h2>What We Care About</h2>
        <div class="topic-grid">{topic_cards}</div>
      </div>
    </section>
    <section class="section section-white">
      <div class="wrap feature-row">
        <figure class="feature-photo portrait"><img src="/images/gallery/03-dune-lake-pines.jpg" alt="Coastal dune lake edged by pines"></figure>
        <div class="prose">
          <h2>Looking to the Future</h2>
          <h3>Preserving 30A for Generations to Come</h3>
          <p>Scenic 30A will continue to evolve. Our goal is not to prevent change, but to help ensure that change occurs thoughtfully. We envision a future where the scenic two-lane roadway remains distinctive, coastal dune lakes and native landscapes remain protected, walking and biking are safe and enjoyable, communities retain their individual character, and future generations can experience the qualities that make Scenic 30A unlike anywhere else. What we protect today becomes the 30A of tomorrow.</p>
        </div>
      </div>
    </section>
    <section class="section section-gulf">
      <div class="wrap cta-band">
        <h2>Be Part of the Future of Scenic 30A</h2>
        <p>Protecting Scenic 30A is a community effort. Whether you live here, own a business, visit year after year, or simply love this special place, there is a role for you in helping preserve its future.</p>
        <p><a class="btn btn-primary" href="/membership/">Become a Member</a></p>
      </div>
    </section>
    <section class="section section-sand">
      <div class="wrap">
        <div class="prose">
          <h2>Preserving Scenic 30A Heritage</h2>
          <p>Scenic 30A stretches across South Walton, connecting distinctive beach communities with coastal dune lakes, state parks, Point Washington State Forest, trails and important north-south corridors. This unique combination of natural, recreational and community resources is what Friends of Scenic 30A works to protect and enhance.</p>
          <p><a href="/our-work/">See how that work takes shape</a></p>
        </div>
        {heritage}
      </div>
    </section>
    """
    write_page(
        "/about/",
        "About the Scenic 30A Byway Organization",
        "Friends of Scenic 30A is the designated Byway Organization for Scenic Highway 30A, protecting its natural beauty, communities, and quality of life.",
        body,
        "/images/blog/story.jpg",
        kind="AboutPage",
        crumbs=[("Home", "/"), ("About", "/about/")],
    )


# Confirmed current initiatives only. Append a dict to publish a card.
# Do not add a project that has not been confirmed.
# Optional keys: why, doing, partners, timeline, sources, image, image_alt, href.
# timeline items: when, text, href, source. sources: href, label.
# Photos only when an existing image shows that project.
TDC_MINUTES = "https://walton.civicweb.net/document/529193/"
SCENIC_WALTON_JULY = "https://www.scenic.org/2026/07/10/scenic-walton-celebrates-progress-in-walton-county/"
CURRENT_PROJECTS = [
    {
        "name": "West 30A Gateway Landscaping",
        "status": "Active — Planning & Funding",
        "summary": "Friends of Scenic 30A is partnering with Scenic Walton on a gateway improvement at the western entrance to Scenic Highway 30A. The concept includes landscaping, pedestrian paths, lighting enhancements, and gateway signage for a more welcoming entrance to the nationally recognized scenic corridor.",
        "why": "The western entrance is an important first impression. Thoughtful landscaping, lighting, pedestrian improvements, and signage reinforce Scenic 30A’s identity and improve the gateway experience.",
        "partners": "Friends of Scenic 30A, Scenic Walton, Walton County Tourism and the Tourist Development Council, and other public partners as the project advances.",
        "timeline": [
            {
                "when": "April 2026",
                "text": "Friends of Scenic 30A joined Scenic Walton before the Walton County Tourist Development Council seeking inclusion in the FY27 tourism budget. The council’s consensus was to move the proposal into its budget workshop process.",
                "href": TDC_MINUTES,
                "source": "Walton County TDC minutes, April 7, 2026",
            },
            {
                "when": "July 2026",
                "text": "Scenic Walton reported that the 30A West Gateway Landscape Project had advanced into the proposed Tourist Development Council budget and was the only capital improvement project in that proposed budget. The same report says additional steps remain before construction begins.",
                "href": SCENIC_WALTON_JULY,
                "source": "Scenic Walton, via Scenic America, July 10, 2026",
            },
        ],
    },
    {
        "name": "Scenic 30A Entry Signage",
        "status": "Active — In Development",
        "summary": "Friends of Scenic 30A and Scenic Walton are working to improve how visitors are welcomed to Scenic Highway 30A. The initiative includes new entry signage at both the western and eastern entrances to 30A from U.S. Highway 98, recognizing Scenic 30A as a Florida Scenic Highway and a National Scenic Byway.",
        "why": "Scenic 30A is more than a local road. Gateway signage helps residents and visitors understand they are entering a nationally recognized scenic corridor with special natural, historic, recreational, and community resources.",
        "doing": "Friends of Scenic 30A is working with Scenic Walton on entry signs for both ends of the corridor.",
        "partners": "Friends of Scenic 30A and Scenic Walton.",
        "sources": [
            {
                "href": SCENIC_WALTON_JULY,
                "label": "Scenic Walton, via Scenic America, July 10, 2026",
            },
        ],
    },
]
PROJECT_STATUSES = {
    "Active",
    "In Planning",
    "Ongoing",
    "Community Discussion",
    "Active — Planning & Funding",
    "Active — In Development",
}

# Years, roles, and results are taken from the existing Our Work and Impact pages.
# Year is omitted when the site does not state one. Photos are included only when
# an existing image illustrates that accomplishment.
ACCOMPLISHMENTS = [
    {
        "year": "2008",
        "name": "Florida Scenic Highway Designation",
        "role": "Friends played a leading role in the designation effort.",
        "result": "Scenic 30A received official Florida Scenic Highway designation, creating a long-term framework for protecting and enhancing the corridor's unique resources.",
        "image": "/images/gallery/06-aerial-gulf-and-lake.jpg",
        "image_alt": "Aerial view of the Gulf, beach, and a dune lake beside 30A",
    },
    {
        "year": "2021",
        "name": "National Scenic Byway Designation",
        "role": "Friends helped prepare and advance the successful application.",
        "result": "Scenic 30A received National Scenic Byway designation.",
        "image": "/images/gallery/02-gulf-sea-oats.jpg",
        "image_alt": "Gulf shoreline and sea oats along Scenic 30A",
    },
    {
        "name": "Wayfinding & Signage Improvements",
        "role": "Friends worked to create a more cohesive and attractive signage system along Scenic 30A.",
        "result": "A corridor signage inventory, removal of duplicate and unnecessary signs, and installation of safety and trail-etiquette signage.",
    },
    {
        "name": "30A Gateway Improvements",
        "role": "Friends partnered with Scenic Walton and others.",
        "result": "Landscaping and gateway improvements celebrating Scenic 30A's state and national scenic designations.",
    },
]


def render_project_links(items, empty_label):
    links = []
    for item in items or []:
        href = item.get("href", "")
        label = item.get("source") or item.get("label") or ""
        if not href or not label:
            raise SystemExit(f"a {empty_label} needs an href and a label")
        if "utm_" in href:
            raise SystemExit(f"strip tracking parameters from {href}")
        links.append(
            f'<a href="{esc(href)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'
        )
    return links


def render_current_projects(projects):
    if not projects:
        return """
        <p class="project-empty">This section lists only confirmed active projects. None are documented on this site yet, so no project cards are shown. Ongoing priorities and completed projects follow.</p>
        """
    cards = []
    for project in projects:
        status = project.get("status", "")
        if status not in PROJECT_STATUSES:
            raise SystemExit(f"unknown project status {status!r} for {project.get('name')}")
        if not project.get("name") or not project.get("summary"):
            raise SystemExit("a current project needs a name and summary")
        image = ""
        if project.get("image"):
            alt = project.get("image_alt")
            if not alt:
                raise SystemExit(f"project image needs alt text: {project['name']}")
            image = f'<img src="{esc(project["image"])}" alt="{esc(alt)}">'
        why = f'<p><strong>Why it matters.</strong> {esc(project["why"])}</p>' if project.get("why") else ""
        doing = f'<p><strong>What Friends is doing.</strong> {esc(project["doing"])}</p>' if project.get("doing") else ""
        partners = f'<p><strong>Partners.</strong> {esc(project["partners"])}</p>' if project.get("partners") else ""
        timeline = ""
        if project.get("timeline"):
            rows = []
            for item in project["timeline"]:
                if not item.get("when") or not item.get("text"):
                    raise SystemExit(f"timeline item needs a date and text: {project['name']}")
                source = ""
                if item.get("href"):
                    source = " " + render_project_links([item], "timeline source")[0]
                rows.append(
                    f"<li><strong>{esc(item['when'])}.</strong> {esc(item['text'])}{source}</li>"
                )
            timeline = f'<p class="card-label">Timeline</p><ul class="project-timeline">{"".join(rows)}</ul>'
        sources = ""
        if project.get("sources"):
            linked = " ".join(render_project_links(project["sources"], "source"))
            sources = f'<p class="card-source"><strong>Source.</strong> {linked}</p>'
        more = ""
        if project.get("href"):
            more = f'<p class="card-more"><a href="{esc(project["href"])}">Learn more</a></p>'
        cards.append(
            f'<article class="project-card">{image}<div class="card-body">'
            f'<p class="status">{esc(status)}</p>'
            f"<h3>{esc(project['name'])}</h3>"
            f"<p>{esc(project['summary'])}</p>"
            f"{why}{doing}{partners}{timeline}{sources}{more}</div></article>\n"
        )
    return f'<div class="project-grid">\n{"".join(cards)}</div>'


FRIENDS_CORNER = {
    "name": "Friends’ Corner at Eastern Lake",
    "completed": "Completed May 2024",
    "summary": "Friends of Scenic 30A spearheaded this project from concept to completion, transforming a previously unused roadside parcel at Scenic Highway 30A and Eastern Lake Road into a landscaped pedestrian and bicycle rest area along the multi-use path. Walton County officials described the former site as suffering from haphazard parking and from visibility and aesthetic problems. A ribbon cutting in May 2024 marked the opening.",
    "amenities": [
        "Rest bench",
        "Bicycle repair and maintenance station",
        "Drinking fountain",
        "Dog-watering station",
        "Low-impact lighting",
        "Landscaping",
        "Irrigation",
        "Bike racks, repair tools, and an air pump",
    ],
    "funding": "Walton County awarded Friends $50,000. The Florida Department of Transportation funded design and planning through Kimley-Horn. Dewberry Engineering donated the survey work. Walton County Beach Operations provided construction labor and additional funding.",
    "image": "/images/friends-corner-eastern-lake.jpg",
    "image_alt": "Landscaped Friends’ Corner rest area with a bench and green bicycle repair station beside the road",
    "photo_credit": "Photo: Walton County Tourism",
    "sources": [
        {
            "href": "https://www.waltoncountyfltourism.com/press/ribbon-cutting-marks-completion-pedestrian-rest-area-on-30a/",
            "label": "Walton County Tourism ribbon cutting, May 2024",
        },
        {
            "href": "https://www.waltoncountyfltourism.com/walton-county-line/new-pedestrian-and-bike-rest-area-enhances-scenic-highway-30a/",
            "label": "Walton County Line",
        },
        {
            "href": "https://www.wjhg.com/2024/05/21/new-rest-area-pedestrians-cyclists-open-30a/",
            "label": "WJHG/WECP, May 21, 2024",
        },
    ],
}


def render_friends_corner(feature):
    amenities = "".join(f"<li>{esc(item)}</li>" for item in feature["amenities"])
    sources = " ".join(render_project_links(feature["sources"], "Friends’ Corner source"))
    return f"""
        <article class="corner-feature">
          <figure>
            <img src="{esc(feature["image"])}" alt="{esc(feature["image_alt"])}">
            <figcaption>{esc(feature["photo_credit"])}</figcaption>
          </figure>
          <div class="card-body">
            <p class="accomplish-year">{esc(feature["completed"])}</p>
            <h3>{esc(feature["name"])}</h3>
            <p>{esc(feature["summary"])}</p>
            <p class="card-label">Completed amenities</p>
            <ul class="priority-list">{amenities}</ul>
            <p><strong>Funding and partners.</strong> {esc(feature["funding"])}</p>
            <p class="card-source"><strong>Sources.</strong> {sources}</p>
          </div>
        </article>
    """


def render_accomplishments(items):
    cards = []
    for item in items:
        if not item.get("name") or not item.get("role") or not item.get("result"):
            raise SystemExit("an accomplishment needs a name, role, and result")
        year = f'<p class="accomplish-year">{esc(item["year"])}</p>' if item.get("year") else ""
        photo = ""
        classes = "accomplish-card"
        if item.get("image"):
            alt = item.get("image_alt")
            if not alt:
                raise SystemExit(f"accomplishment image needs alt text: {item['name']}")
            classes += " has-photo"
            photo = f'<figure><img src="{esc(item["image"])}" alt="{esc(alt)}"></figure>'
        cards.append(
            f'<li class="{classes}">{photo}<div class="card-body">{year}'
            f"<h3>{esc(item['name'])}</h3>"
            f"<p><strong>Friends' role.</strong> {esc(item['role'])}</p>"
            f"<p><strong>Result.</strong> {esc(item['result'])}</p>"
            f"</div></li>\n"
        )
    return f'<ol class="accomplish-list">\n{"".join(cards)}</ol>'


def our_work():
    projects_html = render_current_projects(CURRENT_PROJECTS)
    corner_html = render_friends_corner(FRIENDS_CORNER)
    accomplishments_html = render_accomplishments(ACCOMPLISHMENTS)
    body = f"""
    <header class="page-hero" style="--hero:url('/images/gallery/03-dune-lake-pines.jpg')">
      <div class="wrap">
        <p class="eyebrow">Our work</p>
        <h1>Our Work Along Scenic 30A</h1>
        <p>From protecting the natural character of Scenic 30A to improving safety, trails, signage, landscaping, and public spaces, Friends of Scenic 30A works on projects that help preserve and enhance the corridor for the future.</p>
        <nav class="jump-links" aria-label="On this page">
          <a href="#current-projects">Current Projects</a>
          <a href="#our-priorities">Our Priorities</a>
          <a href="#past-accomplishments">Past Accomplishments</a>
        </nav>
      </div>
    </header>
    <section class="section section-white" id="current-projects">
      <div class="wrap">
        <h2>Current Projects &amp; Initiatives</h2>
        <p class="lede">What Friends is actively working on today appears here as individual project cards.</p>
        {projects_html}
      </div>
    </section>
    <section class="section section-sand" id="our-priorities">
      <div class="wrap">
        <h2>Our Ongoing Priorities</h2>
        <p class="lede">Four areas guide the work along Scenic Highway 30A.</p>
        <div class="priority-grid">
          <article class="priority-card">
            <h3>Protecting Our Natural Landscape</h3>
            <p>These places give Scenic 30A its natural character.</p>
            <ul class="priority-list">
              <li>Coastal dune lakes, dunes, and beaches</li>
              <li>Native vegetation, forests, and wildlife habitat</li>
              <li>Heritage trees</li>
            </ul>
          </article>
          <article class="priority-card">
            <h3>Safer Walking, Biking &amp; Connectivity</h3>
            <p>People walk and bike the corridor as well as drive it.</p>
            <ul class="priority-list">
              <li>Timpoochee Trail safety and maintenance</li>
              <li>Crossings, bicycle facilities, and bike racks</li>
              <li>Trail connections and transportation planning</li>
            </ul>
          </article>
          <article class="priority-card">
            <h3>Keeping Scenic 30A Scenic</h3>
            <p>The roadside should match the character of a scenic highway.</p>
            <ul class="priority-list">
              <li>Landscaping and roadside character</li>
              <li>Wayfinding, signage, and gateways</li>
              <li>Public amenities and screened infrastructure</li>
            </ul>
          </article>
          <article class="priority-card">
            <h3>Education &amp; Community Stewardship</h3>
            <p>Understanding the corridor helps people care for it over time.</p>
            <ul class="priority-list">
              <li>History, the natural environment, and scenic designation</li>
              <li>Safety education for people walking, biking, and driving</li>
              <li>Long-term stewardship with community partners</li>
            </ul>
          </article>
        </div>
      </div>
    </section>
    <section class="section section-white" id="past-accomplishments">
      <div class="wrap">
        <h2>Past Projects &amp; Accomplishments</h2>
        <p class="lede">Specific results recorded for Scenic 30A. A year is shown when a source states one.</p>
        {corner_html}
        {accomplishments_html}
      </div>
    </section>
    <section class="section section-foam">
      <div class="wrap prose">
        <h2>Help Protect Scenic 30A</h2>
        <p>Friends of Scenic 30A is powered by people who care about this extraordinary place. Join us in protecting and enhancing the corridor for generations to come.</p>
        <p class="button-row"><a class="btn btn-gulf" href="/membership/">Become a Member</a> <a class="btn btn-line" href="{DONATE}" target="_blank" rel="noopener noreferrer">Donate</a></p>
      </div>
    </section>
    """
    write_page(
        "/our-work/",
        "Our Work Along Scenic Highway 30A",
        "Current projects, ongoing priorities, and completed work of Friends of Scenic 30A along Scenic Highway 30A in South Walton.",
        body,
        "/images/gallery/03-dune-lake-pines.jpg",
        crumbs=[("Home", "/"), ("Our Work", "/our-work/")],
    )


IMPACT_REDIRECT_TARGET = "/our-work/#past-accomplishments"
IMPACT_REDIRECT_DOC = f"""<!DOCTYPE html>
<html lang="en">
<head>
{GA_SNIPPET}  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Past accomplishments | Friends of Scenic 30A</title>
  <meta name="description" content="Past accomplishments of Friends of Scenic 30A now live on the Our Work page.">
  <link rel="canonical" href="{ORIGIN}/our-work/">
  <meta name="robots" content="noindex">
  <meta http-equiv="refresh" content="0; url={IMPACT_REDIRECT_TARGET}">
  <link rel="icon" href="/favicon.png" type="image/png">
  <script>location.replace("{IMPACT_REDIRECT_TARGET}");</script>
</head>
<body>
  <p><a href="{IMPACT_REDIRECT_TARGET}">Past accomplishments on Our Work</a></p>
</body>
</html>
"""


SHOP_REDIRECT_DOC = f"""<!DOCTYPE html>
<html lang="en">
<head>
{GA_SNIPPET}  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Shop | Friends of Scenic 30A</title>
  <meta name="description" content="Find Friends of Scenic 30A merchandise in the official shop.">
  <link rel="canonical" href="{SHOP_STOREFRONT}">
  <meta name="robots" content="noindex">
  <meta http-equiv="refresh" content="0; url={SHOP_STOREFRONT}">
  <link rel="icon" href="/favicon.png" type="image/png">
  <script>location.replace("{SHOP_STOREFRONT}");</script>
</head>
<body>
  <p><a href="{SHOP_STOREFRONT}">Shop</a></p>
</body>
</html>
"""


GET_INVOLVED_REDIRECT_TARGET = "/membership/"
GET_INVOLVED_REDIRECT_DOC = f"""<!DOCTYPE html>
<html lang="en">
<head>
{GA_SNIPPET}  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Membership | Friends of Scenic 30A</title>
  <meta name="description" content="Membership, volunteering, and updates for Friends of Scenic 30A now live on the Membership page.">
  <link rel="canonical" href="{ORIGIN}/membership/">
  <meta name="robots" content="noindex">
  <meta http-equiv="refresh" content="0; url={GET_INVOLVED_REDIRECT_TARGET}">
  <link rel="icon" href="/favicon.png" type="image/png">
  <script>location.replace("{GET_INVOLVED_REDIRECT_TARGET}");</script>
</head>
<body>
  <p><a href="{GET_INVOLVED_REDIRECT_TARGET}">Membership</a></p>
</body>
</html>
"""


def write_impact_redirect():
    (ROOT / "impact").mkdir(parents=True, exist_ok=True)
    (ROOT / "impact" / "index.html").write_text(IMPACT_REDIRECT_DOC)
    (ROOT / "impact.html").write_text(IMPACT_REDIRECT_DOC)
    (ROOT / "shop").mkdir(parents=True, exist_ok=True)
    (ROOT / "shop" / "index.html").write_text(SHOP_REDIRECT_DOC)
    (ROOT / "_redirects").write_text(
        "/impact /our-work/#past-accomplishments 301\n"
        "/impact/ /our-work/#past-accomplishments 301\n"
        "/impact/index.html /our-work/#past-accomplishments 301\n"
        "/impact.html /our-work/#past-accomplishments 301\n"
        "/shop https://shop.friendsofscenic30a.org/ 301\n"
        "/shop/ https://shop.friendsofscenic30a.org/ 301\n"
        "/shop/index.html https://shop.friendsofscenic30a.org/ 301\n"
        "/get-involved /membership/ 301\n"
        "/get-involved/ /membership/ 301\n"
        "/get-involved/index.html /membership/ 301\n"
    )
    (ROOT / "get-involved").mkdir(parents=True, exist_ok=True)
    (ROOT / "get-involved" / "index.html").write_text(GET_INVOLVED_REDIRECT_DOC)
    print("/impact/ -> /our-work/#past-accomplishments")
    print("/shop/ -> https://shop.friendsofscenic30a.org/")
    print("/get-involved/ -> /membership/")


def gallery():
    figures = "\n".join(
        f'<button type="button" data-full="{src}" data-alt="{esc(alt)}"><img src="{src}" alt="{esc(alt)}"></button>'
        for src, alt in GALLERY
    )
    body = page_hero(
        "Gallery",
        "Scenic 30A Gallery",
        "Explore the untouched beauty and coastal charm of Florida's Scenic Highway 30A through our lens.",
        "/images/gallery/08-gulf-sunset.jpg",
    ) + f"""
    <section class="section section-sand">
      <div class="wrap">
        <div class="gallery">{figures}</div>
        <dialog class="lightbox" id="lightbox">
          <form method="dialog"><button type="submit">Close</button></form>
          <img alt="">
        </dialog>
        <div class="prose">
          <h2>Protect What You See</h2>
          <p>Friends of Scenic 30A helps protect the natural beauty and coastal ecosystems you've just explored. Join us in preserving this extraordinary corridor for generations to come.</p>
          <p class="button-row"><a class="btn btn-gulf" href="/membership/">Become a Member</a> <a class="btn btn-line" href="/contact/#contact-form">Support our work</a></p>
        </div>
      </div>
    </section>
    """
    write_page(
        "/gallery/",
        "Scenic 30A Photo Gallery",
        "Photographs of beaches, coastal dune lakes, the Timpoochee Trail, and beach communities along Scenic Highway 30A in South Walton.",
        body,
        "/images/gallery/08-gulf-sunset.jpg",
        kind="ImageGallery",
        crumbs=[("Home", "/"), ("Gallery", "/gallery/")],
        media=[
            {
                "@type": "ImageObject",
                "contentUrl": ORIGIN + src,
                "caption": alt,
            }
            for src, alt in GALLERY
        ],
    )


def membership_price_grid():
    return f"""        <div class="price-grid">
          <article class="price">
            <h3>Individual</h3>
            <strong>$25 / year</strong>
            <p>Ideal for residents and frequent visitors who want to protect, preserve, and enhance the special character of Scenic 30A for generations to come.</p>
            <a class="btn btn-gulf" href="{MEMBER_INDIVIDUAL}" target="_blank" rel="noopener noreferrer">Join as Individual</a>
          </article>
          <article class="price">
            <h3>Business</h3>
            <strong>$100 / year</strong>
            <p>Ideal for local businesses that want to support the preservation, enhancement, and long-term future of Scenic 30A and the community it serves.</p>
            <a class="btn btn-line" href="{MEMBER_BUSINESS}" target="_blank" rel="noopener noreferrer">Join as Business</a>
          </article>
          <article class="price">
            <h3>Corporate</h3>
            <strong>$1,000 / year</strong>
            <p>Ideal for companies that want to support the preservation, enhancement, and long-term future of Scenic 30A and the community it serves.</p>
            <a class="btn btn-line" href="{MEMBER_CORPORATE}" target="_blank" rel="noopener noreferrer">Join as Corporate</a>
          </article>
        </div>"""


def how_projects_get_funded():
    body = page_hero(
        "Funding",
        "How Projects Get Funded",
        "Improving and protecting Scenic Highway 30A takes more than good ideas. It takes community involvement, partnerships, and the right funding sources.",
        "/images/gallery/06-aerial-gulf-and-lake.jpg",
    ) + f"""
    <section class="section section-white">
      <div class="wrap feature-row">
        <div class="prose">
          <p>Friends of Scenic 30A works to identify projects that can improve, preserve, or enhance the Scenic 30A corridor. Depending on the size and type of the project, funding may come from several different sources.</p>
          <p>Friends of Scenic 30A is led by a 100% volunteer board. We have no paid staff and no administrative or operating expenses, allowing our efforts to remain focused on projects and initiatives that benefit Scenic Highway 30A and the surrounding community.</p>
        </div>
        <figure class="feature-photo"><img src="/images/gallery/11-gulf-path.jpg" alt="Path beside the Gulf with sea oats and pines"></figure>
      </div>
    </section>
    <section class="section section-sand">
      <div class="wrap">
        <div class="feature-row">
          <div>
            <h2>Community Donations</h2>
            <p>Individuals and businesses can help support Friends of Scenic 30A and the projects we pursue. Smaller improvements may be funded directly through donations, while larger projects may use community contributions to help with planning, design, matching funds, or other project-related expenses.</p>
            <p>We believe in transparency and want donors to understand how funds are being used and what they are helping accomplish.</p>
          </div>
          <figure class="feature-photo"><img src="/images/blog/native-landscape.jpg" alt="Boardwalk through sea oats toward the Gulf of Mexico"></figure>
        </div>
        <div class="funding-grid">
          <article class="funding-card">
            <img src="/images/gallery/03-dune-lake-pines.jpg" alt="Coastal dune lake edged by pines">
            <div>
              <h2>Grants</h2>
              <p>Many community, environmental, beautification, transportation, and preservation projects may qualify for grants from foundations, government agencies, and other organizations.</p>
              <p>Friends of Scenic 30A can help identify grant opportunities and work with community partners to pursue funding for projects along the corridor.</p>
            </div>
          </article>
          <article class="funding-card">
            <img src="/images/gallery/07-timpoochee-riders.jpg" alt="People riding the paved Timpoochee Trail">
            <div>
              <h2>Walton County and TDC Partnerships</h2>
              <p>Many improvements along Scenic 30A involve public property, transportation infrastructure, landscaping, pedestrian facilities, or other community assets.</p>
              <p>For these projects, Friends of Scenic 30A can work with Walton County, the Walton County Tourism Department, and other public agencies to advocate for projects and help identify potential funding.</p>
            </div>
          </article>
          <article class="funding-card">
            <img src="/images/gallery/09-aerial-lake-beach.jpg" alt="Aerial view of beach, dunes, and a coastal dune lake">
            <div>
              <h2>State and Federal Funding</h2>
              <p>Larger transportation, environmental, safety, and infrastructure projects may qualify for state or federal funding.</p>
              <p>Friends of Scenic 30A can help bring attention to these opportunities and work with local officials and community partners to move worthy projects forward.</p>
            </div>
          </article>
          <article class="funding-card">
            <img src="/images/gallery/13-palm-path.jpg" alt="Palm-lined path in a 30A beach community">
            <div>
              <h2>Business and Community Partnerships</h2>
              <p>Local businesses, property owners, civic organizations, homeowners associations, and other community groups can also play an important role.</p>
              <p>A project might include private sponsorships, donated materials or services, volunteer participation, or partnerships between several organizations.</p>
            </div>
          </article>
        </div>
      </div>
    </section>
    <section class="section section-white">
      <div class="wrap feature-row">
        <figure class="feature-photo"><img src="/images/gallery/04-boardwalk-beach.jpg" alt="Beach boardwalk opening onto the Gulf"></figure>
        <div>
          <h2>A Project-by-Project Approach</h2>
          <p>There is no single funding source for every project.</p>
          <p>A small landscaping project may be funded by community donations and local sponsors. A pedestrian improvement could involve Walton County or the Tourism Department. An environmental project might qualify for a grant. A major infrastructure improvement could involve county, state, and federal funding.</p>
          <p>Our role is to help bring the right people, organizations, and funding sources together, while keeping Friends of Scenic 30A volunteer-driven and focused on improving and preserving the Scenic 30A corridor.</p>
        </div>
      </div>
    </section>
    <section class="section section-foam">
      <div class="wrap">
        <h2>Become a Member</h2>
{membership_price_grid()}
      </div>
    </section>
    """
    write_page(
        "/how-projects-get-funded/",
        "How Projects Get Funded",
        "How Friends of Scenic 30A funds corridor projects with donations, grants, Walton County partnerships, and state or federal sources.",
        body,
        "/images/gallery/06-aerial-gulf-and-lake.jpg",
        crumbs=[("Home", "/"), ("How Projects Get Funded", "/how-projects-get-funded/")],
    )


def membership():
    body = page_hero(
        "Membership",
        "Become a Friend of Scenic 30A",
        "Membership supports Friends of Scenic 30A's work as the designated Byway Organization for Scenic Highway 30A.",
        "/images/gallery/14-dune-sea-oats.jpg",
    ) + f"""
    <section class="section section-white">
      <div class="wrap prose">
        <p class="lede">Your support helps advance preservation, transportation and trail safety, community education, beautification, advocacy and other initiatives that protect and enhance the corridor.</p>
        <h2>Why Membership Matters</h2>
        <h3>Help Protect What Makes 30A Special</h3>
        <p>Scenic Highway 30A is more than just a road; it is a collection of rare coastal dune lakes, sugar-white sand beaches, and historic communities that define our way of life. By becoming a member, you provide the vital resources needed to advocate for thoughtful planning and development, environmental stewardship, and the preservation of our scenic vistas.</p>
      </div>
    </section>
    <section class="section section-sand">
      <div class="wrap">
        <h2>Together, We’re Working for the Future of Scenic 30A</h2>
        <div class="pillars">
          <article class="pillar"><h3>Conservation Efforts</h3><p>Protecting our rare coastal dune lakes and preserving natural wildlife habitats.</p></article>
          <article class="pillar"><h3>Community Advocacy</h3><p>Working with local leaders to ensure development respects the character of 30A.</p></article>
          <article class="pillar"><h3>Trail Enhancements</h3><p>Maintaining and improving the Timpoochee Trail for safe walking and cycling.</p></article>
          <article class="pillar"><h3>Scenic Vistas</h3><p>Protecting the iconic views and architectural heritage of our beautiful corridor.</p></article>
        </div>
        """ + photos([
            ("/images/blog/trails.jpg", "Trail through the Scenic 30A corridor"),
            ("/images/blog/vision.jpg", "Boardwalk and dunes along Scenic 30A"),
            ("/images/gallery/07-timpoochee-riders.jpg", "People riding the paved Timpoochee Trail"),
        ]) + f"""
      </div>
    </section>
    <section class="section section-foam">
      <div class="wrap">
        <h2>Step 1. Pay through Square</h2>
        <p class="lede">Choose Individual, Business, or Corporate and complete payment on Square. Membership is not finished until you also send your details in step 2.</p>
{membership_price_grid()}
      </div>
    </section>
    <section class="section section-white">
      <div class="wrap prose">
        <h2>Make an Additional Contribution</h2>
        <p>Your additional contributions fund specific preservation projects and educational programs that membership alone cannot cover. Every dollar goes directly toward defending the 30A we all love.</p>
        <p><a class="btn btn-gulf" href="{DONATE}" target="_blank" rel="noopener noreferrer">Donate to Friends of Scenic 30A</a></p>
      </div>
    </section>
    <section class="section section-sand">
      <div class="wrap">
        <h2>Step 2. Submit your member details</h2>
        <p class="lede">After you pay on Square, send your details here so Friends of Scenic 30A can confirm your membership and keep you informed. This form does not collect payment.</p>
        <p class="quote">What We Protect Today Becomes the 30A of Tomorrow.</p>
        <form class="form" data-form="membership">
          <div class="split">
            <label>First name *<input name="first" required autocomplete="given-name"></label>
            <label>Last name *<input name="last" required autocomplete="family-name"></label>
          </div>
          <label>Email *<input type="email" name="email" required autocomplete="email"></label>
          <label>Phone<input type="tel" name="phone" autocomplete="tel"></label>
          <label>Mailing address *<input name="address" required autocomplete="street-address"></label>
          <div class="split">
            <label>City *<input name="city" required autocomplete="address-level2"></label>
            <label>State *<input name="state" required autocomplete="address-level1"></label>
            <label>ZIP *<input name="zip" required autocomplete="postal-code"></label>
          </div>
          <label>Membership type *
            <select name="membership" required>
              <option value="">Select</option>
              <option>Individual Membership – $25/year</option>
              <option>Business Membership – $100/year</option>
              <option>Corporate Membership – $1,000/year</option>
            </select>
          </label>
          <label class="hp">Company<input name="company" tabindex="-1" autocomplete="off"></label>
          <button class="btn btn-gulf" type="submit">Submit Membership Details</button>
          <p class="form-status" role="status"></p>
        </form>
      </div>
    </section>
    <section class="section section-white" id="volunteer">
      <div class="wrap">
        <h2>There’s a Place for You in Our Mission</h2>
        <p class="lede">Friends of Scenic 30A is a volunteer-driven community organization. Whether you live here, own a business, visit regularly, or simply love 30A, your involvement helps strengthen our voice and support our work.</p>
        <p id="stay-informed">To contact Friends, volunteer, or get updates, use the <a href="/contact/#contact-form">contact form</a>.</p>
        <div class="prose">
          <h2>Shop</h2>
          <p>Find Friends of Scenic 30A merchandise in the official shop.</p>
          <p><a class="btn btn-line" href="{SHOP_STOREFRONT}" target="_blank" rel="noopener noreferrer">Shop</a></p>
        </div>
      </div>
    </section>
    """
    write_page(
        "/membership/",
        "Scenic 30A Membership",
        MEMBERSHIP_DESCRIPTION,
        body,
        "/images/gallery/14-dune-sea-oats.jpg",
        crumbs=[("Home", "/"), ("Membership", "/membership/")],
    )


def contact():
    body = page_hero(
        "Contact",
        "Say Hello",
        "Questions, ideas, and partnership notes are welcome. You can also volunteer or get updates. Friends of Scenic 30A reads every message.",
        "/images/gallery/10-sandy-scrub-path.jpg",
    ) + """
    <section class="section section-sand">
      <div class="wrap split">
        <form class="form" id="contact-form" data-form="contact">
          <fieldset class="checks">
            <legend>Choose any that apply</legend>
            <label><input type="checkbox" name="requests" value="Contact Friends"> Contact Friends</label>
            <label><input type="checkbox" name="requests" value="Volunteer"> Volunteer</label>
            <label><input type="checkbox" name="requests" value="Get updates"> Get updates</label>
          </fieldset>
          <div class="split">
            <label>First name *<input name="first" required autocomplete="given-name"></label>
            <label>Last name *<input name="last" required autocomplete="family-name"></label>
          </div>
          <label>Email *<input type="email" name="email" required autocomplete="email"></label>
          <label>Phone<input type="tel" name="phone" autocomplete="tel"></label>
          <label>Message *<textarea name="message" required></textarea></label>
          <label class="hp">Company<input name="company" tabindex="-1" autocomplete="off"></label>
          <button class="btn btn-gulf" type="submit">Submit</button>
          <p class="form-status" role="status"></p>
        </form>
        <div class="prose">
          <h2>Friends of Scenic 30A</h2>
          <p><a href="https://www.google.com/maps/search/?api=1&query=877+N+County+Hwy+393,+Santa+Rosa+Beach,+FL+32459">877 N County Hwy 393<br>Santa Rosa Beach, FL 32459</a></p>
          <p><a href="#contact-form">Get involved</a> or <a href="/membership/">become a member</a>.</p>
        </div>
      </div>
    </section>
    """
    write_page(
        "/contact/",
        "Contact Friends of Scenic 30A",
        "Contact Friends of Scenic 30A, volunteer, or get updates from one form. The office is at 877 N County Hwy 393, Santa Rosa Beach, FL 32459.",
        body,
        "/images/gallery/10-sandy-scrub-path.jpg",
        kind="ContactPage",
        crumbs=[("Home", "/"), ("Contact", "/contact/")],
    )


def privacy():
    body = page_hero("Privacy", "Privacy Policy", "A legal disclaimer. Last updated September 3, 2026.") + """
    <section class="section section-sand"><div class="wrap prose">
      <p>Friends of Scenic 30A respects your privacy and is committed to protecting the personal information you share with us. This Privacy Policy explains how information may be collected, used, and protected when you visit our website, contact us, become a member, volunteer, make a donation, or otherwise interact with Friends of Scenic 30A.</p>
      <h2>Information We Collect</h2>
      <p>We may collect personal information that you voluntarily provide to us, including your name, email address, mailing address, telephone number, membership information, volunteer interests, and other information you choose to provide through forms on our website.</p>
      <p>When you make a donation, membership payment, or other online payment, payment information is collected and processed by Square or another third-party payment processor. Friends of Scenic 30A does not necessarily receive or store your complete credit or debit card information.</p>
      <p>Our website may also automatically collect certain technical information, such as your IP address, browser type, device information, pages visited, and general website usage information through cookies and similar technologies.</p>
      <h2>How We Use Your Information</h2>
      <p>We may use information collected through this website to:</p>
      <ul>
        <li>Process donations and membership requests;</li>
        <li>Respond to questions and messages;</li>
        <li>Communicate with members, volunteers, donors, and supporters;</li>
        <li>Provide news, project updates, event information, and other communications you have requested;</li>
        <li>Coordinate volunteer activities and community initiatives;</li>
        <li>Improve our website and understand how visitors use it;</li>
        <li>Maintain appropriate organizational and financial records; and</li>
        <li>Comply with applicable legal and regulatory requirements.</li>
      </ul>
      <h2>Email Communications</h2>
      <p>If you subscribe to our email list or otherwise request updates, we may send you information about Friends of Scenic 30A, including news, projects, events, volunteer opportunities, and ways to support our mission.</p>
      <p>You may unsubscribe from marketing or informational emails at any time by using the unsubscribe link included in those communications.</p>
      <h2>Donations and Payments</h2>
      <p>Online donations, membership payments, and other transactions are processed through Square and may be processed through other third-party payment providers. Those providers may collect and process information according to their own privacy policies and terms.</p>
      <p>We encourage you to review the privacy policies of any payment provider used when completing a transaction.</p>
      <h2>Cookies and Website Technology</h2>
      <p>Our website may use cookies and similar technologies that help the website function properly, understand website traffic, remember visitor preferences, and improve the user experience.</p>
      <p>Visitors may be able to control or disable certain cookies through their browser settings.</p>
      <h2>Sharing of Information</h2>
      <p>Friends of Scenic 30A does not sell or rent your personal information.</p>
      <p>We may share information with trusted service providers when reasonably necessary to operate our website, process payments, send communications, maintain records, or provide other services on our behalf.</p>
      <p>We may also disclose information when required by law or when reasonably necessary to protect the rights, safety, or property of Friends of Scenic 30A or others.</p>
      <h2>Third-Party Websites</h2>
      <p>Our website may contain links to third-party websites, social media platforms, government resources, or other organizations. Friends of Scenic 30A is not responsible for the privacy practices or content of websites operated by third parties.</p>
      <h2>Data Security</h2>
      <p>We take reasonable steps to protect personal information provided to us. However, no website, electronic transmission, or data storage system can be guaranteed to be completely secure.</p>
      <h2>Children's Privacy</h2>
      <p>This website is intended for a general audience and is not designed to knowingly collect personal information from children under 13.</p>
      <h2>Your Privacy Choices</h2>
      <p>You may contact us to request that we update or correct personal information you have provided to us or to ask questions about how your information is used.</p>
      <p>You may also unsubscribe from email communications at any time.</p>
      <h2>Changes to This Privacy Policy</h2>
      <p>Friends of Scenic 30A may update this Privacy Policy periodically to reflect changes to our website, services, or legal requirements. The date at the top of this page will indicate when the policy was most recently updated.</p>
      <h2>Contact Us</h2>
      <p>If you have questions about this Privacy Policy or our privacy practices, please contact us through the <a href="/contact/">Contact Us</a> form on this website or by mail:</p>
      <p>Friends of Scenic 30A<br>P.O. Box 1931<br>Santa Rosa Beach, FL 32459</p>
    </div></section>
    """
    write_page(
        "/privacy-policy/",
        "Privacy Policy",
        "How Friends of Scenic 30A collects, uses, and protects personal information shared on this website, through membership, volunteering, and donations.",
        body,
        crumbs=[("Home", "/"), ("Privacy Policy", "/privacy-policy/")],
    )


def accessibility():
    body = page_hero("Accessibility", "Accessibility Statement", "This statement was last updated on September 29, 2026.") + """
    <section class="section section-sand"><div class="wrap prose">
      <p>We at Friends of Scenic 30A are working to make our site accessible to people with disabilities.</p>
      <h2>What web accessibility is</h2>
      <p>An accessible site allows visitors with disabilities to browse the site with the same or a similar level of ease and enjoyment as other visitors. This can be achieved with the capabilities of the system on which the site is operating, and through assistive technologies.</p>
      <h2>Accessibility on this site</h2>
      <p>This site is built to conform with the Web Content Accessibility Guidelines (WCAG) 2.2 at Level AA. Pages use the site language, a skip link, keyboard-reachable controls, visible focus, and a single main heading structure. Photographs include alternative text. Color combinations are chosen for contrast. Motion is limited, and animations are reduced when a visitor asks their device to do so.</p>
      <h2>Requests, issues, and suggestions</h2>
      <p>If you find an accessibility issue on the site, or if you require further assistance, contact Friends of Scenic 30A through the <a href="/contact/">contact form</a> or by mail at 877 N County Hwy 393, Santa Rosa Beach, FL 32459.</p>
    </div></section>
    """
    write_page(
        "/accessibility/",
        "Accessibility Statement",
        "Friends of Scenic 30A is working to make this website accessible to people with disabilities, with a goal of WCAG 2.2 Level AA.",
        body,
        crumbs=[("Home", "/"), ("Accessibility", "/accessibility/")],
    )


def terms():
    body = page_hero("Terms", "Terms & Conditions", "How this website may be used.") + """
    <section class="section section-sand"><div class="wrap prose">
      <p>This website is published by Friends of Scenic 30A to share information about Scenic Highway 30A and the organization’s preservation, education, and community work. By using the site you agree to these terms.</p>
      <h2>Information on this site</h2>
      <p>Articles, photographs, and project descriptions are provided for general information. They are not legal, engineering, or professional advice. Scenic corridor conditions, park rules, and public projects can change.</p>
      <h2>Membership and donations</h2>
      <p>Individual membership, business membership, corporate membership, and donations are completed on Square payment pages linked from this site. Those payments are governed by Square’s terms and by the membership description on this website. Submitting the membership details form tells Friends of Scenic 30A how to confirm and record a membership. It does not, by itself, collect payment.</p>
      <h2>Your messages</h2>
      <p>Do not send sensitive payment card numbers through the forms on this site. Messages you submit may be retained so the organization can respond and keep membership or volunteer records.</p>
      <h2>Content and links</h2>
      <p>Unless a page says otherwise, the text and photographs on this site belong to Friends of Scenic 30A. You may share links to these pages. Please ask before reusing photographs or long excerpts. Links to other organizations are provided for convenience. Friends of Scenic 30A is not responsible for those sites.</p>
      <h2>Contact</h2>
      <p>Questions about these terms can be sent through the <a href="/contact/">contact form</a> or by mail to Friends of Scenic 30A, 877 N County Hwy 393, Santa Rosa Beach, FL 32459.</p>
    </div></section>
    """
    write_page(
        "/terms/",
        "Terms & Conditions",
        "Terms for using the Friends of Scenic 30A website, including Square membership payments, donations, messages, and how site content may be shared.",
        body,
        crumbs=[("Home", "/"), ("Terms", "/terms/")],
    )


POSTS = [
    {
        "slug": "protecting-the-natural-character-of-scenic-30a",
        "title": "Protecting the Natural Character of Scenic 30A",
        "date": "2026-09-12",
        "display": "September 12, 2026",
        "minutes": "3 min read",
        "image": "/images/blog/native-landscape.jpg",
        "image_alt": "Boardwalk through sea oats toward the Gulf of Mexico",
        "seo_title": "Natural Character of Scenic 30A",
        "excerpt": "The natural landscape surrounding Scenic Highway 30A is one of the defining features of the corridor.",
        "description": "The natural landscape around Scenic Highway 30A, from dune lakes and dunes to native vegetation, defines the corridor Friends works to protect.",
        "file": "protecting-the-natural-character-of-scenic-30a.txt",
    },
    {
        "slug": "transportation-has-always-been-part-of-friends-of-scenic-30a-s-mission",
        "title": "Transportation Has Always Been Part of Friends of Scenic 30A's Mission",
        "date": "2026-09-12",
        "display": "September 12, 2026",
        "minutes": "2 min read",
        "image": "/images/blog/corridor-beach.jpg",
        "image_alt": "Gulf shoreline and sea oats along Scenic Highway 30A",
        "seo_title": "Transportation on Scenic Highway 30A",
        "excerpt": "Scenic 30A is both a treasured scenic corridor and a working transportation network.",
        "description": "Scenic Highway 30A is a treasured scenic corridor and a working transportation network. Friends of Scenic 30A has treated both as part of its mission.",
        "file": "transportation-has-always-been-part-of-friends-of-scenic-30a-s-mission.txt",
    },
    {
        "slug": "what-makes-scenic-30a-special",
        "title": "What Makes Scenic 30A Special?",
        "date": "2026-09-12",
        "display": "September 12, 2026",
        "minutes": "2 min read",
        "image": "/images/hero.jpg",
        "image_alt": "Beach boardwalk opening onto the Gulf",
        "excerpt": "Scenic Highway 30A is a corridor shaped by natural beauty, communities, state lands, trails, and coastal dune lakes.",
        "description": "Scenic Highway 30A is shaped by natural beauty, beach communities, state lands, trails, and rare coastal dune lakes in Walton County, Florida.",
        "file": "what-makes-scenic-30a-special.txt",
    },
    {
        "slug": "30a-in-360-degrees",
        "title": "30A in 360 Degrees",
        "date": "2026-09-05",
        "display": "September 5, 2026",
        "minutes": "1 min read",
        "image": "/images/gallery/06-aerial-gulf-and-lake.jpg",
        "image_alt": "Aerial view of the Gulf, beach, and a dune lake beside 30A",
        "excerpt": "Check out this 360° drive down 30A and explore the scenery in every direction.",
        "description": "Take a 360-degree drive along Scenic Highway 30A and see the beaches, dune lakes, and beach communities in every direction.",
        "file": "30a-in-360-degrees.txt",
        "video": "https://www.youtube-nocookie.com/embed/55EsjB_V_L8",
    },
    {
        "slug": "the-communities-of-scenic-30a",
        "title": "The Communities of Scenic 30A",
        "date": "2026-09-03",
        "display": "September 3, 2026",
        "minutes": "7 min read",
        "image": "/images/blog/communities.jpg",
        "image_alt": "Palm-lined path in a Scenic 30A beach community",
        "excerpt": "The Scenic 30-A corridor includes 12 distinct beach communities, each with its own history and character.",
        "description": "Scenic Highway 30A includes twelve distinct beach communities in South Walton, each with its own history, character, and sense of place.",
        "file": "the-communities-of-scenic-30a.txt",
    },
    {
        "slug": "history-heritage-of-scenic-30a",
        "title": "History & Heritage of Scenic 30A",
        "date": "2026-09-03",
        "display": "September 3, 2026",
        "minutes": "6 min read",
        "image": "/images/blog/heritage.jpg",
        "image_alt": "Sandy path through coastal scrub and pines",
        "excerpt": "From Grayton Beach cottages to Point Washington’s logging settlement, the corridor has a long story.",
        "description": "From Grayton Beach cottages to Point Washington's logging settlement, the history and heritage of Scenic Highway 30A still shape the corridor.",
        "file": "history-heritage-of-scenic-30a.txt",
    },
    {
        "slug": "explore-scenic-30a",
        "title": "Explore Scenic 30A",
        "date": "2026-09-03",
        "display": "September 3, 2026",
        "minutes": "6 min read",
        "image": "/images/blog/dunes.jpg",
        "image_alt": "Sea oats and a wooden boardwalk on the dunes",
        "excerpt": "Beaches, state parks, trails, and coastal dune lakes give everyone a way to experience Scenic 30-A.",
        "description": "Beaches, state parks, the Timpoochee Trail, and coastal dune lakes give residents and visitors a way to experience Scenic Highway 30A.",
        "file": "explore-scenic-30a.txt",
    },
    {
        "slug": "the-story-of-30a",
        "title": "The Story of 30A",
        "date": "2026-09-03",
        "display": "September 3, 2026",
        "minutes": "2 min read",
        "image": "/images/blog/story.jpg",
        "image_alt": "Beach path through sea oats and dunes toward the Gulf",
        "seo_title": "The Story of Scenic Highway 30A",
        "excerpt": "Twelve beach communities grew from summer cottages into the corridor Friends of Scenic 30A works to protect.",
        "description": "Twelve beach communities grew from summer cottages into the Scenic Highway 30A corridor that Friends of Scenic 30A works to protect.",
        "file": "the-story-of-30a.txt",
    },
    {
        "slug": "vision",
        "title": "A Vision for Scenic 30A",
        "date": "2026-09-03",
        "display": "September 3, 2026",
        "minutes": "3 min read",
        "image": "/images/blog/vision.jpg",
        "image_alt": "Boardwalk through sea oats opening onto the Gulf",
        "excerpt": "A picture of the two-lane scenic drive, the Timpoochee Trail, and the landscapes the Friends set out to protect.",
        "description": "A vision for Scenic Highway 30A's two-lane drive, the Timpoochee Trail, and the landscapes Friends of Scenic 30A set out to protect.",
        "file": "vision.txt",
    },
]


def blog():
    cards = []
    blog_posts = []
    for post in POSTS:
        cards.append(
            f"""<a class="post-card" href="/blog/{post['slug']}/">
              <img src="{post['image']}" alt="{esc(post['image_alt'])}">
              <div>
                <time datetime="{post['date']}">{post['display']}</time>
                <span class="meta"> · {post['minutes']}</span>
                <h2>{esc(post['title'])}</h2>
                <p>{esc(post['excerpt'])}</p>
              </div>
            </a>"""
        )
        blog_posts.append({
            "@type": "BlogPosting",
            "headline": post["title"],
            "url": f"{ORIGIN}/blog/{post['slug']}/",
            "datePublished": post["date"],
            "image": ORIGIN + post["image"],
            "description": post["description"],
        })
    body = page_hero("Blog", "All Posts", "Stories about the landscape, communities, history, and transportation of Scenic 30A.") + f"""
    <section class="section section-sand"><div class="wrap"><div class="posts">{''.join(cards)}</div></div></section>
    """
    write_page(
        "/blog/",
        "Scenic 30A Stories",
        "Stories from Friends of Scenic 30A about Scenic Highway 30A: its landscape, beach communities, history, trails, and transportation.",
        body,
        kind="CollectionPage",
        crumbs=[("Home", "/"), ("Blog", "/blog/")],
        blog_posts=blog_posts,
    )

    for post in POSTS:
        text = (ROOT / "content" / "posts" / post["file"]).read_text()
        extra = ""
        if post.get("video"):
            extra = f'<div class="video"><iframe src="{post["video"]}" title="360 degree drive on Scenic 30A" allow="fullscreen; picture-in-picture" allowfullscreen></iframe></div>'
        path = f"/blog/{post['slug']}/"
        body = f"""
        <article class="section section-sand">
          <div class="wrap prose article-hero">
            <p class="eyebrow">Friends · <time datetime="{post['date']}">{post['display']}</time> · {post['minutes']}</p>
            <h1>{esc(post['title'])}</h1>
            <img src="{post['image']}" alt="{esc(post['image_alt'])}">
            {extra}
            {article_html(text)}
            <p><a href="/blog/">All posts</a></p>
          </div>
        </article>
        """
        write_page(
            path,
            post.get("seo_title", post["title"]),
            post["description"],
            body,
            post["image"],
            image_alt=post["image_alt"],
            kind="BlogPosting",
            crumbs=[("Home", "/"), ("Blog", "/blog/"), (post["title"], path)],
            article={"headline": post["title"], "published": post["date"]},
        )


def missing():
    body = page_hero("404", "That page is not on this site", "The address may have changed. The home page is a good place to continue.") + """
    <section class="section section-sand"><div class="wrap"><a class="btn btn-gulf" href="/">Back home</a></div></section>
    """
    html_doc = layout(
        "Page not found",
        "That address is not a page on the Friends of Scenic 30A website.",
        "/404.html",
        body,
        robots="noindex",
    )
    (ROOT / "404.html").write_text(html_doc)


def page_lines():
    lines = []
    for page in PAGES:
        lines.append(f"- [{page['title']}]({ORIGIN}{page['path']}): {page['description']}")
    return "\n".join(lines)


def llms_documents():
    pages = page_lines()
    intro = (
        f"# {BRAND}\n\n"
        "> Designated Byway Organization for Scenic Highway 30A in Santa Rosa Beach, Walton County, Florida.\n\n"
        "Friends of Scenic 30A protects and enhances the natural beauty, scenic character, distinctive communities, "
        "and quality of life of Scenic Highway 30A. The corridor is a Florida Scenic Highway and a National Scenic Byway. "
        "Friends serves as its designated Byway Organization.\n"
    )
    full_intro = (
        f"# {BRAND}\n\n"
        "> Designated Byway Organization for Scenic Highway 30A in Santa Rosa Beach, Walton County, Florida.\n\n"
        "Friends of Scenic 30A protects and enhances the natural beauty, scenic character, distinctive communities, "
        "and quality of life of Scenic Highway 30A. Scenic 30A received Florida Scenic Highway designation in 2008 and "
        "National Scenic Byway designation in 2021. Friends helped carry both designations forward and remains the "
        "designated Byway Organization.\n\n"
        "The work covers coastal dune lakes, native vegetation, beaches, and forests; the two-lane scenic character of "
        "the highway; the Timpoochee Trail and walking and biking safety; and education for residents, businesses, and "
        "visitors. Friends works with residents, businesses, Walton County, and other community partners.\n\n"
        "Mail: Friends of Scenic 30A, 877 N County Hwy 393, Santa Rosa Beach, FL 32459. "
        "Individual membership is $25 a year, business membership is $100 a year, and corporate membership is $1,000 a year. "
        "Membership payments and donations are completed on Square. This website does not collect card numbers.\n"
    )
    optional_short = (
        "\n## Optional\n\n"
        f"- [Extended guide for language models]({ORIGIN}/llms-full.txt): The same page list, with a longer introduction.\n"
        f"- [Sitemap]({ORIGIN}/sitemap.xml): Every public page on this site.\n"
    )
    optional_full = (
        "\n## Optional\n\n"
        f"- [Short guide for language models]({ORIGIN}/llms.txt): The same page list, with a shorter introduction.\n"
        f"- [Sitemap]({ORIGIN}/sitemap.xml): Every public page on this site.\n"
    )
    pages_block = "\n## Pages\n\n" + pages + "\n"
    (ROOT / "llms.txt").write_text(intro + pages_block + optional_short)
    (ROOT / "llms-full.txt").write_text(full_intro + pages_block + optional_full)


def sitemap():
    urls = [f"  <url><loc>{ORIGIN}{page['path']}</loc></url>" for page in PAGES]
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    agents = [
        "Googlebot",
        "Bingbot",
        "GPTBot",
        "ChatGPT-User",
        "Google-Extended",
        "ClaudeBot",
        "anthropic-ai",
        "PerplexityBot",
        "Applebot-Extended",
        "Bytespider",
        "CCBot",
        "meta-externalagent",
        "FacebookBot",
    ]
    groups = ["User-agent: *\nAllow: /\n"]
    groups.extend(f"User-agent: {agent}\nAllow: /\n" for agent in agents)
    (ROOT / "robots.txt").write_text(
        "# Search and AI crawlers may read this site.\n"
        f"# {ORIGIN}/llms.txt\n"
        f"# {ORIGIN}/llms-full.txt\n\n"
        + "\n".join(groups)
        + f"\nSitemap: {ORIGIN}/sitemap.xml\n"
    )
    llms_documents()
    titles = [page["title"] for page in PAGES]
    descriptions = [page["description"] for page in PAGES]
    if len(titles) != len(set(titles)):
        raise SystemExit("duplicate title")
    if len(descriptions) != len(set(descriptions)):
        raise SystemExit("duplicate description")


def main():
    home()
    about()
    our_work()
    how_projects_get_funded()
    write_impact_redirect()
    gallery()
    membership()
    contact()
    blog()
    privacy()
    accessibility()
    terms()
    missing()
    sitemap()


if __name__ == "__main__":
    main()
