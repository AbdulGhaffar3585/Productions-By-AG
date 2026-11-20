#!/usr/bin/env python3
"""
Builds the static site into ./public from content.py + ./static.

    python3 build.py

No installs needed — standard-library Python only. Vercel serves ./public
as-is and runs ./api/contact.js for the two forms (/start and /contact).
"""
import hashlib
import html
import json
import shutil
from pathlib import Path

import content as C

ROOT = Path(__file__).parent
OUT = ROOT / "public"
STATIC = ROOT / "static"
IMG = STATIC / "img"

e = html.escape
SITE = C.SITE


def asset_version(*paths):
    h = hashlib.sha1()
    for p in paths:
        h.update((STATIC / p).read_bytes())
    return h.hexdigest()[:8]


ARROW = '<svg class="ic" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="square"/></svg>'
ARROW_UP = '<svg class="ic" viewBox="0 0 16 16" aria-hidden="true"><path d="M5 11l6-6M6 5h5v5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="square"/></svg>'
PLAY = '<svg class="play-ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4v16l14-8z" fill="currentColor"/></svg>'

# The AG monogram: the A's crossbar runs on as the G's bar — one horizon line.
# The red counter in the A doubles as a play / REC mark. Defined once per page.
MARK_SYMBOL = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<clipPath id="ag-feet"><rect x="0" y="0" width="160" height="92"/></clipPath>
<symbol id="ag-mark" viewBox="3 8 150 84"><g fill="none" stroke="currentColor" stroke-width="8"><path clip-path="url(#ag-feet)" d="M5 100L35 20L65 100" stroke-miterlimit="10"/><path d="M136.87 23.13A38 38 0 1 0 146.66 60H20"/></g><path d="M35 39L40 53H30Z" fill="#d63a20"/></symbol>
</defs></svg>'''
MARK = '<svg class="mark" aria-hidden="true"><use href="#ag-mark"/></svg>'


# ------------------------------------------------------------------ helpers

def img(name, alt, sizes="100vw", cls="", eager=False, w=None, h=None):
    """<img> with an 800px variant in srcset when one exists (name-sm.jpg)."""
    base = IMG / f"{name}.jpg"
    small = IMG / f"{name}-sm.jpg"
    if w is None or h is None:
        w, h = jpeg_size(base)
    srcset = ""
    if small.exists():
        sw, _ = jpeg_size(small)
        srcset = f' srcset="/img/{name}-sm.jpg {sw}w, /img/{name}.jpg {w}w" sizes="{sizes}"'
    loading = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<img src="/img/{name}.jpg"{srcset} width="{w}" height="{h}" alt="{e(alt)}" {loading}{c}>'


def jpeg_size(path):
    data = path.read_bytes()
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            h = int.from_bytes(data[i + 5:i + 7], "big")
            w = int.from_bytes(data[i + 7:i + 9], "big")
            return w, h
        seg = int.from_bytes(data[i + 2:i + 4], "big")
        i += 2 + seg
    raise ValueError(f"no size in {path}")


def btn(text, href, kind="red", extra=""):
    return f'<a class="btn btn-{kind}" href="{href}"{extra}><span>{e(text)}</span>{ARROW}</a>'


def label(text, cls=""):
    return f'<p class="label {cls}">{e(text)}</p>'


def project(slug):
    return next(p for p in C.PROJECTS if p["slug"] == slug)


def num(i):
    return f"{i:02d}"


def cover(p, sizes, eager=False):
    """Project image, or a typographic title card when no still exists yet."""
    if p.get("cover"):
        alt = f'{p["client"]} — {p["short"]}'
        if p.get("cover_square"):
            return (f'<div class="media media-contain" style="--bg:url(/img/{p["cover"]}-sm.jpg)">'
                    f'{img(p["cover"], alt, sizes, eager=eager)}</div>')
        return f'<div class="media">{img(p["cover"], alt, sizes, eager=eager)}</div>'
    return (f'<div class="media media-type" aria-hidden="true">'
            f'<span class="label"><span>{e(p["type"])}</span><span>{e(p["year"])}</span></span>'
            f'<strong>{e(p["client"])}</strong></div>')


def card(p, i, sizes="(min-width: 1000px) 33vw, (min-width: 640px) 50vw, 100vw"):
    return f'''<a class="card" href="/work/{p["slug"]}" data-type="{e(p["type"])}" data-reveal>
  {cover(p, sizes)}
  <div class="card-body">
    <span class="idx">{num(i)}</span>
    <h3>{e(p["client"])}</h3>
    <p class="muted">{e(p["short"])}</p>
    <p class="label">{e(p["type"])} · {e(p["year"])}</p>
  </div>
