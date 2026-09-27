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

There is no build step, package manager, framework, CMS, or runtime dependency.

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
node --check script.js
node tests/check_copy.js
```

The site uses relative paths for local assets. The public domain is `https://www.vasanthmohan.com/`; the original GitHub Pages project URL redirects to it.

## Publish with GitHub Pages

GitHub Pages deploys from **main** and **/ (root)**. The repository’s `CNAME` names `www.vasanthmohan.com`. The apex domain and original GitHub Pages project URL redirect to the `www` address.

Subsequent pushes to `main` update the same site. There are no deployment secrets or custom build workflows to maintain. A commit is not deployment proof; verify the published pages after each update.

## Search discovery

The five HTML pages have distinct titles, descriptions, self-referencing canonical URLs on the `www` domain, and normal crawlable links. The root sitemap lists only these five pages; it omits `lastmod` rather than guessing dates. The root robots file permits crawling and advertises the sitemap. Check the **live** versions of both files after deployment, including any rules added by the domain's proxy.

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
