"""Export all visible website text of one language as simple HTML for a Google Doc.
Usage: python tools_site_text.py de out.html   (languages: en, de, fr)"""
import re, sys, html, json
from pathlib import Path
lang=sys.argv[1]; out=Path(sys.argv[2])
ROOT=Path("src/pages")/lang
ORDER=["index.html","label.html","playbox.html","partners.html","about.html","sponsoring.html","contact.html","news/index.html","privacy.html"]
NAMES={"en":{"index.html":"Homepage","label.html":"The Label","playbox.html":"PlayBox","partners.html":"Partners","about.html":"About","sponsoring.html":"Sponsoring","contact.html":"Contact","news/index.html":"News","privacy.html":"Privacy policy"},
       "de":{"index.html":"Startseite","label.html":"Das Label","playbox.html":"PlayBox","partners.html":"Partner","about.html":"Über uns","sponsoring.html":"Sponsoring","contact.html":"Kontakt","news/index.html":"News","privacy.html":"Datenschutz"},
       "fr":{"index.html":"Page d'accueil","label.html":"Le label","playbox.html":"PlayBox","partners.html":"Partenaires","about.html":"À propos","sponsoring.html":"Sponsoring","contact.html":"Contact","news/index.html":"News","privacy.html":"Confidentialité"}}
posts=sorted(p for p in (ROOT/"news").glob("*.html") if p.name!="index.html")
pages=ORDER+[f"news/{p.name}" for p in posts]
def esc(s): return html.escape(html.unescape(s.strip()))
def strings_json():
    d=json.loads(Path("src/site.json").read_text(encoding="utf-8"))["strings"][lang]
    rows=[]
    for grp in ("nav","footer"):
        for k,v in d[grp].items(): rows.append(f"<p>{grp}.{k}: {esc(v)}</p>")
    return rows
doc=[f"<h1>Friendly Spaces website, {lang.upper()} text</h1>",
     "<p><i>One block per page, in the order of the site. Headings mirror the page headings; bullets are list items; lines starting with → are buttons or links; [alt], [placeholder] and [option] mark image descriptions, form fields and dropdown choices. Meta title and description are what search engines show.</i></p>"]
for page in pages:
    f=ROOT/page
    if not f.exists(): continue
    t=f.read_text(encoding="utf-8")
    m=re.match(r"^---\s*\n(.*?)\n---\s*\n",t,re.S); meta={}; body=t
    if m:
        for line in m.group(1).splitlines():
            if ":" in line: k,v=line.split(":",1); meta[k.strip()]=v.strip()
        body=t[m.end():]
    name=NAMES[lang].get(page, meta.get("title","").split(" — ")[0].split(" - ")[0] or page)
    doc.append(f"<h1>{esc(name)}</h1>")
    doc.append(f"<p>Meta title: {esc(meta.get('title',''))}</p>")
    doc.append(f"<p>Meta description: {esc(meta.get('description',''))}</p>")
    body=re.sub(r"<style.*?</style>|<script.*?</script>|<svg.*?</svg>|<!--.*?-->","",body,flags=re.S)
    # attributes worth translating
    body=re.sub(r'<img[^>]*\balt="([^"]*)"[^>]*>',lambda m:f'<p>[alt] {m.group(1)}</p>' if m.group(1).strip() else '',body)
    body=re.sub(r'<(?:input|textarea)[^>]*\bplaceholder="([^"]*)"[^>]*>',lambda m:f'<p>[placeholder] {m.group(1)}</p>',body)
    body=re.sub(r'<iframe[^>]*\bdata-guard="([^"]*)"[^>]*>',lambda m:f'<p>[map overlay] {m.group(1)}</p>',body)
    body=re.sub(r'<option[^>]*>(.*?)</option>',lambda m:f'<p>[option] {m.group(1)}</p>',body,flags=re.S)
    body=re.sub(r'<label[^>]*>(.*?)</label>',lambda m:f'<p>[label] {m.group(1)}</p>',body,flags=re.S)
    body=re.sub(r'<(a|button)\b[^>]*class="[^"]*btn[^"]*"[^>]*>(.*?)</\1>',lambda m:f'<p>→ {m.group(2)}</p>',body,flags=re.S)
    body=re.sub(r'<h([1-4])[^>]*>(.*?)</h>',lambda m:f'<h{min(int(m.group(1))+1,4)}>{m.group(2)}</h{min(int(m.group(1))+1,4)}>',body,flags=re.S)
    body=re.sub(r'<span class="(?:eyebrow|chip|sticker|tag|price)"[^>]*>(.*?)</span>',lambda m:f'<p>[small label] {m.group(1)}</p>',body,flags=re.S)
    body=re.sub(r'<(summary|figcaption|time|dt|dd)[^>]*>(.*?)</\1>',lambda m:f'<p>{m.group(2)}</p>',body,flags=re.S)
    body=re.sub(r'<li[^>]*>(.*?)</li>',lambda m:f'<li>{m.group(1)}</li>',body,flags=re.S)
    body=re.sub(r'<br\s*/?>',' ',body)
    keep=[]
    for tag,inner in re.findall(r'<(h2|h3|h4|p|li)[^>]*>(.*?)</\1>',body,flags=re.S):
        txt=re.sub(r'<[^>]+>','',inner); txt=re.sub(r'\s+',' ',txt).strip()
        if not txt: continue
        keep.append(("li",txt) if tag=="li" else (tag,txt))
    # leftover text inside divs/spans not captured (e.g. fact cards, pack cards): grab text of elements with class pack/fact/crit
    for inner in re.findall(r'<div class="(?:pack|fact|packcard|crit|step-card|step|card|venue|post)[^"]*"[^>]*>(.*?)</div>',body,flags=re.S):
        pass
    i=0
    while i<len(keep):
        tag,txt=keep[i]
        if tag=="li":
            items=[]
            while i<len(keep) and keep[i][0]=="li": items.append(keep[i][1]); i+=1
            doc.append("<ul>"+"".join(f"<li>{esc(x)}</li>" for x in items)+"</ul>")
        else:
            doc.append(f"<{tag}>{esc(txt)}</{tag}>"); i+=1
doc.append("<h1>Menu and footer</h1>"); doc+=strings_json()
out.write_text("<html><body>"+"\n".join(doc)+"</body></html>",encoding="utf-8")
print(out, len(doc), "blocks")