</a>'''


def film(f, vertical=False):
    cls = "film film-vertical" if vertical else "film"
    return f'''<figure class="{cls}" data-reveal>
  <button class="facade" type="button" data-vimeo="{f["vimeo"]}" aria-label="Play {e(f["title"])}">
    <img src="/img/{f["poster"]}" alt="" loading="lazy" decoding="async">
    <span class="play">{PLAY}Play</span>
  </button>
  <figcaption><strong>{e(f["title"])}</strong> <span class="muted">{e(f["note"])}</span></figcaption>
</figure>'''


def section_head(lbl, heading, sub="", h="h2"):
    sub_html = f'<p class="sec-sub">{e(sub)}</p>' if sub else ""
    return f'<div class="sec-head" data-reveal>{label(lbl)}<{h} class="h2">{heading}</{h}>{sub_html}</div>'


def cta_band(heading=None, line=None):
    return f'''<section class="cta dark">
  <div class="shell cta-in" data-reveal>
    <div>
      {label("Start a project")}
      <h2 class="display-2">{e(heading or C.CTA["heading"])}</h2>
    </div>
    <div class="cta-side">
      <p class="lede">{e(line or C.CTA["line"])}</p>
      {btn(C.CTA["button"], "/start")}
      <a class="link" href="/contact">Or just say hello {ARROW}</a>
    </div>
  </div>
</section>'''


def page_header(lbl, heading, sub=""):
    sub_html = f'<p class="lede">{e(sub)}</p>' if sub else ""
    return f'''<section class="page-head">
  <div class="shell">
    {label(lbl)}
    <h1 class="display">{heading}</h1>
    {sub_html}
  </div>
