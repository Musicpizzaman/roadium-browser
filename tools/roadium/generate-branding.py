#!/usr/bin/env python3
"""Generate Roadium vector artwork from the supplied brand references."""
from __future__ import annotations
import json
from pathlib import Path
from xml.sax.saxutils import escape
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "branding"
PALETTE = {
    "navy": "#193E74", "teal": "#3C9FA0",
    "orange": "#F4A04A", "warm_white": "#F4F1E8",
}
REAR = "M27,18 H85 Q95,18 95,28 V33 H41 Q28,33 28,46 V99 H26 Q16,99 16,89 V29 Q16,18 27,18 Z"
FRONT = "M41,35 H94 Q109,35 109,50 V65 Q109,85 90,87 H86 Q82,87 84,91 L107,114 Q111,120 104,120 H41 Q30,120 30,109 V46 Q30,35 41,35 Z"
INNER = "M44,52 H76 Q83,52 88,58 Q90,60 96,60 H99 Q104,60 104,65 Q104,81 87,81 H69 Q63,81 63,87 V109 Q63,114 58,114 H44 Q37,114 37,107 V61 Q37,52 44,52 Z"

def circle(x, y, r):
    return f"M{x-r},{y} A{r},{r} 0,1 0 {x+r},{y} A{r},{r} 0,1 0 {x-r},{y} Z"

def logo_paths():
    return [
        (PALETTE["teal"], REAR, None),
        (PALETTE["orange"], circle(27, 25, 3.4), None),
        (PALETTE["warm_white"], circle(37, 25, 3.4), None),
        ("#83BBB8", circle(47, 25, 3.4), None),
        (PALETTE["navy"], FRONT, PALETTE["warm_white"]),
        (PALETTE["warm_white"], INNER, None),
        (PALETTE["orange"], circle(40, 44, 3.4), None),
        (PALETTE["warm_white"], circle(50, 44, 3.4), None),
        (PALETTE["teal"], circle(60, 44, 3.4), None),
    ]

def svg_paths(paths):
    result = []
    for color, path, stroke in paths:
        edge = f' stroke="{stroke}" stroke-width="5" stroke-linejoin="round"' if stroke else ""
        result.append(f'<path fill="{color}" d="{path}"{edge}/>')
    return "\n".join(result)

def svg(width, height, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(label)}">\n'
            f"<title>{escape(label)}</title>\n{body}\n</svg>\n")

def vector(width, height, body, dp_width=None, dp_height=None):
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<!-- Roadium artwork derived from the owner-supplied references. -->\n'
            '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
            f'    android:width="{dp_width or width}dp" android:height="{dp_height or height}dp"\n'
            f'    android:viewportWidth="{width}" android:viewportHeight="{height}">\n'
            f"{body}\n</vector>\n")

def xml_paths(paths):
    result = []
    for color, path, stroke in paths:
        edge = f' android:strokeColor="{stroke}" android:strokeWidth="5" android:strokeLineJoin="round"' if stroke else ""
        result.append(f'    <path android:fillColor="{color}" android:pathData="{path}"{edge} />')
    return "\n".join(result)

def font_paths(filename, weight, text, size, x, baseline, tracking=0):
    font = instantiateVariableFont(TTFont(OUT / "fonts" / filename), {"wght": weight}, inplace=False)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    paths = []
    cursor = x
    for char in text:
        name = cmap[ord(char)]
        glyph = glyph_set[name]
        pen = SVGPathPen(glyph_set, ntos=lambda n: f"{n:.3f}".rstrip("0").rstrip(".") if n else "0")
        glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, cursor, baseline)))
        paths.append(pen.getCommands())
        cursor += glyph.width * scale + tracking
    return paths, cursor - x - tracking

def save(name, text):
    (OUT / name).write_text(text, encoding="utf-8", newline="\n")

