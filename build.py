#!/usr/bin/env python3
"""Generates every page and the certificate border for jaguarinv.com.

Run `python3 build.py` after changing anything here. The .html files and
images/border.svg are outputs: edit this file, not them.
"""
import math
import os
import shutil
import subprocess

INK = "#12100d"
PAPER = "#ece7dc"
SITE = "https://jaguarinv.com"
EMAIL = "contact@jaguarinv.com"
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

# slug, menu label, page title, one-sentence copy, kind
# kind: offering | about | investors | contact
PAGES = [
    ("capital-markets", "Capital Markets", "Capital Markets",
     "Debt and equity financing for real estate and operating companies. We structure the capital, run the process, and negotiate terms with lenders and investors.",
     "offering"),
    ("real-estate", "Real Estate", "Real Estate",
     "We acquire, recapitalize, and co-invest in commercial real estate, on our own account and alongside partners.",
     "offering"),
    ("private-equity", "Private Equity", "Private Equity",
     "Direct and co-investments in private companies and real-asset platforms.",
     "offering"),
    ("underwriting", "Underwriting &amp; Consulting", "Underwriting &amp; Consulting",
     "Independent underwriting, due diligence, and transaction advice for owners, lenders, and investors.",
     "offering"),
    ("research", "Research", "Research",
     "Market and submarket analysis, prepared for our clients and our own investments.",
     "offering"),
    ("asset-management", "Asset Management", "Asset Management",
     "Operations, leasing, and reporting for the assets we own and those we manage for others.",
     "offering"),
    ("about", "About", "About",
     "Jaguar Investments Group advises and invests across real estate and private capital.",
     "about"),
    ("investors", "Investors", "Investors",
     "Secure access for limited partners and co-investors.",
     "investors"),
    ("contact", "Contact", "Contact",
     "For new business, financing requests, and general inquiries.",
     "contact"),
]

# PLACEHOLDERS per offering. Replace before launch.
# Shown under Transactions / Case Studies on each offering page.
PLACEHOLDER_NOTICE = (
    "Senior Loan", "$00,000,000", "Property Name", "City, State",
    "arranged the financing", "Month Year",
)
PLACEHOLDER_STUDY = (
    "Case Study", "Property Name", "City, State",
    "Brief summary of the mandate and outcome goes here.", "Month Year",
)

SHIELD_OUTER = "M50 5 H95 V52 C95 85 74 105 50 116 C26 105 5 85 5 52 V5 H50"
SHIELD_INNER = "M50 14 H86 V52 C86 78 70 95 50 105 C30 95 14 78 14 52 V14 H50"
SHIELD_FANGS = ["14,14 38,14 26,74", "38,14 62,14 50,74", "62,14 86,14 74,74"]
FANGS = "".join(f'<polygon points="{p}" />' for p in SHIELD_FANGS)


# ---------- Certificate border ----------

