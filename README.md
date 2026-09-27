# Vasanth Mohan — Selected Work

A fast, accessible, static portfolio of selected writing, presentations, and public work by Vasanth Mohan.

## Structure

- `index.html` — short introduction, portrait, and selected links
- `writing.html` — recent writing and selected earlier books/tutorials
- `talks.html` — Presentations: talks, podcasts, and panels; the original URL is retained for existing links
- `gallery.html` — nine sourced photographs from conferences, hackathons, and developer meetups
- `about.html` — profile, public links, and copyable speaker bios
- `styles.css` — shared editorial layout, responsive rules, print treatment, and design tokens
- `script.js` — About-page bio copy controls with a clipboard fallback and live status
- `assets/` — local portrait, gallery photographs, and favicon
- `CONTENT.md` — public source ledger and safe update guide
- `tests/check_navigation.py` — focused five-page navigation contract
- `tests/check_static.py` — dependency-free cross-page and content-integrity checks
- `.nojekyll` — serves the site unchanged on GitHub Pages
- `robots.txt` and `sitemap.xml` — public crawl guidance and the five canonical page URLs
- `scripts/build_site.py` — generates a clean deploy artifact and crawl files from root HTML pages
- `.github/workflows/pages.yml` — checks and publishes the generated artifact on each `main` push

There is no framework, package manager, CMS, or runtime dependency. The Pages runner only copies static files and generates crawl files with Python's standard library.

## Preview locally

From the repository root:

```sh
python3 -m http.server 8000
```

Then open `http://localhost:8000/`. Each root HTML page also loads directly, for example `http://localhost:8000/talks.html`.

## Run checks

```sh
python3 tests/check_navigation.py
python3 tests/check_static.py
python3 tests/check_build.py
node --check script.js
node tests/check_copy.js
```

The site uses relative paths for local assets. The public domain is `https://www.vasanthmohan.com/`; the original GitHub Pages project URL redirects to it.

## Publish with GitHub Pages

The repository’s `CNAME` names `www.vasanthmohan.com`. The apex domain and original GitHub Pages project URL redirect to the `www` address. **One-time activation:** in this repository’s **Settings → Pages → Build and deployment → Source**, choose **GitHub Actions** instead of **Deploy from a branch**. Then rerun **Build and publish portfolio** (or push another change) and confirm the `deploy` job succeeds and the live domain still serves the site. Do not remove the existing branch deployment before the Actions deploy is verified. Access to that owner-only setting is required; simply committing the workflow does not change the Pages source.

For every `main` push, the runner validates content, builds `_site`, generates a sitemap from all root HTML pages with correct canonical URLs and a robots file pointing to it, and deploys the artifact using the standard Pages actions. There is no bot commit, secret, dependency install, or manual sitemap edit per page change. The checked-in crawl files remain as fallbacks while branch deployment is active; the runner regenerates them in the deployed artifact. A successful commit or build alone is not deployment proof—verify the deployment job and public URLs.

## Search discovery

The five current HTML pages have distinct titles, descriptions, self-referencing canonical URLs on the `www` domain, and normal crawlable links. The generated root sitemap discovers pages automatically and omits `lastmod` rather than guessing dates. The generated robots file permits crawling and advertises the sitemap. Check the **live** versions of both files after deployment, including any rules added by the domain's proxy.

For indexing diagnostics, the domain owner should verify `vasanthmohan.com` in [Google Search Console](https://search.google.com/search-console/), submit `https://www.vasanthmohan.com/sitemap.xml`, and inspect the homepage and key page URLs there. DNS/domain-property verification may require action in the DNS provider. A valid sitemap and crawlable pages help discovery but do not guarantee inclusion or ranking; only Search Console can show Google's indexing decisions for this property.

## Add or update public work

Follow `CONTENT.md`. Every item needs a public source that verifies its title, link, role, and any displayed date. Keep speaker, host, author, and producer credits distinct. Omit uncertain details until they can be verified.

## Accessibility and performance

- semantic landmarks and heading hierarchy
- skip link and visible keyboard focus
- minimum-size interactive controls
- responsive layouts without client-side rendering
- reduced-motion and print accommodations
- lazy-loaded external video previews
- clipboard fallback plus an ARIA live status
