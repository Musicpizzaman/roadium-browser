# Card 10 — Fullscreen video geometry and preferred 720p playback

Planning date: October 17, 2026
Priority: **P1 — proposed next card** · Effort: **Medium–high**
Status: **In progress — source investigation and diagnostic fixture verified;
geometry fix and 720p preference remain open**

Current findings and scoped verification: [Card 10 investigation](evidence/card10/README.md).
The diagnostic tooling is implemented; this card is not complete and has no
new browser overlay or release artifacts yet.

Owner: __________  Reviewer: __________  Issue: __________
Branch/patch: __________  Start: __________  Target: __________

## Outcome and reported issue

Fullscreen playback uses the entire available app content area on supported
Automotive displays, with no unintended app-owned white strip. Videos retain
their aspect ratio; intentional black letterboxing or pillarboxing is valid.
New videos prefer a 720p rendition when the player exposes a supported quality
selection mechanism, with graceful fallback and a working manual override.

The user reports unused white space with every player on a Chevy infotainment
display and asks for 720p by default. The supplied photo shows a light vertical
wedge at the right edge, alongside persistent vehicle controls and climate UI.
On October 18 the user identified the affected vehicle as a **2024 Chevrolet
Blazer EV running Android 12** and clarified that **every website** is affected:
the whole rendered content area appears square and should extend farther to
the right. Treat this as a shared app/window/compositor-width investigation,
including ordinary browsing, rather than limiting reproduction to video
fullscreen. A square viewport and its cause remain user-reported observations,
not measured bounds. The photo does not establish whether the unused area
belongs to Roadium, the page or the OEM system. Preserve video proportions
when correcting the enclosing content area's width.

Reference photo (local attachment; do not copy the cabin photo into the repo):
`C:\Users\pc\.codex\codex-remote-attachments\01a13530-c227-73d2-b2e7-5111c7d0955e\5F8A799D-C40C-4AFB-8318-A2EA7CDEB846\1-Photo-1.jpg`

## Prerequisites

**Required for implementation acceptance:**

