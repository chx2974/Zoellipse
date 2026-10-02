"""Give Public Sans' curves a slight superellipse feel.

Every cubic segment that turns 90 degrees between a horizontal and a vertical
tangent (a "quarter" of a round, bowl, shoulder ...) gets longer handles.
An ellipse quarter has handles of k(2) = 0.552 of the corner distance; a
superellipse of exponent n has k(n) = (2**(-1/n) - 0.5) / 0.375 (same 45-degree
point). Each handle grows by k(SUPER_N) - k(2), so Public Sans' own curve
tensions are kept and only pushed toward the corner.
Only off-curve points move, so masters stay compatible. Italic outlines are
unslanted first, adjusted, then slanted back.
"""
import math

from . import params as P

TOL = math.radians(2.5)          # how close to horizontal/vertical a tangent must be


def k_of(n):
    return (2 ** (-1 / n) - 0.5) / 0.375


DK = k_of(P.SUPER_N) - k_of(2.0)


def _axis(dx, dy):
    """'h' / 'v' if the vector is (nearly) horizontal / vertical, else None."""
    if dx == 0 and dy == 0:
        return None
    a = math.atan2(dy, dx) % math.pi
    if min(a, math.pi - a) < TOL:
        return "h"
    if abs(a - math.pi / 2) < TOL:
        return "v"
    return None


def _quarter(p0, p1, p2, p3):
    """Corner point if p0..p3 is a 90-degree h/v quarter curve, else None."""
    a0 = _axis(p1[0] - p0[0], p1[1] - p0[1])
    a1 = _axis(p3[0] - p2[0], p3[1] - p2[1])
    if a0 is None or a1 is None or a0 == a1:
        return None
    return (p3[0], p0[1]) if a0 == "h" else (p0[0], p3[1])


def _push(p_on, p_off, corner):
    span = math.dist(p_on, corner)
    if span < P.SUPER_MIN_SPAN:
        return None
    k = math.dist(p_on, p_off) / span
    if k < 0.2 or k > 0.9:                  # deliberately odd handles: leave alone
        return None
    k2 = min(k + DK, 0.92)
    return (p_on[0] + (corner[0] - p_on[0]) * k2, p_on[1] + (corner[1] - p_on[1]) * k2)


def transform(ufo):
    slant = math.tan(math.radians(-(ufo.info.italicAngle or 0)))
    un = lambda p: (p.x - slant * p.y, p.y)                 # noqa: E731
    count = 0
    for g in ufo:
        for c in g.contours:
            pts = c.points
            n = len(pts)
            for i, p in enumerate(pts):
                if p.type != "curve":
                    continue
                q0, q1, q2 = pts[(i - 3) % n], pts[(i - 2) % n], pts[(i - 1) % n]
                if q1.type is not None or q2.type is not None or q0.type is None:
                    continue
                P0, P1, P2, P3 = un(q0), un(q1), un(q2), un(p)
                corner = _quarter(P0, P1, P2, P3)
                if corner is None:
                    continue
                n1, n2 = _push(P0, P1, corner), _push(P3, P2, corner)
                for q, new in ((q1, n1), (q2, n2)):
                    if new is not None:
                        q.x, q.y = round(new[0] + slant * new[1]), round(new[1])
                count += 1
    return count
