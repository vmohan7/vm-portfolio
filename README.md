# Vasanth Mohan — Selected Work

A fast, accessible, static portfolio of selected writing, talks, and public work by Vasanth Mohan.

## Structure

- `index.html` — short introduction, portrait, and selected links
- `writing.html` — verified published writing
- `talks.html` — verified recorded talks and official video previews
- `gallery.html` — three sourced event photographs
- `about.html` — profile, public links, and copyable speaker bios
- `styles.css` — shared editorial layout, responsive rules, print treatment, and design tokens
- `script.js` — About-page bio copy controls with a clipboard fallback and live status
- `assets/` — local portrait, gallery photographs, and favicon
- `CONTENT.md` — public source ledger and safe update guide
- `tests/check_navigation.py` — focused five-page navigation contract
- `tests/check_static.py` — dependency-free cross-page and content-integrity checks
- `.nojekyll` — serves the site unchanged on GitHub Pages

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

The site uses relative paths for local assets, so it works from the `/vm-portfolio/` GitHub Pages project path.

## Publish with GitHub Pages

In this repository’s **Settings → Pages**, select **Deploy from a branch**, choose **main** and **/ (root)**, and save. Once GitHub completes the first deployment, the site’s address is `https://vmohan7.github.io/vm-portfolio/`.

Subsequent pushes to `main` update the same site. There are no deployment secrets or custom build workflows to maintain. The address is a deployment target, not proof that Pages has been enabled; verify the actual page after setup.

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
