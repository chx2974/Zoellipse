"""Outline QA for the generated masters and the variable font.

- every glyph has identical contour/point structure in all masters
- only cubic curves in the UFO sources, every contour closed
- contour direction: outer ccw (positive area), holes cw and inside an outer
- variable font: fvar instances, STAT, vertical metrics consistency
Exit code 1 on failure.
"""
import sys
from pathlib import Path

import ufoLib2
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "build" / "sources"
TTFS = {"upright": ROOT / "fonts" / "variable" / "Zoellipse[wght].ttf",
        "italic": ROOT / "fonts" / "variable" / "Zoellipse-Italic[wght].ttf"}
errors = []


def structure(glyph):
    return [tuple(p.type for p in c) for c in glyph.contours]


def contour_info(contour):
    ap, bp = AreaPen(), BoundsPen(None)
    contour.draw(ap)
    contour.draw(bp)
    return ap.value, bp.bounds


def inside(a, b):
    return a[0] >= b[0] and a[1] >= b[1] and a[2] <= b[2] and a[3] <= b[3]


def check_masters(italic):
    masters = [ufoLib2.Font.open(p) for p in sorted(SOURCES.glob("*.ufo"))
               if p.stem.endswith("Italic") == italic]
    assert len(masters) == 3, f"expected 3 masters, found {len(masters)}"
    names = masters[0].keys()
    for name in sorted(names):
        glyphs = [m[name] for m in masters]
        if len({str(structure(g)) for g in glyphs}) != 1:
            errors.append(f"{name}: incompatible structure across masters")
        for m, g in zip(masters, glyphs):
            tag = f"{name}@{m.info.styleName}"
            for c in g.contours:
                if c.open:
                    errors.append(f"{tag}: open contour")
                if any(p.type == "qcurve" for p in c):
                    errors.append(f"{tag}: quadratic curve in source")
            infos = [contour_info(c) for c in g.contours]
            outers = [b for a, b in infos if a > 0]
            for a, b in infos:
                if a < 0 and not any(inside(b, o) for o in outers):
                    errors.append(f"{tag}: clockwise contour not inside an outer")
            if infos and sum(a for a, _ in infos) <= 0:
                errors.append(f"{tag}: negative total area (wrong direction)")
    print(f"{'italic' if italic else 'upright'} masters: {len(masters)}, glyphs: {len(names)}")


def check_vf(style):
    italic = style == "italic"
    f = TTFont(TTFS[style])
    print(f"--- {style} VF")
    inst = [f["name"].getDebugName(i.subfamilyNameID) for i in f["fvar"].instances]
    print("fvar axis:", [(a.axisTag, a.minValue, a.defaultValue, a.maxValue)
                         for a in f["fvar"].axes])
    print("named instances:", ", ".join(inst))
    print("STAT present:", "STAT" in f)
    os2, hhea, head = f["OS/2"], f["hhea"], f["head"]
    print(f"hhea {hhea.ascent}/{hhea.descent}/{hhea.lineGap}  "
          f"typo {os2.sTypoAscender}/{os2.sTypoDescender}/{os2.sTypoLineGap}  "
          f"win {os2.usWinAscent}/{os2.usWinDescent}  "
          f"USE_TYPO_METRICS={bool(os2.fsSelection & 1 << 7)}")
    if (hhea.ascent, hhea.descent) != (os2.sTypoAscender, os2.sTypoDescender):
        errors.append("hhea and typo metrics differ")
    if hhea.ascent - hhea.descent + hhea.lineGap != (
            os2.usWinAscent + os2.usWinDescent):
        print("note: win line height differs from typo (win covers clipping)")
    if os2.usWinAscent < head.yMax or os2.usWinDescent < -head.yMin:
        errors.append("win metrics clip glyph bounds")
    axes = {a.AxisTag for a in f["STAT"].table.DesignAxisRecord.Axis}
    if axes != {"wght", "ital"}:
        errors.append(f"{style}: STAT axes {axes}")
    if bool(os2.fsSelection & 1) != italic or bool(f["head"].macStyle & 2) != italic:
        errors.append(f"{style}: fsSelection/macStyle italic bit wrong")
    if (f["post"].italicAngle != 0) != italic:
        errors.append(f"{style}: post.italicAngle wrong ({f['post'].italicAngle})")
    print(f"italicAngle {f['post'].italicAngle}  fsSelection {os2.fsSelection:#06x}  "
          f"macStyle {f['head'].macStyle}")
    if len(inst) != 9:
        errors.append(f"expected 9 named instances, got {len(inst)}")


def main():
    for italic in (False, True):
        check_masters(italic)
    for style in TTFS:
        check_vf(style)
    if errors:
        print("FAIL:\n  " + "\n  ".join(errors))
        sys.exit(1)
    print("OK: outlines compatible, closed, cubic, correctly oriented")


if __name__ == "__main__":
    main()
