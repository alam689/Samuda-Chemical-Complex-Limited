"""Static site builder for the Samuda Chemical website.

Usage:  python build.py
Reads   src/layout.html, src/pages/*.html, src/data/products.json
Writes  site/  (deployable static website)
"""
import datetime
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "site"
SITE_URL = "https://www.scclbd.com/"
YEAR = datetime.date.today().year

# ---------------------------------------------------------------- icons
_S = 'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
ICON_PATHS = {
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "chevron": '<path d="M6 9l6 6 6-6"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "doc": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>',
    "flask": '<path d="M9 3h6M10 3v6L4.6 18.2A2 2 0 0 0 6.3 21h11.4a2 2 0 0 0 1.7-2.8L14 9V3"/><path d="M7.5 14h9"/>',
    "thread": '<ellipse cx="12" cy="5" rx="6" ry="2"/><ellipse cx="12" cy="19" rx="6" ry="2"/><path d="M6 5v14M18 5v14M6 9l12 3M6 13l12 3"/>',
    "hex": '<path d="M12 2.8l8 4.6v9.2l-8 4.6-8-4.6V7.4z"/><circle cx="12" cy="12" r="3"/>',
    "drop": '<path d="M12 3s6.5 7 6.5 11.5a6.5 6.5 0 0 1-13 0C5.5 10 12 3 12 3z"/><path d="M9 15a3 3 0 0 0 3 3"/>',
    "factory": '<path d="M3 21V10l6 3.5V10l6 3.5V5h3l1 16z"/><path d="M7 17h2M12 17h2"/>',
    "shield": '<path d="M12 3l7.5 3v6c0 4.5-3.2 8-7.5 9-4.3-1-7.5-4.5-7.5-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "leaf": '<path d="M5 19c0-8 5-13 15-14-1 10-6 15-14 15"/><path d="M5 19l7-7"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.8 3.8 5.8 3.8 9S14.6 18.2 12 21c-2.6-2.8-3.8-5.8-3.8-9S9.4 5.8 12 3z"/>',
    "handshake": '<path d="M3 12l4-4 4 2 3-2 7 5"/><path d="M7 8l-4 4 6 6 2-1 2 2 5-4"/><path d="M11 17l-2-2M13 15l-2-2"/>',
    "microscope": '<path d="M6 21h12M9 18h6M12 18a6 6 0 0 0 6-6"/><path d="M9 4l4 7-2 1-4-7z"/><path d="M10 14h2"/>',
    "truck": '<path d="M3 6h11v10H3zM14 9h4l3 3v4h-7"/><circle cx="7" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>',
    "users": '<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M16 4.5a3.2 3.2 0 0 1 0 6.3M18 14c1.9.8 3 2.9 3 6"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "box": '<path d="M3.5 7.5L12 3l8.5 4.5v9L12 21l-8.5-4.5z"/><path d="M3.5 7.5L12 12l8.5-4.5M12 12v9"/>',
    "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8"/>',
    "award": '<circle cx="12" cy="9" r="6"/><path d="M8.5 13.8L7 21l5-2.6 5 2.6-1.5-7.2"/><path d="M9.5 9l1.8 1.8L14.8 7.5"/>',
    "coin": '<circle cx="12" cy="12" r="9"/><path d="M14.8 9.2c-.5-.9-1.5-1.4-2.8-1.4-1.6 0-2.8.8-2.8 2s1.1 1.7 2.8 2.1 2.8.9 2.8 2.1-1.2 2.1-2.8 2.1c-1.4 0-2.4-.6-2.9-1.5M12 6v1.8M12 16.2V18"/>',
    "heart": '<path d="M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.4 4.3 4.3 0 0 1 19.5 10c0 5.4-7.5 10-7.5 10z"/><path d="M8.5 12h2l1-2 1.5 4 1-2h1.5"/>',
    "alert": '<path d="M12 3.5L21.5 20h-19z"/><path d="M12 10v4.5M12 17.2v.3"/>',
    "scale": '<path d="M12 4v16M7 20h10M5 7h14M12 4l-1 3h2z"/><path d="M5 7l-2.5 6a2.5 2.5 0 0 0 5 0zM19 7l-2.5 6a2.5 2.5 0 0 0 5 0z"/>',
    "cup": '<path d="M4 9h13v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5z"/><path d="M17 11h1.5a2.5 2.5 0 0 1 0 5H17M8 3.5c-.6.8-.6 1.7 0 2.5M12 3.5c-.6.8-.6 1.7 0 2.5"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/>',
}


