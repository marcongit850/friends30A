#!/usr/bin/env python3
"""Generate the static Friends of Scenic 30A pages."""

import html
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = os.environ.get("SITE_ORIGIN", "https://friends30a.workers.dev").rstrip("/")
DONATE = "https://square.link/u/Yzxyi16L"
MEMBER_INDIVIDUAL = "https://square.link/u/GUdeODzg"
MEMBER_BUSINESS = "https://square.link/u/KlIhQxsE"
PAGES = []
FONT_SITE = "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Outfit:wght@400;500;600&display=swap"
FONT_OUR_WORK = "https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&display=swap"

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


def layout(title, description, path, body, image="/images/hero.jpg"):
    canonical = ORIGIN + path
    full_title = title if title.endswith("Friends of Scenic 30A") else f"{title} | Friends of Scenic 30A"
    # Our Work is a type preview: Source Sans 3 for headings and body. Other pages stay Fraunces + Outfit.
    font_href = FONT_OUR_WORK if path == "/our-work/" else FONT_SITE
    body_attr = ' class="page-our-work"' if path == "/our-work/" else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(full_title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(canonical)}">
  <meta property="og:title" content="{esc(full_title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:site_name" content="Friends of Scenic 30A">
  <meta property="og:type" content="website">
  <meta property="og:image" content="{esc(ORIGIN + image)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(full_title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{esc(ORIGIN + image)}">
  <link rel="icon" href="/favicon.png" type="image/png">
  <link rel="apple-touch-icon" href="/images/apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="{font_href}" rel="stylesheet">
  <link rel="stylesheet" href="/styles.css">
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"NGO","name":"Friends of Scenic 30A","url":"{ORIGIN}/","description":"Designated Byway Organization for Scenic Highway 30A.","address":{{"@type":"PostalAddress","streetAddress":"877 N County Hwy 393","addressLocality":"Santa Rosa Beach","addressRegion":"FL","postalCode":"32459","addressCountry":"US"}},"sameAs":["https://www.facebook.com/fof30a","https://nextdoor.com/page/friends-of-scenic-30a-santa-rosa-beach-fl/"]}}</script>
</head>
<body{body_attr}>
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


def write_page(path, title, description, body, image="/images/hero.jpg"):
    PAGES.append((path, title))
    target = ROOT / "index.html" if path == "/" else ROOT / path.strip("/") / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(layout(title, description, path, body, image))
    print(path)


def page_hero(kicker, title, lede, image="/images/hero.jpg"):
    return f"""
    <header class="page-hero" style="--hero:url('{image}')">
      <div class="wrap">
        <p class="eyebrow">{esc(kicker)}</p>
        <h1>{title}</h1>
        <p>{lede}</p>
      </div>
    </header>
    """


def photos(items):
    figures = "\n".join(
        f'<figure><img src="{src}" alt="{esc(alt)}"><figcaption>{esc(alt)}</figcaption></figure>'
        for src, alt in items
    )
    return f'<div class="page-photos">{figures}</div>'


