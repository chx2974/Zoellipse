"""Big close-up: `python scripts/proof_glyph.py [chars] [--weights 100,400,900] [--italic|--both]
[--size 260] [--out a-closeup.png] [--lines "aneo;leal nano aloe"]`
-> specimen/proofs/<out>. --lines gives several texts (';'-separated), each
rendered at every weight. Unhinted, kerning off (uses proof_shaped.render)."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from proof_shaped import OUT, ROOT, render, stack  # noqa: E402

FONTS = {False: ROOT / "fonts" / "variable" / "Zoellipse[wght].ttf",
         True: ROOT / "fonts" / "variable" / "Zoellipse-Italic[wght].ttf"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?", default="aneo")
    ap.add_argument("--weights", default="100,400,900")
    ap.add_argument("--size", type=int, default=260)
    ap.add_argument("--out", default="a-closeup.png")
    ap.add_argument("--lines", default=None)
    ap.add_argument("--italic", action="store_true", help="italic font only")
    ap.add_argument("--both", action="store_true", help="upright and italic rows")
    a = ap.parse_args()
    texts = a.lines.split(";") if a.lines else [a.text]
    ws = [int(x) for x in a.weights.split(",")]
    styles = (False, True) if a.both else (a.italic,)
    rows = [render(FONTS[it], w, t, a.size, kern=False)
            for it in styles for w in ws for t in texts]
    OUT.mkdir(parents=True, exist_ok=True)
    stack(rows).save(OUT / a.out)
    print("wrote", OUT / a.out)


if __name__ == "__main__":
    main()
