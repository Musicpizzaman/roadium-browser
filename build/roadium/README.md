# Building Roadium with verified overlays

Use the Chromium/Cromite release and source tree in [baseline.json](baseline.json). The local upstream compiler image is `uazo/cromite-build:153.0.8010.37-11507ac1061b5ea227806f5e84db5a57df6ccf6a`. It must first be built from the unchanged pinned Cromite Docker contexts; this tag is not a published downloadable Cromite image. Do not substitute a different release or an unverified image.

From the fork root, export the unchanged pinned upstream Docker contexts. Archive extraction preserves the upstream Linux script bytes even when the fork is checked out on Windows. Use a Linux amd64 Docker engine and new scratch directories beside the fork.

~~~sh
git fetch https://github.com/uazo/cromite.git 11507ac1061b5ea227806f5e84db5a57df6ccf6a
git archive --format=tar --output=../cromite-153-context.tar 11507ac1061b5ea227806f5e84db5a57df6ccf6a tools/images/cromite-source tools/images/cromite-build
mkdir ../cromite-153-context
tar -xf ../cromite-153-context.tar -C ../cromite-153-context

docker pull uazo/chromium@sha256:78f9256c90c232af77b0441d557b349094e5157979e72d72870c6120f9755298
docker tag uazo/chromium@sha256:78f9256c90c232af77b0441d557b349094e5157979e72d72870c6120f9755298 uazo/chromium:153.0.8010.37
docker build --progress=plain --build-arg VERSION=153.0.8010.37 --build-arg CROMITE_SHA=11507ac1061b5ea227806f5e84db5a57df6ccf6a -t uazo/cromite:153.0.8010.37-11507ac1061b5ea227806f5e84db5a57df6ccf6a ../cromite-153-context/tools/images/cromite-source
docker build --progress=plain --no-cache --build-arg VERSION=153.0.8010.37 --build-arg CROMITE_SHA=11507ac1061b5ea227806f5e84db5a57df6ccf6a -t uazo/cromite-build:153.0.8010.37-11507ac1061b5ea227806f5e84db5a57df6ccf6a ../cromite-153-context/tools/images/cromite-build
~~~

These contexts download toolchain dependencies and include some moving tooling references. The commands reproduce the build process; image byte identity is not guaranteed. The Roadium loader separately requires the pinned post-Cromite source tree and exact overlay checksum.

Then create the small Roadium image layer:

```sh
docker build -f build/roadium/Dockerfile -t roadium-build:153.0.8010.37-foundation .
```

The Dockerfile applies the ordered, individually checksum-verified patch series on top of the original Cromite source. The loader checks the root source HEAD tree rather than its commit ID because the upstream image construction creates commits with varying timestamps. It preflights the entire series with a disposable Git index, then stages the verified remaining delta, including new files, without committing it. It accepts an exact already-applied series or an exact staged prefix with no unstaged changes and refuses unrelated edits or untracked collisions. Artifact verification checks the exact cumulative source diff, not the first patch's hash. The foundation patch remains unchanged; Card 01 adds a separate diagnostics overlay; Card 02 adds the bundled-filter overlay; Card 03 adds the advanced-filtering default and runtime-policy overlay. Card 04 adds the separate fifth overlay for exact approved GitHub fallback transports. Card 05 adds the sixth overlay for atomic publication and current/previous/bundled recovery.

Create a retained build container with a named output volume. Keep the full source inside the image; mount only the output directory.

```sh
docker volume create roadium-foundation-153-arm64
docker run -d --name roadium-arm64 --mount type=volume,source=roadium-foundation-153-arm64,target=/home/lg/working_dir/chromium/src/out/arm64 --entrypoint tail roadium-build:153.0.8010.37-foundation -f /dev/null
docker exec --user root roadium-arm64 chown lg:lg /home/lg/working_dir/chromium/src/out/arm64
docker exec roadium-arm64 bash /home/lg/working_dir/roadium/tools/roadium/prepare-build.sh /home/lg/working_dir/chromium/src /home/lg/working_dir/cromite /home/lg/working_dir/roadium arm64
docker exec -d -e ROADIUM_ARCH=arm64 roadium-arm64 bash /home/lg/working_dir/roadium/tools/roadium/run-build.sh
```

