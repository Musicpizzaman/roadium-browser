# Card 10 investigation — October 17, 2026

Status: **In progress; diagnostic tooling verified, browser fixes not implemented.**
Neither the Chevy white-strip issue nor preferred 720p playback is accepted as
fixed. No Card 10 browser overlay or new APK/AAB was produced.

## Release-preparation recheck - October 18, 2026

The user's deployment clarification specifies the existing **user-operated
Google Play Console** signing/upload workflow, not automated publication.
The separately prepared Shields internal-test candidate 801003722 retains
Cards 01-09 scope and does not contain a Card 10 fix. This remains an explicit
scope limitation, not completion of this card.

New bounded read-only [layout analysis](local-layout-analysis.json) found no
established shared-width defect. The non-resizable landscape manifest entry
belongs to `XrHostActivity`, not normal `ChromeTabbedActivity`. The normal
browser activity is resizable; the protected viewport already derives physical
width from its supplied measurement. No Automotive inset/fullscreen guard or
keyboard protection was removed based on a photograph. Speculation about
OEM ownership or side-UI insets remains unproven; native window/content/surface
rectangles on the car are still required.

The new [native HLS analysis](local-quality-analysis.json) is advisory only.
Its nearest-resolution suggestion was rejected because the task requires
normal Auto fallback when 720p is absent. It does not supply persistent browser
preference plumbing or cover site-managed MSE/DASH/YouTube. No unsupported
quality setter, nonfunctional settings switch or global hardcoded media cap
was shipped. These analysis records do not establish a playback-quality fix.

## Device clarification — October 18, 2026

A subsequent user-provided About-screen photograph confirms **Android 12** and
**April 5, 2024 security patch**, with kernel `5.4.254-qgki-ga9e7a955a2b6-dirty`
built June 18, 2024. The [software record](device-software-2026-10-18.json)
distinguishes directly visible details from inferred API level and still-missing
native bounds. This photo does not establish installed Roadium version or the
ownership of the reported unused strip. The cabin photo remains an attachment.

The user reports a **2024 Chevrolet Blazer EV running Android 12**. Every
website is affected; the whole content area appears square with unused space
to its right. Prioritize shared Activity/content/compositor width and native
side-inset ownership, starting with ordinary full-width browsing before video
fullscreen. These are user-reported device details and symptoms; no physical
dimensions or root cause have been measured. OEM software build, display
metrics and installed Roadium version remain unknown. This clarification
does not change the separate preferred-720p requirements.