def icon(name, cls="ico"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" {_S} aria-hidden="true">{ICON_PATHS[name]}</svg>'


# ---------------------------------------------------------------- logo
# Vector recreation of the Samuda "S" mark. Replace with the official SVG logo when supplied.
LOGO_MARK = (
    '<svg class="brand__mark" viewBox="0 0 48 48" aria-hidden="true">'
    '<path class="lm-blue" d="M45 5l-4.2 8.4H21.5c-3.3 0-4.6 2.6-2.7 5l2.4 3-9.6 3.4-2.6-3.6C3.3 13.5 8.6 5 18 5z"/>'
    '<path class="lm-blue" d="M3 43l4.2-8.4h19.3c3.3 0 4.6-2.6 2.7-5l-2.4-3 9.6-3.4 2.6 3.6C44.7 34.5 39.4 43 30 43z"/>'
    '<path class="lm-green" d="M9 21.2c7.6-5.4 19.5-6.3 28.6 1.6l-10.9 3.6c-4.6-3-10.4-3.4-15.4-1.3z"/>'
    "</svg>"
)


def logo(variant=""):
    return (
        f'<span class="logo {variant}">{LOGO_MARK}'
        '<span class="logo__text"><span class="logo__name">SAMUDA</span>'
        '<span class="logo__sub">Chemical Complex Limited</span></span></span>'
    )


# ---------------------------------------------------------------- data
DATA = json.loads((SRC / "data" / "products.json").read_text(encoding="utf-8"))
CATS = {c["slug"]: c for c in DATA["categories"]}
INDUSTRIES = DATA["industries"]
PRODUCTS = DATA["products"]
BY_SLUG = {p["slug"]: p for p in PRODUCTS}

e = html.escape


def product_img(p, root, sizes="(max-width: 680px) 100vw, 320px", eager=False):
    loading = "" if eager else ' loading="lazy"'
    return (
        f'<img src="{root}assets/img/products/{p["image"]}.webp" sizes="{sizes}" '
        f'alt="{e(p["name"])} — Samuda Chemical product sample"{loading}>'
    )


def product_card(p, root):
    cat = CATS[p["category"]]
    inds = " ".join(p["industries"])
    if p.get("image"):
        media = f'{product_img(p, root)}<span class="pcard__tag">{e(p["form"])}</span>'
        media_cls = "pcard__media pcard__media--photo"
    else:
        media = f'<span class="pcard__formula">{e(p["formula"])}</span>{icon(cat["icon"], "pcard__icon")}<span class="pcard__tag">{e(p["form"])}</span>'
        media_cls = f"pcard__media pcard__media--{p['category']}"
    return f"""
<article class="pcard reveal" data-product-card data-category="{p['category']}" data-industries="{inds}" data-name="{e(p['name'].lower())} {e(p['formula'].lower())} {e(p['chemical'].lower())}">
  <a class="{media_cls}" href="{root}products/{p['slug']}.html" tabindex="-1" aria-hidden="true">
    {media}
  </a>
  <div class="pcard__body">
    <p class="pcard__cat">{e(p['chemical'])}</p>
    <h3 class="pcard__title"><a href="{root}products/{p['slug']}.html">{e(p['name'])}</a></h3>
    <p class="pcard__text">{e(p['short'])}</p>
    {f'<p class="pcard__cap">{icon("factory")}<span>{e(p["capacityShort"])}</span></p>' if p.get("capacityShort") else ''}
    <div class="pcard__actions">
      <a class="link-arrow" href="{root}products/{p['slug']}.html">Details {icon('arrow')}</a>
      <button class="add-btn" type="button" data-add-inquiry="{e(p['name'])}" aria-label="Add {e(p['name'])} to inquiry list">{icon('plus')}<span>Inquiry</span></button>
    </div>
  </div>
</article>"""


def products_grid(root):
    return "\n".join(product_card(p, root) for p in PRODUCTS)


def category_cards(root):
    out = []
    for i, c in enumerate(DATA["categories"], 1):
        items = [p for p in PRODUCTS if p["category"] == c["slug"]]
        lis = "".join(
            f'<li><a href="{root}products/{p["slug"]}.html">{e(p["name"])}</a></li>' for p in items[:6]
        )
        if len(items) > 6:
            lis += f'<li><a href="{root}products.html?category={c["slug"]}">+ {len(items) - 6} more</a></li>'
        out.append(f"""
<article class="ccard ccard--{c['slug']} reveal" style="--d:{(i-1)*80}ms">
  <div class="ccard__top"><span class="ccard__num">0{i}</span><span class="ccard__count">{len(items)} products</span>{icon(c['icon'], 'ccard__icon')}</div>
  <h3 class="ccard__title">{e(c['name'])}</h3>
  <p class="ccard__text">{e(c['short'])}</p>
  <ul class="ccard__list">{lis}</ul>
  <a class="link-arrow" href="{root}products.html?category={c['slug']}">Explore range {icon('arrow')}</a>
</article>""")
    return "\n".join(out)


def product_gallery(root):
    """Horizontal showcase of products that have real photography."""
    items = [p for p in PRODUCTS if p.get("image")]
    return "".join(
        f"""<a class="gallery__item reveal" style="--d:{i*60}ms" href="{root}products/{p['slug']}.html">
  <span class="gallery__img">{product_img(p, root, "300px")}</span>
  <span class="gallery__cap"><strong>{e(p['name'])}</strong><small>{e(p['chemical'])}</small></span>
</a>"""
        for i, p in enumerate(items)
    )


def mega_feature(root, href, img, label, title_html, text, cta):
    return (
        f'<a class="mm__feature" href="{root}{href}">'
        f'<img src="{root}assets/img/{img}" alt="" loading="lazy">'
        f'<span class="mm__feature-body"><small>{label}</small><strong>{title_html}</strong>'
        f'<span>{text}</span><span class="mm__feature-cta">{cta} {icon("arrow")}</span></span></a>'
    )


def mega_foot(root, icon_name, text, href, cta):
    return (
        f'<div class="mm__foot"><p>{icon(icon_name)}<span>{text}</span></p>'
        f'<a class="btn btn--primary btn--sm" href="{root}{href}">{cta} {icon("arrow")}</a></div>'
    )


COMPANY_GROUPS = [
    ("users", "Who we are", "Our story and reach", [
        ("about.html", "users", "About Samuda", "Our story, mission and locations"),
        ("global-reach.html", "globe", "Global Reach", "Exporting to 30+ countries"),
        ("news.html", "doc", "News", "Company announcements"),
        ("careers.html", "spark", "Careers", "Build your future with us"),
    ]),
    ("factory", "How we work", "Standards we live by", [
        ("manufacturing.html", "factory", "Manufacturing", "Facilities, process and laboratory"),
        ("quality-sustainability.html", "leaf", "Quality & Sustainability", "QA, safety and environment"),
        ("policies.html", "shield", "Company Policies", "Labour rights, ethics and governance"),
    ]),
]


def company_menu(root):
    cols = []
    for i, (ic, title, sub, links) in enumerate(COMPANY_GROUPS):
        items = "".join(
            f'<li><a class="mm__link" href="{root}{href}"><span class="mm__link-ico">{icon(li)}</span>'
            f'<span class="mm__link-text"><strong>{e(name)}</strong><small>{e(desc)}</small></span>'
            f'{icon("arrow", "ico mm__link-go")}</a></li>'
            for href, li, name, desc in links
        )
        cols.append(
            f'<div class="mm__col" style="--i:{i}"><div class="mm__head mm__head--static">'
            f'<span class="mm__icon">{icon(ic)}</span><span class="mm__title"><strong>{title}</strong>'
            f'<small>{sub}</small></span></div><ul class="mm__links">{items}</ul></div>'
        )
    glance = (
        '<div class="mm__col mm__col--glance" style="--i:2"><div class="mm__glance">'
        '<p class="mm__glance-h">At a glance</p>'
        '<div class="mm__stat"><b>2006</b><span>Established</span></div>'
        '<div class="mm__stat"><b>30+</b><span>Export countries</span></div>'
        '<div class="mm__stat"><b>54</b><span>Documented policies</span></div>'
        '<div class="mm__stat"><b>T.K.</b><span>Group concern</span></div>'
        f'<a class="mm__glance-link" href="{root}policies.html#labour-rights">{icon("shield")}'
        '<span>Labour Rights &amp; Appointment Policy</span></a>'
        '</div></div>'
    )
    feature = mega_feature(
        root, "about.html", "plants/caco3-plant.webp", "Since 2006",
        "Chemistry for a <em>better</em> tomorrow.",
        "A concern of T.K. Group and one of Bangladesh&rsquo;s largest caustic soda and hydrogen peroxide producers.",
        "About Samuda",
    )
    foot = mega_foot(
        root, "pin",
        "Head office: T.K. Bhaban, 13 Karwan Bazar, Dhaka &nbsp;·&nbsp; Factory: Sikirgaon, Gazaria, Munshiganj",
        "contact.html", "Contact us",
    )
    return f'<div class="mm">{feature}<div class="mm__cols mm__cols--company">{"".join(cols)}{glance}</div></div>{foot}'


PLANT_CARDS = [
    ("chlor-alkali", "chlorine-plant", "01", "Chlor-Alkali", "Caustic soda, chlorine, HCl & hypochlorite", "Up to 170 MT/day flakes"),
    ("hydrogen-peroxide", "iso-tank", "02", "Hydrogen Peroxide", "35%, 50% & 60% technical grades", "Up to 250 MT/day"),
    ("calcium-carbonate", "caco3-plant", "03", "Calcium Carbonate", "Coated, uncoated & filler compound", "Up to 5,500 MT/month"),
    ("samuda-power", "power-plant", "04", "Samuda Power", "Three Wärtsilä natural-gas engines", "28.19 MW"),
]


def plants_menu(root):
    cards = "".join(
        f'<a class="mm__plant" style="--i:{i}" href="{root}plants.html#{anchor}">'
        f'<span class="mm__plant-img"><img src="{root}assets/img/plants/{img}.webp" alt="" loading="lazy">'
        f'<span class="mm__plant-n">{n}</span></span>'
        f'<span class="mm__plant-body"><strong>{e(name)}</strong><small>{e(desc)}</small>'
        f'<span class="mm__plant-cap">{icon("factory")}{e(cap)}</span></span></a>'
        for i, (anchor, img, n, name, desc, cap) in enumerate(PLANT_CARDS)
    )
    feature = mega_feature(
        root, "plants.html", "aerial-800.webp", "Gazaria complex",
        "One complex.<br><em>Four</em> plants.",
        "An integrated chemical complex on the banks of the Meghna, powered by our own station.",
        "Explore our plants",
    )
    foot = mega_foot(
        root, "users", "Plant visits for customers and partners are available by appointment.",
        "contact.html#general", "Arrange a visit",
    )
    return f'<div class="mm">{feature}<div class="mm__cols mm__cols--plants">{cards}</div></div>{foot}'


# ---------------------------------------------------------------- world map
# Equirectangular projection cropped to 78°N–56°S; the dotted land layer is drawn
# in the browser by assets/js/main.js from the same projection.
MAP_W, MAP_H, MAP_N, MAP_S = 1000, 372, 78, -56
DHAKA = (90.41, 23.81)
EXPORT_REGIONS = [
    # name, lon, lat, label anchor ("start"/"end"), label dx, label dy
    ("Europe", 12, 49, "end", -14, -10),
    ("Africa", 21, 3, "end", -14, 22),
    ("East Asia", 118, 34, "start", 14, -8),
    ("South-East Asia", 105, 5, "start", 14, 22),
    ("South Asia", 77, 14, "middle", 0, 30),
]


def proj(lon, lat):
    return (lon + 180) / 360 * MAP_W, (MAP_N - lat) / (MAP_N - MAP_S) * MAP_H


def world_map():
    hx, hy = proj(*DHAKA)
    arcs, nodes, labels = [], [], []
    for i, (name, lon, lat, anchor, dx, dy) in enumerate(EXPORT_REGIONS):
        x, y = proj(lon, lat)
        dist = ((x - hx) ** 2 + (y - hy) ** 2) ** 0.5
        cx, cy = (x + hx) / 2, min(y, hy) - dist * 0.42 - 10
        d = f"M{hx:.1f} {hy:.1f} Q{cx:.1f} {cy:.1f} {x:.1f} {y:.1f}"
        dur = 2.6 + i * 0.35
        arcs.append(
            f'<path class="wm__arc" d="{d}" style="--i:{i}"/>'
            f'<circle class="wm__spark" r="3.2"><animateMotion dur="{dur:.2f}s" begin="{i*0.5:.1f}s" repeatCount="indefinite" path="{d}"/></circle>'
        )
        nodes.append(
            f'<g class="wm__node" style="--i:{i}"><circle class="wm__ring" cx="{x:.1f}" cy="{y:.1f}" r="9"/>'
            f'<circle class="wm__dot" cx="{x:.1f}" cy="{y:.1f}" r="4.5"/></g>'
        )
        labels.append(f'<text class="wm__label" x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}">{name}</text>')
    hub = (
        f'<g class="wm__hub"><circle class="wm__pulse" cx="{hx:.1f}" cy="{hy:.1f}" r="8"/>'
        f'<circle class="wm__pulse wm__pulse--2" cx="{hx:.1f}" cy="{hy:.1f}" r="8"/>'
        f'<circle class="wm__hubdot" cx="{hx:.1f}" cy="{hy:.1f}" r="7"/></g>'
        f'<text class="wm__label wm__label--hub" x="{hx + 14:.1f}" y="{hy - 14:.1f}">Dhaka</text>'
        f'<text class="wm__sub" x="{hx + 14:.1f}" y="{hy + 1:.1f}">BANGLADESH</text>'
    )
    legend = "".join(
        f'<li><span class="wm__legend-dot"></span>{name}</li>' for name, *_ in EXPORT_REGIONS
    )
    return f"""<figure class="wm" data-world-map data-w="{MAP_W}" data-h="{MAP_H}" data-n="{MAP_N}" data-s="{MAP_S}">
  <svg class="wm__svg" viewBox="0 0 {MAP_W} {MAP_H}" role="img" aria-labelledby="wm-title">
    <title id="wm-title">World map showing exports from Dhaka, Bangladesh to Europe, Africa, East Asia, South-East Asia and South Asia</title>
    <g class="wm__land" data-land></g>
    <g class="wm__arcs">{''.join(arcs)}</g>
    <g class="wm__nodes">{''.join(nodes)}</g>
    {hub}
    <g class="wm__labels">{''.join(labels)}</g>
  </svg>
  <figcaption class="wm__legend"><span class="wm__legend-hub">Head office · Dhaka</span><ul>{legend}</ul></figcaption>
</figure>"""


MEGA_TAGLINES = {
    "basic": "Bulk chemicals",
    "performance": "Samuda textile auxiliaries",
    "calcium": "Fillers & minerals",
}


def mega_menu(root):
    cols = []
    for i, c in enumerate(DATA["categories"]):
        items = [p for p in PRODUCTS if p["category"] == c["slug"]]
        if c["slug"] == "performance":
            # brand names read better with their chemical function underneath
            lis = "".join(
                f'<li><a href="{root}products/{p["slug"]}.html"><span class="mm__name">{e(p["name"])}</span>'
                f'<small>{e(p["chemical"])}</small></a></li>'
                for p in items
            )
        else:
            lis = "".join(
                f'<li><a href="{root}products/{p["slug"]}.html"><span class="mm__name">{e(p["name"])}</span>'
                f'<span class="mm__f">{e(p["formula"])}</span></a></li>'
                for p in items
            )
        extra = ""
        if c["slug"] == "calcium":
            extra = (
                f'<a class="mm__promo" href="{root}plants.html">'
                f'<img src="{root}assets/img/plants/caco3-plant.webp" alt="" loading="lazy">'
                f'<span><small>Our plants</small><strong>See where it&rsquo;s made</strong></span>{icon("arrow")}</a>'
            )
        cols.append(
            f'<div class="mm__col mm__col--{c["slug"]}" style="--i:{i}">'
            f'<a class="mm__head" href="{root}products.html?category={c["slug"]}">'
            f'<span class="mm__icon">{icon(c["icon"])}</span>'
            f'<span class="mm__title"><strong>{e(c["name"])}</strong><small>{len(items)} products · {MEGA_TAGLINES[c["slug"]]}</small></span>'
            f'{icon("arrow", "ico mm__go")}</a>'
            f'<ul class="mm__list">{lis}</ul>{extra}</div>'
        )
    feature = (
        f'<a class="mm__feature" href="{root}products.html">'
        f'<img src="{root}assets/img/plants/chlorine-plant.webp" alt="" loading="lazy">'
        f'<span class="mm__feature-body"><small>Catalogue</small>'
        f'<strong>{len(PRODUCTS)} products.<br><em>Three</em> families.</strong>'
        f'<span>From bulk chlor-alkali chemicals to our own performance range.</span>'
        f'<span class="mm__feature-cta">Browse all products {icon("arrow")}</span></span></a>'
    )
    foot = (
        f'<div class="mm__foot"><p>{icon("doc")}<span>Need a TDS, SDS or a custom grade? Our technical team will help.</span></p>'
        f'<a class="btn btn--primary btn--sm" href="{root}contact.html#rfq">Request a Quote {icon("arrow")}</a></div>'
    )
    return f'<div class="mm">{feature}<div class="mm__cols">{"".join(cols)}</div></div>{foot}'


def footer_categories(root):
    return "".join(
        f'<li><a href="{root}products.html?category={c["slug"]}">{e(c["name"])}</a></li>' for c in DATA["categories"]
    )


def product_options():
    groups = []
    for c in DATA["categories"]:
        opts = "".join(
            f'<option value="{e(p["name"])}">{e(p["name"])}</option>' for p in PRODUCTS if p["category"] == c["slug"]
        )
        groups.append(f'<optgroup label="{e(c["name"])}">{opts}</optgroup>')
    return "".join(groups)


def category_filters():
    return "".join(
        f'<button class="chip" type="button" data-filter-category="{c["slug"]}" aria-pressed="false">{e(c["name"])}</button>'
        for c in DATA["categories"]
    )


def industry_options():
    return "".join(f'<option value="{k}">{e(v)}</option>' for k, v in INDUSTRIES.items())


def industry_products(root, key):
    """Product cards for one industry, grouped by product family."""
    out = []
    for c in DATA["categories"]:
        items = [p for p in PRODUCTS if key in p["industries"] and p["category"] == c["slug"]]
        if not items:
            continue
        cards = []
        for i, p in enumerate(items):
            if p.get("image"):
                thumb = f'<span class="ipc__thumb">{product_img(p, root, "56px")}</span>'
            else:
                thumb = f'<span class="ipc__thumb ipc__thumb--{p["category"]}">{e(p["formula"])}</span>'
            cards.append(
                f'<a class="ipc reveal" style="--d:{i*40}ms" href="{root}products/{p["slug"]}.html">{thumb}'
                f'<span class="ipc__text"><strong>{e(p["name"])}</strong><small>{e(p["chemical"])}</small></span>'
                f'{icon("arrow", "ico ipc__go")}</a>'
            )
        out.append(
            f'<div class="ipgroup"><p class="ipgroup__h"><span class="ipgroup__dot ipgroup__dot--{c["slug"]}"></span>'
            f'{e(c["name"])}<b>{len(items)}</b></p><div class="ipgrid">{"".join(cards)}</div></div>'
        )
    return "".join(out)


def industry_count(key):
    return str(sum(1 for p in PRODUCTS if key in p["industries"]))


def industry_thumbs(root, key):
    """Overlapping circular product photos for the industry visual card."""
    items = [p for p in PRODUCTS if key in p["industries"] and p.get("image")][:4]
    return "".join(
        f'<span class="avatar">{product_img(p, root, "48px")}</span>' for p in items
    )


# ---------------------------------------------------------------- product detail
def spec_table(t):
    head = "".join(f'<th scope="col">{e(h)}</th>' for h in t["head"])
    rows = "".join(
        "<tr>" + "".join((f'<th scope="row">{e(c)}</th>' if i == 0 else f"<td>{e(c)}</td>") for i, c in enumerate(r)) + "</tr>"
        for r in t["rows"]
    )
    return f"""<div class="spec-table reveal"><h3 class="spec-table__title">{e(t['title'])}</h3>
<div class="spec-table__scroll"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div></div>"""


HANDLING = (
    "Use face shields, protective clothing, gloves and boots when handling. Avoid contact with skin and eyes. "
    "If splashed in the eyes, rinse immediately with plenty of water for 10–15 minutes and seek medical advice. "
    "On skin contact, wash immediately with soap and water and remove soiled clothing."
)


def product_page(p):
    root = "../"
    cat = CATS[p["category"]]
    related = [q for q in PRODUCTS if q["category"] == p["category"] and q["slug"] != p["slug"]][:3]
    if len(related) < 3:
        related += [q for q in PRODUCTS if q["slug"] != p["slug"] and q not in related][: 3 - len(related)]
    rel = "\n".join(product_card(q, root) for q in related)
    inds = "".join(
        f'<a class="chip chip--static" href="{root}industries.html#{k}">{e(INDUSTRIES[k])}</a>' for k in p["industries"]
    )
    quote = f"{root}contact.html?product={e(p['name'])}"

    # hero visual: real photo when we have one, otherwise the formula orb
    if p.get("image"):
        cap_chip = ""
        if p.get("capacityShort"):
            cap_chip = f'<span class="pshot__chip pshot__chip--b">{icon("factory")}<span><small>Capacity</small>{e(p["capacityShort"])}</span></span>'
        visual = f"""<div class="pshot">
        <div class="pshot__frame">{product_img(p, root, "(max-width: 980px) 90vw, 440px", eager=True)}</div>
        <span class="pshot__chip pshot__chip--a">{icon('box')}<span><small>Form</small>{e(p['form'])}</span></span>
        {cap_chip}
      </div>"""
    else:
        visual = f"""<div class="formula-tile formula-tile--{p['category']}" aria-hidden="true">
        <span class="formula-tile__f">{e(p['formula'])}</span>
        <span class="formula-tile__n">{e(p['form'])}</span>
        <svg class="formula-tile__orbit" viewBox="0 0 200 200"><circle cx="100" cy="100" r="78"/><circle cx="100" cy="100" r="96"/><circle class="dot" cx="178" cy="100" r="4"/><circle class="dot" cx="31" cy="140" r="3"/></svg>
      </div>"""

    # key facts strip
    facts = [("flask", "Chemical name", p["chemical"]), ("box", "Physical state", p["form"])]
    if p.get("capacity"):
        facts.append(("factory", "Production capacity", p["capacity"]))
    if p.get("packaging"):
        facts.append(("truck", "Packaging", p["packaging"]))
    facts_html = "".join(
        f'<div class="kfact reveal" style="--d:{i*70}ms">{icon(ic)}<small>{e(k)}</small><strong>{e(v)}</strong></div>'
        for i, (ic, k, v) in enumerate(facts)
    )

    blocks = []
    overview = "".join(f"<p>{e(x)}</p>" for x in p["overview"])
    blocks.append(f'<div class="reveal"><p class="eyebrow">Overview</p><h2 class="h2">About {e(p["name"])}</h2><div class="lead-text">{overview}</div></div>')

    if p.get("features"):
        feats = "".join(f"<li>{icon('check')}<span>{e(f)}</span></li>" for f in p["features"])
        blocks.append(f'<div class="reveal"><h3 class="h3">Special features</h3><ul class="check-list">{feats}</ul></div>')

    tables = list(p.get("tables", []))
    if p.get("properties"):
        tables.insert(0, {"title": "Typical properties", "head": ["Property", "Value"], "rows": p["properties"]})
    if tables:
        blocks.append(
            '<div><p class="eyebrow reveal">Technical data</p><h2 class="h2 reveal">Specifications</h2>'
            + "".join(spec_table(t) for t in tables) + "</div>"
        )

    if p.get("dosage") or p.get("usage"):
        dose = "".join(
            f'<div class="dose reveal" style="--d:{i*70}ms"><small>{e(d[0])}</small><strong>{e(d[1])}</strong>'
            + (f"<span>{e(d[2])}</span>" if d[2] else "") + "</div>"
            for i, d in enumerate(p.get("dosage", []))
        )
        dose_html = f'<div class="dose-grid">{dose}</div>' if dose else ""
        usage = "".join(f"<p>{e(u)}</p>" for u in p.get("usage", []))
        blocks.append(f'<div class="reveal"><h3 class="h3">Application &amp; recommended dosage</h3>{dose_html}{usage}</div>')

    if p.get("applications"):
        apps = "".join(f"<li>{icon('check')}<span>{e(a)}</span></li>" for a in p["applications"])
        blocks.append(f'<div class="reveal"><h3 class="h3">Uses &amp; applications</h3><ul class="check-list">{apps}</ul></div>')

    blocks.append(f'<div class="reveal"><h3 class="h3">Industries</h3><div class="chips">{inds}</div></div>')

    if p.get("technology"):
        tech = "".join(f'<li>{icon("gear")}<span>{e(t)}</span></li>' for t in p["technology"])
        blocks.append(f'<div class="reveal"><h3 class="h3">Technology supported by</h3><ul class="tech-list">{tech}</ul></div>')

    storage = f"<p><strong>Storage:</strong> {e(p['storage'])}</p>" if p.get("storage") else ""
    blocks.append(
        f'<div class="safety reveal">{icon("shield")}<div><h3 class="h3">Handling &amp; safety</h3><p>{HANDLING}</p>{storage}'
        '<p class="muted" style="margin:0">Always refer to the product Safety Data Sheet (SDS), available on request.</p></div></div>'
    )

    spec_rows = [("Category", cat["name"]), ("Chemical name", p["chemical"]), ("Physical form", p["form"])]
    if p.get("capacityShort"):
        spec_rows.append(("Capacity", p["capacityShort"]))
    spec_rows.append(("Packaging", p.get("packaging") or "Contact us for options"))
    spec_dl = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in spec_rows)
    reg = '<sup class="reg">®</sup>' if p["category"] == "performance" else ""

    content = f"""
<section class="page-hero page-hero--product">
  <div class="page-hero__bg" aria-hidden="true"></div>
  <div class="container page-hero__inner">
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <a href="{root}index.html">Home</a><span>/</span><a href="{root}products.html">Products</a><span>/</span><a href="{root}products.html?category={cat['slug']}">{e(cat['name'])}</a>
    </nav>
    <div class="pdetail-hero">
      <div>
        <p class="eyebrow eyebrow--light">{e(cat['name'])}</p>
        <h1 class="page-hero__title">{e(p['name'])}{reg}</h1>
        <p class="pdetail-hero__chem">{e(p['chemical'])}</p>
        <p class="page-hero__lead">{e(p['short'])}</p>
        <div class="hero__actions">
          <a class="btn btn--primary" href="{quote}#rfq">Request a Quote {icon('arrow')}</a>
          <button class="btn btn--ghost" type="button" data-add-inquiry="{e(p['name'])}">{icon('plus')} Add to inquiry list</button>
        </div>
      </div>
      {visual}
    </div>
  </div>
</section>

<section class="kfacts-wrap">
  <div class="container"><div class="kfacts">{facts_html}</div></div>
</section>

<section class="section" style="padding-top:72px">
  <div class="container pdetail">
    <div class="pdetail__main">
      {''.join(blocks)}
    </div>
    <aside class="pdetail__aside reveal">
      <div class="spec-card">
        <h2 class="spec-card__title">At a glance</h2>
        <dl class="spec">{spec_dl}</dl>
        <div class="docs">
          <a class="doc-link" href="{quote}&amp;doc=TDS#rfq">{icon('doc')}<span><strong>Technical Data Sheet</strong><small>Available on request</small></span></a>
          <a class="doc-link" href="{quote}&amp;doc=SDS#rfq">{icon('shield')}<span><strong>Safety Data Sheet</strong><small>Available on request</small></span></a>
        </div>
        <a class="btn btn--primary btn--block" href="{quote}#rfq">Request a Quote {icon('arrow')}</a>
      </div>
    </aside>
  </div>
</section>

<section class="section section--mist">
  <div class="container">
    <div class="section-head reveal">
      <div><p class="eyebrow">Related</p><h2 class="h2">You may also need</h2></div>
      <a class="link-arrow" href="{root}products.html">All products {icon('arrow')}</a>
    </div>
    <div class="pgrid">{rel}</div>
  </div>
</section>
"""

    jsonld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p["name"],
        "description": p["short"],
        "category": cat["name"],
        "brand": {"@type": "Organization", "name": "Samuda Chemical Complex Limited"},
    }
    content += f'\n<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>\n'
    meta = {
        "title": f"{p['name']} — {cat['name']}",
        "description": f"{p['name']} ({p['chemical']}) by Samuda Chemical Complex Limited. {p['short']}",
        "nav": "products",
    }
    return render(content, meta, root, f"products/{p['slug']}.html")


