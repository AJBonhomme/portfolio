#!/usr/bin/env python3
"""Static site generator for the portfolio. Run: python3 build.py  ->  writes ../site/"""
import os, glob, html, shutil
from PIL import Image, ImageOps
from content import SITE, ABOUT, PROJECTS, HOME_INTRO

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
:root{
 --bg:#111113;--panel:#19191c;--panel2:#202024;
 --fg:#ededed;--body:#b4b4b8;--muted:#86868c;--rule:#26262a;--rule2:#34343a;
 --accent:#f2c14e;--blue:#38bdf8;
 --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,Helvetica,Arial,sans-serif;
 --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
 --wrap:1120px;--gut:clamp(18px,4vw,40px)
}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--sans);font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
img{max-width:100%;display:block;height:auto}
:focus-visible{outline:2px solid var(--fg);outline-offset:3px}
.wrap{max-width:var(--wrap);margin:0 auto;padding-left:var(--gut);padding-right:var(--gut)}
h1,h2,h3{font-weight:600;letter-spacing:-.01em;color:var(--fg)}

/* header */
.hdr .wrap{position:relative;display:flex;align-items:center;gap:24px;height:72px}
.brand{font-weight:600;font-size:17px;white-space:nowrap}
.nav{margin-left:auto;display:flex;align-items:center;gap:24px}
.nav a{font-size:15px;color:var(--muted);transition:color .15s}
.nav a:hover,.nav a.on{color:var(--fg)}
.menu{display:none;margin-left:auto;background:none;border:1px solid var(--rule2);border-radius:6px;color:var(--fg);font:inherit;font-size:14px;padding:6px 12px;cursor:pointer}
@media (max-width:760px){
 .menu{display:block}
 .nav{display:none;position:absolute;top:64px;left:0;right:0;z-index:20;flex-direction:column;align-items:stretch;gap:0;background:var(--bg);border-bottom:1px solid var(--rule);padding:0 var(--gut) 10px}
 .hdr.open .nav{display:flex}
 .nav a{padding:12px 0;border-top:1px solid var(--rule)}
}

/* buttons */
.cta{display:flex;flex-wrap:wrap;gap:10px}
.b{display:inline-block;font-size:15px;font-weight:500;padding:9px 16px;border:1px solid var(--rule2);border-radius:6px;color:var(--fg);transition:border-color .15s,background .15s}
.b:hover{border-color:var(--muted)}
.b.y{background:var(--fg);border-color:var(--fg);color:var(--bg)}
.b.y:hover{background:#fff}

/* home */
.intro{padding-top:48px;padding-bottom:40px}
.intro h1{font-size:clamp(28px,3.4vw,36px);line-height:1.2;margin:0 0 10px}
.intro p{color:var(--body);font-size:17px;max-width:620px;margin:0}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:40px 24px}
.card .ph{aspect-ratio:4/3;overflow:hidden;border-radius:6px;background:var(--panel)}
.card .ph img{width:100%;height:100%;object-fit:cover;transition:opacity .2s}
.card:hover .ph img{opacity:.85}
.card h3{font-size:17px;line-height:1.3;margin:14px 0 2px}
.card .ctx{font-size:14px;color:var(--muted);line-height:1.45}
@media (max-width:900px){.grid{grid-template-columns:1fr 1fr}}
@media (max-width:560px){.grid{grid-template-columns:1fr}}
.labnote{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;margin-top:56px;padding:18px 20px;border:1px solid var(--rule);border-radius:6px;color:var(--body);transition:border-color .15s}
.labnote b{color:var(--fg);font-weight:600}
.labnote:hover{border-color:var(--rule2)}
.labnote span:last-child{color:var(--fg);white-space:nowrap}

/* footer */
.foot{margin-top:96px;border-top:1px solid var(--rule)}
.foot .wrap{display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px 24px;padding-top:24px;padding-bottom:32px;font-size:14px;color:var(--muted)}
.foot .links{display:flex;flex-wrap:wrap;gap:8px 20px}
.foot a:hover{color:var(--fg)}

