# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools==4.55.3", "uharfbuzz==0.51.1"]
# ///
# Render README link badges as standalone SVGs: icon + uppercase tracked label, no background.
# Text is converted to paths so the font (Inter Tight, same family as the hero) renders identically everywhere.
import re
from pathlib import Path

from fontcache import font
from textpath import Face

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets/badges"
INK = {"light": "#1f2328", "dark": "#f0f6fc"}  # GitHub's default text color per theme
BADGES = [  # (file, label, icon file)
    ("x", "@anthod0", "x.svg"),
    ("reela", "Reela", "globe-16.svg"),
    ("pontia", "Pontia", "globe-16.svg"),
    ("skills", "skills", "mark-github-16.svg"),
    ("dotfiles", "dotfiles", "mark-github-16.svg"),
]
H, PAD, SIZE, TRACK = 28, 10, 12, 1.8  # badge height, side padding, font size, letter spacing
ICON, GAP = 14, 8  # icon box size and space between icon and label

face = Face(font("InterTight-VF.ttf"), wght=600)
baseline = (H + face.cap_height(SIZE)) / 2
icon_y = (H - ICON) / 2


def icon(file):
    """Return (path data, viewBox size) of a single-path square icon."""
    src = (ROOT / "icons" / file).read_text()
    size = float(re.search(r'viewBox="0 0 ([\d.]+) [\d.]+"', src).group(1))
    return re.search(r' d="([^"]+)"', src).group(1), size


OUT.mkdir(parents=True, exist_ok=True)
for theme, ink in INK.items():
    for name, label, icon_file in BADGES:
        icon_d, icon_size = icon(icon_file)
        x = PAD + ICON + GAP
        # textpath adds tracking after every glyph (CSS behaviour); drop the trailing one from the width.
        text_d, text_w = face.path(label.upper(), x, baseline, SIZE, TRACK)
        w = round(x + text_w - TRACK + PAD)
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="0 0 {w} {H}" role="img" aria-label="{label}">'
            f"<title>{label}</title>"
            f'<g fill="{ink}">'
            f'<path transform="translate({PAD} {icon_y:g}) scale({ICON / icon_size:g})" d="{icon_d}"/>'
            f'<path d="{text_d}"/>'
            f"</g></svg>\n"
        )
        (OUT / f"{name}-{theme}.svg").write_text(svg)
        print(f"{name}-{theme}.svg", w, len(svg))
