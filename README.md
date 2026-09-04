# Friendly Spaces — website

Rebuild of friendlyspaces.ch (replacing the Wix site). Static HTML, hosted on Cloudflare Pages.

## Layout

- `index.html`, `sponsoring.html` — the built pages Cloudflare serves. **Don't edit these directly.**
- `src/templates/` — the editable sources. Edit here, then run `build.cmd`.
- `assets/` — fonts (Kaio Black), photos, logos.
- `_headers`, `_redirects` — Cloudflare Pages config.
- `robots.txt` — currently blocks indexing (preview). Flip it at launch.

## Working on it

1. Edit a template in `src/templates/`.
2. Double-click `build.cmd` (regenerates the root pages).
3. Double-click `preview.cmd` to check it at http://localhost:8081.
4. Commit and push `main` — Cloudflare Pages deploys automatically.

Push when a change is finished, not after every save: Pages has a monthly build allowance.

## Deployment

Cloudflare Pages project `friendly-spaces` (https://friendly-spaces.pages.dev), connected to this GitHub repo: every push to `main` deploys. Framework preset: none. Build command: empty. Output directory: `/`.

## The live map

The map on the homepage is an iframe of the map web app at https://app.friendlyspaces.ch (its own repo, currently on Netlify — to be migrated to Cloudflare Pages).
