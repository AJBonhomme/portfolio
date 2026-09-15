#!/usr/bin/env python3
"""Static site generator for the portfolio. Run: python3 build.py  ->  writes ../site/"""
import os, glob, html, shutil
from PIL import Image, ImageOps
from content import SITE, ABOUT, PROJECTS

HERE = os.path.dirname(os.path.abspath(__file__))
EXTRACT = os.environ.get("EXTRACT_DIR", "/home/claude/extract")
OUT = os.path.join(os.path.dirname(HERE), "site")
IMG = os.path.join(OUT, "img")
os.makedirs(IMG, exist_ok=True)

MAX_W = 1600

def find_src(deck, h):
    m = glob.glob(os.path.join(EXTRACT, deck, f"*_{h}.*"))
    if not m:
        raise SystemExit(f"missing image {deck}/{h}")
    return m[0]

_cache = {}
def img(deck, h, max_w=MAX_W):
    """Resize + convert to web JPEG, return site-relative path."""
    key = (deck, h, max_w)
    if key in _cache:
        return _cache[key]
    src = find_src(deck, h)
    name = f"{deck}-{h}{'-t' if max_w != MAX_W else ''}.jpg"
    dst = os.path.join(IMG, name)
    if not os.path.exists(dst):
        im = Image.open(src)
        im = ImageOps.exif_transpose(im)
        if im.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", im.size, (255, 255, 255))
            im = im.convert("RGBA"); bg.paste(im, mask=im.split()[-1]); im = bg
        else:
            im = im.convert("RGB")
        if im.width > max_w:
            im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
        im.save(dst, "JPEG", quality=84, optimize=True, progressive=True)
    _cache[key] = "/img/" + name
    return _cache[key]

def cover_thumb(deck, h):
    """Card thumbnail: center-cropped 4:3, 900px wide."""
    key = (deck, h, "cover")
    if key in _cache: return _cache[key]
    src = find_src(deck, h)
    name = f"{deck}-{h}-cover.jpg"
    dst = os.path.join(IMG, name)
    if not os.path.exists(dst):
        im = ImageOps.exif_transpose(Image.open(src))
        if im.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", im.size, (255, 255, 255)); im = im.convert("RGBA"); bg.paste(im, mask=im.split()[-1]); im = bg
        else: im = im.convert("RGB")
        im = ImageOps.fit(im, (900, 675), Image.LANCZOS, centering=(0.5, 0.45))
        im.save(dst, "JPEG", quality=84, optimize=True, progressive=True)
    _cache[key] = "/img/" + name
    return _cache[key]

e = html.escape

