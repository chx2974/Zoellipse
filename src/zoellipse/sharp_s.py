"""Capital sharp s (U+1E9E), missing from Public Sans, drawn per master.

Shape: B's stem with a flat top bar, a diagonal from the top right down to the
lower bowl, and a lower bowl with Zoellipse's superelliptic curves. Every number
is measured from the master's own I (stem) and B (width, spacing, stroke
thicknesses; the lower bowl is as tall as B's), so it follows Public Sans
across weights. Drawn unslanted, then slanted by the italic angle. Same point
structure in every master.
"""
import math

from fontTools.pens.areaPen import AreaPen
from ufoLib2.objects import Contour, Glyph, Point

from . import params as P
from .squircle import k_of

NAME, UNI = "Germandbls", 0x1E9E
K = k_of(P.SUPER_N)                 # handle length of a superelliptic quarter


def _xs(ufo, name, slant):
    """Unslanted x extent of a glyph's outline."""
    xs = [p.x - slant * (p.y - P.CAP / 2) for c in ufo[name].contours for p in c.points]
    return min(xs), max(xs)


def _b_counters(ufo):
    """(y min, y max) of B's two counters, lower first."""
    out = []
    for c in ufo["B"].contours:
        pen = AreaPen()
        c.draw(pen)
        if pen.value < 0:
            ys = [p.y for p in c.points]
            out.append((min(ys), max(ys)))
    return sorted(out)


def _contour(pts):
    return Contour(points=[Point(x, y, t) for x, y, t in pts])


def draw(ufo):
    slant = math.tan(math.radians(-(ufo.info.italicAngle or 0)))
    i0, i1 = _xs(ufo, "I", slant)
    b0, b1 = _xs(ufo, "B", slant)
    (lo0, lo1), (up0, up1) = _b_counters(ufo)
    S, C = i1 - i0, P.CAP
    H, Ht = lo0, C - up1                            # B's bottom / top stroke
    x0, x1, xr = b0, b0 + S, b1                     # stem left/right, bowl right
    dw = S * 1.0                                    # horizontal width of the diagonal
    yj = up0                                        # top of the lower bowl = B's middle bar top
    xt = xr - 0.04 * (xr - x0)                      # end of the top bar
    xi = xr - S * 0.97                              # inner right of the bowl
    cx = x1 + 0.4 * (xi - x1)                       # where the bowl curves start
    xm = max(cx - dw / 2, x1 + 0.3 * S)             # diagonal foot (left edge); keeps an opening by the stem
    ym = yj / 2
    lean = (xt - dw - xm) / (C - (yj - H))          # dx/dy of the diagonal's left edge
    stem = [(x0, 0, "line"), (x1, 0, "line"), (x1, C - Ht, "line"), (xt - dw, C - Ht, "line"),
            (xt - dw, C, "line"), (x0, C, "line")]
    diag = [(xm, yj - H, "line"), (xm + dw, yj - H, "line"), (xt, C, "line"), (xt - dw, C, "line")]
    bowl = [(x1 - 10, 0, "line"), (cx, 0, "line"),
            (cx + K * (xr - cx), 0, None), (xr, ym - K * ym, None), (xr, ym, "curve"),
            (xr, ym + K * ym, None), (cx + K * (xr - cx), yj, None), (cx, yj, "curve"),
            (xm + H * lean, yj, "line"), (xm, yj - H, "line"), (cx, yj - H, "line"),
            (cx + K * (xi - cx), yj - H, None), (xi, ym + K * (ym - H), None), (xi, ym, "curve"),
            (xi, ym - K * (ym - H), None), (cx + K * (xi - cx), H, None), (cx, H, "curve"),
            (x1 - 10, H, "line")]
    g = Glyph(width=ufo["B"].width, unicodes=[UNI])
    for pts in (stem, diag, bowl):
        g.contours.append(_contour([(round(x + slant * (y - C / 2)), round(y), t) for x, y, t in pts]))
    ufo.layers.defaultLayer.insertGlyph(g, name=NAME)
    order = ufo.lib.get("public.glyphOrder")
    if order is not None and NAME not in order:
        order.append(NAME)
    for name, members in ufo.groups.items():        # kern like B on both sides
        if "B" in members and NAME not in members:
            members.append(NAME)
    return NAME
