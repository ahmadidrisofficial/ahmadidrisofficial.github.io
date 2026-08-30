#!/usr/bin/env python3
"""Build the deployable website into _site/.

Run: python3 sitegen.py
Environment: BASE_URL sets the canonical site address (defaults to the
GitHub Pages address). Requires Pillow for the social image; if Pillow
or the fonts are missing, image generation is skipped gracefully.

Contact form: if a file named w3f_key.txt exists next to this script
(containing only a Web3Forms access key), the contact form is enabled
with that key. Without it, the form is omitted and the contact page
offers LinkedIn as the contact route.
"""
import os
import re
import shutil
import subprocess
import sys


def main():
    try:
        make_gallery()
    except Exception as exc:
        print("gallery generation skipped:", exc)

    env = dict(os.environ)
    env.setdefault("BASE_URL", "https://www.ahmadidrisofficial.com")
    subprocess.check_call([sys.executable, "build.py"], env=env)

    key = None
    if os.path.exists("w3f_key.txt"):
        key = open("w3f_key.txt", encoding="utf-8").read().strip()
    for page in ["contact.html", "pathways.html"]:
        if not os.path.exists(page):
            continue
        text = open(page, encoding="utf-8").read()
        if key:
            text = text.replace("W3F_ACCESS_KEY", key)
        else:
            text = re.sub("<!-- FORM-START -->.*?<!-- FORM-END -->", "",
                          text, flags=re.S)
        open(page, "w", encoding="utf-8").write(text)

    try:
        make_images()
    except Exception as exc:
        print("image generation skipped:", exc)

    out = "_site"
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    for p in os.listdir("."):
        if p.endswith(".html"):
            shutil.copy(p, os.path.join(out, p))
    for sub in output_subdirs():
        if not os.path.isdir(sub):
            continue
        os.makedirs(os.path.join(out, sub), exist_ok=True)
        for p in os.listdir(sub):
            if p.endswith(".html"):
                shutil.copy(os.path.join(sub, p), os.path.join(out, sub, p))
    shutil.copytree("assets", os.path.join(out, "assets"),
                    ignore=shutil.ignore_patterns("gallery-b64"))
    for extra in ["favicon.svg", "sitemap.xml", "robots.txt"]:
        shutil.copy(extra, os.path.join(out, extra))
    print("site written to _site/")


