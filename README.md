# Vasanth Mohan — Selected Work

A fast, accessible, static portfolio of selected writing, presentations, and public work by Vasanth Mohan.

## Structure

- `index.html` — short introduction, portrait, and selected links
- `writing.html` — recent writing and selected earlier books/tutorials
- `talks.html` — Presentations: talks, podcasts, and panels; the original URL is retained for existing links
- `gallery.html` — thirteen sourced photographs from conferences, hackathons, and developer meetups
- `about.html` — profile, public links, and copyable speaker bios
- `styles.css` — shared editorial layout, responsive rules, print treatment, and design tokens
- `script.js` — About-page bio copy controls with a clipboard fallback and live status
- `assets/` — local portrait, gallery photographs, and favicon
- `CONTENT.md` — public source ledger and safe update guide
- `tests/check_navigation.py` — focused five-page navigation contract
- `tests/check_static.py` — dependency-free cross-page and content-integrity checks
- `.nojekyll` — serves the site unchanged on GitHub Pages
- `robots.txt` and `sitemap.xml` — generated crawl guidance also committed as branch-Pages fallbacks until the Pages source is switched
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

The repository’s `CNAME` names `www.vasanthmohan.com`. The apex domain and original GitHub Pages project URL redirect to the `www` address. **Pages is currently configured to deploy from the `main` branch.** Its built-in `pages build and deployment` job runs alongside **Build and publish portfolio** and may publish *after* the custom Actions job; a successful Actions run does not prove that its artifact is the final live site.

**One-time owner action for fully automatic publishing:** In this repository’s **Settings → Pages → Build and deployment → Source**, select **GitHub Actions** instead of **Deploy from a branch**. Then verify a fresh push has only the intended Actions deployment and check the uncached sitemap and robots responses. Until that setting is changed, both the generated artifact and the branch must include identical crawl files; `tests/check_build.py` enforces byte-for-byte parity. When adding a new page before switching, regenerate the checked-in copies from the build output and commit them. Do not remove those copies merely because the custom Actions job reports success.

On every `main` push, the custom runner validates content, builds `_site`, generates a sitemap from canonical root HTML pages and a robots file pointing to it, and deploys the artifact using standard Pages actions. After the source switch, the branch copies may be removed in a separately verified change, leaving no manual sitemap upkeep. A successful commit or build alone is not deployment proof—verify the final public URLs after *both* deployment jobs finish.

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
