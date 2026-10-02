"""Zoellipse: every number that makes it differ from Public Sans.

Zoellipse is a Modified Version of Public Sans (OFL 1.1). The pipeline loads the
upstream Glyphs sources unchanged and applies the transforms below in code.
Units are Public Sans' (UPM 2000).
"""
from pathlib import Path

FAMILY = "Zoellipse"
FILE = "Zoellipse"                      # file-name / PostScript-name prefix
VERSION = (1, 0)
VENDOR = "NONE"

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "upstream" / "public-sans"
GLYPHS_SOURCES = {False: UPSTREAM / "PublicSans.glyphs",
                  True: UPSTREAM / "PublicSans-Italic.glyphs"}

UPM = 2000
DEFAULT_WGHT = 400                   # variable-font default (Public Sans' is Thin 100)
CAP = 1446                           # Public Sans cap height (= ascender), unchanged
XH_UPSTREAM = 1034                   # Public Sans x-height: 71.5% of cap
XH = 1056                            # Zoellipse: 73% of cap (Inter is 75%)
XH_PUNCT = ("hyphen", "softhyphen", "endash", "emdash", "guillemetleft", "guillemetright",
            "guilsinglleft", "guilsinglright", "colon", "semicolon", "periodcentered", "bullet")
LINE_ASC, LINE_DESC = 1925, -475     # hhea/typo: 2400 = 1.2 em (Public Sans 1900/-450)

# Superellipse feel: curves running from a horizontal to a vertical tangent get
# longer handles, as if an ellipse (n = 2) became a superellipse of exponent N.
SUPER_N = 2.4
SUPER_MIN_SPAN = 60                  # skip quarter curves smaller than this (joins, tiny details)

# Tabular figures: default digits all DIGIT_WIDTH wide at every weight,
# upright and italic. Public Sans' proportional digits become *.pnum.
DIGIT_WIDTH = 1240                   # 620 / 1000
DIGITS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
MATHS = ("plus", "minus", "equal", "less", "greater", "plusminus", "multiply", "divide",
         "notequal", "lessequal", "greaterequal", "approxequal")
CURRENCY = ("dollar", "euro", "sterling", "yen", "cent", "colonsign", "dong", "florin",
            "franc", "lira", "liraTurkish", "rupeeIndian")
TAB_FULL = DIGITS + MATHS + CURRENCY  # DIGIT_WIDTH wide
TAB_HALF = ("period", "comma")        # DIGIT_WIDTH / 2 wide

COPYRIGHT = ("Copyright 2026 The Zoellipse Project Authors (https://github.com/chx2974/Zoellipse); "
             "Copyright 2015 The Public Sans Project Authors (https://github.com/uswds/public-sans)")
DESIGNER = "Charlie Champanhet; Public Sans: USWDS; Libre Franklin: Pablo Impallari, Rodrigo Fuenzalida"
DESCRIPTION = ("Zoellipse is a Modified Version of Public Sans (itself based on Libre Franklin) "
               "with subtly superelliptic curves, a taller x-height and tabular figures by default.")
LICENSE = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
           "This license is available with a FAQ at: https://openfontlicense.org")
LICENSE_URL = "https://openfontlicense.org"