def main():
    (OUT / "android").mkdir(parents=True, exist_ok=True)
    paths = logo_paths()
    art = svg_paths(paths)
    save("roadium-symbol.svg", svg(128, 128, art, "Roadium browser-window R"))
    # Adaptive foreground stays inside the central 66dp safe circle.
    transform = 'translate(26.06 23.64) scale(.44)'
    fg = f'<g transform="{transform}">{art}</g>'
    save("roadium-adaptive-foreground.svg", svg(108, 108, fg, "Roadium adaptive foreground"))
    save("roadium-app-icon.svg", svg(512, 512,
        f'<rect width="512" height="512" fill="{PALETTE["warm_white"]}"/>\n'
        f'<g transform="translate(7 -8) scale(4)">{art}</g>', "Roadium Browser app icon"))
    adaptive = ('  <group android:scaleX=".44" android:scaleY=".44"\n'
                '      android:translateX="26.06" android:translateY="23.64">\n'
                f"{xml_paths(paths)}\n  </group>")
    save("android/roadium_launcher_foreground.xml", vector(108, 108, adaptive))
    mono_path = FRONT + " " + INNER
    mono = ('  <group android:scaleX=".44" android:scaleY=".44"\n'
            '      android:translateX="26.06" android:translateY="23.64">\n'
            f'    <path android:fillColor="#FFFFFF" android:pathData="{REAR}" />\n'
            f'    <path android:fillColor="#FFFFFF" android:fillType="evenOdd" android:pathData="{mono_path}" />\n'
            '  </group>')
    save("android/themed_app_icon.xml", vector(108, 108, mono))
    save("roadium-monochrome.svg", svg(108, 108,
        f'<g transform="{transform}"><path fill="white" d="{REAR}"/>'
        f'<path fill="white" fill-rule="evenodd" d="{mono_path}"/></g>', "Roadium monochrome R"))

    title, title_width = font_paths("LeagueSpartan-wght.ttf", 700, "ROADIUM", 106, 210, 108)
    subtitle_size = 35
    subtitle, subtitle_width = font_paths("Montserrat-wght.ttf", 500, "BROWSER", subtitle_size, 0, 163, 14)
    subtitle, _ = font_paths("Montserrat-wght.ttf", 500, "BROWSER", subtitle_size,
                            210 + (title_width - subtitle_width) / 2, 163, 14)
    width = round(210 + title_width + 30)
    header_paths = [(PALETTE["navy"], d, None) for d in title]
    sub_paths = [(PALETTE["teal"], d, None) for d in subtitle]
    wordmark_body = (f'<g transform="translate(3 -3) scale(1.35)">{art}</g>\n'
                     f"{svg_paths(header_paths + sub_paths)}")
    save("roadium-wordmark.svg", svg(width, 186, wordmark_body, "Roadium Browser"))
    # Keep the symbol navy in dark mode; only the letter paths change.
    wordmark_dark = (f'<g transform="translate(3 -3) scale(1.35)">{art}</g>\n'
                     f'{svg_paths([(PALETTE["warm_white"], d, None) for d in title] + sub_paths)}')
    save("roadium-wordmark-dark.svg", svg(width, 186, wordmark_dark, "Roadium Browser"))
    title_xml = [( "@color/roadium_wordmark_text", d, None) for d in title]
    wordmark_xml = ('  <group android:scaleX="1.35" android:scaleY="1.35" android:translateX="3" android:translateY="-3">\n'
                    f"{xml_paths(paths)}\n  </group>\n{xml_paths(title_xml + sub_paths)}")
    save("android/roadium_wordmark.xml", vector(width, 186, wordmark_xml, 280, 72))
    colors = (f'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
              f'    <color name="roadium_launcher_background">{PALETTE["warm_white"]}</color>\n'
              f'    <color name="roadium_wordmark_text">{PALETTE["navy"]}</color>\n</resources>\n')
    save("android/roadium_brand_colors.xml", colors)
    save("android/roadium_brand_colors_night.xml",
         '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
         f'    <color name="roadium_wordmark_text">{PALETTE["warm_white"]}</color>\n</resources>\n')
    save("palette.json", json.dumps({
        "brand": PALETTE,
        "light": {"surface": PALETTE["warm_white"], "primary": PALETTE["navy"],
                  "text": PALETTE["navy"], "accent": PALETTE["teal"], "highlight": PALETTE["orange"]},
        "dark": {"surface": "#0D1B2A", "surface_container": "#172A40",
                 "primary": "#76CECB", "text": PALETTE["warm_white"], "accent": PALETTE["teal"],
                 "highlight": PALETTE["orange"]},
        "website_default": "follow_system",
        "wordmark_fonts": {"title": "League Spartan Bold", "subtitle": "Montserrat Medium"},
        "font_sources": ["https://github.com/google/fonts/tree/main/ofl/leaguespartan",
                         "https://github.com/google/fonts/tree/main/ofl/montserrat"]
    }, indent=2) + "\n")
    print(f"Generated Roadium artwork in {OUT}")

if __name__ == "__main__":
    main()