</section>'''


def stars(text):
    """Escape text and turn *phrase* into <em>phrase</em>."""
    parts = e(text).split("*")
    return "".join(f"<em>{p}</em>" if i % 2 else p for i, p in enumerate(parts))


def italic_last(text):
    """'Selected work.' -> 'Selected <em>work.</em>' — the house headline style."""
    words = e(text).rsplit(" ", 1)
    return words[0] if len(words) == 1 else f"{words[0]} <em>{words[1]}</em>"


# ------------------------------------------------------------------ layout

def layout(path, title, description, body, page_class="", og_image="/og.jpg", jsonld=None, extra=""):
    full_title = title if title.startswith(SITE["name"]) else f'{title} — {SITE["name"]}'
    canonical = SITE["url"] + (path if path != "/" else "")
    current = "/" + path.strip("/").split("/")[0] if path != "/" else "/"

    def nav_link(name, href, i=None):
        cur = ' aria-current="page"' if href == current else ""
        n = f'<span class="idx">{num(i)}</span>' if i else ""
        return f'<a href="{href}"{cur}>{n}{name}</a>'

    nav = "".join(nav_link(n, h) for n, h in C.NAV)
    menu = "".join(nav_link(n, h, i) for i, (n, h) in enumerate([("Home", "/")] + C.NAV, 1))
    foot = "".join(f'<li><a href="{h}">{n}</a></li>' for n, h in C.FOOTER_NAV)
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#121110">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(SITE["name"])}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE["url"]}{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter+Tight:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap">
<link rel="stylesheet" href="/css/site.css?v={CSS_V}">
<script>document.documentElement.classList.add('js')</script>
{ld}
</head>
<body class="{page_class}">
{MARK_SYMBOL}
<a class="skip" href="#main">Skip to content</a>
<header class="nav" id="top">
  <div class="shell nav-in">
    <a class="logo" href="/" aria-label="{e(SITE["name"])} — home">{MARK}<span class="logo-word">Productions <i>by</i> AG</span></a>
    <nav class="nav-links" aria-label="Main">{nav}</nav>
    <a class="btn btn-red btn-sm nav-cta" href="/start"><span>Start a project</span>{ARROW}</a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="menu"><span class="nav-toggle-text">Menu</span><span class="bars"><span></span><span></span></span></button>
  </div>
  <div class="menu dark" id="menu" hidden>
    <nav class="shell menu-links" aria-label="Mobile">{menu}</nav>
    <div class="shell menu-foot">
      {btn("Start a project", "/start")}
      <a class="label" href="mailto:{SITE["email"]}">{SITE["email"]}</a>
    </div>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="foot dark">
  <div class="shell">
    <div class="foot-top">
      <div>
        {label("Productions by AG")}
        <p class="foot-tag">{e(SITE["tagline"])}</p>
      </div>
      <ul>{label("Pages")}{foot}</ul>
      <ul>{label("Talk")}<li><a href="/start">Start a project</a></li><li><a href="/contact">Contact</a></li><li><a href="mailto:{SITE["email"]}">Email</a></li></ul>
      <ul>{label("Elsewhere")}
        <li><a href="{SITE["instagram"]}" target="_blank" rel="noopener">Instagram {ARROW_UP}</a></li>
        <li><a href="{SITE["linkedin"]}" target="_blank" rel="noopener">LinkedIn {ARROW_UP}</a></li>
      </ul>
    </div>
    <div class="foot-word" aria-hidden="true"><span class="word">Productions <i>by</i> AG</span>{MARK}</div>
    <div class="foot-bottom label">
      <span>© {SITE["year"]} {e(SITE["name"])}</span>
      <span>{e(SITE["location"])}</span>
      <a href="#top">Back to top ↑</a>
    </div>
  </div>
</footer>
{extra}
<script src="/js/site.js?v={JS_V}" defer></script>
</body>
</html>
'''


# ------------------------------------------------------------------ pages

