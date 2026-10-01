# Building the Roadium foundation

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

The Dockerfile applies the checksum-verified patch on top of the original Cromite source. The loader checks the root source HEAD tree rather than its commit ID because the upstream image construction creates commits with varying timestamps. It stages the verified overlay, including new files, without committing it. Repeated application accepts only that exact patch and refuses unrelated changes.

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

Use `--arch x64` for the emulator build. `--workspace` can override `WORKSPACE`. The verifier checks the pinned source tree and overlay, all bundle module manifests, APK metadata, native libraries in both archives, ZIP integrity, the APK signature and bundletool validation. It derives architecture-specific version codes from Chromium's generator (ARM64 801003702; x64 801003708 for this baseline).

The resulting `roadium-ARCH-build-manifest.json` records artifact hashes, ABI and the verified APK certificate SHA256. AAB signing entries are recorded separately; their presence does not prove a valid signature. The current development AAB is unsigned and needs upload-key signing before Play distribution. Playback unit tests and runtime restrictions are separate checks.


## Focused playback tests

```sh
cd "$WORKSPACE/chromium/src"
export PATH="$WORKSPACE/depot_tools:$PATH"
python3 "$WORKSPACE/depot_tools/siso.py" ninja -C out/arm64 --offline --local_jobs=12 roadium_media_junit_tests
vpython3 out/arm64/bin/run_roadium_media_junit_tests --json-results-file out/arm64/roadium-media-tests.json
python3 "$WORKSPACE/roadium/tools/roadium/test-apply-overlay.py"
```

Run these inside the prepared container with depot_tools on PATH. The focused target avoids existing selection-menu test compile errors in Cromite's broader content_junit_tests target.

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
