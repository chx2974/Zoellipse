"""Tabular by default: digits, maths signs and currency are DIGIT_WIDTH wide,
period and comma half of it, in every master (P.TAB_FULL / P.TAB_HALF).

Public Sans' proportional digits, currency, period and comma are kept as
<name>.pnum (`pnum` switches to them, `tnum` back); its *.tf glyphs become
plain references to the new defaults, so `tnum` changes nothing. Digits are
taken out of kerning (tabular figures are never kerned).
"""
import copy
import math
import re

from fontTools.pens.transformPen import TransformPointPen
from ufoLib2.objects import Component, Glyph

from . import params as P

MIN_SB = {100: 60, 900: 80}      # smallest side bearing per master (Weight)


def _unslanted(p, slant, y0):
    return p.x - slant * (p.y - y0)


def _stem(ufo, slant):
    """Vertical stem of the capital I (unslanted width of its ink)."""
    xs = [_unslanted(p, slant, P.CAP / 2) for c in ufo["I"].contours for p in c.points]
    return max(xs) - min(xs)


def _embolden_x(contour, xs, ys, d):
    """Horizontal-only emboldening by d (FreeType-style vertex normals, x part):
    vertical edges move d/2 outward from the ink, horizontal edges stay put.
    Contours are PostScript-oriented, so the ink is left of the travel direction."""
    n = len(xs)
    out = []
    for i in range(n):
        normals = []
        for j, k in ((i - 1, i), (i, i + 1)):
            dx, dy = xs[k % n] - xs[j % n], ys[k % n] - ys[j % n]
            ln = (dx * dx + dy * dy) ** 0.5 or 1.0
            normals.append((dy / ln, -dx / ln))
        (ax, ay), (bx, by) = normals
        den = 1 + ax * bx + ay * by
        out.append(xs[i] + (d / 2) * (ax + bx) / den if den > 0.2 else xs[i])
    return out


def _fit(g, min_sb, slant, stem, width=P.DIGIT_WIDTH, bold=1.0):
    """Centre the ink in DIGIT_WIDTH. Too-wide digits are condensed and their
    vertical strokes thickened back by what condensing took (stem * (1 - f)),
    so heavy digits keep the letters' weight. All of it in unslanted space
    (italic side bearings are measured that way)."""
    y0 = P.CAP / 2
    un = [[_unslanted(p, slant, y0) for p in c.points] for c in g.contours]
    x0, x1 = min(map(min, un)), max(map(max, un))
    room = width - 2 * min_sb
    f = 1.0 if x1 - x0 <= room else (room - stem) / (x1 - x0 - stem)
    d = stem * (1 - f) * bold
    cx = (x0 + x1) / 2
    for c, xs in zip(g.contours, un):
        ys = [p.y for p in c.points]
        xs = _embolden_x(c, [width / 2 + (x - cx) * f for x in xs], ys, d)
        for p, x in zip(c.points, xs):
            p.x = round(x + slant * (p.y - y0))
    for a in g.anchors:
        a.x = round(width / 2 + (_unslanted(a, slant, y0) - cx) * f + slant * (a.y - y0))
    g.width = width
    return f


def transform(ufo, weight):
    min_sb = MIN_SB[weight]
    slant = math.tan(math.radians(-(ufo.info.italicAngle or 0)))
    stem = _stem(ufo, slant)
    factors = {}
    widths = {n: P.DIGIT_WIDTH for n in P.TAB_FULL} | {n: P.DIGIT_WIDTH // 2 for n in P.TAB_HALF}
    for name, width in widths.items():
        if name not in ufo:
            continue
        orig = ufo[name]
        tf = ufo[name + ".tf"] if name + ".tf" in ufo else None
        if tf is not None or name in P.DIGITS:      # keep the proportional design for `pnum`
            pnum = copy.deepcopy(orig)
            pnum.unicodes = []
            ufo.layers.defaultLayer.insertGlyph(pnum, name=name + ".pnum")
            _order(ufo, name + ".pnum")
        if name in P.DIGITS and tf is not None and tf.contours:   # Public Sans' own tabular design (e.g. one)
            orig.clearContours()
            for c in tf.contours:
                orig.appendContour(copy.deepcopy(c))
        if orig.components:                         # fit outlines, not references
            _decompose(ufo, orig)
        digit = name in P.DIGITS
        # symbols have thinner inner strokes (slashes, bars): tighter side room, less re-thickening
        factors[name] = round(_fit(orig, min_sb if digit else min_sb / 2, slant, stem, width,
                                   1.0 if digit else 0.6), 3)
        if tf is not None:
            tf.clear()
            tf.components.append(Component(name))
            tf.width = width
    if "figurespace" not in ufo:
        ufo.layers.defaultLayer.insertGlyph(Glyph(width=P.DIGIT_WIDTH, unicodes=[0x2007]), name="figurespace")
        _order(ufo, "figurespace")
    _ungroup(ufo)
    ufo.features.text = _features(ufo.features.text, [n for n in widths if n + ".pnum" in ufo])
    return factors


def _decompose(ufo, g):
    """Replace components by their (transformed) outlines, nested ones included."""
    comps = list(g.components)
    g.components.clear()
    for c in comps:
        ufo[c.baseGlyph].drawPoints(TransformPointPen(g.getPointPen(), c.transformation))
    if g.components:
        _decompose(ufo, g)


def _order(ufo, name):
    order = ufo.lib.get("public.glyphOrder")
    if order is not None and name not in order:
        order.append(name)


def _ungroup(ufo):
    """Proportional digits inherit Public Sans' kerning; tabular ones get none."""
    ren = {d: d + ".pnum" for d in P.DIGITS}
    for name, members in list(ufo.groups.items()):
        ufo.groups[name] = [ren.get(m, m) for m in members]
    for pair in list(ufo.kerning):
        new = tuple(ren.get(s, s) for s in pair)
        if new != pair:
            ufo.kerning[new] = ufo.kerning.pop(pair)


def _features(fea, names):
    alt = "|".join(re.escape(n) for n in names)
    fea = re.sub(rf"\bsub ({alt}) by \1\.tf;", r"sub \1.pnum by \1;", fea)      # tnum
    fea = re.sub(rf"\bsub ({alt})\.tf by \1;", r"sub \1 by \1.pnum;", fea)      # pnum
    return fea
