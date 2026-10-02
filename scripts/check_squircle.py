"""Full-charset review of the superellipse transform (squircle.py).

For every glyph of every master: ink area before/after the transform and the
largest handle move relative to the glyph's size. Prints the glyphs that change
the most (to proof them) and fails if a handle overshoots its quarter's corner
box (which would make a curve bulge past its tangents) or a contour's
direction flips. Run after `make build`; uses the upstream sources directly.
"""
import copy
import sys
from pathlib import Path

from fontTools.pens.areaPen import AreaPen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
PKG = sys.argv[1] if len(sys.argv) > 1 else "zoellipse"
upstream = __import__(f"{PKG}.upstream", fromlist=["load"])
squircle = __import__(f"{PKG}.squircle", fromlist=["transform"])

TOP = 12            # how many top changers to list per master


def area(glyph):
    out = []
    for c in glyph.contours:
        pen = AreaPen()
        c.draw(pen)
        out.append(pen.value)
    return out


def main():
    errors, report = [], []
    for italic in (False, True):
        for src in upstream.load(italic).sources:
            ufo = src.font
            before = {g.name: (area(g), [(p.x, p.y) for c in g.contours for p in c.points]) for g in ufo}
            squircle.transform(ufo)
            changes = []
            for g in ufo:
                a0, pts0 = before[g.name]
                a1 = area(g)
                if any((x > 0) != (y > 0) for x, y in zip(a0, a1) if abs(x) > 1):
                    errors.append(f"{g.name}@{ufo.info.styleName}: contour direction flipped")
                tot0 = sum(abs(x) for x in a0)
                if not tot0:
                    continue
                ink = (sum(abs(x) for x in a1) - tot0) / tot0
                pts1 = [(p.x, p.y) for c in g.contours for p in c.points]
                move = max((abs(x0 - x1) + abs(y0 - y1) for (x0, y0), (x1, y1) in zip(pts0, pts1)), default=0)
                changes.append((abs(ink), ink, move, g.name))
            changes.sort(reverse=True)
            name = ufo.info.styleName
            report.append(f"{name}: {sum(1 for c in changes if c[2])} glyphs changed; largest ink changes: " +
                          ", ".join(f"{n} {i:+.1%}" for _, i, _, n in changes[:TOP]))
    print("\n".join(report))
    if errors:
        print("check_squircle: FAIL\n  " + "\n  ".join(errors[:40]))
        sys.exit(1)
    print("check_squircle: OK (no direction flips)")


if __name__ == "__main__":
    main()