ICON = {
    "leaf": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="currentColor" d="M5 19s7-1 11-8 3-9 3-9-6 1-9 6-5 11-5 11z"/><path fill="none" stroke="currentColor" stroke-width="1.6" d="M8 16c2-2 5-5 8-7"/></svg>',
    "road": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.7" d="M7 21 10 3M17 21 14 3M4 8h16M5 14h14"/></svg>',
    "trail": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><circle cx="7" cy="6" r="2" fill="currentColor"/><path fill="none" stroke="currentColor" stroke-width="1.7" d="M6 9l2 3-2 2 3 6M14 7l3 2-1 4 3 6M11 14h5"/></svg>',
    "people": '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><circle cx="8" cy="8" r="2.2" fill="currentColor"/><circle cx="16" cy="9" r="1.8" fill="currentColor"/><path fill="none" stroke="currentColor" stroke-width="1.7" d="M3.5 19c.6-3 2.4-4.5 4.5-4.5S12 16 12.6 19M13 19c.3-2.2 1.6-3.4 3.2-3.4 1.7 0 3 1.2 3.4 3.4"/></svg>',
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
        f'<a href="/gallery/"><img src="{src}" alt="{esc(alt)}"><span>{esc(alt)}</span></a>'
        for src, alt in GALLERY[:6]
    )
    resources = [
        ("30A", "https://30a.com/"),
        ("America's Byways", "https://www.byways.org/"),
        ("Beaches of South Walton", "https://www.visitsouthwalton.com/"),
        ("Florida Scenic Highways Program", "https://floridascenichighways.com/"),
        ("Visit Florida", "https://www.visitflorida.com/"),
        ("Walton Area Chamber of Commerce", "https://www.waltonareachamber.com/"),
        ("South Walton", "https://sowal.com/"),
    ]
    resource_html = "\n".join(
        f'<a href="{url}" target="_blank" rel="noopener noreferrer">{esc(name)} <span>Visit</span></a>'
        for name, url in resources
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
          <a class="btn btn-ghost" href="/impact/">Our Impact</a>
        </div>
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
        <p><a href="/impact/">Explore our impact →</a></p>
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
        </div>
      </div>
    </section>
    <section class="section section-sand">
      <div class="wrap">
        <p class="eyebrow">Along Scenic 30A</p>
        <h2>The corridor, up close</h2>
        <div class="strip">{strip}</div>
        <p><a class="btn btn-line" href="/gallery/">Open the gallery</a></p>
      </div>
    </section>
    <section class="section section-white">
      <div class="wrap">
        <p class="eyebrow">Scenic 30A resources</p>
        <h2>Organizations connected to the corridor</h2>
        <p class="subhead">Explore organizations and resources connected to Scenic 30A, South Walton and Florida's scenic highway community.</p>
        <div class="resources">{resource_html}</div>
      </div>
    </section>
    """
    write_page(
        "/",
        "Scenic Highway 30A Preservation | Friends of Scenic 30A",
        "Scenic Highway 30A preservation starts with community. Join us in protecting its natural beauty, scenic character, neighborhoods, and quality of life.",
        body,
    )


def about():
    body = page_hero(
        "About Friends of Scenic 30A",
        "Preserving What Makes 30A Special",
        "We are a community-led organization dedicated to maintaining the unique character, natural beauty, and environmental health of the Scenic Highway 30A corridor for all who live here and visit.",
    ) + """
    <section class="section section-sand">
      <div class="wrap prose">
        """ + photos([
            ("/images/gallery/07-timpoochee-riders.jpg", "People riding the paved Timpoochee Trail"),
            ("/images/gallery/03-dune-lake-pines.jpg", "Coastal dune lake edged by pines"),
            ("/images/gallery/14-dune-sea-oats.jpg", "Sea oats on the dunes"),
        ]) + """
        <h2>Our Story</h2>
        <p>Friends of Scenic 30A serves as the designated Byway Organization for Scenic Highway 30A. Since Scenic 30A received its Florida Scenic Highway designation in 2008, Friends has helped carry forward a community vision centered on preserving the corridor's extraordinary natural, scenic, historic, recreational and cultural resources.</p>
        <p>That role extends well beyond preservation. Friends works with residents, businesses, Walton County, the Tourist Development Council and other community and regional partners on transportation and trail safety, signage and wayfinding, beautification, public education, community engagement and thoughtful improvements throughout the Scenic 30A corridor.</p>
        <p>In 2021, Scenic 30A received National Scenic Byway designation, further recognizing the national significance of the corridor and its remarkable natural resources. Today, Friends continues working to protect what makes Scenic 30A special while helping prepare the corridor for the challenges and opportunities ahead.</p>
        <h2>Our Mission</h2>
        <p class="quote">Protect. Preserve. Enhance.</p>
        <p>Our mission is to help preserve and enhance the natural, scenic, recreational, historic, and community resources that define Scenic Highway 30A. Our efforts focus on protecting the character of the corridor while supporting improvements that make 30A safer, more beautiful, accessible, and enjoyable for residents and visitors alike.</p>
        <h2>What We Care About</h2>
        <h3>Protecting Natural Resources</h3>
        <p>We support the preservation of the coastal dune lakes, native vegetation, forests, dunes, beaches, and natural landscapes that are fundamental to the identity of Scenic 30A.</p>
        <h3>Preserving Scenic 30A</h3>
        <p>We advocate for thoughtful planning, landscaping, infrastructure, and maintenance that respect the beauty and distinctive character of the scenic corridor.</p>
        <h3>Trails, Walking &amp; Biking</h3>
        <p>The Timpoochee Trail is an important part of the 30A experience. We support improvements to trails, pedestrian connections, crossings, signage, and transportation infrastructure that enhance safety and connectivity.</p>
        <h3>Community &amp; Heritage</h3>
        <p>Scenic 30A is defined not only by its natural environment but also by its distinctive communities and history. We support efforts that celebrate and preserve the places, stories, and character that make the corridor unique.</p>
        <h3>Education &amp; Stewardship</h3>
        <p>Preservation begins with understanding. We work to educate and engage residents, visitors, businesses, and community leaders about Scenic 30A's resources and the importance of protecting them.</p>
        <h2>Looking to the Future</h2>
        <h3>Preserving 30A for Generations to Come</h3>
        <p>Scenic 30A will continue to evolve. Our goal is not to prevent change, but to help ensure that change occurs thoughtfully. We envision a future where the scenic two-lane roadway remains distinctive, coastal dune lakes and native landscapes remain protected, walking and biking are safe and enjoyable, communities retain their individual character, and future generations can experience the qualities that make Scenic 30A unlike anywhere else. What we protect today becomes the 30A of tomorrow.</p>
        <h2>Be Part of the Future of Scenic 30A</h2>
        <p>Protecting Scenic 30A is a community effort. Whether you live here, own a business, visit year after year, or simply love this special place, there is a role for you in helping preserve its future.</p>
        <p><a class="btn btn-gulf" href="/membership/">Become a Member</a></p>
        <h2>Preserving Scenic 30A Heritage</h2>
        <p>Scenic 30A stretches across South Walton, connecting distinctive beach communities with coastal dune lakes, state parks, Point Washington State Forest, trails and important north-south corridors. This unique combination of natural, recreational and community resources is what Friends of Scenic 30A works to protect and enhance.</p>
        <p><a href="/our-work/">See how that work takes shape</a></p>
      </div>
    </section>
    """
    write_page(
        "/about/",
        "About Us",
        "Friends of Scenic 30A is the designated Byway Organization for Scenic Highway 30A, protecting its natural beauty, communities, and quality of life.",
        body,
    )


def our_work():
    body = page_hero(
        "Our work",
        "Protecting the Character and Future of Scenic 30A",
        "Friends of Scenic 30A works to preserve and enhance the natural, scenic, recreational, historic, and community resources that make Scenic Highway 30A extraordinary.",
        "/images/gallery/03-dune-lake-pines.jpg",
    ) + """
    <section class="section section-sand">
      <div class="wrap prose">
        """ + photos([
            ("/images/blog/trails.jpg", "Trail through the Scenic 30A corridor"),
            ("/images/gallery/07-timpoochee-riders.jpg", "People riding the paved Timpoochee Trail"),
            ("/images/gallery/11-gulf-path.jpg", "Path beside the Gulf with sea oats and pines"),
        ]) + """
        <h2>Protecting the Landscape That Defines 30A</h2>
        <p>Scenic 30A passes through an extraordinary natural environment of coastal dune lakes, beaches, dunes, forests, native vegetation, state parks, and wildlife habitat. We support efforts that preserve these resources and maintain the natural character and beauty of the scenic corridor.</p>
        <p>Our priorities include:</p>
        <ul>
          <li>Native vegetation and landscape preservation</li>
          <li>Heritage trees and natural resources</li>
          <li>Coastal dune lakes</li>
          <li>Thoughtful landscaping</li>
          <li>Appropriate screening of infrastructure and utilities</li>
          <li>Clean and well-maintained roadsides and public spaces</li>
        </ul>
        <h2>Creating a Safer, More Connected 30A</h2>
        <p>Scenic 30A is experienced by more than motorists. Walking and bicycling are fundamental parts of the corridor. We support improvements that enhance safety and connectivity while respecting the scenic character of the highway.</p>
        <p>Our priorities include:</p>
        <ul>
          <li>Timpoochee Trail safety and maintenance</li>
          <li>Safer pedestrian crossings</li>
          <li>Bicycle facilities and bike racks</li>
          <li>Trail and directional signage</li>
          <li>Wayfinding</li>
          <li>Additional trail connections</li>
          <li>Thoughtful transportation and parking planning</li>
        </ul>
        <h2>Keeping Scenic 30A Scenic</h2>
        <p>The Scenic Highway designation represents more than beautiful views. It recognizes a corridor where natural landscapes, communities, recreation, history, and transportation come together to create a distinctive sense of place. We advocate for thoughtful planning, maintenance, landscaping, signage, and infrastructure that respect and enhance that character.</p>
        <p>Our priorities include:</p>
        <ul>
          <li>Scenic corridor preservation</li>
          <li>Road and trail maintenance</li>
          <li>Landscaping standards</li>
          <li>Wayfinding and signage</li>
          <li>Public amenities</li>
          <li>Thoughtful infrastructure improvements</li>
        </ul>
        <h2>Sharing the Story of 30A</h2>
        <p>Understanding Scenic 30A helps people appreciate why it deserves to be protected. We support education about the corridor’s natural environment, history, communities, recreational resources, and unique sense of place.</p>
        <p>Our priorities include:</p>
        <ul>
          <li>Historic and interpretive markers</li>
          <li>Environmental education</li>
          <li>Native landscape education</li>
          <li>Bicycle, pedestrian, and vehicle safety education</li>
          <li>Interpretation of natural and cultural resources</li>
          <li>Awareness of Scenic 30A’s Florida Scenic Highway designation</li>
        </ul>
        <h2>Working Together for 30A</h2>
        <p>Protecting Scenic 30A requires cooperation. Friends of Scenic 30A brings together residents, businesses, property owners, community organizations, land managers, and local government to address challenges and pursue opportunities that benefit the scenic corridor.</p>
        <p class="quote">“The future of Scenic 30A is a shared responsibility.”</p>
        <h2>Our Vision</h2>
        <h3>A Scenic Corridor Worth Passing On</h3>
        <p>We envision a future where Scenic 30A retains its beautiful two-lane character, coastal dune lakes and native landscapes remain protected, walking and bicycling are safe and enjoyable, trails connect our communities, and the history and distinctive character of the corridor remain visible for generations to come.</p>
        <p class="quote">“What we protect today becomes the 30A of tomorrow.”</p>
        <h2>Help Protect Scenic 30A</h2>
        <p>Friends of Scenic 30A is powered by people who care about this extraordinary place. Join us in protecting and enhancing the corridor for generations to come.</p>
        <p class="button-row"><a class="btn btn-gulf" href="/membership/">Become a Member</a> <a class="btn btn-line" href="%s" target="_blank" rel="noopener noreferrer">Donate</a></p>
      </div>
    </section>
    """ % DONATE
    write_page(
        "/our-work/",
        "Our Work",
        "Friends of Scenic 30A protects the landscape, trails, scenic character, and story of Scenic Highway 30A.",
        body,
        "/images/gallery/03-dune-lake-pines.jpg",
    )


def impact():
    body = page_hero(
        "Our impact",
        "Protecting and Enhancing Scenic 30A",
        "For more than two decades, Friends of Scenic 30A has worked to preserve the character, natural beauty, history, and quality of life that make the Scenic 30A corridor special.",
        "/images/gallery/06-aerial-gulf-and-lake.jpg",
    ) + """
    <section class="section section-sand">
      <div class="wrap prose">
        """ + photos([
            ("/images/gallery/06-aerial-gulf-and-lake.jpg", "Aerial view of the Gulf, beach, and a dune lake beside 30A"),
            ("/images/gallery/07-timpoochee-riders.jpg", "People riding the paved Timpoochee Trail"),
            ("/images/gallery/02-gulf-sea-oats.jpg", "Gulf shoreline and sea oats along Scenic 30A"),
        ]) + """
        <p>Through community leadership, advocacy, partnerships, and hands-on projects, Friends has helped ensure that Scenic 30A remains much more than just a roadway.</p>
        <h2>Major Accomplishments</h2>
        <p>For more than 20 years, Friends of Scenic 30A has helped turn community ideas into action. Here are some of the milestones that have helped shape and protect the Scenic 30A corridor.</p>
        <h3>Florida Scenic Highway Designation</h3>
        <p>Friends played a leading role in the effort that resulted in Scenic 30A receiving official Florida Scenic Highway designation in 2008, creating a long-term framework for protecting and enhancing the corridor's unique resources.</p>
        <h3>National Scenic Byway Designation</h3>
        <p>Friends helped prepare and advance the successful application that resulted in Scenic 30A receiving National Scenic Byway designation in 2021.</p>
        <h3>Friends’ Corner at Eastern Lake</h3>
        <p>Friends spearheaded the creation of Friends' Corner at Scenic 30A and Eastern Lake Road, transforming the site into a landscaped rest area for pedestrians and bicyclists using the Timpoochee Trail.</p>
        <h3>Stewardship of Scenic 30A</h3>
        <p>As the corridor's designated caretaker organization, Friends works with local, regional and state partners to protect and enhance Scenic 30A's scenic, environmental, recreational and historic resources.</p>
        <h2>Transportation, Trails &amp; Safety</h2>
        <h3>Wayfinding &amp; Signage</h3>
        <p>Friends has worked to create a more cohesive and attractive signage system along Scenic 30A. Earlier efforts included a corridor signage inventory, removal of duplicate and unnecessary signs, and installation of safety and trail-etiquette signage, while ongoing efforts focus on wayfinding, safety and reducing visual clutter.</p>
        <h3>Timpoochee Trail &amp; Bicycle/Pedestrian Safety</h3>
        <p>Friends has worked for years to improve bicycle and pedestrian safety throughout the Scenic 30A corridor, supporting safer crossings, trail improvements, bicycle facilities, better signage and expanded multimodal connections.</p>
        <h3>Transportation &amp; Connectivity</h3>
        <p>Transportation planning has long been part of Friends' stewardship of Scenic 30A. Friends participates in discussions involving roadway safety, trail and sidewalk connections, traffic, emergency access and regional mobility while supporting solutions that protect Scenic 30A's two-lane scenic character.</p>
        <h2>Beautification &amp; Preservation</h2>
        <h3>30A Gateway Improvements</h3>
        <p>Friends has partnered with Scenic Walton and others on landscaping and gateway improvements celebrating Scenic 30A's state and national scenic designations.</p>
        <h3>Protecting Our Natural Resources</h3>
        <p>Friends advocates for the protection of coastal dune lakes, native vegetation, state parks, Point Washington State Forest and the many other natural resources that define Scenic 30A.</p>
        <h3>Preserving Scenic &amp; Historic Character</h3>
        <p>From heritage trees and historic resources to visual improvements and thoughtful infrastructure, Friends works to preserve the qualities that distinguish Scenic 30A from an ordinary roadway.</p>
        <h2>Community Leadership &amp; Advocacy</h2>
        <h3>A Voice for Scenic 30A</h3>
        <p>Friends works with Walton County, FDOT, the Okaloosa-Walton TPO, community organizations, businesses and residents to ensure Scenic 30A has a strong voice when decisions are made about transportation, development, infrastructure and public improvements.</p>
        <h3>Planning for 30A’s Future</h3>
        <p>Friends advocates for responsible solutions to the challenges created by South Walton's growth—including traffic, infrastructure, pedestrian and bicycle safety, environmental protection and preservation of Scenic 30A's distinctive character.</p>
        <h3>Bringing Our Community Together</h3>
        <p>Friends helps connect residents, businesses, nonprofits and government around projects and initiatives that protect and enhance the Scenic 30A corridor.</p>
        <h2>Protecting 30A Today. Preserving It for Generations.</h2>
        <p>For more than 20 years, Friends of Scenic 30A has helped turn community ideas into action—from achieving state and national recognition for Scenic 30A to improving trails, public spaces, signage, transportation planning and preservation efforts.</p>
        <p>Our mission remains the same: protect what makes Scenic 30A special while working toward thoughtful solutions that make it better for the people who live, work and visit here.</p>
        <p class="button-row"><a class="btn btn-gulf" href="/membership/">Become a Member</a> <a class="btn btn-line" href="/get-involved/">Support our work</a></p>
      </div>
    </section>
    """
    write_page(
        "/impact/",
        "Our Impact",
        "For more than 20 years Friends of Scenic 30A has helped secure scenic designations, Friends' Corner, trail safety, and corridor stewardship.",
        body,
        "/images/gallery/06-aerial-gulf-and-lake.jpg",
    )


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
          <p class="button-row"><a class="btn btn-gulf" href="/membership/">Become a Member</a> <a class="btn btn-line" href="/get-involved/">Support our work</a></p>
        </div>
      </div>
    </section>
    """
    write_page(
        "/gallery/",
        "Gallery",
        "Photographs of beaches, coastal dune lakes, trails, and communities along Scenic Highway 30A.",
        body,
        "/images/gallery/08-gulf-sunset.jpg",
    )


def get_involved():
    body = page_hero(
        "Get involved",
        "Help Protect What Makes 30A Special",
        "Scenic 30A belongs to everyone who values its natural beauty, distinctive communities, trails, scenic character, and extraordinary sense of place.",
        "/images/gallery/07-timpoochee-riders.jpg",
    ) + f"""
    <section class="section section-sand">
      <div class="wrap">
        <p>Friends of Scenic 30A brings people together to help protect and enhance this special corridor for generations to come.</p>
        <div class="involve-grid">
          <article class="involve"><h3>Become a Member</h3><p>Join the community working to preserve and enhance Scenic 30A.</p><a class="btn btn-gulf" href="/membership/">Become a Member</a></article>
          <article class="involve"><h3>Donate</h3><p>Help provide the resources needed to support preservation, education, advocacy, and community initiatives.</p><a class="btn btn-line" href="{DONATE}" target="_blank" rel="noopener noreferrer">Donate</a></article>
        </div>
        <div class="prose">
          <h2>There’s a Place for You in Our Mission</h2>
          <p>Friends of Scenic 30A is a volunteer-driven community organization. Whether you live here, own a business, visit regularly, or simply love 30A, your involvement helps strengthen our voice and support our work.</p>
        </div>
        <div class="price-grid">
          <article class="price">
            <h3>Individual Membership</h3>
            <strong>$25 annually</strong>
            <p>Join as an Individual.</p>
            <a class="btn btn-gulf" href="{MEMBER_INDIVIDUAL}" target="_blank" rel="noopener noreferrer">Join as an Individual</a>
          </article>
          <article class="price">
            <h3>Business Membership</h3>
            <strong>$100 annually</strong>
            <p>Join as a Business.</p>
            <a class="btn btn-line" href="{MEMBER_BUSINESS}" target="_blank" rel="noopener noreferrer">Join as a Business</a>
          </article>
        </div>
        <p>Every member adds another voice for the thoughtful stewardship of Scenic 30A.</p>
        <div class="split">
          <form class="form" data-form="volunteer">
            <h2>Volunteer</h2>
            <p>Put your passion for 30A to work. Tell us how you would like to help, and we’ll keep you informed about opportunities to participate.</p>
            <div class="split">
              <label>First name *<input name="first" required autocomplete="given-name"></label>
              <label>Last name *<input name="last" required autocomplete="family-name"></label>
            </div>
            <label>Email *<input type="email" name="email" required autocomplete="email"></label>
            <label>Phone number<input type="tel" name="phone" autocomplete="tel"></label>
            <fieldset class="checks">
              <legend>Areas of interest *</legend>
              <label><input type="checkbox" name="interests" value="Natural Resources"> Natural Resources</label>
              <label><input type="checkbox" name="interests" value="Trails"> Trails</label>
              <label><input type="checkbox" name="interests" value="Community Outreach"> Community Outreach</label>
              <label><input type="checkbox" name="interests" value="Events"> Events</label>
              <label><input type="checkbox" name="interests" value="Communications"> Communications</label>
              <label><input type="checkbox" name="interests" value="Photography"> Photography</label>
              <label><input type="checkbox" name="interests" value="Other"> Other</label>
            </fieldset>
            <label>Message<textarea name="message"></textarea></label>
            <label class="hp">Company<input name="company" tabindex="-1" autocomplete="off"></label>
            <button class="btn btn-gulf" type="submit">I'd Like to Help</button>
            <p class="form-status" role="status"></p>
          </form>
          <div>
            <form class="form" data-form="updates">
              <h2>Stay Informed</h2>
              <p>Know what’s happening along Scenic 30A. Stay informed about Friends projects, community issues, upcoming meetings and opportunities to help protect and enhance Scenic 30A.</p>
              <label>Email address *<input type="email" name="email" required autocomplete="email"></label>
              <label class="hp">Company<input name="company" tabindex="-1" autocomplete="off"></label>
              <button class="btn btn-gulf" type="submit">Stay Informed</button>
              <p class="form-status" role="status"></p>
            </form>
            <div class="prose">
              <h2>Your Support Helps Protect Scenic 30A</h2>
              <p>Friends of Scenic 30A relies on community support to advance its mission. Your contribution helps support the organization’s preservation, education, community engagement, and corridor stewardship efforts.</p>
              <p><a class="btn btn-gulf" href="{DONATE}" target="_blank" rel="noopener noreferrer">Donate Now</a></p>
              <p>Additional contributions help support preservation projects, advocacy, education and community initiatives that protect and enhance Scenic 30A.</p>
              <h2>30A’s Future Is Something We All Share</h2>
              <p>Protecting the character of Scenic 30A takes a community. Become a member, lend your time, make a contribution, or simply stay informed. Every person who gets involved helps strengthen the future of this extraordinary place.</p>
              <p class="button-row"><a class="btn btn-gulf" href="/membership/">Become a Member</a> <a class="btn btn-line" href="{DONATE}" target="_blank" rel="noopener noreferrer">Donate</a></p>
            </div>
          </div>
        </div>
      </div>
    </section>
    """
    write_page(
        "/get-involved/",
        "Get Involved",
        "Become a member, donate, volunteer, or stay informed with Friends of Scenic 30A.",
        body,
        "/images/gallery/07-timpoochee-riders.jpg",
    )


def membership():
    body = page_hero(
        "Membership",
        "Become a Friend of Scenic 30A",
        "Membership supports Friends of Scenic 30A's work as the designated Byway Organization for Scenic Highway 30A.",
        "/images/gallery/14-dune-sea-oats.jpg",
    ) + f"""
    <section class="section section-sand">
      <div class="wrap">
        <div class="prose">
          <p>Your support helps advance preservation, transportation and trail safety, community education, beautification, advocacy and other initiatives that protect and enhance the corridor.</p>
          <h2>Why Membership Matters</h2>
          <h3>Help Protect What Makes 30A Special</h3>
          <p>Scenic Highway 30A is more than just a road; it is a collection of rare coastal dune lakes, sugar-white sand beaches, and historic communities that define our way of life. By becoming a member, you provide the vital resources needed to advocate for thoughtful planning and development, environmental stewardship, and the preservation of our scenic vistas.</p>
          <h2>Together, We’re Working for the Future of Scenic 30A</h2>
        </div>
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
        <h2>Step 1. Pay through Square</h2>
        <p>Choose Individual or Business and complete payment on Square. Membership is not finished until you also send your details in step 2.</p>
        <div class="price-grid">
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
        </div>
        <div class="prose">
          <h2>Make an Additional Contribution</h2>
          <p>Your additional contributions fund specific preservation projects and educational programs that membership alone cannot cover. Every dollar goes directly toward defending the 30A we all love.</p>
          <p><a class="btn btn-gulf" href="{DONATE}" target="_blank" rel="noopener noreferrer">Donate to Friends of Scenic 30A</a></p>
          <h2>Step 2. Submit your member details</h2>
          <p>After you pay on Square, send your details here so Friends of Scenic 30A can confirm your membership and keep you informed. This form does not collect payment.</p>
          <h2>What We Protect Today Becomes the 30A of Tomorrow.</h2>
        </div>
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
            </select>
          </label>
          <label class="hp">Company<input name="company" tabindex="-1" autocomplete="off"></label>
          <button class="btn btn-gulf" type="submit">Submit Membership Details</button>
          <p class="form-status" role="status"></p>
        </form>
      </div>
    </section>
    """
    write_page(
        "/membership/",
        "Membership",
        "Join Friends of Scenic 30A. Individual membership is $25 a year and business membership is $100 a year.",
        body,
        "/images/gallery/14-dune-sea-oats.jpg",
    )


def contact():
    body = page_hero(
        "Contact",
        "Say Hello",
        "Questions, ideas, and partnership notes are welcome. Friends of Scenic 30A reads every message.",
        "/images/gallery/10-sandy-scrub-path.jpg",
    ) + """
    <section class="section section-sand">
      <div class="wrap split">
        <form class="form" data-form="contact">
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
          <p>Mail is also received at P.O. Box 1931, Santa Rosa Beach, FL 32459.</p>
          <p><a href="/get-involved/">Get involved</a> or <a href="/membership/">become a member</a>.</p>
        </div>
      </div>
    </section>
    """
    write_page(
        "/contact/",
        "Say Hello",
        "Contact Friends of Scenic 30A at 877 N County Hwy 393, Santa Rosa Beach, FL 32459.",
        body,
        "/images/gallery/10-sandy-scrub-path.jpg",
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
    write_page("/privacy-policy/", "Privacy Policy", "How Friends of Scenic 30A collects, uses, and protects personal information.", body)


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
    write_page("/accessibility/", "Accessibility Statement", "Friends of Scenic 30A is working to make this website accessible to people with disabilities.", body)


def terms():
    body = page_hero("Terms", "Terms & Conditions", "How this website may be used.") + """
    <section class="section section-sand"><div class="wrap prose">
      <p>This website is published by Friends of Scenic 30A to share information about Scenic Highway 30A and the organization’s preservation, education, and community work. By using the site you agree to these terms.</p>
      <h2>Information on this site</h2>
      <p>Articles, photographs, and project descriptions are provided for general information. They are not legal, engineering, or professional advice. Scenic corridor conditions, park rules, and public projects can change.</p>
      <h2>Membership and donations</h2>
      <p>Individual membership, business membership, and donations are completed on Square payment pages linked from this site. Those payments are governed by Square’s terms and by the membership description on this website. Submitting the membership details form tells Friends of Scenic 30A how to confirm and record a membership. It does not, by itself, collect payment.</p>
      <h2>Your messages</h2>
      <p>Do not send sensitive payment card numbers through the forms on this site. Messages you submit may be retained so the organization can respond and keep membership or volunteer records.</p>
      <h2>Content and links</h2>
      <p>Unless a page says otherwise, the text and photographs on this site belong to Friends of Scenic 30A. You may share links to these pages. Please ask before reusing photographs or long excerpts. Links to other organizations are provided for convenience. Friends of Scenic 30A is not responsible for those sites.</p>
      <h2>Contact</h2>
      <p>Questions about these terms can be sent through the <a href="/contact/">contact form</a> or by mail to Friends of Scenic 30A, 877 N County Hwy 393, Santa Rosa Beach, FL 32459.</p>
    </div></section>
    """
    write_page("/terms/", "Terms & Conditions", "Terms for using the Friends of Scenic 30A website, including membership and donation payments.", body)


POSTS = [
    {
        "slug": "protecting-the-natural-character-of-scenic-30a",
        "title": "Protecting the Natural Character of Scenic 30A",
        "date": "2026-09-12",
        "display": "September 12, 2026",
        "minutes": "3 min read",
        "image": "/images/blog/native-landscape.jpg",
        "excerpt": "The natural landscape surrounding Scenic Highway 30A is one of the defining features of the corridor.",
        "file": "protecting-the-natural-character-of-scenic-30a.txt",
    },
    {
        "slug": "transportation-has-always-been-part-of-friends-of-scenic-30a-s-mission",
        "title": "Transportation Has Always Been Part of Friends of Scenic 30A's Mission",
        "date": "2026-09-12",
        "display": "September 12, 2026",
        "minutes": "2 min read",
        "image": "/images/blog/corridor-beach.jpg",
        "excerpt": "Scenic 30A is both a treasured scenic corridor and a working transportation network.",
        "file": "transportation-has-always-been-part-of-friends-of-scenic-30a-s-mission.txt",
    },
    {
        "slug": "what-makes-scenic-30a-special",
        "title": "What Makes Scenic 30A Special?",
        "date": "2026-09-12",
        "display": "September 12, 2026",
        "minutes": "2 min read",
        "image": "/images/hero.jpg",
        "excerpt": "Scenic Highway 30A is a corridor shaped by natural beauty, communities, state lands, trails, and coastal dune lakes.",
        "file": "what-makes-scenic-30a-special.txt",
    },
    {
        "slug": "30a-in-360-degrees",
        "title": "30A in 360 Degrees",
        "date": "2026-09-05",
        "display": "September 5, 2026",
        "minutes": "1 min read",
        "image": "/images/gallery/06-aerial-gulf-and-lake.jpg",
        "excerpt": "Check out this 360° drive down 30A and explore the scenery in every direction.",
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
        "excerpt": "The Scenic 30-A corridor includes 12 distinct beach communities, each with its own history and character.",
        "file": "the-communities-of-scenic-30a.txt",
    },
    {
        "slug": "history-heritage-of-scenic-30a",
        "title": "History & Heritage of Scenic 30A",
        "date": "2026-09-03",
        "display": "September 3, 2026",
        "minutes": "6 min read",
        "image": "/images/blog/heritage.jpg",
        "excerpt": "From Grayton Beach cottages to Point Washington’s logging settlement, the corridor has a long story.",
        "file": "history-heritage-of-scenic-30a.txt",
    },
    {
        "slug": "explore-scenic-30a",
        "title": "Explore Scenic 30A",
        "date": "2026-09-03",
        "display": "September 3, 2026",
        "minutes": "6 min read",
        "image": "/images/blog/dunes.jpg",
        "excerpt": "Beaches, state parks, trails, and coastal dune lakes give everyone a way to experience Scenic 30-A.",
        "file": "explore-scenic-30a.txt",
    },
    {
        "slug": "the-story-of-30a",
        "title": "The Story of 30A",
        "date": "2026-09-03",
        "display": "September 3, 2026",
        "minutes": "2 min read",
        "image": "/images/blog/story.jpg",
        "excerpt": "Twelve beach communities grew from summer cottages into the corridor Friends of Scenic 30A works to protect.",
        "file": "the-story-of-30a.txt",
    },
    {
        "slug": "vision",
        "title": "A Vision for Scenic 30A",
        "date": "2026-09-03",
        "display": "September 3, 2026",
        "minutes": "3 min read",
        "image": "/images/blog/vision.jpg",
        "excerpt": "A picture of the two-lane scenic drive, the Timpoochee Trail, and the landscapes the Friends set out to protect.",
        "file": "vision.txt",
    },
]


def blog():
    cards = []
    for post in POSTS:
        cards.append(
            f"""<a class="post-card" href="/blog/{post['slug']}/">
              <img src="{post['image']}" alt="">
              <div>
                <time datetime="{post['date']}">{post['display']}</time>
                <span class="meta"> · {post['minutes']}</span>
                <h2>{esc(post['title'])}</h2>
                <p>{esc(post['excerpt'])}</p>
              </div>
            </a>"""
        )
    body = page_hero("Blog", "All Posts", "Stories about the landscape, communities, history, and transportation of Scenic 30A.") + f"""
    <section class="section section-sand"><div class="wrap"><div class="posts">{''.join(cards)}</div></div></section>
    """
    write_page("/blog/", "Blog", "Stories from Friends of Scenic 30A about the corridor’s landscape, communities, history, and trails.", body)

    for post in POSTS:
        text = (ROOT / "content" / "posts" / post["file"]).read_text()
        extra = ""
        if post.get("video"):
            extra = f'<div class="video"><iframe src="{post["video"]}" title="360 degree drive on Scenic 30A" allow="fullscreen; picture-in-picture" allowfullscreen></iframe></div>'
        body = f"""
        <article class="section section-sand">
          <div class="wrap prose article-hero">
            <p class="eyebrow">Friends · <time datetime="{post['date']}">{post['display']}</time> · {post['minutes']}</p>
            <h1>{esc(post['title'])}</h1>
            <img src="{post['image']}" alt="">
            {extra}
            {article_html(text)}
            <p><a href="/blog/">All posts</a></p>
          </div>
        </article>
        """
        write_page(
            f"/blog/{post['slug']}/",
            post["title"],
            post["excerpt"],
            body,
            post["image"],
        )


def missing():
    body = page_hero("404", "That page is not on this site", "The address may have changed. The home page is a good place to continue.") + """
    <section class="section section-sand"><div class="wrap"><a class="btn btn-gulf" href="/">Back home</a></div></section>
    """
    html_doc = layout(
        "Page not found",
        "That page is not on the Friends of Scenic 30A website.",
        "/404.html",
        body,
    )
    (ROOT / "404.html").write_text(html_doc)


def sitemap():
    urls = []
    for path, _title in PAGES:
        urls.append(f"  <url><loc>{ORIGIN}{path}</loc></url>")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: " + ORIGIN + "/sitemap.xml\n"
    )


def main():
    home()
    about()
    our_work()
    impact()
    gallery()
    get_involved()
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