def home():
    H = C.HOME
    h1 = f'{e(H["headline"][0])} {e(H["headline"][1])} <em>{e(H["headline"][2])}</em>'
    disciplines = "".join(
        f'<a class="disc" href="/services#{d["id"]}" data-reveal><span class="idx">{num(i)}</span>'
        f'<strong>{e(d["name"])}</strong><span class="muted">{e(d["line"])}</span>{ARROW}</a>'
        for i, d in enumerate(C.DISCIPLINES, 1))

    features = ""
    for i, slug in enumerate(H["featured"], 1):
        p = project(slug)
        features += f'''<article class="feature" data-reveal>
  <a class="feature-media" href="/work/{p["slug"]}" tabindex="-1" aria-hidden="true">{cover(p, "(min-width: 860px) 58vw, 100vw")}</a>
  <div class="feature-text">
    <span class="feature-no">{num(i)}</span>
    {label(f'{p["type"]} · {p["year"]} · {p["role"]}')}
    <h3 class="feature-title"><a href="/work/{p["slug"]}">{e(p["client"])}</a></h3>
    <p class="muted">{e(p["short"])}</p>
    <a class="link" href="/work/{p["slug"]}" tabindex="-1">View the project {ARROW}</a>
  </div>
</article>'''

    names = "".join(f"<li>{e(n)}</li>" for n in H["trusted"])

    body = f'''
<section class="hero dark">
  <div class="hero-media" data-vimeo-bg="{SITE["showreel_vimeo"]}">
    <img src="/img/hero-poster.jpg" alt="" fetchpriority="high" width="1280" height="720">
  </div>
  <div class="hero-shade"></div>
  <div class="shell hero-in">
    <p class="label rec"><span class="rec-dot"></span>Showreel · {SITE["year"]}</p>
    <h1 class="display hero-h">{h1}</h1>
    <div class="hero-row">
      <p class="lede">{e(H["subhead"])}</p>
      <div class="actions">
        <button class="btn btn-red" type="button" data-reel="{SITE["showreel_vimeo"]}"><span>Watch the showreel</span>{PLAY}</button>
        {btn("View work", "/work", "line")}
      </div>
    </div>
  </div>
  <p class="label hero-meta shell"><span>Lahore, Pakistan</span><span>Brand · Documentary · Social · Photography</span><span>Scroll ↓</span><span data-timecode>00:00:00:00</span></p>
</section>

<section class="intro">
  <div class="shell intro-grid">
    <p class="label">What I make</p>
    <div data-reveal>
      <p class="statement">{stars(H["statement"])}</p>
    </div>
  </div>
  <div class="shell"><div class="disc-list">{disciplines}</div></div>
</section>

<section class="section">
  <div class="shell">
    {section_head("Selected work", italic_last(H["featured_heading"]))}
    <div class="features">{features}</div>
    <div class="sec-foot">{btn("See all work", "/work", "ink")}</div>
  </div>
</section>

<section class="trusted dark" aria-label="{e(H["trusted_heading"])}">
  <div class="shell trusted-head">
    {label(H["trusted_heading"])}
    <a class="link" href="/collaborations">All collaborations {ARROW}</a>
  </div>
  <div class="marquee"><ul>{names}</ul><ul aria-hidden="true">{names}</ul></div>
</section>

<section class="section">
  <div class="shell about-teaser">
    <figure class="portrait" data-reveal>{img("abdul-ghaffar", "Abdul Ghaffar, filmmaker", "(min-width: 900px) 40vw, 100vw")}<figcaption class="label"><span>Abdul Ghaffar</span><span>Lahore</span></figcaption></figure>
    <div data-reveal>
      {label("About")}
      <h2 class="h2">{italic_last(H["about_heading"])}</h2>
      <p class="lede">Filmmaker, editor and photographer. More than fifty documentaries for Alkhidmat Foundation, brand films for companies across Pakistan, and partnerships with Sony, Nikon, Sigma, Insta360 and Hollyland.</p>
      {btn("About me", "/about", "line")}
    </div>
  </div>
</section>
{cta_band()}'''
    jsonld = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": SITE["name"],
        "url": SITE["url"],
        "email": SITE["email"],
        "image": SITE["url"] + "/og.jpg",
        "logo": SITE["url"] + "/brand/ag-mark.svg",
        "description": SITE["description"],
        "address": {"@type": "PostalAddress", "addressLocality": "Lahore", "addressCountry": "PK"},
        "founder": {"@type": "Person", "name": "Abdul Ghaffar", "jobTitle": "Filmmaker"},
        "sameAs": [SITE["linkedin"], SITE["instagram"]],
    }
    reel = f'''<dialog class="reel" id="reel" aria-label="Showreel">
  <button class="reel-close" type="button" data-reel-close>Close <span aria-hidden="true">×</span></button>
  <div class="reel-frame"></div>
</dialog>'''
    return layout("/", f'{SITE["name"]} — Brand films & documentaries, Lahore', SITE["description"], body, "page-home", jsonld=jsonld, extra=reel)