def border_svg():
    corner, edge = 60, 104
    size = corner * 2 + edge
    mid, amp = 30.5, 20.5

    def wave(fn, scale):
        pts = [f"{x},{mid + amp * scale * fn(2 * math.pi * x / edge):.1f}" for x in range(0, edge + 1, 2)]
        return f'<path d="M{" ".join(pts)}"/>'

    steps = 3
    waves = [wave(math.sin, i / steps) for i in range(-steps, steps + 1)]
    waves += [wave(math.cos, i / steps) for i in range(-steps, steps + 1) if i]

    def ring(radius, depth, lobes, count, n=240):
        out = []
        for j in range(count):
            phase = 2 * math.pi * j / count
            pts = []
            for i in range(n):
                t = 2 * math.pi * i / n
                r = radius + depth * math.sin(lobes * t + phase)
                pts.append(f"{31 + r * math.cos(t):.1f},{31 + r * math.sin(t):.1f}")
            out.append(f'<path d="M{" ".join(pts)}Z"/>')
        return out

    rosette = ring(16.5, 7.5, 6, 5) + ring(5, 2.5, 4, 2)
    edge_g = (
        f'<g id="e"><g stroke-width="1">{"".join(waves)}</g>'
        f'<path d="M0 1.7H{edge}" stroke-width="3.4"/><path d="M0 58.85H{edge}" stroke-width="2.3"/></g>'
    )
    corner_g = (
        f'<g id="c"><g stroke-width="1">{"".join(rosette)}</g>'
        f'<path d="M0 1.7H60M1.7 0V60" stroke-width="3.4"/><path d="M0 58.85H60M58.85 0V60" stroke-width="2.3"/></g>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
        f'fill="none" stroke="{INK}"><defs>{edge_g}{corner_g}</defs>'
        f'<use href="#c"/>'
        f'<use href="#c" transform="translate({size} 0) scale(-1 1)"/>'
        f'<use href="#c" transform="translate(0 {size}) scale(1 -1)"/>'
        f'<use href="#c" transform="translate({size} {size}) scale(-1 -1)"/>'
        f'<use href="#e" transform="translate({corner} 0)"/>'
        f'<use href="#e" transform="translate({corner} {size}) scale(1 -1)"/>'
        f'<use href="#e" transform="matrix(0 1 1 0 0 {corner})"/>'
        f'<use href="#e" transform="matrix(0 1 -1 0 {size} {corner})"/>'
        f'</svg>\n'
    )


# ---------- Pages ----------