Use a different container and volume with `x64` for the x86_64 Automotive emulator. Run the two architecture builds sequentially. Each compiler is limited to 12 jobs; separate containers do not share a lock or a combined memory budget.

The build uses diagnostic signing unless a proper keystore is explicitly configured. Do not upload these diagnostic outputs as a Play release.

## Completion and recovery

`out/ARCH/roadium-build-status/current-run` points to an attempt directory. It contains the log, launch PID, boot identifier, recipe checksum and UTC start time. An `exit` file with value zero confirms compiler success; validate the artifacts separately. A missing exit file requires checking the container and compiler processes. A saved PID alone does not establish that a build is running after a restart.

The retained container and named output volume preserve incremental work. If Docker or the PC stops, restart the same container and rerun the durable launcher. Do not delete the output volume during recovery.

Outputs are `out/ARCH/apks/ChromePublic.apk` and `ChromePublic.aab`; the inherited filenames do not determine the Roadium app label or package. Verify package, label, SDK levels, ABI, ZIP integrity and bundletool validation. Record checksums and the exact source patch with each artifact set.

Run the verifier inside the prepared container after a successful build:

```sh
python3 "$WORKSPACE/roadium/tools/roadium/verify-artifacts.py" --arch arm64
```

Use `--arch x64` for the emulator build. `--workspace` can override `WORKSPACE`. The verifier checks the pinned source tree and overlay, all bundle module manifests, APK metadata, native libraries in both archives, ZIP integrity, the APK signature and bundletool validation. It derives architecture-specific version codes from Chromium's generator plus the validated `roadium_version_code_offset` in baseline.json (ARM64 801003712; x64 801003718 with the current Roadium offset of 10).

The resulting `$WORKSPACE/roadium-ARCH-build-manifest.json` (outside `out/ARCH`) records artifact hashes, ABI and the verified APK certificate SHA256. `source_patch_sha256` identifies the cumulative source diff; `source_patches` records each ordered patch and its hash, and `source_overlay_tree` identifies the resulting source tree. AAB signing entries are recorded separately; their presence does not prove a valid signature. The current development AAB is unsigned and needs upload-key signing before Play distribution. Playback unit tests and runtime restrictions are separate checks; see the [design verification record](verification-design-2026-10-02.json).

## Frozen native filter bundles

Card 02 uses the frozen EasyList and ABP Anti-Circumvention inputs under
`build/roadium/filters/`, mirrored in the Chromium overlay's native resource
folder. The manifest records immutable upstream URLs, version, compressed and
uncompressed SHA-256 hashes, licenses and attribution. Builds verify those
bytes before compiling and never download replacement inputs. Source notices
and the GPL license are packaged alongside both converted native resources.
License/manifest text uses LF; filter source bytes remain unchanged in gzip.

The pinned native converter emits FlatBuffers and rule-count JSON; a generated
manifest binds the input provenance to the exact converted bytes. Card 03
converts AntiCV with privileged rules while EasyList remains nonprivileged.
Advanced filtering defaults to enabled for unset profiles and preserves every
stored user choice. Current policy, global blocking and exact existing trust
identities gate privileged execution even for cached/preloaded data. Manual
rules cannot gain privileged execution. The Acceptable Ads exception list stays unbundled.
A selected bundle remains available after a failed update; installed data takes
precedence and explicit list removal removes the bootstrap data too.

`verify-artifacts.py` reads the actual APK and AAB resource packs and requires
both lists, the generated manifest and notices to match the build outputs.
Missing or altered packaged resources fail verification. Run its focused gate
tests inside the prepared container:

```sh
CHROMIUM_SOURCE="$WORKSPACE/chromium/src" python3 "$WORKSPACE/roadium/tools/roadium/test-filter-artifacts.py"
python3 "$WORKSPACE/chromium/src/components/adblock/core/resources/roadium/test_verify_inputs.py"
```

