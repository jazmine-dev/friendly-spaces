"""Structure parity check: the DE and FR page sources must have the same tag skeleton
(tag name, class, id, href, src, style blocks) as the EN source. Text is ignored.
Run: python tools_parity.py   -> prints differences per page, exit 1 if any."""
import re, sys, difflib
from html.parser import HTMLParser
from pathlib import Path

PAGES = ["index.html","label.html","playbox.html","partners.html","about.html","sponsoring.html","contact.html","privacy.html","news/index.html"]
KEEP_ATTRS = ("class","id","href","src","type","name","value","for","action","method","datetime","data-nav","data-bg","width","height","viewBox","d")

class Skel(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False); self.out=[]; self.in_style=False; self.style=[]
    def handle_starttag(self, tag, attrs):
        a={k:v for k,v in attrs}
        keep=[(k,a[k]) for k in KEEP_ATTRS if k in a]
        # hrefs that differ only by language root or lang query are fine
        keep=[(k,re.sub(r'\?lang=\w+','?lang=X',v.replace('{{root}}','/').replace('//','/')) if isinstance(v,str) else v) for k,v in keep]
        self.out.append(("<%s %s>"%(tag,keep)))
        if tag=="style": self.in_style=True
    def handle_endtag(self, tag):
        self.out.append("</%s>"%tag)
        if tag=="style": self.in_style=False
    def handle_startendtag(self, tag, attrs): self.handle_starttag(tag, attrs)
    def handle_data(self, data):
        if self.in_style: self.style.append(data)
    def handle_comment(self, data): self.out.append("<!--%s-->"%re.sub(r'\s+',' ',data.strip())[:60])

def skel(path):
    text=Path(path).read_text(encoding="utf-8")
    body=re.sub(r"^---.*?---\s*\n","",text,count=1,flags=re.S)
    p=Skel(); p.feed(body); return p.out, "".join(p.style)

bad=0
for page in PAGES:
    en_out, en_style = skel(Path("src/pages/en")/page)
    for lang in ("de","fr"):
        f=Path("src/pages")/lang/page
        if not f.exists(): print(f"MISSING {f}"); bad+=1; continue
        out, style = skel(f)
        if out!=en_out:
            bad+=1; print(f"\n== {lang}/{page}: tag skeleton differs from en/{page}")
            for l in difflib.unified_diff(en_out,out,"en","%s"%lang,lineterm="",n=1): print("  "+l)
        if re.sub(r"\s+"," ",style)!=re.sub(r"\s+"," ",en_style):
            bad+=1; print(f"\n== {lang}/{page}: <style> block differs from en/{page}")
            for l in difflib.unified_diff(en_style.splitlines(),style.splitlines(),"en","%s"%lang,lineterm="",n=0): print("  "+l)
print("\nPARITY OK" if not bad else f"\n{bad} difference group(s)")
sys.exit(1 if bad else 0)
