#!/usr/bin/env python3
"""Static site builder for friendlyspaces.ch.

    python build.py            (or double-click build.cmd)

Sources
  src/site.json              languages, nav/footer strings per language
  src/partials/*.html        head, nav, footer, scripts — shared by every page
  src/pages/<lang>/*.html    one file per page and language: a small front
                             matter block (--- key: value ---) then the body

Output
  English pages at the site root (/index.html, /label.html ...), every other
  language under its code (/de/, /fr/, /it/). Plus sitemap.xml.

Variables usable inside pages and partials:  {{root}} {{lang}} {{title}}
{{description}} {{path}} {{canonical}} {{alternates}} {{nav.<key>}}
{{footer.<key>}} {{year}}.  Body text is written directly in each language
file — no string tables for page copy, so translations read like prose.
"""
import json, re, sys, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
SITE = json.loads((SRC / "site.json").read_text(encoding="utf-8"))
BASE_URL = SITE["baseUrl"].rstrip("/")
LANGS = SITE["languages"]              # ordered list of codes, first = default
DEFAULT = LANGS[0]
PARTIALS = {p.stem: p.read_text(encoding="utf-8") for p in (SRC / "partials").glob("*.html")}

FRONT = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def parse_page(text):
    m = FRONT.match(text)
    if not m:
        raise SystemExit("page is missing its front matter block")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text[m.end():]


def lang_root(lang):
    return "/" if lang == DEFAULT else f"/{lang}/"


def render(template, ctx):
    def sub(m):
        key = m.group(1).strip()
        cur = ctx
        for part in key.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return m.group(0)          # leave unknown tokens visible
        return str(cur)
    return re.sub(r"\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}", sub, template)


def main():
    pages = {}   # (lang, relpath) -> (meta, body)
    for lang in LANGS:
        d = SRC / "pages" / lang
        if not d.exists():
            continue
        for f in d.rglob("*.html"):
            rel = f.relative_to(d).as_posix()
            pages[(lang, rel)] = parse_page(f.read_text(encoding="utf-8"))

    written, sitemap = [], []
    for (lang, rel), (meta, body) in pages.items():
        strings = SITE["strings"][lang]
        alternates_html, alternates = [], []
        for l in LANGS:
            if (l, rel) in pages:
                url = f"{BASE_URL}{lang_root(l)}{'' if rel == 'index.html' else rel}"
                alternates.append((l, url))
                alternates_html.append(f'<link rel="alternate" hreflang="{l}" href="{url}">')
        default_url = next((u for l, u in alternates if l == DEFAULT), None)
        if default_url:
            alternates_html.append(f'<link rel="alternate" hreflang="x-default" href="{default_url}">')

        canonical = f"{BASE_URL}{lang_root(lang)}{'' if rel == 'index.html' else rel}"
        ctx = {
            "root": lang_root(lang), "lang": lang, "path": rel, "canonical": canonical,
            "title": meta.get("title", "Friendly Spaces"),
            "description": meta.get("description", ""),
            "navActive": meta.get("nav", ""),
            "alternates": "\n".join(alternates_html),
            "altLinks": " ".join(f'{l}:{u}' for l, u in alternates),
            "year": str(datetime.date.today().year),
            "nav": strings["nav"], "footer": strings["footer"], "ui": strings["ui"],
        }
        html = (
            "<!doctype html>\n"
            f'<html lang="{lang}">\n<head>\n' + render(PARTIALS["head"], ctx) + "\n</head>\n"
            f'<body data-lang="{lang}" data-alternates="{ctx["altLinks"]}">\n'
            + render(PARTIALS["nav"], ctx) + "\n"
            + render(body, ctx) + "\n"
            + render(PARTIALS["footer"], ctx) + "\n"
            + render(PARTIALS["scripts"], ctx) + "\n</body>\n</html>\n"
        )
        # mark the active nav link
        html = html.replace(f'data-nav="{ctx["navActive"]}"', f'data-nav="{ctx["navActive"]}" aria-current="page"') if ctx["navActive"] else html

        out = ROOT / lang_root(lang).strip("/") / rel if lang != DEFAULT else ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8", newline="\n")
        written.append(out.relative_to(ROOT).as_posix())
        if meta.get("noindex", "").lower() != "true":
            sitemap.append((canonical, alternates))

    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for url, alts in sorted(sitemap):
        sm.append(f"  <url><loc>{url}</loc>")
        for l, u in alts:
            sm.append(f'    <xhtml:link rel="alternate" hreflang="{l}" href="{u}"/>')
        sm.append("  </url>")
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8", newline="\n")

    for w in written:
        print("built", w)
    print("built sitemap.xml")


if __name__ == "__main__":
    main()
