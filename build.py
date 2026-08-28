#!/usr/bin/env python3
"""Assemble the site's pages from content fragments in content/.

Each fragment starts with a small header block:
    title: Page title
    desc: Meta description
    out: output path relative to site root
    ---
    ...body HTML...

Run: python3 build.py
Set BASE_URL below (no trailing slash) before deploying so canonical
and Open Graph URLs are correct.
"""
import os, re, html

BASE_URL = os.environ.get("BASE_URL", "https://SITE_BASE_URL")
ROOT = os.path.dirname(os.path.abspath(__file__))

NAV = [
    ("index.html", "Home"),
    ("work.html", "Work"),
    ("case-studies.html", "Case studies"),
    ("speaking.html", "Speaking"),
    ("writing.html", "Notes"),
    ("about.html", "About"),
    ("contact.html", "Contact"),
]

PERSON_JSONLD = """{
  "@context": "https://schema.org",
  "@type": "Person",
  "name": "Ahmad A. Idris",
  "alternateName": "Ahmad Aminu Idris",
  "url": "%(base)s/",
  "jobTitle": "Academic Team Lead, Fairfield School of Business",
  "worksFor": {"@type": "Organization", "name": "Fairfield School of Business"},
  "alumniOf": {"@type": "CollegeOrUniversity", "name": "University of Birmingham"},
  "knowsAbout": ["Education technology", "Higher education", "Digital skills", "Social innovation", "Product development"],
  "sameAs": ["https://www.linkedin.com/in/ahmadidris001/"],
  "address": {"@type": "PostalAddress", "addressLocality": "Leicester", "addressCountry": "GB"}
}"""

WEBSITE_JSONLD = """{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Ahmad A. Idris",
  "url": "%(base)s/"
}"""

TEMPLATE = """<!DOCTYPE html>
<html lang="en-GB" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(canonical)s">
<meta property="og:type" content="website">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(canonical)s">
<meta property="og:image" content="%(base)s/assets/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name" content="Ahmad A. Idris">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#16233B">
<link rel="icon" href="%(root)sfavicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="%(root)sassets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap" media="print" onload="this.media='all'">
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap"></noscript>
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
        <p style="margin-top:0.8rem; max-width:22rem; color:#C9C2B0;">Educator, technology builder and social innovation practitioner working across the UK and Africa.</p>
      </div>
      <div>
        <h2 style="font-size:1rem; color:#F5EFE3;">Explore</h2>
        <ul>
          <li><a href="%(root)swork.html">Work and impact</a></li>
          <li><a href="%(root)scase-studies.html">Case studies</a></li>
          <li><a href="%(root)sspeaking.html">Speaking and advisory</a></li>
          <li><a href="%(root)swriting.html">Notes and research</a></li>
        </ul>
      </div>
      <div>
        <h2 style="font-size:1rem; color:#F5EFE3;">Connect</h2>
        <ul>
          <li><a href="%(root)scontact.html">Contact</a></li>
          <li><a href="https://www.linkedin.com/in/ahmadidris001/" rel="me noopener" target="_blank">LinkedIn<span class="visually-hidden"> (opens in a new tab)</span></a></li>
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

def build():
    content_dir = os.path.join(ROOT, "content")
    for name in sorted(os.listdir(content_dir)):
        if not name.endswith(".html"):
            continue
        raw = open(os.path.join(content_dir, name), encoding="utf-8").read()
        head, body = raw.split("\n---\n", 1)
        meta = dict(re.match(r"(\w+):\s*(.*)", l).groups() for l in head.strip().splitlines())
        out = meta["out"]
        depth = out.count("/")
        root = "../" * depth
        canonical = BASE_URL + "/" + (out if out != "index.html" else "")
        jsonld = ""
        if out == "index.html":
            jsonld = ('<script type="application/ld+json">%s</script>\n'
                      '<script type="application/ld+json">%s</script>') % (
                PERSON_JSONLD % {"base": BASE_URL}, WEBSITE_JSONLD % {"base": BASE_URL})
        nav_items = []
        for href, label in NAV:
            current = ' aria-current="page"' if href == out else ""
            nav_items.append('        <li><a href="%s%s"%s>%s</a></li>' % (root, href, current, label))
        page = TEMPLATE % {
            "title": html.escape(meta["title"], quote=True),
            "desc": html.escape(meta["desc"], quote=True),
            "canonical": canonical,
            "base": BASE_URL,
            "root": root,
            "nav": "\n".join(nav_items),
            "body": body.replace("{{root}}", root),
            "jsonld": jsonld,
        }
        dest = os.path.join(ROOT, out)
        os.makedirs(os.path.dirname(dest) or ROOT, exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(page)
        print("built", out)

def sitemap_and_robots():
    pages = ["", "about.html", "work.html", "case-studies.html",
             "case-studies/allon-fasaha.html", "case-studies/techxplorer.html",
             "case-studies/digital-skills.html", "case-studies/higher-education.html",
             "speaking.html", "writing.html", "contact.html", "privacy.html"]
    urls = "\n".join(
        "  <url><loc>%s/%s</loc></url>" % (BASE_URL, p) for p in pages)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                + urls + "\n</urlset>\n")
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % BASE_URL)
    print("built sitemap.xml, robots.txt")

if __name__ == "__main__":
    build()
    sitemap_and_robots()
