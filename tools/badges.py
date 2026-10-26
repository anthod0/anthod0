# /// script
# requires-python = ">=3.12"
# dependencies = ["fonttools==4.55.3", "uharfbuzz==0.51.1"]
# ///
# Render README link badges as standalone SVGs: icon + uppercase tracked label, no background.
# Text is converted to paths so the font (Inter Tight, same family as the hero) renders identically everywhere.
#
# Badges are responsive. The README sets each <img> to a percentage width (printed below) and a fixed
# 28px height, so badges scale with the README column like the hero does. The SVG has no intrinsic
# size and fills that box; its media queries match the box width. Below the hero's breakpoint the
# label is hidden and only a larger icon is shown, so all badges stay on one row on phones.
import re
from pathlib import Path

from fontcache import font
from textpath import Face

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets/badges"
INK = {"light": "#1f2328", "dark": "#f0f6fc"}  # GitHub's default text color per theme
# The label tells the two repos apart on desktop, so they share the GitHub mark there.
# Icon-only (narrow) layouts need distinct icons instead.
BADGES = [  # (file, label, desktop icon, narrow icon)
    ("x", "anthod0", "x.svg", "x.svg"),
    ("reela", "Reela", "reela.svg", "reela.svg"),
    ("pontia", "Pontia", "pontia.svg", "pontia.svg"),
    ("skills", "skills", "mark-github-16.svg", "sparkle-fill-16.svg"),
    ("dotfiles", "dotfiles", "mark-github-16.svg", "terminal-16.svg"),
]
H, PAD, SIZE, TRACK = 28, 10, 12, 1.8  # badge height, side padding, font size, letter spacing
ICON, GAP = 14, 8  # icon box size and space between icon and label
ICON_ONLY = 18  # icon size in the narrow (icon-only) layout
# The X mark fills its whole box edge to edge, so it reads larger than the other icons at the same size.
OPTICAL = {"x.svg": 0.85}
COLUMN = 846  # README column width (px) on desktop GitHub; badges show at natural size there
NARROW = 560  # column width below which only icons are shown; same breakpoint as hero.py

face = Face(font("InterTight-VF.ttf"), wght=600)
baseline = (H + face.cap_height(SIZE)) / 2


def icon(file):
    """Return (path attributes, viewBox size) of a single-path square icon."""
    src = (ROOT / "icons" / file).read_text()
    size = float(re.search(r'viewBox="0 0 ([\d.]+) [\d.]+"', src).group(1))
    d = re.search(r' d="([^"]+)"', src).group(1)
    rule = ' fill-rule="evenodd"' if 'fill-rule="evenodd"' in src else ""
    return f'd="{d}"{rule}', size


def place(attrs, size, x, y, box):
    """Icon path scaled into a box x box square at x/y."""
    return f'<path transform="translate({x:g} {y:g}) scale({box / size:g})" {attrs}/>'


OUT.mkdir(parents=True, exist_ok=True)
for name, label, wide_icon, narrow_icon in BADGES:
    x = PAD + ICON + GAP
    # textpath adds tracking after every glyph (CSS behaviour); drop the trailing one from the width.
    text_d, text_w = face.path(label.upper(), x, baseline, SIZE, TRACK)
    w = round(x + text_w - TRACK + PAD)
    wide = place(*icon(wide_icon), PAD, (H - ICON) / 2, ICON) + f'<path d="{text_d}"/>'
    box = ICON_ONLY * OPTICAL.get(narrow_icon, 1)
    narrow = place(*icon(narrow_icon), (H - box) / 2, (H - box) / 2, box)
    for theme, ink in INK.items():
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">'
            f"<title>{label}</title>"
            f"<style>.n{{display:none}}@media (max-width:{w * NARROW / COLUMN - 0.02:.2f}px)"
            f"{{.w{{display:none}}.n{{display:inline}}}}</style>"
            f'<g fill="{ink}">'
            f'<svg class="w" width="100%" height="100%" viewBox="0 0 {w} {H}">{wide}</svg>'
            f'<svg class="n" width="100%" height="100%" viewBox="0 0 {H} {H}">{narrow}</svg>'
            f"</g></svg>\n"
        )
        (OUT / f"{name}-{theme}.svg").write_text(svg)
    print(f"{name}: {w}px on desktop -> README width=\"{w / COLUMN * 100:.2f}%\"")