CSS = r"""
:root{--bg:#333333;--bg2:#2b2b2b;--fg:#eeeeee;--muted:#888888;--body:#bdbdbd;--rule:#474747;--accent:#f2c14e}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font-family:"Figtree","Helvetica Neue",Arial,sans-serif;font-size:16px;line-height:1.55}
a{color:inherit;text-decoration:none}
img{max-width:100%;display:block;height:auto}
.serif{font-family:"Lora",Georgia,"Times New Roman",serif}
.layout{display:flex;min-height:100vh}
.side{position:sticky;top:0;align-self:flex-start;height:100vh;overflow-y:auto;width:320px;flex:0 0 320px;padding:56px 24px 40px 64px;font-family:"Lora",Georgia,serif;scrollbar-width:thin}
.side .name{font-size:26px;line-height:1.15;color:#fff;display:block}
.side .tag{font-size:14.5px;color:#ddd;margin:16px 0 0;display:block}
.side nav{margin-top:56px}
.side nav a{display:block;font-size:14px;color:var(--muted);padding:4.5px 0;transition:color .15s}
.side nav a:hover,.side nav a.active{color:#fff}
.side .label{font-family:"Figtree",sans-serif;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--fg);margin:34px 0 8px}
.side .foot{margin-top:56px;font-family:"Figtree",sans-serif;font-size:12px;color:#666}
.side .foot a{color:#777}
.side .foot a:hover{color:#fff}
.side .mtoggle{display:none}
.main{flex:1;min-width:0;padding:42px 74px 90px 36px}
/* work grid */
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px 12px;max-width:1120px}
.card{display:block}
.card .ph{aspect-ratio:4/3;overflow:hidden;background:#222}
.card .ph img{width:100%;height:100%;object-fit:cover;transition:transform .5s ease,opacity .3s}
.card:hover .ph img{transform:scale(1.03)}
.card h3{font-family:"Lora",Georgia,serif;font-weight:400;font-size:15.5px;color:#fff;margin:14px 0 2px}
.card .yr{font-size:11px;font-weight:700;color:var(--muted);letter-spacing:.02em;margin-bottom:26px}
/* project page */
.proj{max-width:1120px}
.proj h1{font-size:30px;font-weight:700;letter-spacing:.02em;text-transform:uppercase;text-align:center;margin:36px 0 6px;color:#fff}
.proj .sub{text-align:center;color:var(--muted);font-size:14px;margin:0 0 44px;font-family:"Lora",Georgia,serif}
.proj .intro{max-width:860px;margin:0 auto 54px;text-align:center;color:var(--body);font-size:17px;line-height:1.65}
.proj .intro p{margin:0 0 22px}
.sec{margin:0 0 60px}
.sec h2{font-size:12.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#fff;text-align:center;margin:0 0 18px}
.sec h2::after{content:"";display:block;width:34px;height:2px;background:var(--accent);margin:12px auto 0}
.sec .txt{max-width:860px;margin:0 auto 30px;text-align:center;color:var(--body);font-size:16px;line-height:1.65}
.sec .txt p{margin:0 0 18px}
.sec ul{max-width:640px;margin:0 auto 30px;padding-left:22px;color:var(--body);text-align:left}
.sec ul li{margin:6px 0}
.imgs{display:grid;gap:12px}
.imgs.stack{grid-template-columns:1fr}
.imgs.pair{grid-template-columns:repeat(2,1fr)}
.imgs.triple{grid-template-columns:repeat(3,1fr)}
.imgs figure{margin:0}
.imgs .fr{background:#232323;overflow:hidden}
.imgs.stack .fr img{width:100%}
.imgs.pair .fr,.imgs.triple .fr{aspect-ratio:4/3}
.imgs.pair .fr img,.imgs.triple .fr img{width:100%;height:100%;object-fit:contain}
.imgs figcaption{font-size:12px;color:var(--muted);text-align:center;margin-top:8px}
.pn{display:flex;justify-content:space-between;gap:20px;border-top:1px solid var(--rule);padding-top:26px;margin-top:70px;font-family:"Lora",Georgia,serif;font-size:14px;color:var(--muted)}
.pn a:hover{color:#fff}
.pn span{display:block;font-family:"Figtree",sans-serif;font-size:10.5px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#666;margin-bottom:4px}
/* about */
.about{max-width:900px}
.about h1{font-size:30px;font-weight:700;letter-spacing:.02em;text-transform:uppercase;text-align:center;margin:36px 0 40px;color:#fff}
.about .hero{display:grid;grid-template-columns:300px 1fr;gap:40px;align-items:start;margin-bottom:50px}
.about .hero img{width:100%;aspect-ratio:3/4;object-fit:cover}
.about p{color:var(--body);font-size:16.5px;line-height:1.7;margin:0 0 18px}
.about h2{font-size:12.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#fff;margin:44px 0 16px}
.exp{border-top:1px solid var(--rule)}
.exp div{display:grid;grid-template-columns:1fr auto;gap:8px 20px;padding:13px 0;border-bottom:1px solid var(--rule);color:var(--body)}
.exp b{color:#fff;font-weight:600;display:block;font-family:"Lora",Georgia,serif}
.exp i{font-style:normal;color:var(--muted);font-size:14px;white-space:nowrap}
.skills div{padding:10px 0;border-bottom:1px solid var(--rule);color:var(--body)}
.skills b{color:#fff;font-weight:600;display:inline-block;min-width:190px}
.gal{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:20px}
.gal img{aspect-ratio:1;object-fit:cover;width:100%}
/* contact */
.contact{max-width:640px;margin:40px auto 0;text-align:center}
.contact h1{font-size:30px;font-weight:700;letter-spacing:.02em;text-transform:uppercase;margin:36px 0 26px;color:#fff}
.contact p{color:var(--body);font-size:17px;line-height:1.7}
.contact .rows{margin-top:36px;border-top:1px solid var(--rule)}
.contact .rows a,.contact .rows div{display:flex;justify-content:space-between;gap:16px;padding:16px 4px;border-bottom:1px solid var(--rule);font-size:16px;color:#fff}
.contact .rows span{color:var(--muted);font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;align-self:center}
.contact .rows a:hover{color:var(--accent)}
.top{display:block;text-align:center;margin-top:80px;font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#666}
.top:hover{color:#fff}
@media (max-width:1100px){.grid,.imgs.triple{grid-template-columns:repeat(2,1fr)}.main{padding:36px 40px 80px 30px}}
@media (max-width:760px){
 .layout{display:block}
 .side{position:static;height:auto;width:auto;flex:none;padding:28px 22px 6px;border-bottom:1px solid var(--rule)}
 .side .name{font-size:24px}
 .side nav{margin-top:18px}
 .side .mtoggle{display:block;background:none;border:0;padding:0;font-family:"Figtree",sans-serif;font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--fg);margin:14px 0 8px;cursor:pointer}
 .side .mtoggle::after{content:" ▾";color:var(--muted)}
 .side nav.open .mtoggle::after{content:" ▴"}
 .side .plist{display:none}
 .side nav.open .plist{display:block}
 .side .label{display:none}
 .side .foot{margin:14px 0 12px}
 .main{padding:26px 18px 60px}
 .grid,.imgs.pair,.imgs.triple{grid-template-columns:1fr}
 .imgs.pair .fr,.imgs.triple .fr{aspect-ratio:auto}
 .imgs.pair .fr img,.imgs.triple .fr img{height:auto;object-fit:unset}
 .proj h1,.about h1,.contact h1{font-size:23px}
 .about .hero{grid-template-columns:1fr}
 .about .hero img{aspect-ratio:4/3;max-height:380px}
 .gal{grid-template-columns:repeat(2,1fr)}
 .exp div{grid-template-columns:1fr}
 .exp i{white-space:normal}
}
"""

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{og}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;600;700&family=Lora:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
</head>
<body>
<div class="layout">
"""

def sidebar(active):
    links = "".join(
        f'<a href="/{p["slug"]}"{" class=active" if active == p["slug"] else ""}>{e(p["title"])}</a>'
        for p in PROJECTS)
    return f"""<aside class="side">
