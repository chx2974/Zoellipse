"""Tabular figures: digits, figure space, maths signs and currency are
DIGIT_WIDTH wide, period and comma half of it, at several weights, upright and
italic, with and without `tnum`; no kerning touches them; `pnum` reaches the
proportional digits. Exit code 1 on failure."""
import sys
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from zoellipse import params as P  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TTFS = {"upright": ROOT / "fonts/variable/Zoellipse[wght].ttf",
        "italic": ROOT / "fonts/variable/Zoellipse-Italic[wght].ttf"}
WEIGHTS = [100, 250, 400, 700, 900]
FULL = "0123456789\u2007+\u2212=<>\u00b1\u00d7\u00f7\u2260\u2264\u2265\u2248$\u20ac\u00a3\u00a5\u00a2"
HALF = ".,"                     # measured between digits (punctuation pairs like ".." keep their kerning)
TEXT = FULL + "0.0,0" + "".join(a + b for a in "0123456789" for b in "0123456789.,$+")
errors = []


def advances(blob, wght, features=None):
    font = hb.Font(hb.Face(blob))
    font.set_variations({"wght": wght})
    buf = hb.Buffer()
    buf.add_str(TEXT)
    buf.guess_segment_properties()
    hb.shape(font, buf, features or {})
    return [(TEXT[i.cluster], p.x_advance) for i, p in zip(buf.glyph_infos, buf.glyph_positions)]


for style, path in TTFS.items():
    blob = path.read_bytes()
    for w in WEIGHTS:
        for feats in ({}, {"tnum": True}):
            adv = advances(blob, w, feats)
            full = {a for ch, a in adv if ch in FULL}
            half = {a for ch, a in adv if ch in HALF}
            ok = full == {P.DIGIT_WIDTH} and half == {P.DIGIT_WIDTH // 2}
            tag = "tnum" if feats else "dflt"
            print(f"{'OK  ' if ok else 'FAIL'} {style:8} {w:3} {tag}  full={sorted(full)}  half={sorted(half)}")
            if not ok:
                errors.append((style, w, tag, full, half))
        pnum = {a for ch, a in advances(blob, w, {"pnum": True}) if ch in "0123456789"}
        if len(pnum) < 3:
            errors.append((style, w, "pnum has no effect"))
    ttf = instantiateVariableFont(TTFont(path), {"wght": 400})
    cmap = ttf.getBestCmap()
    print(f"     {style:8} glyphs: {', '.join(cmap[ord(c)] for c in '0123456789')}")

if errors:
    print("check_tabular: FAIL", errors)
    sys.exit(1)
print("check_tabular: OK")