/* project page */
.back{display:inline-block;margin-top:28px;font-size:14px;color:var(--muted)}
.back:hover{color:var(--fg)}
.ptitle{margin:18px 0 28px}
.ptitle h1{font-size:clamp(28px,3.6vw,40px);line-height:1.15;margin:0 0 6px}
.ptitle p{margin:0;color:var(--muted);font-size:15px}
.pcover{border-radius:6px;overflow:hidden;background:var(--panel)}
.pcover img{width:100%;max-height:620px;object-fit:cover}
.lead{max-width:760px;margin:36px 0 0;font-size:18px;line-height:1.65;color:var(--fg)}
.lead p{margin:0 0 16px}
.sec{margin-top:52px}
.sec h2{font-size:22px;line-height:1.3;margin:0 0 12px}
.txt{max-width:760px;color:var(--body);font-size:16.5px;line-height:1.7}
.txt p{margin:0 0 14px}
.sec ul{max-width:760px;color:var(--body);margin:0 0 14px;padding-left:20px}
.sec ul li{margin:6px 0}
.imgs{display:grid;gap:14px;margin-top:20px}
.imgs.stack{grid-template-columns:1fr}
.imgs.pair{grid-template-columns:repeat(2,1fr)}
.imgs.triple{grid-template-columns:repeat(3,1fr)}
.imgs figure{margin:0}
.imgs .fr{background:var(--panel);border-radius:4px;overflow:hidden}
.imgs .fr img{cursor:zoom-in}
.imgs.pair .fr,.imgs.triple .fr{aspect-ratio:4/3}
.imgs.pair .fr img,.imgs.triple .fr img{width:100%;height:100%;object-fit:contain}
.imgs.stack .fr img{width:100%}
figcaption{font-size:13px;color:var(--muted);margin-top:8px;line-height:1.45}
.pn{display:flex;justify-content:space-between;gap:20px;margin-top:72px;padding-top:24px;border-top:1px solid var(--rule);font-size:15px}
.pn a{color:var(--body)}
.pn a:hover{color:var(--fg)}
.pn span{display:block;font-size:13px;color:var(--muted)}
.pn .nx{text-align:right}
@media (max-width:820px){.imgs.triple{grid-template-columns:1fr 1fr}}
@media (max-width:560px){
 .imgs.pair,.imgs.triple{grid-template-columns:1fr}
 .imgs.pair .fr,.imgs.triple .fr{aspect-ratio:auto}
 .imgs.pair .fr img,.imgs.triple .fr img{height:auto}
}

/* lightbox */
.lb{position:fixed;inset:0;z-index:100;background:rgba(0,0,0,.9);display:grid;place-items:center;padding:4vh 4vw;cursor:zoom-out}
.lb img{max-width:100%;max-height:92vh;object-fit:contain}
.lb button{position:absolute;top:14px;right:18px;background:none;border:0;color:#fff;font-size:28px;line-height:1;width:44px;height:44px;cursor:pointer}

/* about / contact */
.phead{padding-top:48px}
.phead h1{font-size:clamp(28px,3.6vw,40px);line-height:1.15;margin:0}
.phead .sub2{color:var(--body);font-size:17px;margin:10px 0 0;max-width:620px}
.ab-top{display:grid;grid-template-columns:320px 1fr;gap:44px;align-items:start;margin-top:32px}
.ab-top img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:6px}
.ab-top p{color:var(--body);font-size:17px;line-height:1.7;margin:0 0 16px}
.ab-top p:first-child{color:var(--fg)}
.ab-top .cta{margin-top:24px}
.gal{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:56px}
.gal img{aspect-ratio:1;object-fit:cover;width:100%;border-radius:4px}
@media (max-width:820px){.ab-top{grid-template-columns:1fr}.ab-top img{max-width:400px;aspect-ratio:4/3}}
@media (max-width:560px){.gal{grid-template-columns:1fr 1fr}}
.contact .rows{margin-top:32px;max-width:640px;border-top:1px solid var(--rule)}
.contact .rows a{display:grid;grid-template-columns:110px 1fr;gap:16px;padding:16px 0;border-bottom:1px solid var(--rule);font-size:17px}
.contact .rows a span{color:var(--muted)}
.contact .rows a:hover b{text-decoration:underline;text-underline-offset:3px}
.contact .rows a b{font-weight:500;word-break:break-word}