Public-specification lookup October 18 confirmed the center touchscreen's
**17.7-inch diagonal** in [Chevrolet's model-specific announcement](https://news.chevrolet.com/newsroom.detail.html/Pages/news/us/en/2024/apr/0425-blazerev.html).
Exact active width/height and native pixel resolution were not verified in the
sources located. Do not convert the diagonal into a guessed aspect ratio or
use unrelated photo dimensions as panel resolution. The intended fix must size
to the current Android app window and applicable insets, including OEM-reserved
regions, rather than a hardcoded panel dimension.

## Changes and verification

Added `tools/roadium/fixtures/fullscreen-video.html` and integrated it into
`tools/roadium/make-fixtures.py`. The fixture measures page, container and video
bounds, intrinsic media dimensions, fullscreen state and visual viewport values.
It has distinct page/player/video fullscreen controls, portrait/ultrawide
container shapes, a keyboard input, bounded history and local JSON export.
It uses the existing Chromium `bear.mp4` (320×180), without autoplay or external
dependencies. Changing container shape does not select a different rendition.

Checks performed on the final reviewed files:

- Exact generated HTML matches the source; existing media/tone/index assets
  still generate. Missing media inputs fail before output creation, and an
  output path that overwrites source fixtures is refused.
- Desktop in-app browser: all three fullscreen modes enter and exit;
  fullscreen player/video bounds match the viewport within one CSS pixel.
  Portrait and ultrawide containers retain the video's intrinsic dimensions.
  Forty-five additional recordings leave exactly 40 retained samples.
  Report download was requested successfully; download contents were not
  independently inspected. The directly collected report is retained below.
- Installed x64 Automotive baseline: all three fullscreen modes report bounds
  matching the available page viewport within one CSS pixel; media time advances
  after explicit playback and pauses. These are DOM/runtime observations,
  not proof of physical pixel coverage or OEM compatibility.
- Local independent review (`gemma-4-12b-qat:latest`) found no concrete bugs.
  Optional clear-history control was deferred. Fullscreen was retested after
  review, followed by generator positive/negative checks and emulator execution.

Reports: [desktop transitions](desktop-fixture-report.json),
[bounded history](desktop-bounded-report.json),
[installed emulator](emulator-fixture-report.json).
Images: [desktop preview](desktop-preview.png),
[emulator initial render](emulator-initial.png),
[emulator display after the initial transition/playback sequence](emulator-display.png),
[corresponding page capture](emulator-page.png).

The first combined emulator sequence produced a blank page capture after
fullscreen transitions and playback, despite valid DOM state. Reload restored
visible content. Subsequent isolated page/player/video enter/exit captures
rendered content. This is an unresolved observation; neither a rendering pass
nor the root cause of the photographed Chevy strip is established. Native
screenshots and page captures must be compared during further testing.

## Source audit and decisions

The retained x64 source matches the Card 06 record:

- Chromium 153.0.8010.37 / Cromite `11507ac1061b5ea227806f5e84db5a57df6ccf6a`.
- Applied tree: `03cd90f156aad8219ab85df710dfea017d348062`.
- Cumulative diff SHA-256:
  `4bb773e6959f620cacf96891e11d890f9338996abf5942c0a0b0d7acdcc4a3a8`.
- No unstaged source edits; the seven existing overlays remain unchanged.
- Tested installed Card 06 APK SHA-256:
  `d18d2781075d5bb788341788894680814f45f9575f948ee328a952dbd0325a4b`.
- Read-only `RoadiumAAOS33` API 33 x64 session; 1280×720 display override,
  density 160. Separate `ShieldsCard10` lab user. First-run UI skipped using
  test command-line flags; no keyboard/privacy/media restriction switches used.

Confirmed fullscreen implementation is in
`chrome/android/java/src/org/chromium/chrome/browser/fullscreen/`:
`FullscreenHtmlApiHandlerFactory`, `FullscreenHtmlApiHandlerCompat`,
`FullscreenHtmlApiHandlerLegacy` and their base. The separate
`chrome/browser/fullscreen/android/.../FullscreenManager.java` is an interface.
The factory chooses handlers through existing feature flags. The compat
handler intentionally avoids edge-to-edge layout on Automotive; the legacy
handler intentionally suppresses system-UI visibility changes there.
Do not remove these guards based on the photograph alone.

The protected viewport maintains neutral content height and resets its baseline
on width changes. A worker's proposed compositor width mismatch remains a
hypothesis; it was not accepted as a diagnosed defect. Page-visible geometry
does not identify the native content/surface boundary or the OEM-owned area.

Native HLS does have selectable variants in
`media/formats/hls/rendition_manager.{h,cc}`. `SelectBestVariant` uses bandwidth
and player size; an explicit preferred variant takes precedence. It currently
has no persistent generic target-resolution preference. The engine creates
this manager in `media/filters/hls_manifest_demuxer_engine.cc`. A future HLS
implementation needs browser preference plumbing, migration, Auto mode and
tests; hardcoding a shared library limit would neither implement that contract
nor cover site-managed MSE/DASH playback. The worker's nearest-resolution
suggestion was not applied: it does not establish the required no-720p fallback.

YouTube's documented IFrame API no longer supports quality setters or the
suggested-quality argument. See the
[official revision history](https://developers.google.com/youtube/iframe_api_revision_history).
No unsupported quality calls or menu-automation adapter was added. No user-facing
720p setting was added without a verified consumer capable of honoring it.

Local analysis used `gemma4:26b` for bounded compositor, fullscreen and HLS
batches. An initial oversized request was rejected; a smaller bounded retry
succeeded. Workers were advisory and did not edit files.

## Reproduce and remaining work

Generate fixtures with the existing tool:

```text
python tools/roadium/make-fixtures.py --source <pinned-chromium-src> --output <isolated-fixtures>
python -m http.server 8870 --bind 127.0.0.1 --directory <isolated-fixtures>
adb -s <test-device> reverse tcp:8870 tcp:8870
```

Open `http://127.0.0.1:8870/fullscreen-video.html` in Roadium while parked.
Capture normal/page/player/video fullscreen and exit/re-entry, with and without
keyboard use. Save reports and a system screenshot alongside an external photo.
Confirm the reported vehicle/Android details and record the OEM build, display
resolution, Roadium version, a baseline URL and affected physical region. Record native window,
content and compositor bounds; do not infer them from JavaScript dimensions.
Keep raw device dumps and cabin photos outside the repository.

Remaining: physical Chevy reproduction and surface ownership; follow-up on
the emulator rendering observation; evidence-backed geometry fix; persistent
720p integration and player support matrix; deterministic multi-rendition,
fallback/override/upgrade checks; final browser builds, local review and parked
safety/physical acceptance. No acceptance row VQ-01 through VQ-08 is closed.

Cleanup: removed the owned lab user, flags and port mappings; restored user 10,
closed the read-only emulator and stopped the loopback fixture server.