See [Card 02's evidence](../../docs/shields/evidence/card02/README.md) for exact
conversion counts, artifact provenance and installed acceptance results.

## Focused Shields diagnostics tests

From the prepared pinned source, build the scoped native and Android targets:

~~~sh
python3 "$WORKSPACE/depot_tools/siso.py" ninja -C out/x64 --offline --local_jobs=12 roadium_shields_unit_tests roadium_shields_junit_tests
vpython3 out/x64/bin/run_roadium_shields_unit_tests -d EMULATOR_SERIAL --test-launcher-retry-limit 0 --json-results-file out/x64/roadium-shields-native-results.json
vpython3 out/x64/bin/run_roadium_shields_junit_tests --json-results-file out/x64/roadium-shields-junit-results.json
python3 "$WORKSPACE/roadium/tools/roadium/test-apply-overlay.py"
~~~

Replace `EMULATOR_SERIAL` with the isolated Automotive emulator's actual ADB
serial. A remote local ADB server can be selected through `ADB_SERVER_SOCKET`;
the host configuration must reach only the intended test device. Native tests
exercise controlled transport/storage boundaries; JVM cases run at API 29 and
36. Installed browser diagnostics and real filtering evidence remain separate
checks. See [Card 01's audit](../../docs/shields/CARD01_AUDIT.md).


## Focused playback tests

```sh
cd "$WORKSPACE/chromium/src"
export PATH="$WORKSPACE/depot_tools:$PATH"
python3 "$WORKSPACE/depot_tools/siso.py" ninja -C out/arm64 --offline --local_jobs=12 roadium_media_junit_tests
vpython3 out/arm64/bin/run_roadium_media_junit_tests --json-results-file out/arm64/roadium-media-tests.json
python3 "$WORKSPACE/roadium/tools/roadium/test-apply-overlay.py"
```

Run these inside the prepared container with depot_tools on PATH. The focused target avoids existing selection-menu test compile errors in Cromite's broader content_junit_tests target.

## Focused website-theme tests

```sh
cd "$WORKSPACE/chromium/src"
export PATH="$WORKSPACE/depot_tools:$PATH"
python3 "$WORKSPACE/depot_tools/siso.py" ninja -C out/arm64 --offline --local_jobs=12 roadium_theme_junit_tests
vpython3 out/arm64/bin/run_roadium_theme_junit_tests --json-results-file out/arm64/roadium-theme-tests.json
```

This binary owns the two existing theme test classes directly. They contain 17 controller tests and 15 renderer-preference tests, run across API 29 and API 36 (64 passing executions for the design update), including inherited defaults, explicit Light/Dark in both system appearances and clearing exceptions. Native rendering, saved choices, authored dark styles and automatic darkening require separate runtime checks. Use the local fixtures `theme-native.html` and `theme-light.html`, and `tools/roadium/theme-fixture.mjs` after forwarding the browser's DevTools socket to localhost port 9222. The probe refuses non-fixture pages and never emulates CSS media preferences.

## Emulator restrictions

Use an Automotive image with usable hardware acceleration and test its declared ABI. The configured API 33 emulator requires the x64 APK; it cannot execute the ARM64 build.

After boot, set Park:

```sh
adb shell cmd car_service inject-vhal-event 0x11600207 0
adb shell cmd car_service inject-vhal-event 0x11400400 4
```

Use a freshly booted emulator for this bounded injection recipe. Launch Roadium, verify ordinary browsing, and start media. Then simulate Moving for a 60-second capture window:

```sh
adb shell cmd car_service inject-vhal-event 0x11400400 8
adb shell cmd car_service inject-vhal-event 0x11200402 false
adb shell cmd car_service inject-vhal-event 0x11600207 30 -t 60
adb shell cmd media_session dispatch play
adb shell dumpsys car_service --services CarDrivingStateService CarUxRestrictionsManagerService
adb shell dumpsys activity activities
adb shell dumpsys media_session
```

Confirm that the OS blocks the browser UI and no resumed Roadium activity remains, playback stops, external play commands cannot restore restricted output, and returning to Park restores browsing. Verify audio, video and WebAudio separately. Cromite disables website speech synthesis and voice enumeration in the pinned baseline; Roadium preserves that default. Record speech as disabled, rather than counting silence as a speech restriction pass. Use a parked positive audio signal to validate any PCM capture measurement. Launcher/start-command success alone is insufficient evidence.

Restore Park after the capture:

```sh
adb shell cmd car_service inject-vhal-event 0x11400400 4
adb shell cmd car_service inject-vhal-event 0x11600207 0 -t 60
```

Confirm state 0 and DO false, and verify Roadium's own activity is resumed. Use an explicit play action on the same audio/video element and verify its clock advances and speaker output returns without reloading the page. Park does not automatically restart HTML playback. Ordinary speed injections can be overwritten by recurring zero-speed events in the fake HAL. The `-t 60` argument future-dates the event by 60 seconds; it is an emulator testing mechanism. Android 13's `emulate-driving-state drive` command uses a much longer future timestamp, so reboot before using this bounded recipe if that command was used. See [CarShellCommand](https://android.googlesource.com/platform/packages/services/Car/+/refs/heads/android13-release/service/src/com/android/car/CarShellCommand.java) and [VehicleHal](https://android.googlesource.com/platform/packages/services/Car/+/refs/heads/android13-release/service/src/com/android/car/hal/VehicleHal.java).

Generate the local fixture assets from the prepared Chromium source:

~~~sh
python3 /home/lg/working_dir/roadium/tools/roadium/make-fixtures.py --source /home/lg/working_dir/chromium/src --output /home/lg/working_dir/fixtures
~~~

Copy that fixtures directory to the host when running the HTTP server outside Docker. Start the server with a local directory and event log:

~~~sh
python3 tools/roadium/serve-fixtures.py /path/to/local/fixtures --events /path/to/local/fixture-events.jsonl
~~~

The development fixture in tools/roadium/fixtures/index.html provides audio, video, WebAudio, speech and MediaSession controls. Retained Cromite privacy patches can prevent beacon event reporting; page state and measured speaker output remain the verification evidence. A speech button is not proof that the baseline supports website speech. It uses a generated tone.wav and Chromium's media/test/data/bear.mp4. Keep media assets in a local runtime directory, then run tools/roadium/serve-fixtures.py with that directory and a local --events log path. The server binds only to 127.0.0.1. `adb reverse tcp:8765 tcp:8765` connects the emulator to it. Tests must not infer app driving permissions from raw gear or speed values; those values are injected only into the emulator's system service.

For repeatable fixture actions, forward Roadium's active DevTools socket to host TCP port 9222 and load exactly one tab at `http://127.0.0.1:8765/`. The Node 24 helper selects that exact page and checks its address again during evaluation:

```sh
node tools/roadium/control-fixture.mjs status
node tools/roadium/control-fixture.mjs audio
node tools/roadium/control-fixture.mjs stop
```

Actions are `status`, `audio`, `video`, `web`, `speech`, `cancel`, `retry` and `stop`. The playback actions toggle the existing fixture buttons. `stop` also turns off auto-retry, pauses both media elements, suspends WebAudio and cancels speech. Each invocation has a ten-second deadline and prints page state as JSON. These states supplement speaker measurements; they do not prove inaudibility under driving restrictions.

An API 33 emulator result does not establish compatibility or Play eligibility on the Android 12 Blazer EV. The car test remains a separate step.

The inherited Cromite patch-check workflow skips ordinary fork pushes because it resolves commit IDs against uazo/cromite. It remains available by manual dispatch with a valid upstream reference. Roadium overlay checks run locally using the commands above.

## Speaker output measurements

The developer audio capture helper uses grpcio in a local Python environment. It reads the emulator's authentication token directly from its discovery file and writes only PCM statistics. Keep discovery files and generated test logs outside the public fork.

Launch the headless emulator with authentication enabled and omit explicit console/gRPC ports. On the tested emulator 37.3.2, explicit console ports suppress automatic gRPC startup; explicit numeric gRPC ports can change the listener binding.

~~~sh
emulator -avd RoadiumAAOS33 -no-window -no-snapshot -no-audio -gpu swiftshader_indirect -grpc-use-token
~~~

Verify the actual listener is loopback-only. Locate the current engine PID's discovery file under the emulator's temporary avd/running directory. The helper requires its port.serial to match the intended emulator (5554 by default). It uses the installed emulator's authenticated IPv4 loopback service.

~~~sh
python3 -m venv /path/to/local/test-venv
/path/to/local/test-venv/bin/python -m pip install grpcio==1.84.0
/path/to/local/test-venv/bin/python tools/roadium/capture-emulator-audio.py --discovery /path/to/pid_current.ini --serial 5554 --seconds 30 --output /path/to/local/audio-stats.jsonl
~~~

On Windows use test-venv/Scripts/python.exe. Each record contains the emulator's Unix-epoch timestamp in microseconds, sample count, RMS and peak for 48kHz stereo signed 16-bit output. A deadline bounds capture; no PCM is a failure. A successful connection or idle stream is not a playback restriction result.

Capture a positive parked browser signal, the transition into Drive, and an external play attempt. Allow transition buffers to drain before comparing the restricted segment with idle noise. Return to Park and establish another positive signal. The silent host output backend still produced measurable speaker PCM in the tested setup, verified with a finite AudioTrack tone (peak 250 against idle peak 2). Browser runtime results remain separate from this instrumentation check.

## Card 03 verified behavior

The fourth overlay preserves the first three patches byte-for-byte. Preference
changes update a shared live policy gate; selected trusted basic caches refresh
without deleting working data or changing list selections. Global blocking
stays independent, including an interactive advanced switch while it is off.
Diagnostics distinguish eligible privileged data from basic cache awaiting
refresh. The existing scriptlet command allowlist and disabled header filters
are preserved.

Both architecture builds and package verifiers passed. Installed x64 checks
cover fresh offline defaults, preserved explicit choices, actual supported
scriptlet effects, off/on reload behavior, global gating and untrusted/manual
negatives. Native tests cover conversion/storage races and stale callbacks.
See [Card 03 evidence](../../docs/shields/evidence/card03/README.md) and
[acceptance JSON](../../docs/shields/evidence/card03/verification.json).
Physical ARM64 vehicle acceptance and release signing remain pending.

## Card 04 approved transport fallback

The fifth overlay enumerates 31 exact canonical Cromite identities and their
approved raw GitHub pages transports. Every logical update starts at primary,
then tries fallback at most once after failure/unusable data. Converter,
callback, metadata identity and current privilege policy remain canonical.
Unknown/custom URLs gain no automatic mapping or trust.

Approved transports omit credentials, reject HTTP redirects before follow and
have a 60-second deadline including throttle/offline waiting plus a 32 MiB input
limit. Real plaintext conversion, verified schema/identity and supported rules
are required; declared subscription redirects cannot rename identity. Old data
stays active until replacement storage activation. Existing scheduled checks
remain 11–13 hours; the 45-second manual summary can report that work continues.

Both complete architecture builds and actual package verifiers passed. Final
post-review tests passed 57 native, 28 diagnostics and 26 media executions. Eight
installed x64 cases demonstrate actual fallback, policy-controlled scriptlets,
valid-primary avoidance of fallback, bad-content/redirect rejection, one-result
counters and retained filtering/data across failure and restart. The original
disposable profile and temporary injection state were restored.

See [Card 04 evidence](../../docs/shields/evidence/card04/README.md) and
[acceptance JSON](../../docs/shields/evidence/card04/verification.json). These
development APKs/AABs still require physical vehicle acceptance and release
signing before distribution. Card 05 supplies recovery in the separate sixth overlay.

## Card 05 atomic updates and last-known-good recovery

The sixth overlay retains immutable current/previous generations in the existing
Eyeo storage. It flushes and validates a candidate before atomic record
publication; successful activation controls counters. Restart revalidates current,
then previous, then eligible bundled data without resetting user configuration.
Current selected-list and live advanced-filter policy remain authoritative.
The first five overlays and bundled inputs remain unchanged.

The final source passed 128 focused executions, 16 loader and eight resource-gate
tests, both architecture APK/AAB builds and complete package verification.
Twenty installed scenarios include actual forced stops, corrupt/missing data,
write failure, offline bundle blocking and repair of recovered previous data.
See [Card 05 evidence](../../docs/shields/evidence/card05/README.md) for source and
artifact hashes, transaction/disk limits, commands, local reviews and cleanup.
Physical vehicle, production signing and extended storage/soak checks remain
release gates. Cards 06–09 remain on hold.

### Card Six YouTube compatibility

The seventh overlay keeps the legacy experimental list as an explicit choice
and stops selecting it automatically for fresh profiles. Maintained AntiCV stays
selected; existing selections and advanced opt-out survive upgrade. Trust, parser,
library, storage and Automotive enforcement are unchanged. The145-rule audit and
278 focused test executions are recorded in [Card Six evidence](../../docs/shields/evidence/card06/README.md).
Audit-only BadBlock/1Hosts snapshots in tools/roadium are not packaged resources.
Shorts, observed pre-/mid-roll ad opportunities, `[-]` JSON removal semantics and
physical vehicle/release checks remain explicit gates.

### Card Seven protection presets

The eighth overlay adds Standard, Balanced, Strict and derived Custom selection
and five eligible category controls to existing Android filtering settings.
Balanced preserves the existing four-list fresh default. Strict adds the exact
Social and Notifications catalog entries; neither grants privileged filtering.
Cookie-banner filtering is explicitly unavailable without a supported list.
Presets and managed reset preserve nonmanaged subscriptions, custom rules,
exceptions, homepage, global pause and advanced opt-out. Upgrades are not reset.

The native full-set update validates before mutation and persists/notifies once.
Frozen test-only optional inputs, notices and byte-exact regeneration are in
`tools/roadium/preset-snapshots/` and `preset_inventory.py`; they are not added
bundled browser resources. The first seven overlays remain byte-identical.

[Card Seven evidence](../../docs/shields/evidence/card07/README.md) records 294
focused executions, loader/resource/integrity checks, final x64/ARM64 APK/AAB
verification, installed presets/custom/exception/failure tests, reviews and
cleanup. Physical Blazer EV, production signing and extended soak are release
gates. Cards 08/09 and Card 10 geometry/preferred 720p implementation remain open.

### Card Eight site controls and local activity

The ninth overlay adds Shields to regular HTTP(S) page information. Site disable
and restore reuse saved allowed domains; temporary exceptions use a separate
memory-only native vector with browser-session lifetime. Original-profile
filtering is shared with Incognito by the existing browser client, so the help
text makes that scope and other-tab reload requirements explicit. The new panel
is offered in regular tabs. No alternative engine/preference store was added.

A bounded per-page counter records actual blocked frame-backed requests without
URL/rule history. Dispatch-time weak document references prevent attribution to a
new document after frame reuse. Site actions, counters, existing local diagnostics
and settings keep global pause, advanced opt-out, custom data and exception
ownership separate. Legacy raw Unicode records are preserved without a false
claim that the engine recognizes them as canonical punycode exceptions.

[Card Eight evidence](../../docs/shields/evidence/card08/README.md) records exact
source/package identity, 311 focused executions, loader/resource checks, installed
site/exception/private-scope/lifecycle acceptance, reviews and cleanup. Synthetic
site/filter fixtures live in `tools/roadium/fixtures/`. Final APK/AABs remain
development artifacts; physical Blazer EV, signing and extended soak are release
gates. Card 09 and Card 10 geometry/preferred 720p implementation remain open.


## Card 09 regression automation

Run fork-only checks with `python tools/roadium/run-regressions.py --output <new-directory>`.
Full mode requires the exact prepared pinned source and an owned disposable
x64 Automotive emulator; it recompiles the three focused targets and requires
all 311 test executions. See the [runbook](../../docs/shields/REGRESSION_RUNBOOK.md)
and [results](../../docs/shields/evidence/card09/README.md). The separate
`release-gates.py` checker verifies current source/tool/result/package bindings
and explicitly blocks missing runtime/physical/signing/CI evidence. Fork PR CI
runs only offline checks with read-only permissions and no release credentials.
No browser overlay, signing material or package bytes change for Card 09.
