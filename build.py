#!/usr/bin/env python3
"""Assemble the site's pages from content fragments in content/.

Each fragment starts with a small header block:
    title: Page title
    desc: Meta description
    out: output path relative to site root
    date: optional ISO date, used for Article structured data
    ---
    ...body HTML...

Run: python3 build.py
Set BASE_URL below (no trailing slash) before deploying so canonical
and Open Graph URLs are correct.

Revision, 31 August 2026:
- Navigation marks the PARENT section current on child pages, so a reader
  inside a case study or guide can still see which section they are in.
- Case studies and guides emit Article structured data.
- Fonts load with a preload hint rather than a print-media swap, which was
  guaranteeing a flash of fallback type on a site whose identity is type.
- theme-color now points at a colour that exists in DESIGN.md.
- The footer gallery link appears only when the gallery does, matching the
  sitemap, so an empty gallery cannot leave a dead link in the footer.
- The sitemap carries lastmod, taken from each fragment's modification time.
"""
import os, re, html, json, datetime

BASE_URL = os.environ.get("BASE_URL", "https://SITE_BASE_URL")
ROOT = os.path.dirname(os.path.abspath(__file__))

NAV = [
    ("work.html", "Work"),
    ("build.html", "Build"),
    ("writing.html", "Writing"),
    ("about.html", "About"),
    ("contact.html", "Contact"),
]

# Child pages that belong to a navigation section. Without this, no nav item
# is marked current on any case study or guide.
def nav_target(out):
    if out.startswith("case-studies"):
        return "work.html"
    if out.startswith("build/"):
        return "build.html"
    return out

FONTS = ("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600"
         "&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&display=swap")

PERSON_JSONLD = """{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Ahmad A. Idris",
  "alternateName": "Ahmad Aminu Idris",
  "url": "%(base)s/",
  "image": "%(base)s/assets/img/portrait-plate.jpg",
  "description": "Educator, technology builder and social innovation practitioner. Co-founded Steamledge in Nigeria, consulted on national digital skills strategies, and leads an academic team in UK higher education.",
  "jobTitle": "Academic Team Lead, Fairfield School of Business",
  "worksFor": {"@type": "Organization", "name": "Fairfield School of Business"},
  "alumniOf": {"@type": "CollegeOrUniversity", "name": "University of Birmingham"},
  "knowsAbout": ["Education technology", "Higher education", "Digital skills", "Social innovation", "Product development"],
  "sameAs": ["%(base)s/", "https://www.linkedin.com/in/ahmadidris001/", "https://www.instagram.com/ahmadidris_ai/", "https://www.tiktok.com/@a_idrisofficial"],
  "address": {"@type": "PostalAddress", "addressLocality": "Leicester", "addressCountry": "GB"}
}"""

WEBSITE_JSONLD = """{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Ahmad A. Idris",
  "url": "%(base)s/"
}"""


def article_jsonld(meta, canonical):
    """Case studies and guides are the strongest content on the site and were
    previously invisible to search as anything more specific than a page."""
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": meta["title"].split(" | ")[0],
        "description": meta["desc"],
        "mainEntityOfPage": canonical,
        "author": {"@type": "Person", "name": "Ahmad A. Idris", "url": BASE_URL + "/"},
        "publisher": {"@type": "Person", "name": "Ahmad A. Idris"},
        "isPartOf": {"@type": "WebSite", "name": "Ahmad A. Idris", "url": BASE_URL + "/"},
    }
    # no date is invented: it appears only when the fragment states one
    if meta.get("date"):
        data["datePublished"] = meta["date"]
    return json.dumps(data, indent=2)


TEMPLATE = """<!DOCTYPE html>
<html lang="en-GB" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(canonical)s">
<meta property="og:type" content="%(ogtype)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(canonical)s">
<meta property="og:image" content="%(base)s/assets/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="Ahmad A. Idris">
<meta property="og:locale" content="en_GB">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#1B2547">
<link rel="icon" href="%(root)sfavicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="%(root)sassets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="%(fonts)s">
<link rel="stylesheet" href="%(fonts)s">
<link rel="stylesheet" href="%(root)sassets/css/styles.css">
<script>document.documentElement.classList.remove('no-js');</script>
%(jsonld)s
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="%(root)sindex.html">Ahmad A. Idris</a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav class="site-nav" id="site-nav" aria-label="Main navigation">
      <ul>
%(nav)s
      </ul>
    </nav>
  </div>
</header>
<main id="main">
%(body)s
</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="%(root)sindex.html">Ahmad A. Idris</a>
        <p style="margin-top:0.8rem; max-width:22rem;">Educator, technology builder and social innovation practitioner working across the UK and Africa.</p>
      </div>
      <div>
        <h2>Explore</h2>
        <ul>
          <li><a href="%(root)swork.html">Work and impact</a></li>
          <li><a href="%(root)scase-studies.html">Case studies</a></li>
          <li><a href="%(root)sspeaking.html">Speaking and advisory</a></li>
          <li><a href="%(root)spathways.html">Pathways weekly</a></li>
          <li><a href="%(root)sbuild.html">AI on a Naira Budget</a></li>
          <li><a href="%(root)swriting.html">Notes and research</a></li>
%(gallery_li)s
        </ul>
      </div>
      <div>
        <h2>Connect</h2>
        <ul>
          <li><a href="%(root)scontact.html">Contact</a></li>
          <li><a href="https://www.linkedin.com/in/ahmadidris001/" rel="me noopener" target="_blank">LinkedIn<span class="visually-hidden"> (opens in a new tab)</span></a></li>
          <li><a href="https://www.instagram.com/ahmadidris_ai/" rel="me noopener" target="_blank">Instagram<span class="visually-hidden"> (opens in a new tab)</span></a></li>
          <li><a href="https://www.tiktok.com/@a_idrisofficial" rel="me noopener" target="_blank">TikTok<span class="visually-hidden"> (opens in a new tab)</span></a></li>
        </ul>
      </div>
    </div>
    <div class="fine">
      <span>&copy; 2026 Ahmad A. Idris. All rights reserved.</span>
      <span><a href="%(root)sprivacy.html">Privacy notice</a></span>
    </div>
  </div>
</footer>
<script src="%(root)sassets/js/main.js" defer></script>
</body>
</html>
"""


