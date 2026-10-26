# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools==4.55.3", "uharfbuzz==0.51.1"]
# ///
# Render assets/hero.svg (light) and assets/hero-dark.svg (dark). All text is converted to paths,
# so the SVGs need no embedded or installed fonts.
#
# The hero is shown at 100% of the README column. SVG media queries match the image's own width,
# so below NARROW px the SVG switches to a layout with larger, fewer elements that stay readable on phones.
from pathlib import Path

from fontcache import font
from textpath import Face

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
W, H = 1200, 376
NARROW = 560  # README column width (px) below which the narrow layout is used; same as badges.py

PALETTES = {
    "hero.svg": {"ink": "#0e0e0e", "paper": "#ffffff", "muted": "#6b6862", "accent": "#ff4f00"},
    "hero-dark.svg": {"ink": "#f1efea", "paper": "#0d1117", "muted": "#9a968f", "accent": "#ff4f00"},
}

display = Face(font("InterTight-VF.ttf"), wght=700)
text = Face(font("InterTight-VF.ttf"), wght=500)
mono = Face(font("IBMPlexMono-Regular.ttf"))

TAGLINE = ("The model is the easy part.", "I build the harness.")


def wide():
    """Desktop layout. Returns (text items, cursor rect)."""
    items = [  # (face, string, x, baseline, size, tracking, anchor, color role)
        (mono, "ANTHOD", 0, 56, 12, 1.2, "start", "ink"),
        (mono, "RUST · TYPESCRIPT", W / 2, 56, 12, 1.2, "middle", "muted"),
        (mono, "PRODUCT ENGINEER @ REELA", W, 56, 12, 1.2, "end", "ink"),
        (display, "anthod", -4, 300, 210, -9, "start", "ink"),
        (text, TAGLINE[0], W, 262, 30, -0.6, "end", "muted"),
        (text, TAGLINE[1], W, 300, 30, -0.6, "end", "ink"),
    ]
    return items, cursor(210)


def narrow():
    """Phone layout: about 3x larger meta and tagline text, a smaller name so the tagline fits beside it."""
    meta, tag = 40, 52
    items = [
        (mono, "RUST · TYPESCRIPT", 0, 58, meta, 1.5, "start", "muted"),
        (mono, "PRODUCT ENGINEER @ REELA", W, 58, meta, 1.5, "end", "ink"),
        (text, TAGLINE[0], W, 252, tag, -0.9, "end", "muted"),
        (text, TAGLINE[1], W, 300, tag, -0.9, "end", "ink"),
    ]
    left = mono.path(items[0][1], 0, 0, meta, 1.5)[1]
    right = mono.path(items[1][1], 0, 0, meta, 1.5)[1]
    assert left + right + 40 <= W, "narrow meta row overlaps"
    # Largest name size whose name + cursor still leaves a 48-unit gap before the wider tagline line.
    tag_w = max(text.path(s, 0, 0, tag, -0.9)[1] for s in TAGLINE)
    size = 210
    while name_end(size) + 48 > W - tag_w:
        size -= 1
    items.append((display, "anthod", -4 * size / 210, 300, size, -9 * size / 210, "start", "ink"))
    return items, cursor(size)


def name_end(size):
    """Right edge of the blinking cursor that follows the name at this size."""
    x, w = cursor(size)[0], cursor(size)[2]
    return x + w


def cursor(size):
    """(x, y, width, height) of the cursor block that sits just after the name, on its baseline."""
    k = size / 210
    end = -4 * k + display.path("anthod", 0, 0, size, -9 * k)[1]
    s = 36 * k
    return end + 5 * k, 300 - s, s, s


LAYOUTS = {"w": wide(), "n": narrow()}


def render(ink, paper, muted, accent):
    colors = {"ink": ink, "muted": muted}
    groups = []
    for cls, (items, (cx, cy, cw, ch)) in LAYOUTS.items():
        paths = "\n".join(
            f'    <path fill="{colors[role]}" d="{face.path(s, x, y, size, track, anchor)[0]}"/>'
            for face, s, x, y, size, track, anchor, role in items
        )
        groups.append(
            f'  <g class="{cls}">\n{paths}\n'
            f'    <rect class="cursor" x="{cx:.2f}" y="{cy:.2f}" width="{cw:.2f}" height="{ch:.2f}" fill="{accent}"/>\n'
            f"  </g>"
        )
    body = "\n".join(groups)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">anthod</title>
  <desc id="d">Product engineer at Reela. The model is the easy part. I build the harness.</desc>
  <style>
    line {{ shape-rendering: crispEdges; stroke-width: 1; }}
    .n {{ display: none; }}
    @media (max-width: {NARROW - 0.02}px) {{
      .w {{ display: none; }}
      .n {{ display: inline; }}
      line {{ stroke-width: 3.5; }}
    }}

    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}

    @media (prefers-reduced-motion: reduce) {{
      .cursor {{ animation: none; }}
    }}
  </style>

  <rect width="{W}" height="{H}" fill="{paper}"/>
{body}
  <line x1="0" y1="76" x2="{W}" y2="76" stroke="{ink}"/>
  <line x1="0" y1="{H - 48}" x2="{W}" y2="{H - 48}" stroke="{ink}"/>
</svg>
'''


for name, palette in PALETTES.items():
    svg = render(**palette)
    (OUT / name).write_text(svg)
    print(name, len(svg))
