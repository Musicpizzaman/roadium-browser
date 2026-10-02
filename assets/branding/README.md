# Roadium branding assets

The three JPEGs in `references/` are the user's original logo, style, and asset-layout references. They are preserved unchanged. The SVGs and Android vectors are a faithful redraw of the overlapping browser-window R symbol, with outlined wordmarks derived from the supplied font matches. The reference-board screen mockups are design guides; they are not screenshots of Roadium.

Brand palette: navy `#193E74`, teal `#3C9FA0`, orange `#F4A04A`, and warm white `#F4F1E8`. Normal dark-mode UI uses deeper navy surfaces and a brighter derived teal `#76CECB` for readable controls. Incognito keeps the upstream gray palette.

`roadium-app-icon.png` is the 512×512 store icon. `roadium-adaptive-foreground.*` uses Android's 108dp adaptive-icon coordinate space and fits the 66dp safe circle. `roadium-monochrome.*` supplies the themed launcher silhouette. `roadium-wordmark.*` and `roadium-wordmark-dark.*` provide light/dark brand artwork. Runtime Android XML is in `android/` and embedded in the checksum-verified source overlay.

The wordmark uses League Spartan at weight 700 and Montserrat at weight 500, converted to paths. Runtime text rendering does not require installing these fonts. The bundled font files are from the official [Google Fonts League Spartan directory](https://github.com/google/fonts/tree/main/ofl/leaguespartan) and [Montserrat directory](https://github.com/google/fonts/tree/main/ofl/montserrat). Each font's SIL Open Font License and copyright notices are retained separately in `fonts/`. These font licenses do not establish a license for the user's reference artwork.

To regenerate vectors, install fontTools in a development Python environment, then run `python tools/roadium/generate-branding.py` from the repository root. Raster PNG exports are rendered from the generated SVGs. Export actual store screenshots from the built app on the emulator or car.
