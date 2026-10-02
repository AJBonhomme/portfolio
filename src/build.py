#!/usr/bin/env python3
"""Static site generator for the portfolio. Run: python3 build.py  ->  writes ../site/"""
import os, glob, html, shutil
from PIL import Image, ImageOps
from content import SITE, ABOUT, PROJECTS, HERO, STATS, FILTERS, TAGS

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
 --bg:#0b0c0e;--bg2:#101216;--panel:#14171c;--panel2:#1a1e24;
 --fg:#f3f4f6;--body:#b9c0ca;--muted:#7f8691;--rule:#22262d;--rule2:#323842;
 --accent:#f2c14e;--accent2:#ffd166;--blue:#38bdf8;
 --display:"Barlow Condensed","Arial Narrow",Impact,sans-serif;
 --sans:"Barlow","Helvetica Neue",Arial,sans-serif;
 --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
 --wrap:1200px;--gut:clamp(18px,4vw,48px)
}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:80px}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--sans);font-size:17px;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
img{max-width:100%;display:block;height:auto}
::selection{background:var(--accent);color:#111}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.wrap{max-width:var(--wrap);margin:0 auto;padding-left:var(--gut);padding-right:var(--gut)}
.kicker{font-family:var(--mono);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
.tag{font-family:var(--mono);font-size:10.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--body);border:1px solid var(--rule2);padding:3px 7px;white-space:nowrap}
.tags{display:flex;flex-wrap:wrap;gap:6px}

/* ---------- header ---------- */
.hdr{position:sticky;top:0;z-index:50;background:rgba(11,12,14,.84);backdrop-filter:saturate(140%) blur(10px);-webkit-backdrop-filter:saturate(140%) blur(10px);border-bottom:1px solid var(--rule)}
.hdr .wrap{position:relative;display:flex;align-items:center;gap:24px;height:64px}
.brand{display:flex;align-items:center;gap:12px;font-family:var(--display);font-weight:700;font-size:21px;letter-spacing:.05em;text-transform:uppercase;white-space:nowrap}
.plate{display:grid;place-items:center;width:34px;height:34px;background:var(--accent);color:#111;font-family:var(--display);font-weight:800;font-size:17px;clip-path:polygon(0 0,100% 0,100% 72%,72% 100%,0 100%)}
.nav{margin-left:auto;display:flex;align-items:center;gap:26px}
.nav a{position:relative;font-family:var(--mono);font-size:12.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--body);padding:6px 0;transition:color .15s}
.nav a:hover,.nav a.on{color:#fff}
.nav a.on::after{content:"";position:absolute;left:0;right:0;bottom:-3px;height:2px;background:var(--accent)}
.live{display:inline-block;width:7px;height:7px;border-radius:50%;background:#22c55e;margin-right:8px;vertical-align:1px;animation:ping 2s infinite}
@keyframes ping{0%{box-shadow:0 0 0 0 rgba(34,197,94,.55)}70%{box-shadow:0 0 0 7px rgba(34,197,94,0)}100%{box-shadow:0 0 0 0 rgba(34,197,94,0)}}
.nav .cv{border:1px solid var(--accent);color:var(--accent);padding:8px 13px}
.nav .cv:hover{background:var(--accent);color:#111}
.menu{display:none;margin-left:auto;background:none;border:1px solid var(--rule2);color:#fff;font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;padding:9px 13px;cursor:pointer}
@media (max-width:840px){
 .menu{display:block}
 .nav{display:none;position:absolute;top:64px;left:0;right:0;flex-direction:column;align-items:stretch;gap:0;background:var(--bg2);border-bottom:1px solid var(--rule);padding:4px var(--gut) 16px}
 .hdr.open .nav{display:flex}
 .nav a{padding:14px 0;border-bottom:1px solid var(--rule)}
 .nav a.on::after{display:none}
 .nav a.on{color:var(--accent)}
 .nav .cv{margin-top:14px;text-align:center;border-bottom:1px solid var(--accent)}
}

/* ---------- buttons ---------- */
.cta{display:flex;flex-wrap:wrap;gap:12px}
.b{display:inline-flex;align-items:center;gap:10px;font-family:var(--mono);font-size:12.5px;letter-spacing:.08em;text-transform:uppercase;padding:14px 20px;border:1px solid var(--rule2);color:#fff;transition:all .18s}
.b:hover{border-color:#fff}
.b.y{background:var(--accent);border-color:var(--accent);color:#111;font-weight:500}
.b.y:hover{background:var(--accent2);border-color:var(--accent2)}

/* ---------- home: hero ---------- */
.hero{position:relative;overflow:hidden;border-bottom:1px solid var(--rule);background-color:var(--bg);
 background-image:radial-gradient(900px 520px at 76% 42%,rgba(242,193,78,.09),transparent 62%),
  linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);
 background-size:auto,48px 48px,48px 48px}
.hero::after{content:"";position:absolute;inset:auto 0 0 0;height:120px;background:linear-gradient(180deg,transparent,var(--bg));pointer-events:none}
.hero .wrap{position:relative;z-index:1;display:grid;grid-template-columns:1.02fr .98fr;gap:40px;align-items:center;min-height:min(80vh,720px);padding-top:56px;padding-bottom:72px}
.hero h1{font-family:var(--display);font-weight:800;text-transform:uppercase;font-size:clamp(60px,9.4vw,132px);line-height:.84;letter-spacing:.005em;margin:18px 0 24px}
.hero h1 span{display:block;color:var(--accent)}
.lede{font-size:clamp(18px,1.7vw,21px);color:var(--body);max-width:560px;margin:0 0 32px;line-height:1.55}
.lede b{color:#fff;font-weight:600}
.track-wrap{position:relative}
.track{width:100%;height:auto;display:block;filter:drop-shadow(0 30px 60px rgba(0,0,0,.5))}
.rline{stroke-dasharray:100;stroke-dashoffset:100;animation:draw 2.6s .35s cubic-bezier(.6,0,.2,1) forwards}
@keyframes draw{to{stroke-dashoffset:0}}
.track text{font-family:var(--mono);font-size:11px;fill:var(--muted);letter-spacing:.08em}
.legend{display:flex;flex-wrap:wrap;gap:8px 20px;margin-top:6px;font-family:var(--mono);font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.legend i{display:inline-block;width:12px;height:6px;margin-right:8px;vertical-align:2px}
@media (max-width:900px){.hero .wrap{grid-template-columns:1fr;min-height:0;padding-top:40px;padding-bottom:48px}.track-wrap{max-width:560px}}

/* ---------- home: stats ---------- */
.stats{border-bottom:1px solid var(--rule)}
.stats .wrap{display:grid;grid-template-columns:repeat(4,1fr)}
.stat{padding:30px 24px 32px;border-left:1px solid var(--rule)}
.stat:first-child{border-left:0;padding-left:0}
.stat b{display:block;font-family:var(--display);font-weight:700;font-size:clamp(44px,5vw,62px);line-height:1;color:#fff}
.stat b em{font-style:normal;color:var(--accent);font-size:.55em;vertical-align:.55em;margin-left:2px}
.stat span{display:block;font-family:var(--mono);font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-top:12px;line-height:1.5}
@media (max-width:760px){.stats .wrap{grid-template-columns:1fr 1fr}.stat{padding:22px 16px 24px}.stat:nth-child(odd){border-left:0;padding-left:0}.stat:nth-child(n+3){border-top:1px solid var(--rule)}}

/* ---------- home: work ---------- */
.shead{display:flex;align-items:flex-end;justify-content:space-between;gap:20px 30px;flex-wrap:wrap;margin:80px 0 28px}
.shead h2{font-family:var(--display);font-weight:700;text-transform:uppercase;font-size:clamp(38px,5vw,60px);line-height:.95;margin:10px 0 0}
.filters{display:flex;flex-wrap:wrap;gap:6px}
.f{font-family:var(--mono);font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--body);background:transparent;border:1px solid var(--rule2);padding:9px 13px;cursor:pointer;transition:all .15s}
.f:hover{color:#fff;border-color:#fff}
.f.on{background:var(--accent);border-color:var(--accent);color:#111}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.card{position:relative;display:flex;flex-direction:column;background:var(--panel);border:1px solid var(--rule);transition:border-color .2s,transform .25s}
.card:hover{border-color:var(--rule2);transform:translateY(-4px)}
.card[hidden]{display:none}
.card .ph{position:relative;aspect-ratio:4/3;overflow:hidden;background:#0e1013}
.card .ph img{width:100%;height:100%;object-fit:cover;transition:transform .7s cubic-bezier(.2,.7,.2,1)}
.card:hover .ph img{transform:scale(1.05)}
.card .no,.card .yr{position:absolute;top:12px;font-family:var(--mono);font-size:11px;letter-spacing:.08em;background:rgba(11,12,14,.8);color:#fff;padding:5px 8px}
.card .no{left:12px}.card .yr{right:12px;color:var(--body)}
.card .bd{display:flex;flex-direction:column;gap:8px;flex:1;padding:18px 18px 20px}
.card h3{font-family:var(--display);font-weight:700;text-transform:uppercase;font-size:26px;line-height:1;margin:0;letter-spacing:.01em}
.card .ctx{font-size:14.5px;color:var(--muted);line-height:1.4}
.card .tags{margin-top:auto;padding-top:10px}
.card::after{content:"";position:absolute;left:-1px;right:-1px;bottom:-1px;height:3px;background:var(--accent);transform:scaleX(0);transform-origin:left;transition:transform .35s}
.card:hover::after{transform:scaleX(1)}
@media (max-width:1000px){.grid{grid-template-columns:1fr 1fr}}
@media (max-width:620px){.grid{grid-template-columns:1fr}}

/* ---------- home: racetrack promo ---------- */
.promo{margin-top:84px;border:1px solid var(--rule);background:linear-gradient(115deg,#1b170b 0%,var(--panel) 58%);overflow:hidden}
.promo .in{display:grid;grid-template-columns:1.25fr .75fr;gap:40px;align-items:center;padding:clamp(26px,4vw,48px)}
.promo h2{font-family:var(--display);font-weight:800;text-transform:uppercase;font-size:clamp(36px,4.8vw,62px);line-height:.92;margin:12px 0 16px}
.promo h2 em{font-style:normal;color:var(--accent)}
.promo p{color:var(--body);margin:0 0 26px;max-width:540px}
.tower{background:#0d0f12;border:1px solid var(--rule2);font-family:var(--mono);font-size:13px}
.tower .th{padding:10px 14px;font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--rule2)}
.tower .row{display:grid;grid-template-columns:34px 1fr auto;gap:10px;align-items:center;padding:12px 14px;border-bottom:1px solid var(--rule)}
.tower .row:last-child{border-bottom:0}
.tower .row span{color:var(--muted)}
.tower .row b{font-weight:500;color:#fff;text-transform:uppercase;letter-spacing:.04em}
.tower .row i{font-style:normal;color:#fff;font-variant-numeric:tabular-nums}
.tower .ai{box-shadow:inset 3px 0 0 var(--accent)}
.tower .you{box-shadow:inset 3px 0 0 var(--blue)}
.tower .you i{color:var(--blue);animation:blink 1.1s steps(2) infinite}
@keyframes blink{50%{opacity:.25}}
@media (max-width:820px){.promo .in{grid-template-columns:1fr}}

/* ---------- footer ---------- */
.foot{margin-top:110px;border-top:1px solid var(--rule);background:var(--bg2)}
.foot .wrap{padding-top:64px;padding-bottom:36px}
.foot h2{font-family:var(--display);font-weight:800;text-transform:uppercase;font-size:clamp(44px,7.5vw,104px);line-height:.88;margin:12px 0 30px}
.foot h2 a{transition:color .2s}
.foot h2 a:hover{color:var(--accent)}
.foot .links{display:flex;flex-wrap:wrap;gap:12px 30px;font-family:var(--mono);font-size:13px;letter-spacing:.06em;text-transform:uppercase}
.foot .links a{color:var(--body)}
.foot .links a:hover{color:var(--accent)}
.foot .small{display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px 20px;margin-top:56px;padding-top:20px;border-top:1px solid var(--rule);font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.foot .small a:hover{color:#fff}

/* ---------- project page ---------- */
.phero{position:relative;height:min(62vh,600px);min-height:380px;overflow:hidden;border-bottom:1px solid var(--rule);background:#0e1013}
.phero img{width:100%;height:100%;object-fit:cover;object-position:center 42%}
.phero::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,12,14,.35) 0%,rgba(11,12,14,.05) 30%,rgba(11,12,14,.86) 80%,var(--bg) 100%)}
.phero .wrap{position:absolute;left:0;right:0;bottom:0;z-index:1;padding-bottom:34px}
.phero h1{font-family:var(--display);font-weight:800;text-transform:uppercase;font-size:clamp(46px,7.6vw,108px);line-height:.86;margin:14px 0 0;text-shadow:0 2px 34px rgba(0,0,0,.55);max-width:14ch}
.meta{border-bottom:1px solid var(--rule)}
.meta .wrap{display:grid;grid-template-columns:1.5fr .5fr 1.4fr;gap:24px}
.mcell{padding:20px 0 22px}
.mcell span{display:block;font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
.mcell b{font-weight:500;color:#fff;font-size:16px;line-height:1.4}
.lead{max-width:880px;margin:56px 0 0;font-size:clamp(19px,1.9vw,22px);line-height:1.6;color:#e5e8ec}
.lead p{margin:0 0 18px}
.sec{margin-top:68px;padding-top:28px;border-top:1px solid var(--rule)}
.sec .sh{display:flex;align-items:baseline;gap:16px;margin:0 0 20px}
.sec .num{font-family:var(--mono);font-size:13px;color:var(--accent);letter-spacing:.08em}
.sec h2{font-family:var(--display);font-weight:700;text-transform:uppercase;font-size:clamp(30px,3.4vw,42px);line-height:1;margin:0}
.txt{max-width:840px;color:var(--body);font-size:17px;line-height:1.72}
.txt p{margin:0 0 16px}
.sec ul,.role ul{list-style:none;padding:0;margin:0 0 18px;max-width:840px;color:var(--body)}
.sec ul li,.role ul li{position:relative;padding-left:24px;margin:9px 0}
.sec ul li::before,.role ul li::before{content:"";position:absolute;left:0;top:.72em;width:12px;height:2px;background:var(--accent)}
.imgs{display:grid;gap:14px;margin-top:26px}
.imgs.stack{grid-template-columns:1fr}
.imgs.pair{grid-template-columns:repeat(2,1fr)}
.imgs.triple{grid-template-columns:repeat(3,1fr)}
.imgs figure{margin:0}
.imgs .fr{background:#0f1114;border:1px solid var(--rule);overflow:hidden}
.imgs .fr img{cursor:zoom-in;transition:opacity .2s}
.imgs .fr img:hover{opacity:.88}
.imgs.pair .fr,.imgs.triple .fr{aspect-ratio:4/3}
.imgs.pair .fr img,.imgs.triple .fr img{width:100%;height:100%;object-fit:contain}
.imgs.stack .fr img{width:100%}
figcaption{font-family:var(--mono);font-size:11.5px;color:var(--muted);margin-top:9px;line-height:1.5}
figcaption b{color:var(--accent);font-weight:500;margin-right:8px}
.pn{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:96px}
.pn a{display:flex;align-items:center;gap:16px;background:var(--panel);border:1px solid var(--rule);padding:14px;transition:border-color .2s}
.pn a:hover{border-color:var(--accent)}
.pn img{width:132px;flex:0 0 132px;aspect-ratio:4/3;object-fit:cover}
.pn span{display:block;font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-bottom:6px}
.pn b{display:block;font-family:var(--display);font-weight:700;text-transform:uppercase;font-size:24px;line-height:1.02}
.pn .nx{flex-direction:row-reverse;text-align:right}
@media (max-width:900px){.imgs.triple{grid-template-columns:1fr 1fr}.meta .wrap{grid-template-columns:1fr 1fr}.mcell:last-child{grid-column:1/-1;padding-top:0}}
@media (max-width:620px){
 .imgs.pair,.imgs.triple{grid-template-columns:1fr}
 .imgs.pair .fr,.imgs.triple .fr{aspect-ratio:auto}
 .imgs.pair .fr img,.imgs.triple .fr img{height:auto}
 .pn{grid-template-columns:1fr}.pn img{width:96px;flex-basis:96px}
}

/* ---------- lightbox ---------- */
.lb{position:fixed;inset:0;z-index:100;background:rgba(5,6,8,.93);display:grid;place-items:center;padding:4vh 4vw;cursor:zoom-out}
.lb img{max-width:100%;max-height:92vh;object-fit:contain;box-shadow:0 20px 80px rgba(0,0,0,.6)}
.lb button{position:absolute;top:16px;right:20px;background:none;border:1px solid var(--rule2);color:#fff;font-size:22px;line-height:1;width:44px;height:44px;cursor:pointer}

/* ---------- inner page heads (about / contact) ---------- */
.phead{padding-top:72px}
.phead h1{font-family:var(--display);font-weight:800;text-transform:uppercase;font-size:clamp(56px,9vw,124px);line-height:.86;margin:14px 0 0}
.phead .sub2{max-width:640px;color:var(--body);font-size:19px;margin:22px 0 0}

/* ---------- about ---------- */
.ab-top{display:grid;grid-template-columns:340px 1fr;gap:48px;align-items:start;margin-top:44px}
.ab-top img{width:100%;aspect-ratio:4/5;object-fit:cover;border:1px solid var(--rule)}
.ab-top p{color:var(--body);font-size:18px;line-height:1.7;margin:0 0 18px}
.ab-top p:first-child{color:#e9ebee;font-size:21px;line-height:1.55}
.ab-top .cta{margin-top:26px}
.ab h2{font-family:var(--display);font-weight:700;text-transform:uppercase;font-size:clamp(32px,3.8vw,46px);line-height:1;margin:80px 0 18px}
.roles{border-top:1px solid var(--rule)}
.role{padding:24px 0;border-bottom:1px solid var(--rule)}
.role .hd{display:flex;justify-content:space-between;align-items:baseline;gap:20px}
.role .hd b{display:block;font-family:var(--display);font-weight:700;text-transform:uppercase;font-size:26px;line-height:1.05;color:#fff}
.role .rl{display:block;font-family:var(--mono);font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin-top:6px}
.role .hd i{font-style:normal;font-family:var(--mono);font-size:12.5px;color:var(--muted);white-space:nowrap}
.role h4{margin:16px 0 0;font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.role ul{margin-top:8px;font-size:16px;line-height:1.6}
.role .edd{margin:10px 0 0;color:var(--body)}
.rlinks{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}
.rlinks a{font-family:var(--mono);font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);border:1px solid var(--rule2);padding:7px 11px;transition:border-color .15s}
.rlinks a:hover{border-color:var(--accent)}
.skills{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.skills>div{background:var(--panel);border:1px solid var(--rule);padding:20px}
.skills>div>b{display:block;font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);margin-bottom:12px}
.gal{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:80px}
.gal img{aspect-ratio:1;object-fit:cover;width:100%;border:1px solid var(--rule)}
@media (max-width:900px){.ab-top{grid-template-columns:1fr}.ab-top img{max-width:420px;aspect-ratio:4/3}.skills{grid-template-columns:1fr}}
@media (max-width:620px){.role .hd{flex-direction:column;gap:6px}.role .hd i{white-space:normal}.gal{grid-template-columns:1fr 1fr}}

/* ---------- contact ---------- */
.contact .rows{margin-top:48px;border-top:1px solid var(--rule)}
.contact .rows a{display:grid;grid-template-columns:150px 1fr auto;align-items:center;gap:20px;padding:24px 0;border-bottom:1px solid var(--rule);transition:color .15s}
.contact .rows a span{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.contact .rows a b{font-family:var(--display);font-weight:600;font-size:clamp(24px,3.2vw,40px);line-height:1.1;word-break:break-word}
.contact .rows a::after{content:"↗";font-family:var(--mono);font-size:18px;color:var(--muted)}
.contact .rows a:hover{color:var(--accent)}
.contact .rows a:hover::after{color:var(--accent)}
@media (max-width:620px){.contact .rows a{grid-template-columns:1fr auto}.contact .rows a span{grid-column:1/-1}}

/* ---------- racetrack lab ---------- */
.labwrap{padding-top:56px}
.lab h1{font-family:var(--display);font-weight:800;text-transform:uppercase;font-size:clamp(52px,8vw,112px);line-height:.86;margin:0 0 14px}
.lab .sub{font-family:var(--mono);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin:0 0 18px}
.lab .intro{max-width:820px;margin:0 0 26px;color:var(--body);font-size:17.5px;line-height:1.65}
.lab .intro p{margin:0}
.lab .intro b{color:#fff}
.tracks{display:flex;flex-wrap:wrap;align-items:center;gap:7px;margin-bottom:12px}
.tlabel{font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-right:6px}
.chip{font-family:var(--mono);font-size:12px;letter-spacing:.03em;color:var(--body);background:var(--panel);border:1px solid var(--rule2);padding:8px 12px;cursor:pointer;transition:all .15s}
.chip i{font-style:normal;color:var(--muted);font-size:11px;margin-left:6px}
.chip:hover{color:#fff;border-color:#fff}
.chip.on{background:var(--accent);border-color:var(--accent);color:#111}
.chip.on i{color:#5a4510}
.canvasbox{position:relative;border:1px solid var(--rule2);background:#2a2f27}
#track{display:block;width:100%;height:auto;aspect-ratio:5/3;touch-action:none;cursor:crosshair}
.hint{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none;font-family:var(--display);font-weight:600;text-transform:uppercase;letter-spacing:.04em;font-size:24px;color:rgba(255,255,255,.6);text-align:center;padding:0 20px}
.dpad{display:none;grid-template-columns:repeat(4,1fr);gap:7px;margin-top:8px}
.dpad.show{display:grid}
@media (hover:hover) and (pointer:fine){.dpad.show{display:none}}
.dbtn{font-family:var(--mono);font-size:14px;font-weight:500;color:#fff;background:var(--panel2);border:1px solid var(--rule2);padding:16px 0;cursor:pointer;user-select:none;-webkit-user-select:none;touch-action:none}
.dbtn:active{background:var(--accent);color:#111}
.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin:12px 0 14px}
.toolbar .grow{flex:1}
.btn{font-family:var(--mono);font-size:12px;font-weight:500;letter-spacing:.05em;text-transform:uppercase;color:var(--fg);background:var(--panel);border:1px solid var(--rule2);padding:10px 14px;cursor:pointer;transition:all .15s}
.btn:hover:not(:disabled){border-color:#fff;color:#fff}
.btn:disabled{opacity:.35;cursor:not-allowed}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#111;font-weight:600}
.btn.primary:hover:not(:disabled){background:var(--accent2);border-color:var(--accent2);color:#111}
.btn.on{border-color:var(--accent);color:var(--accent)}
.scoreboard{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--rule);border:1px solid var(--rule);margin-bottom:16px}
.sb{background:var(--panel);padding:13px 16px;min-width:0;border-top:2px solid transparent}
.sb.you{border-top-color:var(--blue)}
.sb.ai{border-top-color:var(--accent)}
.sb span{display:block;font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-bottom:4px}
.sb b{display:block;font-family:var(--display);font-weight:600;font-size:26px;color:#fff;font-variant-numeric:tabular-nums;line-height:1.08}
.sb i{display:block;font-style:normal;font-family:var(--mono);font-size:11.5px;color:var(--muted);margin-top:3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.panel{border:1px solid var(--rule);background:var(--panel);margin-bottom:12px}
.panel summary{padding:14px 16px;font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:#fff;cursor:pointer;list-style:none}
.panel summary::-webkit-details-marker{display:none}
.panel summary::before{content:"▸ ";color:var(--accent)}
.panel[open] summary::before{content:"▾ "}
.panel summary:hover{background:var(--panel2)}
.tuning{display:grid;grid-template-columns:repeat(4,1fr);gap:14px 24px;padding:6px 16px 18px}
.tune label{display:flex;justify-content:space-between;font-family:var(--mono);font-size:11px;letter-spacing:.05em;text-transform:uppercase;margin-bottom:6px}
.tune label .n{color:var(--muted)}
.tune label span:last-child{color:var(--accent);font-variant-numeric:tabular-nums}
.tune input{width:100%;accent-color:var(--accent)}
#pycode{display:block;width:100%;height:330px;background:#0d0f12;color:#d8dde3;border:0;border-top:1px solid var(--rule);padding:14px 16px;font-family:var(--mono);font-size:12.5px;line-height:1.6;resize:vertical;outline:none;tab-size:4}
.codebar{display:flex;align-items:center;gap:10px;padding:12px 16px;border-top:1px solid var(--rule);flex-wrap:wrap}
.pyerr{font-family:var(--mono);font-size:11.5px;color:#f87171}
.pyerr.ok{color:#4ade80}
.panel .note{margin:0;padding:0 16px 16px;font-size:13px;color:var(--muted)}
.panel .note a{color:var(--accent);text-decoration:underline}
@media (max-width:1000px){.tuning{grid-template-columns:repeat(2,1fr)}}
@media (max-width:760px){
 .scoreboard{grid-template-columns:repeat(2,1fr)}
 .toolbar .grow{display:none}
 .toolbar .btn{flex:1 1 auto}
 #pycode{height:260px;font-size:11.5px}
 .hint{font-size:18px}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}.rline{stroke-dashoffset:0}}
"""

FONTS = "https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Barlow:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0b0c0e">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{og}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fonts}" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
</head>
<body>
"""

SITE_JS = r"""
(function(){
  // work filters
  var fs = document.querySelectorAll('.f[data-f]');
  fs.forEach(function(b){ b.addEventListener('click', function(){
    fs.forEach(function(x){ x.classList.toggle('on', x === b); });
    var k = b.dataset.f, n = 0;
    document.querySelectorAll('.card[data-cats]').forEach(function(c){
      var show = k === 'all' || c.dataset.cats.split(' ').indexOf(k) !== -1;
      c.hidden = !show; if (show) n++;
    });
    var cnt = document.getElementById('wcount');
    if (cnt) cnt.textContent = (n < 10 ? '0' : '') + n + (n === 1 ? ' project' : ' projects');
  }); });
  // image lightbox
  var lb = document.getElementById('lb');
  if (lb) {
    var li = lb.querySelector('img');
    var close = function(){ lb.hidden = true; li.removeAttribute('src'); document.body.style.overflow = ''; };
    document.querySelectorAll('.imgs img').forEach(function(im){
      im.addEventListener('click', function(){ li.src = im.currentSrc || im.src; li.alt = im.alt; lb.hidden = false; document.body.style.overflow = 'hidden'; });
    });
    lb.addEventListener('click', close);
    document.addEventListener('keydown', function(ev){ if (ev.key === 'Escape' && !lb.hidden) close(); });
  }
  // respect reduced motion for the SVG circuit (SMIL ignores CSS)
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.querySelectorAll('svg.track').forEach(function(s){ if (s.pauseAnimations) s.pauseAnimations(); });
  }
})();
"""

def header(active):
    def nl(href, label, key, pre=""):
        on = ' class="on"' if active == key else ""
        return f'<a href="{href}"{on}>{pre}{label}</a>'
    toggle = "var h=this.closest('.hdr');h.classList.toggle('open');this.setAttribute('aria-expanded',h.classList.contains('open'))"
    return (f'<header class="hdr" id="top"><div class="wrap">'
            f'<a class="brand" href="/"><span class="plate">AB</span><span>{e(SITE["name"])}</span></a>'
            f'<button class="menu" type="button" aria-expanded="false" onclick="{toggle}">Menu</button>'
            '<nav class="nav">'
            + nl("/", "Work", "work")
            + nl("/racetrack", "Racetrack Lab", "racetrack", '<i class="live"></i>')
            + nl("/about", "About", "about")
            + nl("/contact", "Contact", "contact")
            + f'<a class="cv" href="{e(SITE["resume"])}" target="_blank" rel="noopener">Résumé ↗</a>'
            '</nav></div></header>\n')

def footer(cta=True):
    import datetime
    big = (f'<div class="kicker">Get in touch</div>'
           f'<h2><a href="mailto:{e(SITE["email"])}">Let’s build<br>something.</a></h2>') if cta else ""
    links = (f'<a href="mailto:{e(SITE["email"])}">Email</a>'
             f'<a href="{e(SITE["linkedin"])}" target="_blank" rel="noopener">LinkedIn ↗</a>'
             f'<a href="{e(SITE["github"])}" target="_blank" rel="noopener">GitHub ↗</a>'
             f'<a href="{e(SITE["resume"])}" target="_blank" rel="noopener">Résumé ↗</a>'
             '<a href="/racetrack">Race the AI →</a>')
    return (f'<footer class="foot"><div class="wrap">{big}<div class="links">{links}</div>'
            f'<div class="small"><span>© {datetime.date.today().year} {e(SITE["name"])}</span>'
            f'<span>{e(SITE["tagline"])}</span><a href="#top">Back to top ↑</a></div></div></footer>\n'
            '<div class="lb" id="lb" hidden><img alt=""><button type="button" aria-label="Close">×</button></div>\n'
            '<script>' + SITE_JS + '</script>\n</body>\n</html>\n')

def page(path, title, desc, active, body, og="", cta=True):
    with open(os.path.join(OUT, path), "w") as f:
        f.write(HEAD.format(title=e(title), desc=e(desc), og=e(og), fonts=FONTS))
        f.write(header(active))
        f.write("<main>\n" + body + "\n</main>\n")
        f.write(footer(cta))

def tag_html(tags):
    return "".join(f'<span class="tag">{e(t)}</span>' for t in tags)

# ---- the animated circuit in the hero: AI (yellow) laps the human car (blue)
TRACK_D = ("M120 360 C60 360 50 280 100 250 C150 220 150 160 110 130 C70 100 110 50 170 60 "
           "C260 75 360 62 440 68 C520 74 575 80 580 125 C585 170 540 195 480 192 "
           "C420 189 385 225 425 268 C465 311 590 290 588 360 C586 430 530 432 455 422 "
           "C380 412 200 360 120 360 Z")

def track_svg():
    def car(fill, dur, begin):
        return (f'<g><rect x="-10" y="-5" width="20" height="10" rx="2" fill="{fill}"/>'
                '<rect x="2" y="-3.2" width="4.5" height="6.4" fill="#0b0c0e" opacity=".6"/>'
                f'<animateMotion dur="{dur}" begin="{begin}" repeatCount="indefinite" rotate="auto">'
                '<mpath href="#trk"/></animateMotion></g>')
    checker = "".join(
        f'<rect x="{c*5}" y="{-17 + r*5.67:.2f}" width="5" height="5.67" fill="{"#f3f4f6" if (r+c) % 2 == 0 else "#0b0c0e"}"/>'
        for r in range(6) for c in range(2))
    labels = "".join(f'<text x="{x}" y="{y}">{t}</text>' for t, x, y in
                     [("T1", 44, 300), ("T2", 66, 128), ("T3", 600, 108), ("T4", 506, 236), ("T5", 604, 380), ("S/F", 108, 400)])
    return (f'<svg class="track" viewBox="28 28 600 430" role="img" '
            'aria-label="Animated race circuit: the autonomous car laps ahead of the human-driven car">'
            f'<defs><path id="trk" d="{TRACK_D}"/></defs>'
            '<use href="#trk" fill="none" stroke="#2a2f37" stroke-width="42" stroke-linejoin="round"/>'
            '<use href="#trk" fill="none" stroke="#15181d" stroke-width="35" stroke-linejoin="round"/>'
            '<use href="#trk" fill="none" stroke="rgba(255,255,255,.16)" stroke-width="1.4" stroke-dasharray="7 10"/>'
            f'<path class="rline" d="{TRACK_D}" pathLength="100" fill="none" stroke="#f2c14e" stroke-width="2.2" stroke-linecap="round" opacity=".9"/>'
            f'<g transform="translate(117 360)">{checker}</g>{labels}'
            + car("#38bdf8", "10.6s", "-0.7s") + car("#f2c14e", "9s", "0s") + '</svg>')

# ---- Home
hero = (f'<section class="hero"><div class="wrap"><div class="htext">'
        f'<div class="kicker">{e(HERO["kicker"])}</div>'
        f'<h1>Antoine<span>Bonhomme</span></h1>'
        f'<p class="lede">{HERO["lede_html"]}</p>'
        '<div class="cta"><a class="b y" href="#work">View work ↓</a><a class="b" href="/racetrack">Race my AI →</a>'
        f'<a class="b" href="{e(SITE["resume"])}" target="_blank" rel="noopener">Résumé ↗</a></div></div>'
        f'<div class="track-wrap">{track_svg()}'
        '<div class="legend"><span><i style="background:#f2c14e"></i>AI · Python controller</span>'
        '<span><i style="background:#38bdf8"></i>Human driver</span></div></div>'
        '</div></section>')
stats = ('<section class="stats"><div class="wrap">'
         + "".join(f'<div class="stat"><b>{big}</b><span>{e(lbl)}</span></div>' for big, lbl in STATS)
         + '</div></section>')
fbtns = "".join(f'<button class="f{" on" if k == "all" else ""}" type="button" data-f="{k}">{e(l)}</button>' for k, l in FILTERS)
cards = []
for i, p in enumerate(PROJECTS, 1):
    tags, cats = TAGS.get(p["slug"], ([], []))
    cards.append(f'<a class="card" href="/{p["slug"]}" data-cats="{" ".join(cats)}">'
                 f'<div class="ph"><img src="{cover_thumb(*p["cover"])}" alt="{e(p["title"])}" loading="lazy">'
                 f'<span class="no">{i:02d}</span><span class="yr">{e(p["year"])}</span></div>'
                 f'<div class="bd"><h3>{e(p["title"])}</h3><div class="ctx">{e(p.get("subtitle", ""))}</div>'
                 f'<div class="tags">{tag_html(tags)}</div></div></a>')
oval_gold = 11.43 * 1.05
promo = ('<div class="promo"><div class="in"><div><div class="kicker">Racetrack Lab · playable</div>'
         '<h2>Can you out-drive<br>my <em>Python</em> controller?</h2>'
         '<p>Draw any circuit, then race a car driven by the same kinematic bicycle model and path-following '
         'controller I built for Formula SAE. It runs live in your browser.</p>'
         '<a class="b y" href="/racetrack">Race the AI →</a></div>'
         '<div class="tower"><div class="th">Timing · Big Oval</div>'
         '<div class="row ai"><span>P1</span><b>AI · Python</b><i>11.43</i></div>'
         '<div class="row you"><span>P2</span><b>You</b><i>–:––.––</i></div>'
         f'<div class="row"><span>🥇</span><b>Gold target</b><i>{oval_gold:.2f}</i></div></div></div></div>')
work = (f'<section class="wrap" id="work"><div class="shead"><div>'
        f'<div class="kicker" id="wcount">{len(PROJECTS):02d} projects</div><h2>Selected work</h2></div>'
        f'<div class="filters" role="group" aria-label="Filter projects">{fbtns}</div></div>'
        f'<div class="grid">{"".join(cards)}</div>{promo}</section>')
page("index.html", f"{SITE['name']} — Mechanical Engineer",
     f"{SITE['name']}: mechanical engineering student at UC Berkeley building autonomous machines — race cars, subsea robots, powertrain and chassis design.",
     "work", hero + stats + work, og=cover_thumb(*PROJECTS[0]["cover"]))

# ---- Project pages
N = len(PROJECTS)
for i, p in enumerate(PROJECTS):
    tags, _ = TAGS.get(p["slug"], ([], []))
    b = [f'<section class="phero"><img src="{img(*p["cover"])}" alt=""><div class="wrap">'
         f'<div class="kicker">Project {i+1:02d} / {N:02d}</div><h1>{e(p["title"])}</h1></div></section>',
         '<section class="meta"><div class="wrap">'
         f'<div class="mcell"><span>Context</span><b>{e(p.get("subtitle", ""))}</b></div>'
         f'<div class="mcell"><span>Year</span><b>{e(p["year"])}</b></div>'
         f'<div class="mcell"><span>Disciplines</span><div class="tags">{tag_html(tags)}</div></div>'
         '</div></section>',
         '<article class="wrap pbody">',
         '<div class="lead">' + "".join(f"<p>{e(t)}</p>" for t in p["intro"]) + "</div>"]
    fig = 0
    for n, s in enumerate(p["sections"], 1):
        b.append(f'<section class="sec"><div class="sh"><span class="num">{n:02d}</span>'
                 f'<h2>{e(s.get("heading") or "Gallery")}</h2></div>')
        if s.get("text"): b.append('<div class="txt">' + "".join(f"<p>{e(t)}</p>" for t in s["text"]) + "</div>")
        if s.get("bullets"): b.append("<ul>" + "".join(f"<li>{e(t)}</li>" for t in s["bullets"]) + "</ul>")
        if s.get("images"):
            b.append(f'<div class="imgs {s.get("layout", "stack")}">')
            for deck, h, cap in s["images"]:
                fig += 1
                b.append(f'<figure><div class="fr"><img src="{img(deck, h)}" alt="{e(cap)}" loading="lazy"></div>'
                         f'<figcaption><b>FIG. {fig:02d}</b>{e(cap)}</figcaption></figure>')
            b.append("</div>")
        b.append("</section>")
    prev, nxt = PROJECTS[(i - 1) % N], PROJECTS[(i + 1) % N]
    b.append('<nav class="pn">'
             f'<a href="/{prev["slug"]}"><img src="{cover_thumb(*prev["cover"])}" alt="" loading="lazy"><div><span>← Previous</span><b>{e(prev["title"])}</b></div></a>'
             f'<a class="nx" href="/{nxt["slug"]}"><img src="{cover_thumb(*nxt["cover"])}" alt="" loading="lazy"><div><span>Next →</span><b>{e(nxt["title"])}</b></div></a>'
             '</nav></article>')
    page(f"{p['slug']}.html", f"{SITE['name']} — {p['title']}", p["intro"][0][:200], "work", "".join(b), og=img(*p["cover"]))

# ---- About
def roles_html(roles):
    out = ['<div class="roles">']
    for r in roles:
        out.append('<div class="role"><div class="hd"><div>'
                   f'<b>{e(r["org"])}</b><span class="rl">{e(r["role"])}</span></div><i>{e(r["dates"])}</i></div>')
        for label, bullets in r["groups"]:
            if label: out.append(f"<h4>{e(label)}</h4>")
            out.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in bullets) + "</ul>")
        if r.get("links"):
            out.append('<div class="rlinks">' + "".join(f'<a href="{e(h)}">{e(t)} →</a>' for t, h in r["links"]) + "</div>")
        out.append("</div>")
    out.append("</div>")
    return "".join(out)

ed = ABOUT["education"]
skills = "".join(f'<div><b>{e(k)}</b><div class="tags">' + tag_html([x.strip() for x in v.split(",") if x.strip()]) + "</div></div>"
                 for k, v in ABOUT["skills"].items())
a = ['<section class="wrap phead"><div class="kicker">About</div><h1>Hi, I’m Antoine.</h1></section>',
     '<article class="wrap ab"><div class="ab-top">'
     f'<img src="{img(*ABOUT["photo"], max_w=900)}" alt="{e(SITE["name"])}"><div>'
     + "".join(f"<p>{e(t)}</p>" for t in ABOUT["paragraphs"])
     + f'<div class="cta"><a class="b y" href="{e(SITE["resume"])}" target="_blank" rel="noopener">Download résumé ↓</a>'
       '<a class="b" href="/contact">Get in touch →</a></div></div></div>',
     '<h2>Education</h2><div class="roles"><div class="role"><div class="hd"><div>'
     f'<b>{e(ed["school"])}</b><span class="rl">{e(ed["degree"])}</span></div><i>{e(ed["dates"])}</i></div>'
     f'<p class="edd">{e(ed["detail"])}</p></div></div>',
     "<h2>Experience</h2>" + roles_html(ABOUT["experience"]),
     "<h2>Research</h2>" + roles_html(ABOUT["research"]),
     f'<h2>Technical skills</h2><div class="skills">{skills}</div>',
     '<div class="gal">' + "".join(f'<img src="{img(d, h, max_w=700)}" alt="" loading="lazy">' for d, h in ABOUT["gallery"]) + "</div>",
     "</article>"]
page("about.html", f"{SITE['name']} — About", ABOUT["paragraphs"][0], "about", "".join(a), og=img(*ABOUT["photo"], max_w=900))

# ---- Contact
rows = [("Email", SITE["email"], f"mailto:{SITE['email']}", False),
        ("Phone", SITE["phone"], f"tel:+1{SITE['phone'].replace(' ', '')}", False),
        ("LinkedIn", "linkedin.com/in/antoine-bonhomme", SITE["linkedin"], True),
        ("GitHub", "github.com/AJBonhomme", SITE["github"], True),
        ("Résumé", "Download PDF", SITE["resume"], True)]
c = ('<section class="wrap phead"><div class="kicker">Contact</div><h1>Let’s talk.</h1>'
     '<p class="sub2">I’m always happy to hear from people — whether it’s about a project, an internship, or robots in general.</p></section>'
     '<section class="wrap contact"><div class="rows">'
     + "".join(f'<a href="{e(href)}"{" target=_blank rel=noopener" if ext else ""}><span>{e(k)}</span><b>{e(v)}</b></a>' for k, v, href, ext in rows)
     + "</div></section>")
page("contact.html", f"{SITE['name']} — Contact", "Get in touch with Antoine Bonhomme.", "contact", c, cta=False)

# ---- Racetrack Lab
lab = open(os.path.join(HERE, "lab.html")).read()
lab = lab.replace("__LAB_SIM__", open(os.path.join(HERE, "lab_sim.py")).read())
lab = lab.replace("/lab_sim.py", "https://github.com/AJBonhomme/portfolio/blob/main/src/lab_sim.py")
page("racetrack.html", f"{SITE['name']} — Racetrack Lab",
     "Draw a racetrack with your mouse and watch a car driven by a live Python path-following controller try to lap it.",
     "racetrack", '<div class="wrap labwrap">' + lab + '</div>', og=cover_thumb(*PROJECTS[1]["cover"]))

# remove pages from earlier builds that no longer correspond to anything
expected = {"index.html", "about.html", "contact.html", "racetrack.html"} | {p["slug"] + ".html" for p in PROJECTS}
for stale in glob.glob(os.path.join(OUT, "*.html")):
    if os.path.basename(stale) not in expected:
        os.remove(stale)
        print("removed stale page:", os.path.basename(stale))

with open(os.path.join(OUT, "style.css"), "w") as f: f.write(CSS)
with open(os.path.join(OUT, "favicon.svg"), "w") as f:
    f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><path d="M0 0H64V46L46 64H0Z" fill="#f2c14e"/><text x="30" y="44" font-family="Arial Narrow,Arial,sans-serif" font-weight="800" font-size="30" fill="#0b0c0e" text-anchor="middle">AB</text></svg>')
with open(os.path.join(OUT, "vercel.json"), "w") as f:
    import json as _json
    f.write(_json.dumps({
        "cleanUrls": True,
        "redirects": [
            {"source": "/" + old, "destination": "/small-projects", "permanent": True}
            for old in ("obstacle-avoiding-rc-car", "rc-car-iterations", "handheld-distance-finder")
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