/* racetrack lab */
.labwrap{padding-top:40px}
.lab h1{font-size:clamp(28px,3.6vw,40px);line-height:1.15;margin:0 0 6px}
.lab .sub{color:var(--muted);font-size:15px;margin:0 0 14px}
.lab .intro{padding:0!important;max-width:760px;margin:0 0 24px;color:var(--body);font-size:16.5px;line-height:1.65}
.lab .intro p{margin:0;font-size:inherit}
.lab .intro b{color:var(--fg)}
.tracks{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-bottom:12px}
.tlabel{font-size:14px;color:var(--muted);margin-right:6px}
.chip{font:inherit;font-size:14px;color:var(--body);background:var(--panel);border:1px solid var(--rule2);border-radius:6px;padding:6px 11px;cursor:pointer}
.chip i{font-style:normal;color:var(--muted);font-size:12.5px;margin-left:6px}
.chip:hover{color:var(--fg)}
.chip.on{background:var(--fg);border-color:var(--fg);color:var(--bg)}
.chip.on i{color:#555}
.canvasbox{position:relative;border-radius:6px;overflow:hidden;background:#2a2f27}
#track{display:block;width:100%;height:auto;aspect-ratio:5/3;touch-action:none;cursor:crosshair}
.hint{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none;font-weight:600;font-size:20px;color:rgba(255,255,255,.65);text-align:center;padding:0 20px}
.dpad{display:none;grid-template-columns:repeat(4,1fr);gap:7px;margin-top:8px}
.dpad.show{display:grid}
@media (hover:hover) and (pointer:fine){.dpad.show{display:none}}
.dbtn{font:inherit;font-size:15px;font-weight:600;color:var(--fg);background:var(--panel2);border:1px solid var(--rule2);border-radius:6px;padding:16px 0;cursor:pointer;user-select:none;-webkit-user-select:none;touch-action:none}
.dbtn:active{background:var(--fg);color:var(--bg)}
.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:12px 0 14px}
.toolbar .grow{flex:1}
.btn{font:inherit;font-size:14px;font-weight:500;color:var(--fg);background:var(--panel);border:1px solid var(--rule2);border-radius:6px;padding:8px 13px;cursor:pointer}
.btn:hover:not(:disabled){border-color:var(--muted)}
.btn:disabled{opacity:.35;cursor:not-allowed}
.btn.primary{background:var(--fg);border-color:var(--fg);color:var(--bg);font-weight:600}
.btn.primary:hover:not(:disabled){background:#fff;border-color:#fff}
.btn.on{border-color:var(--fg)}
.scoreboard{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:6px;overflow:hidden;margin-bottom:16px}
.sb{background:var(--panel);padding:11px 14px;min-width:0;border-top:2px solid transparent}
.sb.you{border-top-color:var(--blue)}
.sb.ai{border-top-color:var(--accent)}
.sb span{display:block;font-size:13px;color:var(--muted);margin-bottom:2px}
.sb b{display:block;font-weight:600;font-size:22px;color:var(--fg);font-variant-numeric:tabular-nums;line-height:1.2}
.sb i{display:block;font-style:normal;font-size:12.5px;color:var(--muted);margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.panel{border:1px solid var(--rule);border-radius:6px;overflow:hidden;background:var(--panel);margin-bottom:12px}
.panel summary{padding:12px 16px;font-size:14.5px;font-weight:500;color:var(--fg);cursor:pointer}
.panel summary:hover{background:var(--panel2)}
.tuning{display:grid;grid-template-columns:repeat(4,1fr);gap:14px 24px;padding:6px 16px 18px}
.tune label{display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px}
.tune label .n{color:var(--muted)}
.tune label span:last-child{color:var(--fg);font-variant-numeric:tabular-nums}
.tune input{width:100%;accent-color:var(--fg)}
#pycode{display:block;width:100%;height:330px;background:#0c0c0e;color:#d8dde3;border:0;border-top:1px solid var(--rule);padding:14px 16px;font-family:var(--mono);font-size:12.5px;line-height:1.6;resize:vertical;outline:none;tab-size:4}
.codebar{display:flex;align-items:center;gap:10px;padding:12px 16px;border-top:1px solid var(--rule);flex-wrap:wrap}
.pyerr{font-family:var(--mono);font-size:12px;color:#f87171}
.pyerr.ok{color:#4ade80}
.panel .note{margin:0;padding:0 16px 16px;font-size:13.5px;color:var(--muted)}
.panel .note a{color:var(--fg);text-decoration:underline}
@media (max-width:1000px){.tuning{grid-template-columns:repeat(2,1fr)}}
@media (max-width:760px){
 .scoreboard{grid-template-columns:repeat(2,1fr)}
 .toolbar .grow{display:none}
 .toolbar .btn{flex:1 1 auto}
 #pycode{height:260px;font-size:11.5px}
 .hint{font-size:17px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#111113">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{og}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/style.css">
</head>
<body>
"""

SITE_JS = r"""
(function(){
  var lb = document.getElementById('lb');
  if (!lb) return;
  var li = lb.querySelector('img');
  var close = function(){ lb.hidden = true; li.removeAttribute('src'); document.body.style.overflow = ''; };
  document.querySelectorAll('.imgs img').forEach(function(im){
    im.addEventListener('click', function(){ li.src = im.currentSrc || im.src; li.alt = im.alt; lb.hidden = false; document.body.style.overflow = 'hidden'; });
  });
  lb.addEventListener('click', close);
  document.addEventListener('keydown', function(ev){ if (ev.key === 'Escape' && !lb.hidden) close(); });
})();
"""

def header(active):
    def nl(href, label, key):
        on = ' class="on"' if active == key else ""
        return f'<a href="{href}"{on}>{label}</a>'
    toggle = "var h=this.closest('.hdr');h.classList.toggle('open');this.setAttribute('aria-expanded',h.classList.contains('open'))"
    return (f'<header class="hdr"><div class="wrap">'
            f'<a class="brand" href="/">{e(SITE["name"])}</a>'
            f'<button class="menu" type="button" aria-expanded="false" onclick="{toggle}">Menu</button>'
            '<nav class="nav">'
            + nl("/", "Work", "work")
            + nl("/racetrack", "Racetrack Lab", "racetrack")
            + nl("/about", "About", "about")
            + nl("/contact", "Contact", "contact")
            + f'<a href="{e(SITE["resume"])}" target="_blank" rel="noopener">Résumé</a>'
            '</nav></div></header>\n')

def footer():
    import datetime
    links = (f'<a href="mailto:{e(SITE["email"])}">Email</a>'
             f'<a href="{e(SITE["linkedin"])}" target="_blank" rel="noopener">LinkedIn</a>'
             f'<a href="{e(SITE["github"])}" target="_blank" rel="noopener">GitHub</a>'
             f'<a href="{e(SITE["resume"])}" target="_blank" rel="noopener">Résumé</a>')
    return (f'<footer class="foot"><div class="wrap"><span>© {datetime.date.today().year} {e(SITE["name"])}</span>'
            f'<div class="links">{links}</div></div></footer>\n'
            '<div class="lb" id="lb" hidden><img alt=""><button type="button" aria-label="Close">×</button></div>\n'
            '<script>' + SITE_JS + '</script>\n</body>\n</html>\n')

def page(path, title, desc, active, body, og=""):
    with open(os.path.join(OUT, path), "w") as f:
        f.write(HEAD.format(title=e(title), desc=e(desc), og=e(og)))
        f.write(header(active))
        f.write("<main>\n" + body + "\n</main>\n")
        f.write(footer())

# ---- Home
cards = "".join(
    f'<a class="card" href="/{p["slug"]}">'
    f'<div class="ph"><img src="{cover_thumb(*p["cover"])}" alt="{e(p["title"])}" loading="lazy"></div>'
    f'<h3>{e(p["title"])}</h3><div class="ctx">{e(p.get("subtitle", ""))}</div></a>'
    for p in PROJECTS)
home = (f'<section class="wrap intro"><h1>{e(SITE["name"])}</h1><p>{e(HOME_INTRO)}</p></section>'
        f'<section class="wrap"><div class="grid">{cards}</div>'
        '<a class="labnote" href="/racetrack"><span><b>Racetrack Lab.</b> Draw a track and race a car '
        'driven by a Python path-following controller.</span><span>Try it →</span></a></section>')
page("index.html", f"{SITE['name']}", f"{SITE['name']}: {HOME_INTRO}",
     "work", home, og=cover_thumb(*PROJECTS[0]["cover"]))

# ---- Project pages
N = len(PROJECTS)
for i, p in enumerate(PROJECTS):
    b = ['<article class="wrap">',
         '<a class="back" href="/">← All work</a>',
         f'<div class="ptitle"><h1>{e(p["title"])}</h1><p>{e(p.get("subtitle", ""))}</p></div>',
         f'<div class="pcover"><img src="{img(*p["cover"])}" alt=""></div>',
         '<div class="lead">' + "".join(f"<p>{e(t)}</p>" for t in p["intro"]) + "</div>"]
    for s in p["sections"]:
        b.append('<section class="sec">')
        if s.get("heading"): b.append(f'<h2>{e(s["heading"])}</h2>')
        if s.get("text"): b.append('<div class="txt">' + "".join(f"<p>{e(t)}</p>" for t in s["text"]) + "</div>")
        if s.get("bullets"): b.append("<ul>" + "".join(f"<li>{e(t)}</li>" for t in s["bullets"]) + "</ul>")
        if s.get("images"):
            b.append(f'<div class="imgs {s.get("layout", "stack")}">')
            for deck, h, cap in s["images"]:
                b.append(f'<figure><div class="fr"><img src="{img(deck, h)}" alt="{e(cap)}" loading="lazy"></div>'
                         f'<figcaption>{e(cap)}</figcaption></figure>')
            b.append("</div>")
        b.append("</section>")
    prev, nxt = PROJECTS[(i - 1) % N], PROJECTS[(i + 1) % N]
    b.append('<nav class="pn">'
             f'<a href="/{prev["slug"]}"><span>Previous</span>← {e(prev["title"])}</a>'
             f'<a class="nx" href="/{nxt["slug"]}"><span>Next</span>{e(nxt["title"])} →</a>'
             '</nav></article>')
    page(f"{p['slug']}.html", f"{p['title']} · {SITE['name']}", p["intro"][0][:200], "work", "".join(b), og=img(*p["cover"]))

# ---- About
a = ['<section class="wrap phead"><h1>Hi, I’m Antoine.</h1></section>',
     '<article class="wrap"><div class="ab-top">'
     f'<img src="{img(*ABOUT["photo"], max_w=900)}" alt="{e(SITE["name"])}"><div>'
     + "".join(f"<p>{e(t)}</p>" for t in ABOUT["paragraphs"])
     + f'<div class="cta"><a class="b y" href="{e(SITE["resume"])}" target="_blank" rel="noopener">Résumé (PDF)</a>'
       '<a class="b" href="/contact">Contact</a></div></div></div>',
     '<div class="gal">' + "".join(f'<img src="{img(d, h, max_w=700)}" alt="" loading="lazy">' for d, h in ABOUT["gallery"]) + "</div>",
     "</article>"]
page("about.html", f"About · {SITE['name']}", ABOUT["paragraphs"][0], "about", "".join(a), og=img(*ABOUT["photo"], max_w=900))

# ---- Contact
rows = [("Email", SITE["email"], f"mailto:{SITE['email']}", False),
        ("Phone", SITE["phone"], f"tel:+1{SITE['phone'].replace(' ', '')}", False),
        ("LinkedIn", "linkedin.com/in/antoine-bonhomme", SITE["linkedin"], True),
        ("GitHub", "github.com/AJBonhomme", SITE["github"], True),
        ("Résumé", "PDF", SITE["resume"], True)]
c = ('<section class="wrap phead"><h1>Contact</h1>'
     '<p class="sub2">Email is the best way to reach me.</p></section>'
     '<section class="wrap contact"><div class="rows">'
     + "".join(f'<a href="{e(href)}"{" target=_blank rel=noopener" if ext else ""}><span>{e(k)}</span><b>{e(v)}</b></a>' for k, v, href, ext in rows)
     + "</div></section>")
page("contact.html", f"Contact · {SITE['name']}", "Get in touch with Antoine Bonhomme.", "contact", c)

# ---- Racetrack Lab
lab = open(os.path.join(HERE, "lab.html")).read()
lab = lab.replace("__LAB_SIM__", open(os.path.join(HERE, "lab_sim.py")).read())
lab = lab.replace("/lab_sim.py", "https://github.com/AJBonhomme/portfolio/blob/main/src/lab_sim.py")
page("racetrack.html", f"Racetrack Lab · {SITE['name']}",
     "Draw a racetrack with your mouse and watch a car driven by a live Python path-following controller try to lap it.",
     "racetrack", '<div class="wrap labwrap">' + lab + '</div>', og=cover_thumb(*next(p for p in PROJECTS if p["slug"] == "mesafsd-autonomous-go-kart")["cover"]))

# remove pages from earlier builds that no longer correspond to anything
expected = {"index.html", "about.html", "contact.html", "racetrack.html"} | {p["slug"] + ".html" for p in PROJECTS}
for stale in glob.glob(os.path.join(OUT, "*.html")):
    if os.path.basename(stale) not in expected:
        os.remove(stale)
        print("removed stale page:", os.path.basename(stale))

with open(os.path.join(OUT, "style.css"), "w") as f: f.write(CSS)
with open(os.path.join(OUT, "favicon.svg"), "w") as f:
    f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#111113"/><text x="32" y="42" font-family="Helvetica,Arial,sans-serif" font-weight="700" font-size="26" fill="#ededed" text-anchor="middle">AB</text></svg>')
with open(os.path.join(OUT, "vercel.json"), "w") as f:
    import json as _json
    f.write(_json.dumps({
        "cleanUrls": True,
        "redirects": [
            {"source": "/" + old, "destination": "/small-projects", "permanent": True}
            for old in ("obstacle-avoiding-rc-car", "rc-car-iterations", "handheld-distance-finder")
        ] + [
            # retired project pages
            {"source": "/" + old, "destination": "/bfr-engine-mount", "permanent": True}
            for old in ("feb-differential-mount", "feb-path-following-controller")
        ] + [
            # stable short link that always points at the current résumé file
            {"source": "/resume", "destination": SITE["resume"], "permanent": False},
        ],
    }, indent=2) + "\n")

# static assets (the résumé PDF) are copied verbatim to the site root
for asset in glob.glob(os.path.join(HERE, "assets", "*")):
    shutil.copy2(asset, os.path.join(OUT, os.path.basename(asset)))
    print("asset:", os.path.basename(asset))
print("built", OUT, "images:", len(os.listdir(IMG)))
