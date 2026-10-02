"""Proof sheets WITH OpenType shaping (kerning), needs `uharfbuzz` (optional).

python scripts/proof_shaped.py --out sp-x.png [--weights 100,400,900] [--size 110]
    [--both|--italic] [--features pnum] [--fontdir DIR] [--lines "Text one;Text two"] [--nokern]
Renders every line at every weight (upright rows, then italic rows).
--fontdir points at a folder holding Zoellipse[wght].ttf / Zoellipse-Italic[wght].ttf
(default: fonts/variable), useful for before/after comparisons.
"""
import argparse
from pathlib import Path

import freetype
import uharfbuzz as hb
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "specimen" / "proofs"
LINES = ["Hamburgefontsiv", "The quick brown fox jumps over a lazy dog",
         "AVATAR WAVY Toyota LYNX", "Voilà: Tea, Yes."]


def shape(path, wght, text, kern=True, feats=()):
    blob = hb.Blob.from_file_path(str(path))
    font = hb.Font(hb.Face(blob))
    font.set_variations({"wght": wght})
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": kern, **{f: True for f in feats}})
    return buf.glyph_infos, buf.glyph_positions


def render(path, wght, text, size, kern=True, feats=()):
    face = freetype.Face(str(path))
    face.set_var_design_coords((wght,))
    face.set_char_size(size * 64)
    sc = size / face.units_per_EM
    infos, poss = shape(path, wght, text, kern, feats)
    asc, desc = int(size * 0.96) + 4, int(size * 0.26) + 4
    width = int(sum(p.x_advance for p in poss) * sc) + 60
    img = Image.new("L", (width, asc + desc), 255)
    x = 20.0
    for i, p in zip(infos, poss):
        face.load_glyph(i.codepoint, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
        g = face.glyph
        bm = g.bitmap
        if bm.width and bm.rows:
            gi = Image.frombytes("L", (bm.width, bm.rows), bytes(bm.buffer))
            img.paste(Image.new("L", gi.size, 0),
                      (int(x + p.x_offset * sc) + g.bitmap_left, asc - g.bitmap_top), gi)
        x += p.x_advance * sc
    return img


def sheet(fontdir, weights, lines, size, styles, kern=True, feats=()):
    rows = []
    for it in styles:
        f = Path(fontdir) / ("Zoellipse-Italic[wght].ttf" if it else "Zoellipse[wght].ttf")
        rows += [render(f, w, t, size, kern, feats) for w in weights for t in lines]
    return rows


def stack(rows):
    img = Image.new("L", (max(r.width for r in rows), sum(r.height for r in rows)), 255)
    y = 0
    for r in rows:
        img.paste(r, (0, y))
        y += r.height
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="sp-test.png")
    ap.add_argument("--weights", default="100,400,900")
    ap.add_argument("--size", type=int, default=110)
    ap.add_argument("--fontdir", default=str(ROOT / "fonts" / "variable"))
    ap.add_argument("--lines", default=None)
    ap.add_argument("--italic", action="store_true")
    ap.add_argument("--both", action="store_true")
    ap.add_argument("--features", default="", help="comma list, e.g. pnum,zero")
    ap.add_argument("--nokern", action="store_true")
    a = ap.parse_args()
    lines = a.lines.split(";") if a.lines else LINES
    styles = (False, True) if a.both else (a.italic,)
    ws = [int(x) for x in a.weights.split(",")]
    img = stack(sheet(a.fontdir, ws, lines, a.size, styles, not a.nokern,
                       [f for f in a.features.split(",") if f]))
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / a.out)
    print("wrote", OUT / a.out)


if __name__ == "__main__":
    main()
