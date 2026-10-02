"""Raise the lowercase x-height from Public Sans' 1034 to Zoellipse's XH.

Heights are remapped piecewise: 0..x-height scales up, x-height..cap/ascender
is compressed so ascenders keep their height, descenders do not move.
Contours lying wholly above the x-height (i/j dots) move up rigidly instead,
and accent components in lowercase composites follow their base anchor.
Punctuation placed on the x-height (hyphen, dashes, guillemets, colon top
dot ...) moves rigidly, contour by contour, by the mapping at its centre;
contours sitting on the baseline stay.
"""
import unicodedata

from . import params as P

SKIP_SUFFIXES = ("sups", "subs", "sinf", "numr", "dnom", "superior", "inferior")


def map_y(y):
    lo, hi, top = P.XH_UPSTREAM, P.XH, P.CAP
    if y <= 0:
        return y
    if y <= lo:
        return y * hi / lo
    if y <= top:
        return hi + (y - lo) * (top - hi) / (top - lo)
    return y


def is_lowercase(ufo, name):
    if any(s in name for s in SKIP_SUFFIXES):
        return False
    parts = name.split(".")[0].split("_")
    for part in parts:
        g = ufo[part] if part in ufo else None
        if g is None or not g.unicodes:
            return False
        if unicodedata.category(chr(g.unicodes[0])) != "Ll":
            return False
    return True


def transform(ufo):
    names = [g.name for g in ufo if is_lowercase(ufo, g.name)]
    deltas = {}                     # (glyph, anchor name) -> dy, for composites
    for name in names:
        g = ufo[name]
        for c in g.contours:
            if min(p.y for p in c.points) > P.XH_UPSTREAM + 40:     # dot: move rigidly
                dy = P.XH - P.XH_UPSTREAM
                for p in c.points:
                    p.y += dy
            else:
                for p in c.points:
                    p.y = round(map_y(p.y))
        for a in g.anchors:
            new = round(map_y(a.y))
            deltas[(name, a.name)] = new - a.y
            a.y = new
    for name in names:
        g = ufo[name]
        if not g.components:
            continue
        base = g.components[0].baseGlyph
        for comp in g.components[1:]:
            mark = ufo[comp.baseGlyph] if comp.baseGlyph in ufo else None
            attach = [a.name[1:] for a in (mark.anchors if mark else []) if a.name.startswith("_")]
            dy = next((deltas[(base, n)] for n in attach if (base, n) in deltas), None)
            if dy is None:
                continue
            t = comp.transformation
            comp.transformation = (t[0], t[1], t[2], t[3], t[4], t[5] + dy)
    for name in P.XH_PUNCT:
        if name in ufo:
            for c in ufo[name].contours:
                ys = [p.y for p in c.points]
                if min(ys) <= 20:
                    continue
                cy = (min(ys) + max(ys)) / 2
                dy = round(map_y(cy) - cy)
                for p in c.points:
                    p.y += dy
    ufo.info.xHeight = P.XH
    return names
