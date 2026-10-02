"""Build Zoellipse: Public Sans sources -> transforms -> UFOs -> variable TTF/WOFF2.

Usage: python -m zoellipse.build [sources]   (via `make build` / `make sources`)
"""
import copy
import shutil
import subprocess
import sys

from fontTools.designspaceLib import SourceDescriptor
from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont
from fontmake.instantiator import Instantiator

from . import digits, fixes, meta, sharp_s, squircle, upstream, xheight
from . import params as P

SOURCES = P.ROOT / "build" / "sources"
OUT = P.ROOT / "fonts" / "variable"
REPO_SOURCES = P.ROOT / "sources"           # commit-ready copy (UFOs + designspaces)


def add_regular_master(ds, italic):
    """Interpolate the Regular (wght 400 = design 375) from the transformed
    Thin/Black and make it the default master, so the variable font's default
    is Regular. Being an exact interpolation, it changes no outlines."""
    axis = ds.axes[0]
    inst = next(i for i in ds.instances if i.styleName == ("Italic" if italic else "Regular"))
    reg = Instantiator.from_designspace(ds).generate_instance(inst)
    thin = ds.sources[0].font
    reg.features.text = thin.features.text
    reg.groups.update(copy.deepcopy(dict(thin.groups)))
    for k, v in thin.lib.items():
        reg.lib.setdefault(k, copy.deepcopy(v))
    reg.lib["public.glyphOrder"] = list(thin.lib["public.glyphOrder"])
    reg.info.styleName = inst.styleName
    reg.info.italicAngle = thin.info.italicAngle
    ds.sources.insert(1, SourceDescriptor(font=reg, location=dict(inst.location), styleName=inst.styleName))
    axis.default = P.DEFAULT_WGHT


def make_sources(italic):
    ds = upstream.load(italic)
    suffix = "-Italic" if italic else ""
    for src in ds.sources:
        ufo, weight = src.font, round(src.location["Weight"])
        lc = xheight.transform(ufo)
        nq = squircle.transform(ufo)
        fit = digits.transform(ufo, weight)
        fixes.add_composites(ufo)
        sharp_s.draw(ufo)
        fixes.add_dotted_circle(ufo)
        fixes.set_base_category(ufo, ["dottedCircle", "Germandbls", "Ucaron", "figurespace"]
                                + [n + ".pnum" for n in P.TAB_FULL + P.TAB_HALF])
        fixes.name_ss01(ufo)
        print(f"  {ufo.info.styleName}: x-height on {len(lc)} lowercase glyphs, "
              f"{nq} quarter curves squared, digit condense {min(fit.values())}-{max(fit.values())}")
    add_regular_master(ds, italic)
    for src in ds.sources:
        ufo = src.font
        meta.font_info(ufo)
        src.filename = f"{P.FILE}-{ufo.info.styleName.replace(' ', '')}.ufo"
        src.path = str(SOURCES / src.filename)
        ufo.save(src.path, overwrite=True)
    meta.designspace(ds)
    path = SOURCES / f"{P.FILE}{suffix}.designspace"
    ds.write(path)
    return path


def add_stat(font, italic):
    """STAT: wght (named weights, Regular elidable, linked to Bold) + ital."""
    names = ["Thin", "ExtraLight", "Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"]
    wvals = []
    for i, name in enumerate(names):
        d = {"value": 100 * (i + 1), "name": name}
        if name == "Regular":
            d.update(flags=2, linkedValue=700)
        wvals.append(d)
    ital = ({"value": 1, "name": "Italic"} if italic else
            {"value": 0, "name": "Roman", "flags": 2, "linkedValue": 1})
    buildStatTable(font, [{"tag": "wght", "name": "Weight", "values": wvals},
                          {"tag": "ital", "name": "Italic", "values": [ital]}],
                   elidedFallbackName="Regular")


def finish(ttf, italic):
    font = TTFont(ttf)
    fixes.unhinted_tables(font)
    add_stat(font, italic)
    name = font["name"]
    name.names = [n for n in name.names if n.platformID != 1]
    name.setName(P.FILE + ("Italic" if italic else ""), 25, 3, 1, 0x409)
    font.save(ttf)
    font.flavor = "woff2"
    font.save(ttf.with_suffix(".woff2"))
    print("wrote", ttf.name, "and", ttf.with_suffix(".woff2").name)


def build(ds_path, italic):
    ttf = OUT / f"{P.FILE}{'-Italic' if italic else ''}[wght].ttf"
    cmd = [sys.executable, "-m", "fontmake", "-m", str(ds_path), "-o", "variable",
           "--output-path", str(ttf), "--flatten-components", "--filter", "DecomposeTransformedComponentsFilter"]
    subprocess.run(cmd, check=True)
    finish(ttf, italic)


def export_sources():
    REPO_SOURCES.mkdir(exist_ok=True)
    for old in list(REPO_SOURCES.glob("*.ufo")) + list(REPO_SOURCES.glob("*.designspace")):
        shutil.rmtree(old) if old.is_dir() else old.unlink()
    for src in sorted(SOURCES.iterdir()):
        if src.suffix == ".ufo":
            shutil.copytree(src, REPO_SOURCES / src.name)
        elif src.suffix == ".designspace":
            shutil.copy2(src, REPO_SOURCES / src.name)
    print("exported sources to", REPO_SOURCES)


def main():
    shutil.rmtree(SOURCES, ignore_errors=True)
    SOURCES.mkdir(parents=True)
    paths = {it: make_sources(it) for it in (False, True)}
    if "sources" not in sys.argv[1:]:
        OUT.mkdir(parents=True, exist_ok=True)
        for it, path in paths.items():
            build(path, it)
    export_sources()


if __name__ == "__main__":
    main()
