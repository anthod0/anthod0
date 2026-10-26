# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools==4.55.3", "uharfbuzz==0.51.1"]
# ///
# Render assets/hero.svg (light) and assets/hero-dark.svg (dark). All text is converted to paths,
# so the SVGs need no embedded or installed fonts.
from pathlib import Path

from fontcache import font
from textpath import Face

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
# Content spans the full width so it aligns with the README column and the badges.
W, H, M = 1200, 376, 0

PALETTES = {
    "hero.svg": {"ink": "#0e0e0e", "paper": "#ffffff", "muted": "#6b6862", "accent": "#ff4f00"},
    "hero-dark.svg": {"ink": "#f1efea", "paper": "#0d1117", "muted": "#9a968f", "accent": "#ff4f00"},
}

display = Face(font("InterTight-VF.ttf"), wght=700)
text = Face(font("InterTight-VF.ttf"), wght=500)
mono = Face(font("IBMPlexMono-Regular.ttf"))

# (face, string, x, baseline, size, tracking, anchor, color role)
TEXT = [
    (mono, "ANTHOD", M, 56, 12, 1.2, "start", "ink"),
    (mono, "RUST · TYPESCRIPT", W / 2, 56, 12, 1.2, "middle", "muted"),
    (mono, "PRODUCT ENGINEER @ REELA", W - M, 56, 12, 1.2, "end", "ink"),
    (display, "anthod", M - 4, 300, 210, -9, "start", "ink"),
    (text, "The model is the easy part.", W - M, 262, 30, -0.6, "end", "muted"),
    (text, "I build the harness.", W - M, 300, 30, -0.6, "end", "ink"),
]
# Path data is identical across themes; only fills change.
PATHS = [(face.path(s, x, y, size, track, anchor)[0], role) for face, s, x, y, size, track, anchor, role in TEXT]


def render(ink, paper, muted, accent):
    colors = {"ink": ink, "muted": muted}
    paths = "\n".join(f'  <path fill="{colors[role]}" d="{d}"/>' for d, role in PATHS)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
  <title id="t">anthod</title>
  <desc id="d">Product engineer at Reela. The model is the easy part. I build the harness.</desc>
  <style>
    line {{ shape-rendering: crispEdges; }}

    .cursor {{ animation: blink 1.1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}

    @media (prefers-reduced-motion: reduce) {{
      .cursor {{ animation: none; }}
    }}
  </style>

  <rect width="{W}" height="{H}" fill="{paper}"/>
{paths}
  <line x1="{M}" y1="76" x2="{W - M}" y2="76" stroke="{ink}"/>
  <rect class="cursor" x="{M + 636}" y="264" width="36" height="36" fill="{accent}"/>
  <line x1="{M}" y1="{H - 48}" x2="{W - M}" y2="{H - 48}" stroke="{ink}"/>
</svg>
'''


for name, palette in PALETTES.items():
    svg = render(**palette)
    (OUT / name).write_text(svg)
    print(name, len(svg))
