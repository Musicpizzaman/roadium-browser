# Roadium Browser

Roadium Browser is an independent Cromite-based browser for parked use on Android Automotive OS. The first development target is a 2024 Chevrolet Blazer EV running Android 12. This repository keeps Cromite's patch series intact and adds a separate Roadium overlay.

Package: `io.github.musicpizzaman.roadium`. App packaging requires Android 12/API 31; the native build retains upstream's API 29 toolchain. The pinned upstream already targets API 36.

The foundation adds Roadium branding and an automotive-only manifest, disables Picture-in-Picture and the upstream APK updater, and applies foreground playback restrictions. Browser sign-in, sync, password saving and credit-card autofill are disabled. Password/payment settings entry points are removed. Third-party Android extensions are disabled at runtime; Cromite's native ad blocker is retained.

The user installed the previous foundation build through Play internal testing and confirmed it works on their 2024 Chevrolet Blazer EV. The design update requires a separate car test after upload-key signing and upload. This remains a development build. As checked on October 1, 2026, Google documents parked browser distribution through internal testing. See the [AAOS browser requirements](https://developer.android.com/training/cars/parked/browser) and [distribution guidance](https://developer.android.com/training/cars/distribute).

## Appearance

The Roadium R launcher icon and first-run wordmark are faithful vector redraws of the supplied artwork. The normal browser uses navy, teal, orange and warm white, with matching light and dark palettes. The separate incognito palette is retained. Source references, fonts, licenses and exported artwork are in [assets/branding](assets/branding/README.md).

The browser follows the system appearance by default; Settings → Theme can select Light or Dark. On an HTTP or HTTPS page, open the menu → Website theme to choose Follow system, Light or Dark for that site. A site choice overrides the browser's current appearance in either direction and survives restart. Follow system clears the exception and restores the browser default. Sites with their own dark styles receive the preferred color scheme; other sites use Chromium's automatic darkening. Automatic darkening can vary with a site's content.

## Source and build

The full Chromium tree lives in the pinned Cromite compiler image. This fork stores the Roadium patch, checksum and build tools. See [build instructions](build/roadium/README.md). The overlay loader verifies the upstream release, source tree and patch bytes before applying changes, and refuses unrelated tracked or staged source edits.

The source is based on Cromite 153.0.8010.37, release commit `11507ac1061b5ea227806f5e84db5a57df6ccf6a`. It is an explicit development baseline; check upstream security updates before distributing a release.

## Playback verification

Android Automotive OS controls parked-only activity access. Roadium additionally requires the owning activity to be resumed for playback. Each WebContents is muted while restricted, and all HTML media players receive an ordinary pause request. Script or renderer playback restarts are paused again. The Roadium path avoids Chromium's frame-closure suspension, which can leave existing players frozen after returning to Park. Park restores the saved mute setting without automatically restarting HTML playback. Cromite's default disables website speech synthesis and voice enumeration entirely; Roadium preserves it. The additional platform speech guards reject restricted playback and cancel queued utterances, but the unit tests for those guards do not establish audible website speech in the shipped configuration.

WebAudio requires separate verification: Pausing HTML media players does not suspend WebAudio graphs. Roadium mutes their browser output while the application is restricted. A graph can continue processing while muted and regain audibility when the application resumes. Do not equate a running AudioContext, or an emulator launched with silent output, with proof that restricted playback is inaudible.

The foundation focused lifecycle and speech test target passed 26 test runs across API 29 and API 36. It covers paused/started activities, new background contents, renderer playback restarts, user mute preservation, deferred speech cancellation and listener cleanup. Eight build-tool tests cover clean application, repeated application and refusal of modified inputs, including an overlay that adds new source files. Emulator and physical-car results must be recorded separately.

## Emulator results

The previous foundation x64 development APK passed ten media cases on the API 33 Google APIs Automotive emulator. HTML audio, video and WebAudio produced measurable speaker output in Park. With the vehicle state confirmed as Moving (state 2, DO required, restrictions 255), output stayed at the quiet reference level despite external Play commands and repeated script restarts. All three produced sound again after Park; HTML players required an explicit play action on the same existing elements, without a page reload. The first recovery test exposed the frame-closure freeze and the ordinary-pause fix corrected it.

The automotive keyboard and typed navigation worked. Password, payment and browser sign-in entries were absent from the inspected main Settings screen. First-run and menu checks identified and corrected the inactive updater option, upstream filter-policy attribution, old first-run logo and extension controls. The final recovery builds include these UI corrections.

A separate finite AudioTrack reference with amplitude at most 2 kept emulator PCM sampling active during long muted periods; it is not part of Roadium. Restricted captures matched its measured peak of 2, while parked browser signals peaked around 984–2500. See the [verification record](build/roadium/verification-2026-10-01.json) for artifact hashes and measurements. Speech is recorded as disabled by the retained Cromite privacy default, not as a successful audible speech restriction test. These emulator results do not establish Android 12 car compatibility, physical audio routing or OEM Play availability.

## Design-update verification

The design update passed 64 focused website-theme test runs and 26 lifecycle/speech runs across API 29 and API 36, plus eight overlay-tool checks. On the API 33 Automotive emulator, 15 theme cases covered system appearance, opposite-direction site overrides, clearing choices and restart persistence. Four painted-image checks confirmed automatic darkening of a page whose authored CSS stays white, and restoration through Light. The supplied launcher icon and first-run wordmark were visually checked in both palettes.

All ten playback regression cases passed on the exact verified x64 APK: parked output was audible, restricted output stayed at the separate quiet reference peak of 2 despite external play and repeated script restarts, and the same players recovered in Park. ARM64 and x64 bundles passed bundletool, manifest/ABI/SDK and ZIP checks. The ARM64 AAB is unsigned and uses update version code 801003712; reuse the existing upload key. The new design still needs its own physical-car test.

See the [design verification record](build/roadium/verification-design-2026-10-02.json), [light first run](build/roadium/design-screenshots/design-first-run-light.png) and [dark first run](build/roadium/design-screenshots/design-first-run-dark.png). Artifact manifests contain compiler/package checks; runtime checks are recorded separately.

## Credits

Roadium is based on [Cromite](https://github.com/uazo/cromite), [Chromium](https://www.chromium.org/) and their third-party components. Upstream copyright notices, licenses and the browser's open-source credits remain available. This repository retains Cromite's [GPL v3 license](LICENSE); upstream components retain their applicable licenses.

Roadium is independently maintained and is not affiliated with or endorsed by either upstream project.
