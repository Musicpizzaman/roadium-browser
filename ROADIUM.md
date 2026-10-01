# Roadium Browser

Roadium Browser is an independent Cromite-based browser for parked use on Android Automotive OS. The first development target is a 2024 Chevrolet Blazer EV running Android 12. This repository keeps Cromite's patch series intact and adds a separate Roadium overlay.

Package: `io.github.musicpizzaman.roadium`. App packaging requires Android 12/API 31; the native build retains upstream's API 29 toolchain. The pinned upstream already targets API 36.

The foundation adds Roadium branding and an automotive-only manifest, disables Picture-in-Picture and the upstream APK updater, and applies foreground playback restrictions. Browser sign-in, sync, password saving and credit-card autofill are disabled. Password/payment settings entry points are removed. Third-party Android extensions are disabled at runtime; Cromite's native ad blocker is retained.

This is a development build. Physical-car behavior, OEM Play eligibility and release signing still require verification. As checked on October 1, 2026, Google documents parked browser distribution through internal testing. See the [AAOS browser requirements](https://developer.android.com/training/cars/parked/browser) and [distribution guidance](https://developer.android.com/training/cars/distribute).

## Source and build

The full Chromium tree lives in the pinned Cromite compiler image. This fork stores the Roadium patch, checksum and build tools. See [build instructions](build/roadium/README.md). The overlay loader verifies the upstream release, source tree and patch bytes before applying changes, and refuses unrelated tracked or staged source edits.

The source is based on Cromite 153.0.8010.37, release commit `11507ac1061b5ea227806f5e84db5a57df6ccf6a`. It is an explicit development baseline; check upstream security updates before distributing a release.

## Playback verification

Android Automotive OS controls parked-only activity access. Roadium additionally requires a resumed application activity for playback. Each WebContents is muted while restricted, media players are suspended, and playback restarts are suspended again. Platform speech synthesis is rejected while restricted; activity transitions cancel the native speech controller's queued utterances.

WebAudio requires separate verification: Chromium's media-player suspension API does not suspend its graphs. Roadium mutes their browser output while the application is restricted. A graph can continue processing while muted and regain audibility when the application resumes. Do not equate a running AudioContext, or an emulator launched with silent output, with proof that restricted playback is inaudible.

The focused lifecycle and speech test target passes 26 test runs across API 29 and API 36. It covers paused/started activities, new background contents, renderer playback restarts, user mute preservation, deferred speech cancellation and listener cleanup. Eight build-tool tests cover clean application, repeated application and refusal of modified inputs, including an overlay that adds new source files. Emulator and physical-car results must be recorded separately.

## Credits

Roadium is based on [Cromite](https://github.com/uazo/cromite), [Chromium](https://www.chromium.org/) and their third-party components. Upstream copyright notices, licenses and the browser's open-source credits remain available. This repository retains Cromite's [GPL v3 license](LICENSE); upstream components retain their applicable licenses.

Roadium is independently maintained and is not affiliated with or endorsed by either upstream project.
