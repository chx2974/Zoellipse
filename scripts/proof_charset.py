"""Full character set as a grid: python scripts/proof_charset.py [--out cs-final.png]
[--weight 400] [--size 78] [--cols 24]. Upright rows, then italic rows.
The character set is the font's own cmap (spaces and controls skipped).
Combining marks are shown on an 'o'. Kerning off (each glyph on its own)."""
import argparse
import sys
import unicodedata
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from proof_shaped import OUT, ROOT, render, stack  # noqa: E402

NAMES = ("Zoellipse[wght].ttf", "Zoellipse-Italic[wght].ttf")


def charset(path):
    return [c for c in sorted(TTFont(path)["cmap"].getBestCmap())
            if unicodedata.category(chr(c))[0] not in "ZC"]


def cell(c):
    ch = chr(c)
    return "o" + ch if unicodedata.category(ch) in ("Mn", "Me") else ch


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="cs-final.png")
    ap.add_argument("--weight", type=int, default=400)
    ap.add_argument("--size", type=int, default=78)
    ap.add_argument("--cols", type=int, default=24)
    a = ap.parse_args()
    rows = []
    for name in NAMES:
        f = ROOT / "fonts" / "variable" / name
        chars = charset(f)
        for i in range(0, len(chars), a.cols):
            text = "  ".join(cell(c) for c in chars[i:i + a.cols])
            rows.append(render(f, a.weight, text, a.size, kern=False))
        rows.append(Image.new("L", (10, 30), 255))
    OUT.mkdir(parents=True, exist_ok=True)
    stack(rows).save(OUT / a.out)
    print("wrote", OUT / a.out)


if __name__ == "__main__":
    main()
