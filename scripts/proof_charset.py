"""Full character set as a grid: python scripts/proof_charset.py [--out cs-final.png]
[--weight 400] [--size 78] [--cols 24]. Upright rows, then italic rows.
Combining marks are shown on an 'o'. Kerning off (each glyph on its own)."""
import argparse
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from check_charset import TARGET  # noqa: E402
from proof_shaped import OUT, ROOT, render, stack  # noqa: E402


def cell(c):
    if c in (0x20, 0xA0, 0x2007):
        return "·" if False else " "
    ch = chr(c)
    return "o" + ch if 0x300 <= c < 0x370 else ch


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="cs-final.png")
    ap.add_argument("--weight", type=int, default=400)
    ap.add_argument("--size", type=int, default=78)
    ap.add_argument("--cols", type=int, default=24)
    a = ap.parse_args()
    chars = [c for c in TARGET if c not in (0x20, 0xA0, 0x2007)]
    rows = []
    for name in ("Zoellipse[wght].ttf", "Zoellipse-Italic[wght].ttf"):
        f = ROOT / "fonts" / "variable" / name
        for i in range(0, len(chars), a.cols):
            text = "  ".join(cell(c) for c in chars[i:i + a.cols])
            rows.append(render(f, a.weight, text, a.size, kern=False))
        rows.append(Image.new("L", (10, 30), 255))
    OUT.mkdir(parents=True, exist_ok=True)
    stack(rows).save(OUT / a.out)
    print("wrote", OUT / a.out)


if __name__ == "__main__":
    main()
