# Shape text with HarfBuzz and emit SVG path data, so SVGs render identically without fonts.
import io
import re

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer


class Face:
    def __init__(self, path, wght=None):
        font = TTFont(path)
        if wght is not None:
            font = instancer.instantiateVariableFont(font, {"wght": wght})
        buf = io.BytesIO()
        font.save(buf)
        # Same binary for shaping (HarfBuzz) and outlines (fontTools), so glyph IDs line up.
        self.font = TTFont(io.BytesIO(buf.getvalue()))
        self.hb = hb.Font(hb.Face(buf.getvalue()))
        self.upm = self.font["head"].unitsPerEm
        self.glyphs = self.font.getGlyphSet()
        self.order = self.font.getGlyphOrder()

    def cap_height(self, size):
        return self.font["OS/2"].sCapHeight * size / self.upm

    def path(self, text, x, baseline, size, tracking=0.0, anchor="start"):
        """Return (path data, width). Tracking matches CSS letter-spacing (added after every character)."""
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf)  # default features: kern, liga, calt
        scale = size / self.upm
        width = sum(p.x_advance for p in buf.glyph_positions) * scale + tracking * len(buf.glyph_infos)
        x -= {"start": 0, "middle": width / 2, "end": width}[anchor]
        pen = SVGPathPen(self.glyphs)
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            gx, gy = x + pos.x_offset * scale, baseline - pos.y_offset * scale
            self.glyphs[self.order[info.codepoint]].draw(TransformPen(pen, (scale, 0, 0, -scale, gx, gy)))
            x += pos.x_advance * scale + tracking
        return round_path(pen.getCommands()), width


def round_path(d):
    # Trim float noise to keep files small.
    return re.sub(r"-?\d+\.\d+", lambda m: f"{float(m.group()):.2f}".rstrip("0").rstrip("."), d)
