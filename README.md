# Friendly Spaces — website

Rebuild of friendlyspaces.ch (replacing the Wix site). Static HTML, hosted on Cloudflare Pages
(project `friendly-spaces`, https://friendly-spaces.pages.dev — every push to `main` deploys).

## Layout

- `src/pages/<lang>/*.html` — **the editable sources**, one file per page and language
  (`en` is the default and lives at the site root; `de`, `fr`, `it` build to `/de/`, `/fr/`, `/it/`).
  Each file starts with a small front matter block (title, description, nav key) and then the page body,
  including its own `<style>` block. Use `{{root}}` for links to other pages so they work in every language.
- `src/partials/` — head, nav, footer, scripts shared by every page.
- `src/site.json` — languages and the nav/footer strings per language.
- `assets/` — fonts (Kaio Black), photos, logos, `css/site.css` (shared styles), `js/site.js` (shared behaviour:
  mobile nav, language switch + first-visit auto-detect, scroll animations, form sending).
- `map/` — the embeddable web map (copy of the `friendlyspaceswebmap` repo). It reads venue data and photos
  from https://app.friendlyspaces.ch (the native app's data host). Basemap: Esri Light Gray, no API key.
- `index.html`, `label.html`, … and `de/`, `fr/`, `it/`, `sitemap.xml` — **generated**. Don't edit by hand.
- `_headers`, `_redirects` — Cloudflare Pages config. `robots.txt` blocks indexing until launch.

## Working on it

1. Edit a page in `src/pages/…` (or a partial / `site.json`).
2. Double-click `build.cmd` (runs `python build.py`).
3. Double-click `preview.cmd` and check http://localhost:8081.
4. Commit everything (sources and generated pages) and push `main`.

## Forms

Forms post to Netlify Forms on the app host (https://app.friendlyspaces.ch/), like the native app does.
Form names: `website-contact`, `website-nominate`, `website-newsletter`. They must be declared as hidden
forms in the app repo (`friendlyspaces-app/index.html`) so Netlify registers them, and email notifications
to hello@ are switched on in the Netlify dashboard.

## Launch checklist

- Attach `friendlyspaces.ch` and `www` to the Pages project (Custom domains) and point the DNS records
  in the Cloudflare zone at it (currently they point at the Wix site).
- Flip `robots.txt` to allow indexing.
- Cancel the Wix plan only after DNS and email have been confirmed working for a few days.