# ---------------------------------------------------------------- rendering
LAYOUT = (SRC / "layout.html").read_text(encoding="utf-8")


def fill_tokens(text, root):
    tokens = {
        "root": root,
        "year": str(YEAR),
        "logo": logo(),
        "logo_light": logo("logo--light"),
        "mega_menu": mega_menu(root),
        "company_menu": company_menu(root),
        "world_map": world_map(),
        "plants_menu": plants_menu(root),
        "footer_categories": footer_categories(root),
        "products_grid": products_grid(root),
        "category_cards": category_cards(root),
        "product_options": product_options(),
        "category_filters": category_filters(),
        "industry_options": industry_options(),
        "product_count": str(len(PRODUCTS)),
        "product_gallery": product_gallery(root),
    }
    text = re.sub(r"\{\{icon:([a-z]+)(?::([a-z_-]+))?\}\}", lambda m: icon(m.group(1), m.group(2) or "ico"), text)
    text = re.sub(r"\{\{industry_products:([a-z]+)\}\}", lambda m: industry_products(root, m.group(1)), text)
    text = re.sub(r"\{\{industry_count:([a-z]+)\}\}", lambda m: industry_count(m.group(1)), text)
    text = re.sub(r"\{\{industry_thumbs:([a-z]+)\}\}", lambda m: industry_thumbs(root, m.group(1)), text)
    for k, v in tokens.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def render(content, meta, root, path):
    title = meta.get("title", "")
    full_title = (
        "Samuda Chemical Complex Limited — Industrial Chemicals Manufacturer in Bangladesh"
        if path == "index.html"
        else f"{title} | Samuda Chemical"
    )
    page = LAYOUT.replace("{{content}}", content)
    page = page.replace("{{title}}", e(full_title))
    page = page.replace("{{description}}", e(meta.get("description", "")))
    page = page.replace("{{path}}", "" if path == "index.html" else path)
    head_extra = ""
    if meta.get("bengali") == "yes":
        head_extra = '<link href="https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600&display=swap" rel="stylesheet">'
    page = page.replace("{{head_extra}}", head_extra)
    page = page.replace("{{bodyclass}}", f"page-{meta.get('nav', 'none')}")
    page = fill_tokens(page, root)
    # mark the active nav item
    nav = meta.get("nav")
    if nav:
        page = page.replace(f'data-nav-key="{nav}"', f'data-nav-key="{nav}" data-active')
    return page