- [ ] Revalidate [PRE-01 and PRE-02](README.md#shared-prerequisites) against
  the current pinned source and available isolated build environment. Historical
  scratch paths are evidence references, not proof that a checkout still exists.
- [ ] Inventory the foundation's parked-only media behavior and existing
  fullscreen/viewport handling before choosing an integration point.
- [ ] Read [protected keyboard geometry](../ANDROID_PROTECTED_KEYBOARD_GEOMETRY.md)
  and distinguish logical page dimensions from physical Android view bounds.
- [ ] Record a reproducible baseline for fullscreen geometry and existing quality
  behavior, including fresh and upgraded profiles. Identify supported player APIs.
- [ ] Define which players can honor a rendition preference and which can only
  play the supplied stream; review that support matrix before implementation.

**Supporting:** [Card 06 media evidence](evidence/card06/README.md) supplies
playback, captions, fullscreen, background and tab-transition baselines. Its
open ad-format and Shorts checks do not prevent this investigation. Cards 07
and 08 are not prerequisites; use existing settings architecture.

**Release gates:** Physical reproduction and before/after evidence on the
affected Chevy display, parked-only regression checks, ARM64 packaging and
[Card 09](09-regression-and-release-gates.md) coverage if this card ships.
Emulator success alone cannot close the reported OEM display issue.

Vehicle/model/year: **2024 Chevrolet Blazer EV (user reported)**
Android/OEM software: **Android 12 confirmed by the October 18 About-screen photo;
security patch April 5, 2024; kernel 5.4.254-qgki-ga9e7a955a2b6-dirty.**
The OEM build line begins `aegean_orange-user 12`; exact full transcription and
native app/display measurements remain pending. See the
[software record](evidence/card10/device-software-2026-10-18.json).
Display resolution/density: __________  Roadium version/package: __________
Published panel size: **17.7-inch diagonal center touchscreen**, confirmed in
[Chevrolet's 2024 model announcement](https://news.chevrolet.com/newsroom.detail.html/Pages/news/us/en/2024/apr/0425-blazerev.html).
Public-specification lookup October 18 did not establish exact active width,
height or native pixel resolution. Diagonal size alone cannot determine them.
Use Android's current app window bounds and applicable insets for sizing;
do not hardcode a guessed Blazer resolution or assume the whole panel is
available to the browser.
Reproduction scope: **Every website; whole content area appears square with
unused room on the right (user reported).**
Specific baseline URL/video: __________  Device access/owner: __________

## Source spots to inspect

This fork stores overlays; inspect candidate Chromium paths in the exact
pinned checkout before relying on their location or APIs.

| Spot | Purpose |
| --- | --- |
| `build/roadium/baseline.json`, `build/roadium/patches/` | Preserve ordered overlays and record the new patch's provenance |
| `build/roadium/patches/0001-roadium-aaos-foundation.patch` | Existing Automotive playback restrictions and WebContents changes |
| `build/patches/Protect-keyboard-geometry-on-Android.patch` | Existing viewport/compositor geometry and privacy behavior |
| `chrome/android/java/src/org/chromium/chrome/browser/compositor/CompositorViewHolder.java` | Physical content sizing and compositor layout |
| Same compositor directory, `ProtectedViewportScrollView.java` | Protected logical viewport versus physical scrolling/sizing |
| `chrome/android/java/src/org/chromium/chrome/browser/fullscreen/` | Candidate `FullscreenManager.java` and `BrowserControlsManager.java`; verify pinned paths |
| `chrome/android/java/src/org/chromium/chrome/browser/app/tab_activity_glue/ActivityTabWebContentsDelegateAndroid.java` | Existing WebContents/fullscreen activity integration |
| `content/public/android/java/src/org/chromium/content/browser/webcontents/WebContentsImpl.java` | Existing media policy hooks; inspect only if relevant |
| Existing settings/preferences and media player integration in pinned source | Locate persistent quality preference and supported rendition controls |
| `tools/roadium/`, `docs/shields/evidence/card06/` | Fixture conventions, focused verification and prior playback evidence |

Confirmed files/methods/targets: __________  Proposed patch filename: __________

## Work breakdown

### A. Locate the unused area before proposing a fix

- [ ] Reproduce on the reported Android 12 / 2024 Blazer EV setup using an
  ordinary full-width page first, then fullscreen players. Compare the right
  edge of the Activity window, content parent, protected viewport, compositor
  and rendered page. Check width constraints, side insets and stale display
  configuration against the available app rectangle; do not impose a square
  aspect ratio or stretch video to compensate for an undersized container.
- [ ] Reproduce in Park with the exact installed build. Record system screenshot
  and an external photo so app pixels can be compared with physical display edges.
- [ ] Capture window bounds, OEM reserved regions, system-bar/cutout insets,
  content/compositor bounds, browser-controls visibility and player element bounds.
  Include video intrinsic dimensions, viewport dimensions and fullscreen state.
- [ ] Test normal pages, DOM fullscreen and HTML video fullscreen. Compare a
  neutral full-viewport color fixture with real players to identify surface ownership.
- [ ] Inspect stale layout after entering/exiting fullscreen, resize/orientation,
  keyboard open/close, tab switching and background/foreground transitions.
- [ ] Compare app/container backgrounds, CSS sizing, player fit mode and renderer
  bounds. Determine whether the strip is app-owned, page-owned or OEM-reserved.
- [ ] Record a root-cause statement with measured rectangles and a minimal
  reproduction. If the area is OEM-reserved, document that limitation and any
  supported display configuration; do not promise Roadium can reclaim it.

Root cause/owning layer: __________  Baseline screenshots/metrics: __________

### B. Correct fullscreen geometry at the owning layer

- [ ] Use the supported available app viewport and existing fullscreen lifecycle.
  Preserve OEM climate/navigation controls, cutouts and required system insets.
- [ ] Correct unintended padding, stale bounds or app-owned backgrounds only
  after the evidence identifies the responsible layer. Avoid site-specific sizing
  patches if a shared app surface is responsible for all players.
- [ ] Preserve video aspect ratio and black unused app background. Do not make
  stretching or cropping the default solution to a wide display.
- [ ] Preserve keyboard-geometry privacy, browser controls, captions, seeking,
  touch alignment and clean fullscreen exit/re-entry. Do not disable the privacy
  feature globally to hide a sizing defect.
- [ ] Add focused regression coverage for the measured cause and transitions.

### C. Implement a persistent preferred quality of 720p

- [ ] Add a clearly labeled quality preference using existing settings patterns.
  Default to 720p; offer Auto and preserve explicit stored user selections during
  upgrade. Record migration behavior for profiles with no prior preference.
- [ ] Define 720p as a playback rendition, not display resolution. Prefer the
  provider's 720p tier (normally 1280×720 landscape or the corresponding portrait
  tier); document unusual aspect ratios and provider-specific labels.
- [ ] Inventory native rendition APIs first. Where needed, define narrowly scoped
  adapters for supported sites/players and document unsupported cases. No universal
  quality control exists for every arbitrary HTML video or protected service.
- [ ] Prefer an available 720p rendition at playback start. If absent, use the
  player's normal adaptive/Auto fallback and keep playback working. Do not force
  a higher rendition, upscale, transcode or claim a single-source file is now 720p.
- [ ] Respect network adaptation and buffering recovery. Define when a player may
  lower quality; avoid repeated forcing that fights adaptive bitrate selection.
- [ ] Let a manual per-video choice win for that video. Define session scope for
  players that cannot distinguish a source change; apply the default again to a
  new video, including SPA navigation, without overriding a choice mid-video.
- [ ] Handle iframe players, delayed initialization and source changes without
  runaway polling, duplicate listeners or playback restarts.
- [ ] Preserve autoplay, audio/background restrictions, trusted-list boundaries
  and DRM behavior. Quality selection must not broaden filter/scriptlet privileges.
- [ ] Verify selected rendition with player telemetry or decoded-frame dimensions
  plus source identity where available; a menu label alone is insufficient proof.

Supported players/API and fallback matrix: __________
Preference key/migration: __________  Manual override scope: __________
Rendition-selection evidence method: __________

### D. Verify combined behavior and prepare release evidence

- [ ] Use deterministic multi-rendition fixtures (HLS/DASH where supported),
  a source without 720p, a single-source video and constrained-network cases.
- [ ] Exercise YouTube desktop/mobile/embed/Shorts where playable, another
  supported player and an unsupported player. Record unavailable live scenarios
  separately; do not count an unloaded video as a passing quality test.
- [ ] Test landscape, portrait and ultrawide content on rectangular emulators
  and the affected Chevy display, in windowed and fullscreen modes.
- [ ] Recheck playback controls, captions, audio, background/tab transitions and
  parked/restricted-state behavior after applying both changes together.
- [ ] Follow the shared Ollama implementation/review workflow for substantive
  source changes. Build and verify exact x64/ARM64 APK/AAB artifacts and retain
  the final diff, source identity, hashes, review findings and retest results.

## Acceptance matrix

| ID | Required result | Evidence/status spot |
| --- | --- | --- |
| VQ-01 | Measured ownership of the reported strip; reproducible root cause or verified OEM limitation | __________ |
| VQ-02 | App fullscreen fills usable bounds; no unintended app-owned white gutter; aspect ratio retained | __________ |
| VQ-03 | OEM controls/insets, keyboard privacy and touch/caption alignment preserved across transitions | __________ |
| VQ-04 | New supported playback defaults to an actual available 720p rendition | __________ |
| VQ-05 | No-720p, single-source, unsupported/DRM and constrained-network cases play with documented fallback | __________ |
| VQ-06 | Manual choice wins; new-video default and persistent preference work across restart/upgrade | __________ |
| VQ-07 | Playback, captions, seeking, background/tab and parked-only restrictions retain baseline behavior | __________ |
| VQ-08 | Exact reviewed build verified on emulator and affected physical Chevy; limitations recorded | __________ |

## Deliverables and completion spots

- [ ] Root-cause report and before/after viewport measurements/screenshots.
- [ ] Supported-player quality matrix, default/fallback/override specification.
- [ ] Reviewed overlay/settings changes and focused regression fixtures.
- [ ] Exact source, test, package and physical-device evidence under
  `docs/shields/evidence/card10/` when work begins; no placeholder success reports.
- [ ] Card 09 includes these gates if the feature is in the release.

Investigation owner/findings: __________  Implementation decision: __________
Blocked prerequisite/owner/next action: __________
Test targets/commands/results: __________  Physical-device report: __________
Patch/source/package hashes: __________  Local review/retest: __________
Release scope/acceptance reviewer/date: __________  Remaining limitations: __________
