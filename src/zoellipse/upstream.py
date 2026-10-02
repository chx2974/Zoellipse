"""Load the Public Sans Glyphs sources as a designspace of in-memory UFOs."""
import logging

import glyphsLib
from glyphsLib import to_designspace

from . import params as P


def load(italic):
    """Designspace (sources hold ufoLib2 fonts) for the upright or italic family."""
    logging.getLogger("glyphsLib").setLevel(logging.ERROR)
    gs = glyphsLib.GSFont(str(P.GLYPHS_SOURCES[italic]))
    ds = to_designspace(gs, minimal=False)
    for src in ds.sources:
        clean(src.font)
    return ds


def clean(ufo):
    """Drop backup layers and kerning that points at undefined groups."""
    for name in [layer.name for layer in ufo.layers if layer is not ufo.layers.defaultLayer]:
        del ufo.layers[name]
    groups = set(ufo.groups)
    for pair in list(ufo.kerning):
        if any(side.startswith("public.kern") and side not in groups for side in pair):
            del ufo.kerning[pair]