<a class="name" href="/">{e(SITE['name'])}</a>
<span class="tag">{e(SITE['tagline'])}</span>
<nav>
<a href="/about"{' class=active' if active=='about' else ''}>About Me</a>
<a href="/"{' class=active' if active=='work' else ''}>Work</a>
<a href="/contact"{' class=active' if active=='contact' else ''}>Contact</a>
<button class="mtoggle" type="button" onclick="this.parentNode.classList.toggle('open')">Projects</button>
<div class="plist"><div class="label">Work</div>
{links}
</div>
</nav>
<div class="foot"><a href="{e(SITE['resume'])}" target="_blank" rel="noopener">Resume ↗</a> &nbsp;·&nbsp; <a href="{e(SITE['linkedin'])}" target="_blank" rel="noopener">LinkedIn ↗</a></div>
</aside>
"""

FOOT = """<a class="top" href="#top">Back to top</a>
</main>
</div>
</body>
</html>
"""

def page(path, title, desc, active, body, og=""):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(HEAD.format(title=e(title), desc=e(desc), og=e(og)))
        f.write(sidebar(active))
        f.write('<main class="main" id="top">\n')
        f.write(body)
        f.write(FOOT)

# ---- Work grid (home)
cards = []
for p in PROJECTS:
    cards.append(f'''<a class="card" href="/{p["slug"]}"><div class="ph"><img src="{cover_thumb(*p["cover"])}" alt="{e(p["title"])}" loading="lazy"></div><h3>{e(p["title"])}</h3><div class="yr">{e(p["year"])}</div></a>''')
first_cover = cover_thumb(*PROJECTS[0]["cover"])
page("index.html", f"{SITE['name']} — Work", f"Engineering portfolio of {SITE['name']}, mechanical engineering student at UC Berkeley: autonomous robotics, subsea vehicles, powertrain design, microgrids and fabrication.", "work",
     '<div class="grid">' + "".join(cards) + "</div>\n", og=first_cover)

# ---- Project pages
for i, p in enumerate(PROJECTS):
    b = [f'<article class="proj"><h1>{e(p["title"])}</h1><p class="sub">{e(p.get("subtitle",""))} · {e(p["year"])}</p>']
    b.append('<div class="intro">' + "".join(f"<p>{e(t)}</p>" for t in p["intro"]) + "</div>")
    for s in p["sections"]:
        b.append('<section class="sec">')
        if s.get("heading"): b.append(f'<h2>{e(s["heading"])}</h2>')
        if s.get("text"): b.append('<div class="txt">' + "".join(f"<p>{e(t)}</p>" for t in s["text"]) + "</div>")
        if s.get("bullets"): b.append("<ul>" + "".join(f"<li>{e(t)}</li>" for t in s["bullets"]) + "</ul>")
        if s.get("images"):
            layout = s.get("layout", "stack")
            b.append(f'<div class="imgs {layout}">')
            for deck, h, cap in s["images"]:
                b.append(f'<figure><div class="fr"><img src="{img(deck,h)}" alt="{e(cap)}" loading="lazy"></div><figcaption>{e(cap)}</figcaption></figure>')
            b.append("</div>")
        b.append("</section>")
    prev = PROJECTS[i-1] if i > 0 else None
    nxt = PROJECTS[i+1] if i < len(PROJECTS)-1 else None
    b.append('<nav class="pn">')
    b.append(f'<a href="/{prev["slug"]}"><span>Previous</span>{e(prev["title"])}</a>' if prev else "<div></div>")
    b.append(f'<a href="/{nxt["slug"]}" style="text-align:right"><span>Next</span>{e(nxt["title"])}</a>' if nxt else "<div></div>")
    b.append("</nav></article>\n")
    page(f"{p['slug']}.html", f"{SITE['name']} — {p['title']}", p["intro"][0][:200], p["slug"], "".join(b), og=img(*p["cover"]))

# ---- About
a = [f'<article class="about"><h1>About Me</h1><div class="hero"><img src="{img(*ABOUT["photo"], max_w=900)}" alt="{e(SITE["name"])}"><div>']
a += [f"<p>{e(t)}</p>" for t in ABOUT["paragraphs"]]
a.append("</div></div>")
a.append("<h2>Experience</h2><div class=\"exp\">" + "".join(f"<div><div><b>{e(o)}</b>{e(r)}</div><i>{e(d)}</i></div>" for o, r, d in ABOUT["experience"]) + "</div>")
a.append("<h2>Technical Skills</h2><div class=\"skills\">" + "".join(f"<div><b>{e(k)}</b> {e(v)}</div>" for k, v in ABOUT["skills"].items()) + "</div>")
a.append("<h2>Education</h2><div class=\"exp\"><div><div><b>University of California, Berkeley</b>B.S. Mechanical Engineering · GPA 3.95 · Coursework: Thermodynamics, Engineering Stats &amp; Data Science, Internet-of-Things</div><i>Expected 2028</i></div></div>")
a.append('<div class="gal">' + "".join(f'<img src="{img(d,h,max_w=700)}" alt="" loading="lazy">' for d, h in ABOUT["gallery"]) + "</div></article>\n")
page("about.html", f"{SITE['name']} — About Me", ABOUT["paragraphs"][0], "about", "".join(a), og=img(*ABOUT["photo"], max_w=900))

# ---- Contact
c = f'''<article class="contact"><h1>Contact</h1>
<p>I'm always available to reach out — whether it's about a project, an internship, or robots in general.</p>
<div class="rows">
<a href="mailto:{e(SITE['email'])}"><span>Email</span>{e(SITE['email'])}</a>
<a href="tel:+1{SITE['phone'].replace(' ','')}"><span>Phone</span>{e(SITE['phone'])}</a>
<a href="{e(SITE['linkedin'])}" target="_blank" rel="noopener"><span>LinkedIn</span>linkedin.com/in/antoine-bonhomme</a>
<a href="{e(SITE['github'])}" target="_blank" rel="noopener"><span>GitHub</span>github.com/AJBonhomme</a>
<a href="{e(SITE['resume'])}" target="_blank" rel="noopener"><span>Resume</span>View resume ↗</a>
</div></article>
'''
page("contact.html", f"{SITE['name']} — Contact", "Get in touch with Antoine Bonhomme.", "contact", c)

with open(os.path.join(OUT, "style.css"), "w") as f: f.write(CSS)
with open(os.path.join(OUT, "favicon.svg"), "w") as f:
    f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#333"/><text x="32" y="43" font-family="Georgia,serif" font-size="32" fill="#fff" text-anchor="middle">AB</text></svg>')
with open(os.path.join(OUT, "vercel.json"), "w") as f:
    f.write('{\n  "cleanUrls": true\n}\n')
print("built", OUT, "images:", len(os.listdir(IMG)))