def has_gallery():
    return os.path.exists(os.path.join(ROOT, "content", "gallery.html"))


def build():
    content_dir = os.path.join(ROOT, "content")
    gallery = has_gallery()
    for name in sorted(os.listdir(content_dir)):
        if not name.endswith(".html"):
            continue
        path = os.path.join(content_dir, name)
        raw = open(path, encoding="utf-8").read()
        head, body = raw.split("\n---\n", 1)
        meta = dict(re.match(r"(\w+):\s*(.*)", l).groups() for l in head.strip().splitlines())
        out = meta["out"]
        depth = out.count("/")
        root = "../" * depth
        canonical = BASE_URL + "/" + (out if out != "index.html" else "")

        blocks = []
        if out == "index.html":
            blocks.append(PERSON_JSONLD % {"base": BASE_URL})
            blocks.append(WEBSITE_JSONLD % {"base": BASE_URL})
        is_article = out.startswith("case-studies/") or out.startswith("build/")
        if is_article:
            blocks.append(article_jsonld(meta, canonical))
        jsonld = "\n".join(
            '<script type="application/ld+json">%s</script>' % b for b in blocks)

        nav_items = []
        target = nav_target(out)
        for href, label in NAV:
            current = ' aria-current="page"' if href == target else ""
            nav_items.append('        <li><a href="%s%s"%s>%s</a></li>' % (root, href, current, label))

        gallery_li = ('          <li><a href="%sgallery.html">Gallery</a></li>' % root) if gallery else ""

        page = TEMPLATE % {
            "title": html.escape(meta["title"], quote=True),
            "desc": html.escape(meta["desc"], quote=True),
            "canonical": canonical,
            "base": BASE_URL,
            "root": root,
            "fonts": html.escape(FONTS, quote=True),
            "ogtype": "article" if is_article else "website",
            "nav": "\n".join(nav_items),
            "gallery_li": gallery_li,
            "body": body.replace("{{root}}", root),
            "jsonld": jsonld,
        }
        dest = os.path.join(ROOT, out)
        os.makedirs(os.path.dirname(dest) or ROOT, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(page)
        print("built", out)


def sitemap_and_robots():
    """lastmod comes from the fragment's modification time, so it is a real
    date rather than a hand-kept one that drifts."""
    pages = ["", "about.html", "work.html", "case-studies.html",
             "case-studies/allon-fasaha.html", "case-studies/techxplorer.html",
             "case-studies/digital-skills.html", "case-studies/higher-education.html",
             "speaking.html", "pathways.html", "build.html",
             "build/marking-and-lesson-prep.html",
             "writing.html", "contact.html", "privacy.html"]
    if has_gallery():
        pages.insert(11, "gallery.html")

    # map an output path back to the fragment that produced it
    mtimes = {}
    content_dir = os.path.join(ROOT, "content")
    for name in os.listdir(content_dir):
        if not name.endswith(".html"):
            continue
        p = os.path.join(content_dir, name)
        try:
            first = open(p, encoding="utf-8").read().split("\n---\n", 1)[0]
            m = re.search(r"^out:\s*(.*)$", first, re.M)
            if m:
                key = m.group(1).strip()
                mtimes["" if key == "index.html" else key] = os.path.getmtime(p)
        except Exception:
            pass

    rows = []
    for p in pages:
        ts = mtimes.get(p)
        lastmod = ""
        if ts:
            lastmod = "<lastmod>%s</lastmod>" % datetime.date.fromtimestamp(ts).isoformat()
        rows.append("  <url><loc>%s/%s</loc>%s</url>" % (BASE_URL, p, lastmod))

    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + "\n".join(rows) + "\n</urlset>\n")
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % BASE_URL)
    print("built sitemap.xml, robots.txt")


if __name__ == "__main__":
    build()
    sitemap_and_robots()
