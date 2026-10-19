# Card 01 evidence

Verified October 13, 2026 against the separate Card 01 overlay. This directory
contains local test results and controlled emulator observations, not browsing
history. The live public-list conversion counts are observations of that day's
download; automated failure/converter tests use controlled fixtures.

## Exact build

[Build manifest](x64-build-manifest.json) records source trees, patch hashes,
compiler exit, bundletool validation and artifact checksums. Its generated
runtime fields were pending at export; subsequent installed checks are recorded
in [verification.json](verification.json).

The exact APK and unsigned AAB are outside Git at
`E:\Android Auto Projects\RoadiumBuild\artifacts\153.0.8010.37-roadium-shields-card01-x64`.
The APK uses the diagnostic development certificate. This is an x64 development
build; ARM64 packaging and physical-car checks remain release gates.

## Tests and commands

- Loader: `python tools/roadium/test-apply-overlay.py` — 16 passing tests.
- [Native results](native-results.json) — 15 passing tests on API 33 Automotive.
- [Android results](android-results.json) — 20 passing executions, API 29/36.
- [Existing media results](media-results.json) — 26 passing executions, API 29/36.
- `git diff --check` — passed; foundation hash unchanged.

In the pinned Chromium source, with depot_tools on PATH and updates disabled:

```sh
python3 "$WORKSPACE/depot_tools/siso.py" ninja -C out/x64 --offline --local_jobs=12 roadium_shields_unit_tests roadium_shields_junit_tests roadium_media_junit_tests
vpython3 out/x64/bin/run_roadium_shields_junit_tests --json-results-file out/x64/roadium-shields-junit-results.json
ADB_SERVER_SOCKET=tcp:host.docker.internal:5037 vpython3 out/x64/bin/run_roadium_shields_unit_tests -d emulator-5554 --test-launcher-retry-limit 0 --json-results-file out/x64/roadium-shields-native-results.json
vpython3 out/x64/bin/run_roadium_media_junit_tests --json-results-file out/x64/roadium-card01-media-junit-results.json
```

## Installed observations

| Observation | Evidence |
| --- | --- |
| Fresh offline selection does not mean active data; finite manual timeout | [Report](fresh-report.png), [baseline](baseline-fresh-offline-adblock.json) |
| Five online activations; EasyList and anti-circumvention loaded | [Settings](online-completed.png), [counts](online-conversion-diagnostics.json) |
| All five later updates fail; prior data remains loaded | [Report](failed-update-report.png), [metadata](failed-update-diagnostics.json) |
| Existing profile settings and installed versions preserved | [Comparison](upgrade-existing-verification.json), [baseline](baseline-upgrade-adblock.json) |
| Explicit opt-out, site exception and manual rule preserved | [Before](upgrade-fixture-before.json), [after](upgrade-fixture-after.json) |
| Only EasyList selected: controlled advertising fetch blocked | [Enabled](easylist-enabled-probe.json), [disabled control](easylist-disabled-probe.json) |
| Global-off diagnostics distinguish paused data | [Report](global-off-report.png) |
| Driving restriction screen and paused HTML media | [Screen](media-restricted.png), [state](media-restricted-status.json), [return to Park](media-return-parked-status.json) |

The filtering probe fetches one fixed advertising URL without executing its
code. With only EasyList selected and no matching custom rule, it reports
`net::ERR_BLOCKED_BY_ADMINISTRATOR`; the same fetch completes with global
blocking disabled. The controlled page and restricted DevTools probe are
[shields.html](shields.html) and [probe-filter.mjs](probe-filter.mjs).

The temporary test-emulator TCP 443 rejection rules were removed by their exact
specifications; the proxy was absent, networking restored, original user11 list
selection restored, fixture playback stopped and developer forwarding removed.
The saved AVD disk was preserved through a read-only session.

WebAudio's context stayed running through the driving transition. A context
state does not establish audible output; this run does not claim speaker-level
WebAudio or speech verification. No physical-car or live YouTube result is
claimed. Mixed outcomes, storage failure and cancellation were exercised in
focused native tests rather than each being injected into the installed UI.

## Local review

Independent Ollama reviews are retained in `loader-review-result.json` and the
`review-*-result.json` files. They reported no concrete defects. Advisory gaps
were compared with the actual tests and sequence-owned APIs; concurrency means
joined asynchronous checks on the owning sequence, not cross-thread access.
The final installed checks and artifact verification are Codex's evidence.
