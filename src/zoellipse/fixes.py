"""Small additions on top of Public Sans for current Font Bakery / Google Fonts checks."""
from fontTools.ttLib import newTable
from fontTools.ttLib.tables import ttProgram
from ufoLib2.objects import Component, Glyph

SS01_NAME = "Single-storey g, plain l"

# (new glyph, unicode, base, mark): composites missing from Public Sans
COMPOSITES = [("Ucaron", 0x01D3, "U", "caroncomb")]          # capitals use the raised lowercase marks


def _anchor(glyph, name):
    return next((a for a in glyph.anchors if a.name == name), None)


def add_composites(ufo):
    added = []
    for name, uni, base, mark in COMPOSITES:
        if name in ufo or base not in ufo or mark not in ufo:
            continue
        b, m = ufo[base], ufo[mark]
        top, mtop = _anchor(b, "top"), _anchor(m, "_top")
        dx, dy = (top.x - mtop.x, top.y - mtop.y) if top and mtop else (0, 0)
        g = Glyph(width=b.width, unicodes=[uni])
        g.components.append(Component(base))
        g.components.append(Component(mark, transformation=(1, 0, 0, 1, dx, dy)))
        for a in b.anchors:
            if a.name != "top":
                g.appendAnchor({"name": a.name, "x": a.x, "y": a.y})
        ufo.layers.defaultLayer.insertGlyph(g, name=name)
        order = ufo.lib.get("public.glyphOrder")
        if order is not None and name not in order:
            order.append(name)
        added.append(name)
    return added


def add_dotted_circle(ufo):
    """U+25CC from 12 scaled copies of the period's dot on a circle centred
    on the x-height, with o's mark anchors so every mark attaches to it."""
    import math
    name, base = "dottedCircle", ufo["o"]
    if name in ufo:
        return None
    pts = [p for c in ufo["period"].contours for p in c.points]
    dcx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2
    dcy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    s = min(0.55, 0.11 * ufo.info.xHeight / (max(p.x for p in pts) - min(p.x for p in pts)))  # dots stay apart at Black
    cx, cy = base.width / 2, ufo.info.xHeight / 2
    r = 0.42 * ufo.info.xHeight
    g = Glyph(width=base.width, unicodes=[0x25CC])
    for k in range(12):
        a = math.radians(90 - 30 * k)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        g.components.append(Component("period", transformation=(s, 0, 0, s, round(x - s * dcx), round(y - s * dcy))))
    for a in base.anchors:
        g.appendAnchor({"name": a.name, "x": a.x, "y": a.y})
    ufo.layers.defaultLayer.insertGlyph(g, name=name)
    order = ufo.lib.get("public.glyphOrder")
    if order is not None and name not in order:
        order.append(name)
    return name


def set_base_category(ufo, names):
    """Register added glyphs as GDEF bases: Glyphs exports explicit categories
    (public.openTypeCategories) and ufo2ft only attaches marks to listed bases."""
    cats = ufo.lib.setdefault("public.openTypeCategories", {})
    for n in names:
        if n in ufo:
            cats.setdefault(n, "base")


def name_ss01(ufo):
    fea = ufo.features.text
    head = "feature ss01 {\n"
    if head in fea and "featureNames" not in fea:
        ufo.features.text = fea.replace(head, head + f'featureNames {{ name "{SS01_NAME}"; }};\n', 1)


def unhinted_tables(font):
    """gasp (smooth at all sizes), prep with smart dropout control, meta (Latn)."""
    gasp = newTable("gasp")
    gasp.version = 1
    gasp.gaspRange = {0xFFFF: 0x000F}
    font["gasp"] = gasp
    prep = newTable("prep")
    prep.program = ttProgram.Program()
    prep.program.fromBytecode(bytes([0xB8, 0x01, 0xFF, 0x85, 0xB0, 0x04, 0x8D]))
    font["prep"] = prep
    meta = newTable("meta")
    meta.data = {"dlng": "Latn", "slng": "Latn"}
    font["meta"] = meta
