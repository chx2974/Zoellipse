# Zoellipse

Zoellipse is a variable sans-serif, a Modified Version of
[Public Sans](https://github.com/uswds/public-sans) (by USWDS / GSA), which is
itself a Modified Version of Libre Franklin by Pablo Impallari and Rodrigo
Fuenzalida. Version 1.000.

Designer: Charlie Champanhet. License: SIL OFL 1.1.

## What changed compared to Public Sans

1. **Curves**: a slight superellipse feel. The handles of quarter curves are
   lengthened as if ovals became superellipses of exponent 2.4.
2. **x-height**: raised from 1034 to 1056 units (73% of cap height; Public
   Sans is 71.5%).
3. **Tabular figures by default**: every digit, the figure space (U+2007), the
   maths signs (+ − = < > ± × ÷ ≠ ≤ ≥ ≈) and the currency signs ($ € £ ¥ ¢ …)
   are 620/1000 em wide, period and comma 310/1000, at every weight, upright
   and italic; digits are never kerned. Public Sans' proportional digits,
   currency, period and comma are available with the `pnum` feature (`tnum`
   switches back). At heavy weights the widest glyphs are condensed to fit,
   keeping the weight of their vertical strokes. Punctuation that sits on the
   x-height (hyphen, dashes, guillemets, colon) follows the taller lowercase.
4. **Additions**: capital sharp s ẞ (U+1E9E), Ǔ (U+01D3) and the dotted circle
   ◌ (U+25CC), drawn to match;
   a name for stylistic set ss01 (single-storey g, plain l).
5. **Line height** 1.2 em (Public Sans: 1.175 em).
6. **Renamed** to Zoellipse; the variable fonts default to Regular (400).

Everything else (about 660 glyphs including Latin extended, kerning, OpenType
features, italic at 8 degrees) is Public Sans.

## Fonts

Weight axis `wght` 100-900. Named instances: Thin 100, ExtraLight 200, Light
300, Regular 400, Medium 500, SemiBold 600, Bold 700, ExtraBold 800, Black 900.
The default instance stored in the font file is Regular (400).

- `fonts/variable/Zoellipse[wght].ttf` / `.woff2`
- `fonts/variable/Zoellipse-Italic[wght].ttf` / `.woff2`

The two are linked by the STAT `ital` axis.

## Web usage

```css
@font-face {
  font-family: "Zoellipse";
  src: url("fonts/variable/Zoellipse%5Bwght%5D.woff2") format("woff2"),
       url("fonts/variable/Zoellipse%5Bwght%5D.ttf") format("truetype");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "Zoellipse";
  src: url("fonts/variable/Zoellipse-Italic%5Bwght%5D.woff2") format("woff2"),
       url("fonts/variable/Zoellipse-Italic%5Bwght%5D.ttf") format("truetype");
  font-weight: 100 900;
  font-style: italic;
  font-display: swap;
}
body { font-family: "Zoellipse", system-ui, sans-serif; }
```

Or link `css/zoellipse.css`. For proportional figures in running text use
`font-variant-numeric: proportional-nums`.

## Building

The fonts are generated from the unmodified Public Sans Glyphs sources in
`upstream/public-sans/` (pinned commit e40fcf5). Requirements: Python 3.10+
(`python3`) and `make`; the first `make` creates a local virtualenv in `.venv/`
from `requirements-dev.txt` (pinned versions).

```
make build     # write sources/ (UFOs + designspaces) and fonts/variable/
make check     # check_tabular, check_outlines, check_squircle
make qa        # Font Bakery reports in qa/
make release   # build + check + dist/ (variable + static fonts, zip)
make gfbuild   # rebuild from sources/ with gftools builder (Google Fonts)
make serve     # specimen at http://localhost:8002/specimen/
```

## License

Copyright 2026 The Zoellipse Project Authors (https://github.com/chx2974/Zoellipse)
Copyright 2015 The Public Sans Project Authors (https://github.com/uswds/public-sans)

Licensed under the SIL Open Font License 1.1 (see `OFL.txt`). No Reserved Font
Name. See `FONTLOG.txt`, `AUTHORS.txt` and `CONTRIBUTORS.txt`.