def work():
    counts = {f: sum(p["type"] == f for p in C.PROJECTS) for f in C.WORK_FILTERS}
    chips = f'<button type="button" class="chip" aria-pressed="true" data-filter="all">All <sup>{len(C.PROJECTS)}</sup></button>' + "".join(
        f'<button type="button" class="chip" aria-pressed="false" data-filter="{e(f)}">{e(f)} <sup>{counts[f]}</sup></button>'
        for f in C.WORK_FILTERS if counts[f])
    cards = "".join(card(p, i) for i, p in enumerate(C.PROJECTS, 1))
    cuts = "".join(film(f, vertical=True) for f in C.SHORT_CUTS)
    body = f'''
{page_header("Work", "Selected <em>work.</em>", C.WORK_INTRO)}
<section class="section section-tight">
  <div class="shell">
    <div class="chips" role="group" aria-label="Filter by type">{chips}</div>
    <div class="grid grid-2" id="work-grid">{cards}</div>
    <p class="empty muted" hidden>Nothing in this category yet.</p>
  </div>
</section>
<section class="section">
  <div class="shell">
    {section_head("Short-form", "Recent <em>cuts.</em>", "Vertical films for creator and product partnerships. Sound on.")}
    <div class="cuts">{cuts}</div>
  </div>
</section>
{cta_band()}'''
    return layout("/work", "Work", "Brand films, founder stories, and documentaries by Abdul Ghaffar — Alkhidmat, Total Parco, Care Pharmacy, TEDx GCU and more.", body, "page-work")


