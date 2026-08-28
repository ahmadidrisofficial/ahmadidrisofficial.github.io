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
    os.makedirs(os.path.join(out, "case-studies"), exist_ok=True)
    for p in os.listdir("case-studies"):
        if p.endswith(".html"):
            shutil.copy(os.path.join("case-studies", p),
                        os.path.join(out, "case-studies", p))
    shutil.copytree("assets", os.path.join(out, "assets"))
    for extra in ["favicon.svg", "sitemap.xml", "robots.txt"]:
        shutil.copy(extra, os.path.join(out, extra))
    print("site written to _site/")


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