def output_subdirs():
    """Subdirectories that pages are generated into, read from content headers.

    Each file in content/ declares its output path on an "out:" line. Any
    directory part of that path is a folder the built site needs copied, so
    new sections work without editing this script.
    """
    dirs = set()
    if not os.path.isdir("content"):
        return dirs
    for f in os.listdir("content"):
        if not f.endswith(".html"):
            continue
        with open(os.path.join("content", f), encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("out:"):
                    part = os.path.dirname(line.split(":", 1)[1].strip())
                    if part:
                        dirs.add(part)
                    break
    return dirs


def caption_from(name):
    stem = os.path.splitext(name)[0]
    words = stem.replace("-", " ").replace("_", " ").split()
    words = [w for w in words if not (w.isdigit() and len(w) in (2, 4, 8))]
    text = " ".join(words).strip()
    return (text[:1].upper() + text[1:]) if text else "Photograph"


def make_gallery():
    """Build the gallery page from photos in assets/img/gallery/.

    Also accepts text files in assets/img/gallery-b64/ (base64 of an
    image, filename like my-caption.jpg.b64.txt) and decodes them into
    the gallery folder first. If no photos exist, no gallery page or
    navigation entry is created.
    """
    import base64
    gal = os.path.join("assets", "img", "gallery")
    b64dir = os.path.join("assets", "img", "gallery-b64")
    if os.path.isdir(b64dir):
        os.makedirs(gal, exist_ok=True)
        for f in os.listdir(b64dir):
            if not f.endswith(".b64.txt"):
                continue
            target = os.path.join(gal, f[:-8])
            if os.path.exists(target):
                continue
            raw = open(os.path.join(b64dir, f), encoding="utf-8").read()
            with open(target, "wb") as out:
                out.write(base64.b64decode("".join(raw.split())))
    exts = (".jpg", ".jpeg", ".png", ".webp")
    photos = []
    if os.path.isdir(gal):
        photos = sorted(
            [f for f in os.listdir(gal) if f.lower().endswith(exts)],
            reverse=True)
    page = os.path.join("content", "gallery.html")
    if not photos:
        if os.path.exists(page):
            os.remove(page)
        return
    from PIL import Image
    thumbs = os.path.join(gal, "thumbs")
    os.makedirs(thumbs, exist_ok=True)
    figures = []
    for f in photos:
        stem = os.path.splitext(f)[0]
        thumb_name = stem + ".jpg"
        thumb_path = os.path.join(thumbs, thumb_name)
        if not os.path.exists(thumb_path):
            img = Image.open(os.path.join(gal, f))
            img = img.convert("RGB")
            img.thumbnail((900, 1400))
            img.save(thumb_path, "JPEG", quality=84, optimize=True)
        cap = caption_from(f)
        figures.append(
            '      <figure>\n'
            '        <img src="{{root}}assets/img/gallery/thumbs/%s" data-full="{{root}}assets/img/gallery/%s" alt="%s" loading="lazy">\n'
            '        <figcaption>%s</figcaption>\n'
            '      </figure>' % (thumb_name, f, cap, cap))
    body = (
        "title: Gallery | Ahmad A. Idris\n"
        "desc: Photographs from Ahmad A. Idris's work and journey across education, technology and social innovation in the UK and Nigeria.\n"
        "out: gallery.html\n"
        "---\n"
        '<section class="page-hero">\n'
        '  <div class="wrap">\n'
        '    <h1>The work, in pictures</h1>\n'
        '    <p>Moments from classrooms, stages, workshops and the road: the people and places behind the story this site tells.</p>\n'
        '  </div>\n'
        '</section>\n\n'
        '<section class="section">\n'
        '  <div class="wrap">\n'
        '    <h2 class="visually-hidden">Photographs</h2>\n'
        '    <div class="gallery-grid">\n'
        + "\n".join(figures) + "\n"
        '    </div>\n'
        '  </div>\n'
        '</section>\n')
    open(page, "w", encoding="utf-8").write(body)
    print("gallery built with", len(photos), "photos")


def bez(p0, p1, p2, p3, n=200):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1-t)**3*p0[0] + 3*(1-t)**2*t*p1[0] + 3*(1-t)*t**2*p2[0] + t**3*p3[0]
        y = (1-t)**3*p0[1] + 3*(1-t)**2*t*p1[1] + 3*(1-t)*t**2*p2[1] + t**3*p3[1]
        pts.append((x, y))
    return pts


def make_images():
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1200, 630
    ink = (22, 35, 59)
    gold = (228, 194, 126)
    bronze = (176, 134, 64)
    paper = (245, 239, 227)
    muted = (217, 211, 196)
    img = Image.new("RGB", (W, H), ink)
    d = ImageDraw.Draw(img)
    d.line(bez((-50, 600), (300, 560), (620, 420), (1250, 160)), fill=bronze, width=3)
    d.line(bez((-50, 660), (350, 600), (700, 470), (1260, 250)), fill=(47, 93, 66), width=2)
    d.ellipse((608, 428, 622, 442), fill=gold)
    d.ellipse((935, 300, 945, 310), fill=bronze)
    fp = "/usr/share/fonts/truetype/dejavu/"
    serif_b = ImageFont.truetype(fp + "DejaVuSerif-Bold.ttf", 74)
    serif = ImageFont.truetype(fp + "DejaVuSerif.ttf", 40)
    sans = ImageFont.truetype(fp + "DejaVuSans.ttf", 30)
    d.text((90, 120), "Ahmad A. Idris", font=serif_b, fill=paper)
    d.text((90, 235), "Building better pathways to", font=serif, fill=gold)
    d.text((90, 295), "learning, work and opportunity.", font=serif, fill=gold)
    d.text((90, 420), "Educator  |  EdTech builder  |  Social innovation practitioner", font=sans, fill=muted)
    d.text((90, 470), "UK and Africa", font=sans, fill=muted)
    os.makedirs("assets/img", exist_ok=True)
    img.save("assets/img/og.png", optimize=True)
    S = 180
    icon = Image.new("RGB", (S, S), ink)
    di = ImageDraw.Draw(icon)
    pts = bez((28, 141), (62, 130), (79, 101), (96, 79)) + bez((96, 79), (113, 57), (135, 40), (158, 28))
    di.line(pts, fill=gold, width=11)
    di.ellipse((83, 66, 109, 92), fill=bronze)
    icon.save("assets/img/apple-touch-icon.png", optimize=True)


if __name__ == "__main__":
    main()
