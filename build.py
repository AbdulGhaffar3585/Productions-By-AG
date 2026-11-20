#!/usr/bin/env python3
"""
Builds the static site into ./public from content.py + ./static.

    python3 build.py

No installs needed — standard-library Python only. Vercel serves ./public
as-is and runs ./api/contact.js for the enquiry form.
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


ARROW = '<svg class="ic" viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ARROW_UP = '<svg class="ic" viewBox="0 0 16 16" aria-hidden="true"><path d="M5 11l6-6M6 5h5v5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg>'


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


def btn(label, href, kind="accent", extra=""):
    return f'<a class="btn btn-{kind}" href="{href}"{extra}><span>{e(label)}</span>{ARROW}</a>'


def label(text, cls=""):
    return f'<p class="label {cls}">{e(text)}</p>'


def project(slug):
    return next(p for p in C.PROJECTS if p["slug"] == slug)


def cover(p, sizes, eager=False):
    """Project image, or a typographic title card when no still exists yet."""
    if p.get("cover"):
        alt = f'{p["client"]} — {p["short"]}'
        if p.get("cover_square"):
            return (f'<div class="media media-contain" style="--bg:url(/img/{p["cover"]}-sm.jpg)">'
                    f'{img(p["cover"], alt, sizes, eager=eager)}</div>')
        return f'<div class="media">{img(p["cover"], alt, sizes, eager=eager)}</div>'
    return (f'<div class="media media-type" aria-hidden="true"><span class="label">{e(p["type"])} · {e(p["year"])}</span>'
            f'<strong>{e(p["client"])}</strong><span class="corner tl"></span><span class="corner br"></span></div>')


def card(p, sizes="(min-width: 1000px) 33vw, (min-width: 640px) 50vw, 100vw"):
    return f'''<a class="card" href="/work/{p["slug"]}" data-type="{e(p["type"])}" data-reveal>
  {cover(p, sizes)}
  <div class="card-body">
    <p class="label"><span class="accent">{e(p["type"])}</span> · {e(p["year"])}</p>
    <h3>{e(p["client"])}</h3>
    <p class="muted">{e(p["short"])} — {e(p["role"])}</p>
  </div>
</a>'''


def film(f, vertical=False):
    cls = "film film-vertical" if vertical else "film"
    return f'''<figure class="{cls}" data-reveal>
  <button class="facade" type="button" data-vimeo="{f["vimeo"]}" aria-label="Play {e(f["title"])}">
    <img src="/img/{f["poster"]}" alt="" loading="lazy" decoding="async">
    <span class="play">{PLAY}</span>
  </button>
  <figcaption><strong>{e(f["title"])}</strong> <span class="muted">— {e(f["note"])}</span></figcaption>
</figure>'''


def section_head(lbl, heading, sub="", h="h2"):
    sub_html = f'<p class="sec-sub">{e(sub)}</p>' if sub else ""
    return f'<div class="sec-head" data-reveal>{label(lbl)}<{h} class="h2">{heading}</{h}>{sub_html}</div>'


def cta_band(heading=None, line=None):
    return f'''<section class="cta">
  <div class="shell cta-in" data-reveal>
    {label("Start a project")}
    <h2 class="display-2">{e(heading or C.CTA["heading"])}</h2>
    <p class="lede">{e(line or C.CTA["line"])}</p>
    {btn(C.CTA["button"], "/contact")}
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


# ------------------------------------------------------------------ layout

def layout(path, title, description, body, page_class="", og_image="/og.jpg", jsonld=None):
    full_title = title if title.startswith(SITE["name"]) else f'{title} — {SITE["name"]}'
    canonical = SITE["url"] + (path if path != "/" else "")
    current = "/" + path.strip("/").split("/")[0] if path != "/" else "/"

    def nav_link(name, href):
        cur = ' aria-current="page"' if href == current else ""
        return f'<a href="{href}"{cur}>{name}</a>'

    nav = "".join(nav_link(n, h) for n, h in C.NAV)
    menu = "".join(nav_link(n, h) for n, h in [("Home", "/")] + C.NAV + [("Collaborations", "/collaborations")])
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
<meta name="theme-color" content="#0c0a08">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(SITE["name"])}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE["url"]}{og_image}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&family=Sora:wght@500;600;700&display=swap">
<link rel="stylesheet" href="/css/site.css?v={CSS_V}">
<script>document.documentElement.classList.add('js')</script>
{ld}
</head>
<body class="{page_class}">
<a class="skip" href="#main">Skip to content</a>
<header class="nav" id="top">
  <div class="shell nav-in">
    <a class="logo" href="/" aria-label="{e(SITE["name"])} — home"><span class="logo-dot"></span><span>Productions by <b>AG</b></span></a>
    <nav class="nav-links" aria-label="Main">{nav}</nav>
    <a class="btn btn-light btn-sm nav-cta" href="/contact"><span>Start a project</span>{ARROW}</a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="menu" aria-label="Open menu"><span></span><span></span></button>
  </div>
  <div class="menu" id="menu" hidden>
    <nav class="shell menu-links" aria-label="Mobile">{menu}</nav>
    <div class="shell menu-foot">
      {btn("Start a project", "/contact")}
      <a class="label" href="mailto:{SITE["email"]}">{SITE["email"]}</a>
    </div>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
  <div class="shell">
    <div class="foot-top">
      <div>
        <a class="wordmark" href="/">Productions by AG</a>
        <p class="muted foot-tag">{e(SITE["tagline"])}</p>
      </div>
      <ul class="foot-nav">{foot}</ul>
      <ul class="foot-contact">
        <li><a href="mailto:{SITE["email"]}">{SITE["email"]}</a></li>
        <li><a href="{SITE["linkedin"]}" target="_blank" rel="noopener">LinkedIn {ARROW_UP}</a></li>
        <li><a href="{SITE["instagram"]}" target="_blank" rel="noopener">Instagram {ARROW_UP}</a></li>
      </ul>
    </div>
    <div class="foot-bottom label">
      <span>© {SITE["year"]} {e(SITE["name"])}</span>
      <span>{e(SITE["location"])}</span>
      <a href="#top">Back to top ↑</a>
    </div>
  </div>
</footer>
<script src="/js/site.js?v={JS_V}" defer></script>
</body>
</html>
'''


# ------------------------------------------------------------------ pages

def home():
    H = C.HOME
    h1 = f'{e(H["headline"][0])}<br>{e(H["headline"][1])}<br><em>{e(H["headline"][2])}</em>'
    disciplines = "".join(
        f'<a class="disc" href="/services#{d["id"]}" data-reveal><span class="label">#{i:02d}</span>'
        f'<strong>{e(d["name"])}</strong><span class="muted">{e(d["line"])}</span>{ARROW}</a>'
        for i, d in enumerate(C.DISCIPLINES, 1))
    featured = "".join(card(project(s), "(min-width: 760px) 50vw, 100vw") for s in H["featured"])
    trusted = "".join(f"<li>{e(n)}</li>" for n in H["trusted"])

    body = f'''
<section class="hero">
  <div class="hero-media" data-vimeo-bg="{SITE["showreel_vimeo"]}">
    <img src="/img/hero-poster.jpg" alt="" fetchpriority="high" width="1280" height="720">
  </div>
  <div class="hero-shade"></div>
  <span class="corner tl"></span><span class="corner tr"></span><span class="corner bl"></span><span class="corner br"></span>
  <div class="shell hero-in">
    <p class="label rec"><span class="rec-dot"></span>Showreel · {SITE["year"]}</p>
    <h1 class="display hero-h">{h1}</h1>
    <p class="lede hero-sub">{e(H["subhead"])}</p>
    <div class="actions">
      {btn("View work", "/work")}
      {btn("Start a project", "/contact", "ghost")}
    </div>
  </div>
  <p class="label hero-meta shell"><span>Lahore, Pakistan</span><span>Brand · Documentary · Social · Photography</span></p>
</section>

<section class="disciplines" aria-label="Disciplines">
  <div class="shell disc-grid">{disciplines}</div>
</section>

<section class="section">
  <div class="shell">
    {section_head("Selected work", e(H["featured_heading"]))}
    <div class="grid grid-2">{featured}</div>
    <div class="sec-foot">{btn("See all work", "/work", "ghost")}</div>
  </div>
</section>

<section class="section trusted">
  <div class="shell">
    <div class="trusted-in" data-reveal>
      {label(H["trusted_heading"])}
      <ul class="logos">{trusted}</ul>
      <a class="link" href="/collaborations">All collaborations {ARROW}</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="shell about-teaser">
    <div class="portrait" data-reveal>{img("abdul-ghaffar", "Abdul Ghaffar, filmmaker", "(min-width: 900px) 40vw, 100vw")}<p class="label">Abdul Ghaffar · Lahore</p></div>
    <div data-reveal>
      {label("About")}
      <h2 class="h2">{e(H["about_heading"])}</h2>
      <p class="lede">{e(H["about_text"])}</p>
      {btn("About me", "/about", "ghost")}
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
        "description": SITE["description"],
        "address": {"@type": "PostalAddress", "addressLocality": "Lahore", "addressCountry": "PK"},
        "founder": {"@type": "Person", "name": "Abdul Ghaffar", "jobTitle": "Filmmaker"},
        "sameAs": [SITE["linkedin"], SITE["instagram"]],
    }
    return layout("/", f'{SITE["name"]} — Brand films & documentaries, Lahore', SITE["description"], body, "page-home", jsonld=jsonld)


def work():
    chips = '<button type="button" class="chip" aria-pressed="true" data-filter="all">All</button>' + "".join(
        f'<button type="button" class="chip" aria-pressed="false" data-filter="{e(f)}">{e(f)}</button>' for f in C.WORK_FILTERS)
    cards = "".join(card(p) for p in C.PROJECTS)
    cuts = "".join(film(f, vertical=True) for f in C.SHORT_CUTS)
    body = f'''
{page_header("Work", "Selected work.", C.WORK_INTRO)}
<section class="section section-tight">
  <div class="shell">
    <div class="chips" role="group" aria-label="Filter by type">{chips}</div>
    <div class="grid grid-3" id="work-grid">{cards}</div>
    <p class="empty muted" hidden>Nothing in this category yet.</p>
  </div>
</section>
<section class="section">
  <div class="shell">
    {section_head("Short-form", "Recent cuts.", "Vertical films for creator and product partnerships. Sound on.")}
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
        heading = "The full film." if len(p["films"]) == 1 else "The films."
        films = f'''<section class="section">
  <div class="shell">
    {section_head("Watch", heading)}
    <div class="films">{"".join(film(f) for f in p["films"])}</div>
  </div>
</section>'''

    stills = ""
    if p["stills"]:
        items = "".join(f'<figure data-reveal>{img(s["img"], s["alt"], "(min-width: 760px) 50vw, 100vw")}</figure>' for s in p["stills"])
        stills = f'<section class="section"><div class="shell">{section_head("Stills", "From the shoot.")}<div class="stills">{items}</div></div></section>'

    making = "".join(f'<div><dt class="label">{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in
                     [("Category", p["type"]), ("Year", p["year"])] + p["making"])

    hero_media = ""
    if p.get("cover"):
        hero_media = f'<div class="shell cs-hero" data-reveal>{cover(p, "100vw", eager=True)}</div>'

    body = f'''
<section class="page-head cs-head">
  <div class="shell">
    <p class="label crumbs"><a href="/work">Work</a> / {e(p["client"])}</p>
    <p class="label"><span class="accent">{e(p["type"])}</span> · {e(p["year"])} · {e(p["role"])}</p>
    <h1 class="display">{e(p["title"])}</h1>
    <p class="lede">{e(p["standfirst"])}</p>
  </div>
</section>
{hero_media}
{story}
{films}
{stills}
<section class="section">
  <div class="shell">
    {section_head("Credits", "The making.")}
    <dl class="making" data-reveal>{making}</dl>
  </div>
</section>
<nav class="shell pager" aria-label="More projects">
  <a href="/work/{prev["slug"]}"><span class="label">← Previous</span><strong>{e(prev["client"])}</strong><span class="muted">{e(prev["type"])} · {e(prev["year"])}</span></a>
  <a href="/work/{nxt["slug"]}" class="next"><span class="label">Next →</span><strong>{e(nxt["client"])}</strong><span class="muted">{e(nxt["type"])} · {e(nxt["year"])}</span></a>
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
{page_header("About", e(A["headline"]), A["intro"])}
<section class="section section-tight">
  <div class="shell about-grid">
    <div class="portrait" data-reveal>{img("abdul-ghaffar", "Abdul Ghaffar", "(min-width: 900px) 40vw, 100vw")}</div>
    <div class="about-story" data-reveal>
      {label("Abdul Ghaffar")}
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
    {section_head("Principles", "How I work.")}
    <div class="principles">{principles}</div>
    <div class="sec-foot">{btn("Brands & partners I've worked with", "/collaborations", "ghost")}</div>
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
{page_header("Services", e(C.SERVICES_INTRO["heading"]), C.SERVICES_INTRO["subhead"])}
<section class="section section-tight">
  <div class="shell svc-list">{rows}</div>
</section>
<section class="section">
  <div class="shell photo-band" data-reveal>
    {img("psop", "Badshahi Mosque, Lahore — editorial photograph by Abdul Ghaffar", "(min-width: 900px) 40vw, 100vw")}
    <div>
      {label("Process")}
      <h2 class="h2">How projects start.</h2>
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
{page_header("Collaborations", e(C.COLLAB_INTRO["heading"]), C.COLLAB_INTRO["subhead"])}
<section class="section section-tight"><div class="shell collabs">{groups}</div></section>
{cta_band()}'''
    return layout("/collaborations", "Collaborations", "Brand partnerships with Sony, Nikon, Sigma, Insta360 and Hollyland; TEDx GCU; 50+ documentaries for Alkhidmat Foundation.", body, "page-collab")


def contact():
    K = C.CONTACT
    types = "".join(f'<label class="chip chip-radio"><input type="radio" name="type" value="{e(t)}" required><span>{e(t)}</span></label>' for t in K["project_types"])
    timelines = "".join(f"<option>{e(t)}</option>" for t in K["timelines"])
    body = f'''
{page_header("Contact", e(K["heading"]), K["subhead"])}
<section class="section section-tight">
  <div class="shell contact-grid">
    <form class="form" id="contact-form" action="/api/contact" method="post" novalidate>
      <div class="row2">
        <label class="field"><span class="label">Name *</span><input name="name" autocomplete="name" required></label>
        <label class="field"><span class="label">Email *</span><input name="email" type="email" autocomplete="email" required></label>
      </div>
      <div class="row2">
        <label class="field"><span class="label">Company <span class="muted">(optional)</span></span><input name="company" autocomplete="organization"></label>
        <label class="field"><span class="label">Timeline</span><select name="timeline">{timelines}</select></label>
      </div>
      <fieldset class="field"><legend class="label">Project type *</legend><div class="chips">{types}</div></fieldset>
      <label class="field"><span class="label">Tell me about your project *</span><textarea name="message" rows="6" required placeholder="What are you making, who is it for, and when do you need it?"></textarea></label>
      <label class="hp" aria-hidden="true">Website<input name="website" tabindex="-1" autocomplete="off"></label>
      <div class="form-foot">
        <button class="btn btn-accent" type="submit"><span>Send enquiry</span>{ARROW}</button>
        <p class="label muted">Reply within 2 working days</p>
      </div>
      <p class="form-status" role="status" aria-live="polite"></p>
    </form>
    <aside class="direct">
      <div>{label("Email directly")}<a class="direct-email" href="mailto:{SITE["email"]}">{SITE["email"]}</a></div>
      <div>{label("Studio")}<p>{e(SITE["location"])}</p><p class="muted">{e(K["travel"])}</p></div>
      <div>{label("Response")}<p>Within 2 working days</p><p class="muted">{e(K["hours"])}</p></div>
      <div>{label("Elsewhere")}<p><a href="{SITE["linkedin"]}" target="_blank" rel="noopener">LinkedIn {ARROW_UP}</a> &nbsp; <a href="{SITE["instagram"]}" target="_blank" rel="noopener">Instagram {ARROW_UP}</a></p></div>
    </aside>
  </div>
</section>'''
    return layout("/contact", "Start a project", "Tell me about your film, documentary, or content project. I respond within two working days.", body, "page-contact")


def not_found():
    body = f'''
<section class="page-head nf">
  <div class="shell">
    {label("404 · Scene missing")}
    <h1 class="display">This page didn't make the final cut.</h1>
    <div class="actions">{btn("Back home", "/")}{btn("See the work", "/work", "ghost")}</div>
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
        "contact.html": contact(),
        "404.html": not_found(),
    }
    n = len(C.PROJECTS)
    for i, p in enumerate(C.PROJECTS):
        pages[f'work/{p["slug"]}.html'] = case_study(p, C.PROJECTS[(i - 1) % n], C.PROJECTS[(i + 1) % n])

    for rel, text in pages.items():
        write(rel, text)

    urls = ["/", "/work", "/about", "/services", "/collaborations", "/contact"] + [f'/work/{p["slug"]}' for p in C.PROJECTS]
    sitemap = "".join(f"<url><loc>{SITE['url']}{u if u != '/' else ''}</loc></url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sitemap}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n")
    print(f"Built {len(pages)} pages into {OUT.relative_to(ROOT)}/")


CSS_V = JS_V = ""

if __name__ == "__main__":
    main()
