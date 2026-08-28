# Ahmad A. Idris, personal website

A fast, accessible, static personal website. No frameworks and no database. GitHub Actions builds and publishes it automatically on every change.

## How the site is put together

- content/ holds one file per page. Each file starts with a few lines (title, description, output path), then the page body HTML. This is where you edit words.
- build.py wraps every content file in the shared header, navigation and footer, and generates sitemap.xml and robots.txt.
- sitegen.py runs build.py, wires or removes the contact form, draws the social sharing image, and assembles the finished site into _site/.
- assets/css/styles.css holds the whole design. Colours and fonts are defined once at the top.
- assets/js/main.js is a small enhancement script (mobile menu, contact form). The site works fully without it.
- .github/workflows/deploy.yml publishes _site/ to GitHub Pages on every push to main.

## Updating the site

Edit the relevant file under content/ (or styles.css for design changes) directly on GitHub, commit to main, and the site republishes itself within a couple of minutes. Or simply ask Claude to make the change.

## Contact form

The form posts to Web3Forms, which forwards messages to the site owner's inbox. The access key lives in w3f_key.txt at the repository root and is safe to be public by design. If that file is absent, the build omits the form and the contact page offers LinkedIn instead. Spam protection: a hidden honeypot field plus Web3Forms filtering.

## Housekeeping

- The Open Graph sharing image and the touch icon are drawn by sitegen.py at build time.
- The favicon is favicon.svg.
- Structured data (Person and WebSite) is injected on the homepage by build.py.
- A private research and claim-verification record is kept in the owner's Claude project, not in this repository.
