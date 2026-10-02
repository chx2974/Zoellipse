"""Rename Public Sans to Zoellipse in font info and the designspace."""
from . import params as P

GS_PARAMS = ("Variable Font Origin", "licenseURL", "license", "description")


def style_of(ufo):
    """'Thin', 'Black Italic' ... from the Glyphs master name."""
    return ufo.info.styleName


def ps_name(style):
    return f"{P.FILE}-{style.replace(' ', '') or 'Regular'}"


def font_info(ufo):
    i = ufo.info
    style = style_of(ufo)
    i.familyName = P.FAMILY
    i.styleMapFamilyName = None
    i.openTypeNamePreferredFamilyName = None
    i.openTypeNamePreferredSubfamilyName = None
    i.postscriptFontName = ps_name(style)
    i.postscriptFullName = f"{P.FAMILY} {style}"
    i.openTypeNameUniqueID = None
    i.versionMajor, i.versionMinor = P.VERSION
    i.openTypeNameVersion = None
    i.copyright = P.COPYRIGHT
    i.trademark = None
    i.openTypeNameDesigner = P.DESIGNER
    i.openTypeNameDesignerURL = None
    i.openTypeNameManufacturer = None
    i.openTypeNameManufacturerURL = None
    i.openTypeNameDescription = P.DESCRIPTION
    i.openTypeNameLicense = P.LICENSE
    i.openTypeNameLicenseURL = P.LICENSE_URL
    i.openTypeOS2VendorID = P.VENDOR
    i.openTypeOS2Type = []                       # installable
    # line height 1.2 em (Google Fonts minimum; Public Sans: 1900/-450 = 1.175 em)
    i.openTypeHheaAscender = i.openTypeOS2TypoAscender = P.LINE_ASC
    i.openTypeHheaDescender = i.openTypeOS2TypoDescender = P.LINE_DESC
    i.openTypeHheaLineGap = i.openTypeOS2TypoLineGap = 0
    for k in [k for k in ufo.lib if any(k.endswith("." + n) for n in GS_PARAMS)]:
        del ufo.lib[k]


def designspace(ds):
    for inst in ds.instances:
        inst.familyName = P.FAMILY
        inst.postScriptFontName = ps_name(inst.styleName)
        inst.styleMapFamilyName = None
        inst.lib.pop("com.schriftgestaltung.customParameters", None)
        for attr in ("localisedFamilyName", "localisedStyleMapFamilyName"):
            setattr(inst, attr, {})
    for src in ds.sources:
        src.familyName = P.FAMILY
