"""Assemble dist/<FILE>-v<major>.<minor:03d>/ (+ .zip): variable + static fonts, css, docs.

Generic: reads FAMILY / FILE / VERSION from the package under src/ (no per-project edits).
Run via `make release` (which builds and checks first).
"""
import importlib
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from fontTools.ttLib import TTFont  # noqa: E402
from fontTools.varLib.instancer import instantiateVariableFont  # noqa: E402

pkg = next(p.name for p in (ROOT / "src").iterdir() if (p / "params.py").exists())
params = importlib.import_module(f"{pkg}.params")
FAMILY, FILE, VERSION = params.FAMILY, params.FILE, params.VERSION

NAME = f"{FILE}-v{VERSION[0]}.{VERSION[1]:03d}"
DIST = ROOT / "dist" / NAME
DOCS = ["OFL.txt", "FONTLOG.txt", "AUTHORS.txt", "README.md"]


def set_name(font, nid, text):
    name = font["name"]
    name.removeNames(nameID=nid)
    name.setName(text, nid, 3, 1, 0x409)
    name.setName(text, nid, 1, 0, 0)


def make_static(vf_path, out_dir, italic):
    """Yield (filename, style) for each named instance of the variable font."""
    probe = TTFont(vf_path)
    names = probe["name"]
    insts = [(names.getDebugName(i.subfamilyNameID), i.coordinates["wght"])
             for i in probe["fvar"].instances]
    for sub, wght in insts:
        base = sub.replace("Italic", "").strip() or "Regular"
        style = f"{base} Italic" if italic and base != "Regular" else (
            "Italic" if italic else base)
        font = instantiateVariableFont(TTFont(vf_path), {"wght": wght})
        full = f"{FAMILY} {style}"
        ribbi = base in ("Regular", "Bold")
        if ribbi:
            set_name(font, 1, FAMILY)
            set_name(font, 2, style)
        else:
            set_name(font, 1, f"{FAMILY} {base}")
            set_name(font, 2, "Italic" if italic else "Regular")
        set_name(font, 4, full)
        set_name(font, 6, f"{FILE}-{style.replace(' ', '')}")
        set_name(font, 16, FAMILY)
        set_name(font, 17, style)
        font["name"].removeNames(nameID=25)
        os2, head = font["OS/2"], font["head"]
        os2.usWeightClass = int(wght)
        sel = os2.fsSelection & ~(1 | 32 | 64)
        mac = head.macStyle & ~3
        if italic:
            sel |= 1
            mac |= 2
        if base == "Bold":
            sel |= 32
            mac |= 1
        if base == "Regular" and not italic:
            sel |= 64
        os2.fsSelection, head.macStyle = sel, mac
        fname = f"{FILE}-{style.replace(' ', '')}.ttf"
        font.save(out_dir / fname)
        yield fname


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    zip_path = DIST.parent / f"{NAME}.zip"
    zip_path.unlink(missing_ok=True)
    var_dir, static_dir, css_dir = (DIST / "fonts" / "variable",
                                    DIST / "fonts" / "static", DIST / "css")
    for d in (var_dir, static_dir, css_dir):
        d.mkdir(parents=True)

    nvar = nstatic = 0
    for italic in (False, True):
        stem = f"{FILE}{'-Italic' if italic else ''}[wght]"
        for ext in (".ttf", ".woff2"):
            shutil.copy(ROOT / "fonts" / "variable" / (stem + ext), var_dir)
            nvar += 1
        nstatic += len(list(make_static(ROOT / "fonts" / "variable" / (stem + ".ttf"),
                                        static_dir, italic)))
    for css in (ROOT / "css").glob("*.css"):
        shutil.copy(css, css_dir)
    for doc in DOCS:
        shutil.copy(ROOT / doc, DIST / doc)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(DIST.rglob("*")):
            if f.is_file():
                z.write(f, Path(NAME) / f.relative_to(DIST))
    print(f"{NAME}: {nvar} variable files, {nstatic} static TTFs, "
          f"{len(list(css_dir.glob('*.css')))} css, {len(DOCS)} docs")
    print(f"  {DIST}\n  {zip_path} ({zip_path.stat().st_size / 1024:.0f} KiB)")


if __name__ == "__main__":
    main()