def parse_page(text):
    m = re.match(r"\s*<!--(.*?)-->\s*", text, re.S)
    meta = {}
    if m:
        for line in m.group(1).strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        text = text[m.end():]
    return meta, text


def main():
    written = []
    for src in sorted((SRC / "pages").glob("*.html")):
        meta, body = parse_page(src.read_text(encoding="utf-8"))
        (OUT / src.name).write_text(render(body, meta, "", src.name), encoding="utf-8")
        written.append(src.name)
    (OUT / "products").mkdir(parents=True, exist_ok=True)
    for p in PRODUCTS:
        path = f"products/{p['slug']}.html"
        (OUT / path).write_text(product_page(p), encoding="utf-8")
        written.append(path)

    urls = "".join(
        f"<url><loc>{SITE_URL}{'' if w == 'index.html' else w}</loc></url>"
        for w in written
        if w != "privacy.html"
    )
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>',
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8")
    favicon = LOGO_MARK.replace('class="brand__mark" ', 'xmlns="http://www.w3.org/2000/svg" ').replace(
        'class="lm-blue"', 'fill="#1E56A0"').replace('class="lm-green"', 'fill="#2BAA4A"')
    (OUT / "assets" / "img" / "favicon.svg").write_text(favicon, encoding="utf-8")
    print(f"Built {len(written)} pages into {OUT}")


if __name__ == "__main__":
    main()