def case_study(p, prev, nxt):
    def block(n, title, text, extra=""):
        if not text:
            return ""
        return f'''<div class="cs-block" data-reveal>
  <p class="label"><span class="accent">0{n}</span> · {title}</p>
  <p class="cs-text">{e(text)}</p>{extra}
</div>'''

    quote = f'<blockquote class="quote">“{e(p["brief_quote"])}”</blockquote>' if p.get("brief_quote") else ""
    blocks = block(1, "The brief", p["brief"], quote) + block(2, "The approach", p["approach"]) + block(3, "The outcome", p["outcome"])
    story = f'<section class="section"><div class="shell cs-story">{blocks}</div></section>' if blocks else ""

    films = ""
    if p["films"]:
        heading = "The full <em>film.</em>" if len(p["films"]) == 1 else "The <em>films.</em>"
        films = f'''<section class="section{" section-tight" if not blocks else ""}">
  <div class="shell">
    {section_head("Watch", heading)}
    <div class="films">{"".join(film(f) for f in p["films"])}</div>
  </div>
</section>'''

    stills = ""
    if p["stills"]:
        items = "".join(f'<figure data-reveal>{img(s["img"], s["alt"], "(min-width: 760px) 50vw, 100vw")}</figure>' for s in p["stills"])
        stills = f'<section class="section"><div class="shell">{section_head("Stills", "From the <em>shoot.</em>")}<div class="stills">{items}</div></div></section>'

    making = "".join(f'<div><dt class="label">{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in p["making"])
    making_html = f'''<section class="section{" section-tight" if not (blocks or films or stills) else ""}">
  <div class="shell">
    {section_head("Credits", "The <em>making.</em>")}
    <dl class="making" data-reveal>{making}</dl>
  </div>
</section>''' if making else ""

    meta = "".join(f'<div><dt class="label">{k}</dt><dd>{e(v)}</dd></div>' for k, v in
                   [("Client", p["client"]), ("Category", p["type"]), ("Year", p["year"]), ("Role", p["role"])])

    hero_media = f'<div class="shell cs-hero" data-reveal>{cover(p, "100vw", eager=True)}</div>' if p.get("cover") else ""

    body = f'''
<section class="page-head cs-head">
  <div class="shell">
    <p class="label crumbs"><a href="/work">Work</a> &nbsp;/&nbsp; {e(p["client"])}</p>
    <h1 class="display">{italic_last(p["title"])}</h1>
    <p class="lede">{e(p["standfirst"])}</p>
    <dl class="cs-meta">{meta}</dl>
  </div>
</section>
{hero_media}
{story}
{films}
{stills}
{making_html}
<nav class="shell pager" aria-label="More projects">
  <a href="/work/{prev["slug"]}"><span class="label">← Previous project</span><strong>{e(prev["client"])}</strong></a>
  <a href="/work/{nxt["slug"]}" class="next"><span class="label">Next project →</span><strong>{e(nxt["client"])}</strong></a>
</nav>
{cta_band()}'''
    og = f'/img/{p["cover"]}.jpg' if p.get("cover") else "/og.jpg"
    return layout(f'/work/{p["slug"]}', p["title"], p["standfirst"], body, "page-case", og_image=og)


def about():
    A = C.ABOUT
    story = "".join(f"<p>{e(s)}</p>" for s in A["story"])
    stats = "".join(f'<div class="stat" data-reveal><span class="label">{e(k)}</span><strong>{e(v)}</strong><span class="muted">{e(s)}</span></div>' for k, v, s in A["stats"])
    principles = "".join(
        f'<div class="principle" data-reveal><span class="label accent">0{i}</span><h3>{e(t)}</h3><p class="muted">{e(d)}</p></div>'
        for i, (t, d) in enumerate(A["principles"], 1))
    body = f'''
{page_header("About", italic_last(A["headline"]), A["intro"])}
<section class="section section-tight">
  <div class="shell about-grid">
    <figure class="portrait" data-reveal>{img("abdul-ghaffar", "Abdul Ghaffar", "(min-width: 900px) 40vw, 100vw")}<figcaption class="label"><span>Abdul Ghaffar</span><span>Lahore</span></figcaption></figure>
    <div class="about-story" data-reveal>
      <p class="roles">{e(A["roles"])}</p>
      {story}
    </div>
  </div>
</section>
<section class="section section-tight">
  <div class="shell stats">{stats}</div>
</section>
<section class="section">
  <div class="shell">
    {section_head("Principles", "How I <em>work.</em>")}
    <div class="principles">{principles}</div>
    <div class="sec-foot">{btn("Brands & partners I've worked with", "/collaborations", "line")}</div>
  </div>
</section>
{cta_band()}'''
    return layout("/about", "About Abdul Ghaffar", "Abdul Ghaffar is a filmmaker and photographer in Lahore — 50+ documentaries for Alkhidmat, brand films, founder stories.", body, "page-about")


def services():
    rows = ""
    for i, s in enumerate(C.SERVICES, 1):
        runs = "".join(f"<li>{e(r)}</li>" for r in s["runs"])
        steps = "".join(f"<li>{e(x)}</li>" for x in s["process"])
        ex_label, ex_href = s["example"]
        rows += f'''<details class="svc" id="{s["id"]}" data-reveal>
  <summary>
    <span class="label">0{i} / 0{len(C.SERVICES)}</span>
    <span class="svc-name">{e(s["name"])}</span>
    <span class="svc-covers muted">{e(s["covers"])}</span>
    <ul class="svc-runs label">{runs}</ul>
    <span class="svc-toggle" aria-hidden="true"></span>
  </summary>
  <div class="svc-body">
    <p class="lede">{e(s["body"])}</p>
    <div>
      <p class="label">How it runs</p>
      <ol class="steps">{steps}</ol>
      <a class="link" href="{ex_href}">See: {e(ex_label)} {ARROW}</a>
    </div>
  </div>
</details>'''
    process = "".join(f'<div class="principle" data-reveal><span class="label accent">0{i}</span><h3>{e(t)}</h3><p class="muted">{e(d)}</p></div>'
                      for i, (t, d) in enumerate(C.PROCESS, 1))
    body = f'''
{page_header("Services", italic_last(C.SERVICES_INTRO["heading"]), C.SERVICES_INTRO["subhead"])}
<section class="section section-tight">
  <div class="shell svc-list">{rows}</div>
</section>
<section class="section">
  <div class="shell photo-band" data-reveal>
    {img("psop", "Badshahi Mosque, Lahore — editorial photograph by Abdul Ghaffar", "(min-width: 900px) 40vw, 100vw")}
    <div>
      {label("Process")}
      <h2 class="h2">How projects <em>start.</em></h2>
      <div class="principles principles-stack">{process}</div>
    </div>
  </div>
</section>
{cta_band()}'''
    return layout("/services", "Services", "Brand films, documentaries, social content retainers, and event photography — one point of contact on every project.", body, "page-services")


def collaborations():
    groups = ""
    for g in C.COLLAB_GROUPS:
        note = f'<p class="muted">{e(g["note"])}</p>' if g.get("note") else ""
        rows = "".join(
            f'<tr><th scope="row">{e(n)}{f" <span class=muted>({e(sub)})</span>" if sub else ""}</th><td>{e(w)}</td></tr>'
            for n, sub, w in g["rows"])
        groups += f'''<section class="collab" data-reveal>
  <div class="collab-head"><h2 class="h3">{e(g["title"])}</h2>{note}</div>
  <table class="table"><thead><tr><th scope="col" class="label">{e(g["cols"][0])}</th><th scope="col" class="label">{e(g["cols"][1])}</th></tr></thead><tbody>{rows}</tbody></table>
</section>'''
    body = f'''
{page_header("Collaborations", italic_last(C.COLLAB_INTRO["heading"]), C.COLLAB_INTRO["subhead"])}
<section class="section section-tight"><div class="shell collabs">{groups}</div></section>
{cta_band()}'''
    return layout("/collaborations", "Collaborations", "Brand partnerships with Sony, Nikon, Sigma, Insta360 and Hollyland; TEDx GCU; 50+ documentaries for Alkhidmat Foundation.", body, "page-collab")


FORM_STATUS = '<p class="form-status" role="status" aria-live="polite"></p>'
HONEYPOT = '<label class="hp" aria-hidden="true">Website<input name="website" tabindex="-1" autocomplete="off"></label>'


def start():
    """/start — the project brief."""
    K = C.CONTACT
    S = C.START
    types = "".join(f'<label class="chip chip-radio"><input type="radio" name="type" value="{e(t)}" required><span>{e(t)}</span></label>' for t in K["project_types"])
    timelines = "".join(f"<option>{e(t)}</option>" for t in K["timelines"])
    steps = "".join(f"<li><div><strong>{e(t)}</strong><span>{e(d)}</span></div></li>" for t, d in C.PROCESS)
    body = f'''
{page_header("Start a project", italic_last(S["heading"]), S["subhead"])}
<section class="section section-tight">
  <div class="shell form-grid">
    <form class="form" id="start-form" data-kind="project" action="/api/contact" method="post" novalidate>
      <input type="hidden" name="kind" value="project">
      <div class="row2">
        <label class="field"><span class="label">Your name *</span><input name="name" autocomplete="name" required></label>
        <label class="field"><span class="label">Email *</span><input name="email" type="email" autocomplete="email" required></label>
      </div>
      <div class="row2">
        <label class="field"><span class="label">Company <span class="muted">(optional)</span></span><input name="company" autocomplete="organization"></label>
        <label class="field"><span class="label">Timeline</span><select name="timeline">{timelines}</select></label>
      </div>
      <fieldset class="field"><legend class="label">What are you making? *</legend><div class="chips">{types}</div></fieldset>
      <label class="field"><span class="label">Tell me about the project *</span><textarea name="message" rows="6" required placeholder="What is it, who is it for, and when do you need it? Links to references are welcome."></textarea></label>
      {HONEYPOT}
      <div class="form-foot">
        <button class="btn btn-red" type="submit"><span>Send the brief</span>{ARROW}</button>
        <p class="label">Reply within 2 working days</p>
      </div>
      {FORM_STATUS}
    </form>
    <aside class="aside">
      <div>{label("What happens next")}<ol class="steps-aside">{steps}</ol></div>
      <div>{label("Prefer email?")}<p><a href="mailto:{SITE["email"]}" data-email>{SITE["email"]}</a></p></div>
      <div>{label("Not a project?")}<p><a class="link" href="/contact">Go to the contact page {ARROW}</a></p></div>
    </aside>
  </div>
</section>'''
    return layout("/start", "Start a project", "Send a brief for a brand film, documentary, social content or photography project. I respond within two working days.", body, "page-start")


def contact():
    """/contact — direct details and a short general message."""
    K = C.CONTACT
    body = f'''
{page_header("Contact", italic_last(K["heading"]), K["subhead"])}
<section class="section section-tight">
  <div class="shell">
    {label("Email")}
    <a class="big-email" href="mailto:{SITE["email"]}" data-email>{SITE["email"]}</a>
    <div class="channels">
      <a href="{SITE["instagram"]}" target="_blank" rel="noopener"><span><span class="label">Instagram</span>@productionsbyag</span>{ARROW_UP}</a>
      <a href="{SITE["linkedin"]}" target="_blank" rel="noopener"><span><span class="label">LinkedIn</span>Abdul Ghaffar Khan</span>{ARROW_UP}</a>
      <div><span class="label">Based in</span><p class="city">{e(SITE["location"])}</p><p class="muted city-note">{e(K["travel"])}</p></div>
    </div>
  </div>
</section>
<section class="section section-tight">
  <div class="shell form-grid">
    <form class="form" id="contact-form" data-kind="general" action="/api/contact" method="post" novalidate>
      <input type="hidden" name="kind" value="general">
      {label("Leave a note")}
      <div class="row2">
        <label class="field"><span class="label">Your name *</span><input name="name" autocomplete="name" required></label>
        <label class="field"><span class="label">Email *</span><input name="email" type="email" autocomplete="email" required></label>
      </div>
      <label class="field"><span class="label">Message *</span><textarea name="message" rows="5" required placeholder="What's on your mind?"></textarea></label>
      {HONEYPOT}
      <div class="form-foot">
        <button class="btn btn-ink" type="submit"><span>Send message</span>{ARROW}</button>
        <p class="label">{e(K["hours"])}</p>
      </div>
      {FORM_STATUS}
    </form>
    <aside class="promo">
      {label("Have a project in mind?")}
      <h2 class="h3">Send a proper brief instead.</h2>
      <p>Pick the type of project and timeline, and I'll come back with the right questions.</p>
      {btn("Start a project", "/start")}
    </aside>
  </div>
</section>'''
    return layout("/contact", "Contact", "Email, Instagram and LinkedIn for Productions by AG — or leave a quick note.", body, "page-contact")


def not_found():
    body = f'''
<section class="page-head nf">
  <div class="shell">
    {label("404 · Scene missing")}
    <h1 class="display">This page didn't make the final <em>cut.</em></h1>
    <div class="actions">{btn("Back home", "/")}{btn("See the work", "/work", "line")}</div>
  </div>
</section>'''
    return layout("/404", "Page not found", "This page doesn't exist.", body, "page-404")


# ------------------------------------------------------------------ build

def write(rel, text):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    global CSS_V, JS_V
    CSS_V = asset_version("css/site.css")
    JS_V = asset_version("js/site.js")

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT)

    pages = {
        "index.html": home(),
        "work.html": work(),
        "about.html": about(),
        "services.html": services(),
        "collaborations.html": collaborations(),
        "start.html": start(),
        "contact.html": contact(),
        "404.html": not_found(),
    }
    n = len(C.PROJECTS)
    for i, p in enumerate(C.PROJECTS):
        pages[f'work/{p["slug"]}.html'] = case_study(p, C.PROJECTS[(i - 1) % n], C.PROJECTS[(i + 1) % n])

    for rel, text in pages.items():
        write(rel, text)

    urls = ["/", "/work", "/about", "/services", "/collaborations", "/start", "/contact"] + [f'/work/{p["slug"]}' for p in C.PROJECTS]
    sitemap = "".join(f"<url><loc>{SITE['url']}{u if u != '/' else ''}</loc></url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sitemap}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n")
    print(f"Built {len(pages)} pages into {OUT.relative_to(ROOT)}/")


CSS_V = JS_V = ""

if __name__ == "__main__":
    main()
