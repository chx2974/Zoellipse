"""Big close-up: `python scripts/proof_glyph.py [chars] [--weights 100,400,900] [--italic|--both]
[--size 260] [--out a-closeup.png] [--lines "aneo;leal nano aloe"]`
-> specimen/proofs/<out>. --lines gives several texts (';'-separated), each
rendered at every weight."""
import argparse
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from proofs import OUT, face_at, render_line  # noqa: E402


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
    rows = [render_line(face_at(w, it), t, a.size)
            for it in styles for w in ws for t in texts]
    w = max(r.width for r in rows)
    img = Image.new("L", (w, sum(r.height for r in rows)), 255)
    y = 0
    for r in rows:
        img.paste(r, (0, y))
        y += r.height
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / a.out)
    print("wrote", OUT / a.out)


if __name__ == "__main__":
    main()