def head(title, description, path=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <meta name="theme-color" content="{PAPER}" />
  <link rel="canonical" href="{SITE}/{path}" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Jaguar Investments" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:url" content="{SITE}/{path}" />
  <meta property="og:image" content="{SITE}/images/og.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="The Jaguar Investments shield" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" href="favicon.ico" sizes="48x48" />
  <link rel="icon" href="images/favicon-96.png" type="image/png" sizes="96x96" />
  <link rel="icon" href="images/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="images/apple-touch-icon.png" />
  <script>try{{if(!sessionStorage.getItem("jaguar-seen")){{document.documentElement.classList.add("intro");sessionStorage.setItem("jaguar-seen","1")}}}}catch(e){{}}</script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Display&amp;family=Libre+Caslon+Text:ital@0;1&amp;family=EB+Garamond:ital@1&amp;family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,500;1,8..60,400&amp;family=Inter:wght@400;500;600&amp;display=swap" />
  <link rel="stylesheet" href="base.css?v=10" />
  <link rel="stylesheet" href="themes/merchant.css?v=10" />
</head>
<body>

  <div class="watermark" aria-hidden="true"></div>

  <svg class="defs" aria-hidden="true" focusable="false">
    <filter id="ink">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" result="noise" />
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="1.6" xChannelSelector="R" yChannelSelector="G" />
    </filter>
    <filter id="ink-fine">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" result="noise" />
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="0.8" xChannelSelector="R" yChannelSelector="G" />
    </filter>
    <symbol id="shield" viewBox="0 0 100 120">
      <path d="{SHIELD_OUTER}" fill="none" stroke="currentColor" stroke-width="6" />
      <path d="{SHIELD_INNER}" fill="none" stroke="currentColor" stroke-width="1.5" />
      <g fill="currentColor">{FANGS}</g>
    </symbol>
  </svg>
"""


def header(current):
    links = []
    for i, (slug, label, _, _, _) in enumerate(PAGES):
        attrs = f'href="{slug}.html" data-n="{ROMAN[i]}"'
        if slug == "contact":
            attrs += ' class="nav-cta"'
        if slug == current:
            attrs += ' aria-current="page"'
        links.append(f"      <a {attrs}><span>{label}</span></a>")
    return f"""
  <header class="site-header">
    <a class="logo" href="index.html" aria-label="Jaguar Investments">
      <svg class="shield shield--nav"><use href="#shield" /></svg>
      <span class="logo-word"><span class="brand-j">J</span>aguar</span>
    </a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">Contents</button>
    <nav class="site-nav" id="site-nav" aria-label="Contents">
{chr(10).join(links)}
    </nav>
  </header>
"""


FOOTER = f"""
  <footer class="site-footer">
    <a class="footer-mark" href="index.html">
      <svg class="shield shield--nav" aria-hidden="true"><use href="#shield" /></svg>
      <span class="footer-wordmark">Jaguar Investments Group</span>
    </a>
    <a class="footer-email" href="mailto:{EMAIL}">{EMAIL}</a>
    <p class="footer-legal">&copy; 2026 Jaguar Investments Group</p>
  </footer>

  <script src="site.js?v=2"></script>
</body>
</html>
"""


def cover():
    return f"""
  <main>
    <section class="leaf leaf--cover">
      <svg class="shield shield--hero shield--draw" viewBox="0 0 100 120" aria-hidden="true">
        <path pathLength="1" d="{SHIELD_OUTER}" fill="none" stroke="currentColor" stroke-width="6" />
        <path pathLength="1" d="{SHIELD_INNER}" fill="none" stroke="currentColor" stroke-width="1.5" />
        <g class="fangs" fill="currentColor">{FANGS}</g>
      </svg>
      <h1 class="brand"><span class="brand-j">J</span>aguar</h1>
      <p class="hero-line">Investment and advisory across real estate and private capital.</p>
      <a href="contact.html" class="button">Contact Us</a>
    </section>
  </main>
"""


def leaf_nav(i):
    parts = []
    if i > 0:
        parts.append(f'<a class="prev" href="{PAGES[i - 1][0]}.html">&larr; {PAGES[i - 1][1]}</a>')
    if i < len(PAGES) - 1:
        parts.append(f'<a class="next" href="{PAGES[i + 1][0]}.html">{PAGES[i + 1][1]} &rarr;</a>')
    return f'<nav class="leaf-nav" aria-label="Previous and next">{"".join(parts)}</nav>'


def notice_card(kind, amount, name, place, role, date):
    return f"""        <article class="notice">
          <p class="notice-type">{kind}</p>
          <p class="notice-amount">{amount}</p>
          <p class="notice-name">{name}<br />{place}</p>
          <p class="notice-role">Jaguar Investments<br />{role}</p>
          <p class="notice-date">{date}</p>
        </article>"""


def study_card(kind, name, place, summary, date):
    return f"""        <article class="study">
          <p class="notice-type">{kind}</p>
          <p class="study-name">{name}</p>
          <p class="study-place">{place}</p>
          <p class="study-copy">{summary}</p>
          <p class="notice-date">{date}</p>
        </article>"""


def offering_sections():
    n = notice_card(*PLACEHOLDER_NOTICE)
    s = study_card(*PLACEHOLDER_STUDY)
    return f"""
      <div class="dossier">
        <section class="dossier-block" aria-labelledby="tx-heading">
          <h2 id="tx-heading" class="dossier-label">Transactions</h2>
          <p class="dossier-note">Appear as a matter of record only.</p>
          <div class="notices notices--compact">
{n}
          </div>
        </section>
        <section class="dossier-block" aria-labelledby="cs-heading">
          <h2 id="cs-heading" class="dossier-label">Case Studies</h2>
          <div class="studies">
{s}
          </div>
        </section>
      </div>"""


def about_body(copy):
    return f"""      <p class="page-copy">{copy}</p>
      <p class="page-copy page-copy--follow">
        The firm works with owners, operators, and capital partners on financing,
        investment, and advisory mandates. Engagements are selective and held in confidence.
      </p>
      <a href="contact.html" class="button">Contact Us</a>"""


def investors_body(copy):
    return f"""      <p class="page-copy">{copy}</p>
      <form class="investor-form" action="#" method="post" autocomplete="on">
        <label class="field">
          <span>Email</span>
          <input type="email" name="email" required autocomplete="username" />
        </label>
        <label class="field">
          <span>Password</span>
          <input type="password" name="password" required autocomplete="current-password" />
        </label>
        <button type="submit" class="button button--submit">Sign In</button>
        <p class="form-note">Investor access is by invitation. For credentials, write to <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
      </form>"""


def page(i):
    slug, _, title, copy, kind = PAGES[i]
    leaf_class = "leaf leaf--tall" if kind == "offering" else "leaf"

    if kind == "offering":
        body = f"""      <p class="page-copy">{copy}</p>
      <a href="contact.html" class="button">Contact Us</a>
{offering_sections()}"""
    elif kind == "about":
        body = about_body(copy)
    elif kind == "investors":
        body = investors_body(copy)
        leaf_class = "leaf"
    elif kind == "contact":
        body = f"""      <p class="page-copy">{copy}</p>
      <a href="mailto:{EMAIL}" class="button">{EMAIL}</a>"""
    else:
        body = f"""      <p class="page-copy">{copy}</p>"""

    return f"""
  <main>
    <section class="{leaf_class}">
      <p class="leaf-num">{ROMAN[i]}</p>
      <h1 class="brand brand--page">{title}</h1>
{body}
      {leaf_nav(i)}
    </section>
  </main>
"""


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(root, "images"), exist_ok=True)
    os.makedirs(os.path.join(root, "sketches"), exist_ok=True)

    def write(name, text):
        with open(os.path.join(root, name), "w") as f:
            f.write(text)

    write("images/border.svg", border_svg())
    write("index.html", head(
        "Jaguar Investments",
        "Jaguar Investments. Investment and advisory across real estate and private capital.",
    ) + header(None) + cover() + FOOTER)

    for i, (slug, _, title, copy, kind) in enumerate(PAGES):
        description = copy or title
        write(
            f"{slug}.html",
            head(f"{title} | Jaguar Investments", description, f"{slug}.html") + header(slug) + page(i) + FOOTER,
        )

    write("images/favicon.svg", favicon_svg())
    write("sketches/og-card.html", og_card_html())
    write("sketches/icon-card.html", icon_card_html())
    write("sketches/favicon-card.html", favicon_card_html())
    render_images(root)

    # Remove retired Transactions page if present
    old = os.path.join(root, "transactions.html")
    if os.path.exists(old):
        os.remove(old)

    # Italic type specimen (preview only; not linked from the site)
    write("sketches/type.html", TYPE_SPECIMEN)


# ---------- Share card and icons ----------

def shield_svg(width, height, extra="", fill="none"):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 120" width="{width}" height="{height}"{extra}>'
        f'<path d="{SHIELD_OUTER}" fill="{fill}" stroke="{INK}" stroke-width="6" />'
        f'<path d="{SHIELD_INNER}" fill="none" stroke="{INK}" stroke-width="1.5" />'
        f'<g fill="{INK}">{FANGS}</g></svg>'
    )


def favicon_svg():
    # Paper fill keeps the mark legible on dark browser tabs
    return shield_svg(100, 120, fill=PAPER) + "\n"


def og_card_html():
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8" />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital@1&amp;display=block" />
<style>
  html, body {{ margin: 0; width: 1200px; height: 630px; overflow: hidden; }}
  body {{ background: {PAPER}; color: {INK}; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
  .frame {{ position: absolute; inset: 28px; border: 2px solid {INK}; }}
  .frame::after {{ content: ""; position: absolute; inset: 8px; border: 1px solid {INK}; }}
  .word {{ margin-top: 18px; font: italic 400 112px/1.1 "EB Garamond", serif; letter-spacing: -0.02em; }}
  .word span {{ margin-right: -0.09em; }}
</style></head>
<body>
  <div class="frame"></div>
  {shield_svg(220, 264)}
  <div class="word"><span>J</span>aguar</div>
</body></html>
"""


def icon_card_html():
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8" />
<style>
  html, body {{ margin: 0; width: 180px; height: 180px; overflow: hidden; }}
  body {{ background: {PAPER}; display: flex; align-items: center; justify-content: center; }}
</style></head>
<body>{shield_svg(104, 125)}</body></html>
"""


def favicon_card_html():
    # Tab icons are tiny, so the shield fills the square on a transparent ground
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8" />
<style>
  html, body {{ margin: 0; width: 192px; height: 192px; overflow: hidden; background: transparent; }}
  body {{ display: flex; align-items: center; justify-content: center; }}
</style></head>
<body>{shield_svg(158, 190, fill=PAPER)}</body></html>
"""


def render_images(root):
    """Rasterise the share card and touch icon with headless Chrome, if installed."""
    chrome = next((c for c in (
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome") or "",
        shutil.which("chromium") or "",
    ) if c and os.path.exists(c)), None)
    if not chrome:
        print("Chrome not found; skipped images/og.png and images/apple-touch-icon.png")
        return
    for src, out, size, extra in (
        ("sketches/og-card.html", "images/og.png", "1200,630", []),
        ("sketches/icon-card.html", "images/apple-touch-icon.png", "180,180", []),
        ("sketches/favicon-card.html", "images/favicon-192.png", "192,192",
         ["--default-background-color=00000000"]),
    ):
        subprocess.run([
            chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            f"--window-size={size}", "--virtual-time-budget=5000", *extra,
            f"--screenshot={os.path.join(root, out)}",
            "file://" + os.path.join(root, src),
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Downscale for tabs; sips ships with macOS
    big = os.path.join(root, "images/favicon-192.png")
    if shutil.which("sips"):
        for px, out in ((96, "images/favicon-96.png"), (48, "favicon.ico")):
            fmt = ["-s", "format", "ico"] if out.endswith(".ico") else []
            subprocess.run(["sips", "-z", str(px), str(px), *fmt, big, "--out", os.path.join(root, out)],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(big)


TYPE_SPECIMEN = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Type specimen — Jaguar</title>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Display&amp;family=Libre+Caslon+Text:ital@0;1&amp;family=Source+Serif+4:ital,opsz,wght@0,8..60,400;1,8..60,400&amp;display=swap" />
  <style>
    body { margin: 0; padding: 3rem 4rem; background: #ece7dc; color: #12100d; }
    h1 { font: 400 0.7rem/1 Inter, sans-serif; letter-spacing: 0.2em; text-transform: uppercase; margin: 0 0 2.5rem; }
    .row { display: grid; grid-template-columns: 10rem 1fr; gap: 1rem 2rem; align-items: baseline; padding: 1.5rem 0; border-top: 1.5px solid #12100d; }
    .label { font: 500 0.65rem/1.4 Inter, sans-serif; letter-spacing: 0.14em; text-transform: uppercase; color: #6b6359; }
    .display { font-family: "Libre Caslon Display", serif; font-size: 4.5rem; line-height: 1; }
    .text { font-family: "Libre Caslon Text", serif; font-size: 2.4rem; line-height: 1.15; }
    .text.italic { font-style: italic; }
    .body { font-family: "Source Serif 4", serif; font-size: 1.35rem; line-height: 1.5; }
    .body.italic { font-style: italic; }
    .note { margin-top: 2rem; font: italic 1rem/1.5 "Source Serif 4", serif; color: #3a352e; max-width: 36rem; }
  </style>
</head>
<body>
  <h1>Type specimen</h1>
  <div class="row"><span class="label">Caslon Display</span><p class="display">Jaguar</p></div>
  <div class="row"><span class="label">Caslon Text</span><p class="text">Jaguar Investments</p></div>
  <div class="row"><span class="label">Caslon Text italic</span><p class="text italic">Jaguar Investments</p></div>
  <div class="row"><span class="label">Source Serif</span><p class="body">Investment and advisory across real estate and private capital.</p></div>
  <div class="row"><span class="label">Source Serif italic</span><p class="body italic">Investment and advisory across real estate and private capital.</p></div>
  <p class="note">Libre Caslon Display has no italic cut on Google Fonts. The homepage line under Jaguar now uses Caslon Text italic. Source Serif remains for longer body copy.</p>
</body>
</html>
"""


if __name__ == "__main__":
    main()
