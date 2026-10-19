# Roadium regression and release checks

Card 09 covers Cards 01-09. Card 10 is excluded because its geometry fix and
preferred 720p implementation remain open. Change the reviewed plan and coverage
matrix together when scope changes. A passing offline workflow is only one gate.

## Ordinary fork CI and local checks

Requires Python 3.10+ and Git, with no Chromium checkout, secrets, Android device
or network downloads. From the fork root:

```text
python tools/roadium/run-regressions.py --output <new-result-directory>
```

The output directory must not exist. The runner records failure instead of
reusing prior results. It verifies nine ordered patch hashes; six frozen input
files across three manifest families; immutable source/canonical identities;
compressed/plain lengths and hashes; license/attribution and notice presence;
the Card 08 fixture pair; and byte-exact generated converter inputs in overlays.
It runs 16 loader tests and eight gate tests with multiple negative cases.
These checks establish consistency with reviewed records, not license approval
or authenticity against a malicious edit of both input and manifest.

`.github/workflows/roadium-regressions.yml` runs these same checks for relevant
pushes/PRs and manual dispatch. It has read-only contents permission, pinned
actions, no persisted checkout credentials, a 15-minute bound and 14-day log
retention. It never sends untrusted PR code to a privileged native runner.
Activation and branch-protection requirements must be configured by the fork
maintainer; this local task does not claim a hosted workflow run occurred.

## Full pinned-source suite

Use the existing prepared Linux build environment described in
[build instructions](../../build/roadium/README.md). Source must have the exact
pinned baseline and complete nine-overlay state. The fork inside that environment
must contain all tools, filter/snapshot inputs, fixtures and current evidence
records, not just the files needed for compilation. Missing inputs are failures.
Do not install new dependencies or fetch moving source during verification.

Use an owned disposable Automotive x64 emulator, preferably a read-only launch
of the test AVD with snapshots disabled. Record ownership, launch arguments,
device identity and initial state. Ensure boot is complete and foreground user
is 0 before starting the focused native harness. Never run against a real user's
browser profile. The runner does not create an emulator, switch users or clean
shared devices. Shut down only the owned instance after collecting results.

```bash
export ADB_SERVER_SOCKET=tcp:host.docker.internal:5037
python3 /home/lg/working_dir/roadium/tools/roadium/run-regressions.py \
  --source /home/lg/working_dir/chromium/src \
  --device emulator-5554 --output /home/lg/working_dir/card09-results
```

The host ADB bridge above is specific to the existing Docker Desktop lab; a
native Linux runner uses its own correct ADB endpoint. Do not expose ADB on a
public interface. The pinned SDK bridge executable is selected explicitly.

Full mode verifies the baseline tree and exact cumulative applied source before
execution, checks generated fixture bytes, runs eight packaged-resource tests,
rebuilds three focused targets with pinned `siso.py`, then requires exactly:

| Target | Required executions |
| --- | ---: |
| `roadium_shields_unit_tests` | 231 |
| `roadium_shields_junit_tests` | 54 (27 methods on SDK 29 and 36) |
| `roadium_media_junit_tests` | 26 (13 methods on SDK 29 and 36) |

Every test name is reviewed in `tools/roadium/regression-plan.json`. Missing,
additional, disabled, skipped, retried, timed-out or failed tests fail the gate.
Additions need an explicit plan update, not a lowered count. Native output must
cover all 145 frozen YouTube rule IDs with matching URLs/text and valid outcomes.
Source is rechecked after execution. Every subprocess needs exit zero; full
logs and raw results remain in the unique result directory. Commands have
30-minute bounds, with three hours for focused compilation. A timeout is failure.

This suite tests native behavior and Java models. It does not automate every
installed UI/lifecycle check, website theme test, real restriction state or live
YouTube ad opportunity. Existing per-card installed evidence is retained as
historical evidence; review and rerun relevant scenarios on release candidates.

## Packaging and release evidence

In each prepared architecture workspace, run:

```bash
python3 /home/lg/working_dir/roadium/tools/roadium/verify-artifacts.py \
  --arch x64 --workspace /home/lg/working_dir
# Repeat with --arch arm64 in its ARM64 workspace.
```

This independently verifies APK/AAB bytes/resources, package, version codes,
SDKs, Automotive requirement, PiP restrictions, ABI, APK signatures and bundletool
validation against the applied source. Preserve manifests, badging, signature
and bundle-validation outputs. A build exit alone is insufficient.

Assemble a private release-review directory containing `suite.json`, `native.json`,
`shields.json`, `media.json`, both `<arch>-build-manifest.json` records, each
architecture's APK/AAB under `<arch>/`, and `approvals.json`.

```text
python tools/roadium/release-gates.py --evidence <review-directory> --output <gate-result.json>
```

Exit 1 means blocked, including missing infrastructure/results. The checker
rechecks current inputs/tool hashes, complete results, source/manifest agreement
and actual APK/AAB hashes. It emits an exact `binding` covering source and all
four packages. `approvals.json` must contain that binding, `scope` and
`excluded_cards` matching the plan, and a `gates` object with every named manual
gate. Each entry requires `status: passed`, `reviewer`, `date`, an evidence path
relative to the bundle, and the evidence file's `sha256`. These are accountable
review records, not cryptographic attestations or proof the assertions are true.
Maintainers must review their contents. Old-package evidence cannot silently
approve new source/packages because the binding must change.

All manual gates start pending. They include installed fresh/upgrade/offline/
recovery, site/private scope, parked/restricted media plus website theme and tab
controls, physical Android 12 Blazer EV, soak, live Card 06 limits, production
signing/Play readiness, and real fork/native-runner provisioning. The known
diagnostic APK certificate and unverified/unsigned AABs independently block the
checker. Current `verify-artifacts.py` does not verify an AAB upload signature;
a separately authorized production-signing workflow must add real verification
before this condition can pass. Never hand-edit a production manifest to assert
that verification. `evidence_complete` is a review result, never authority to
sign, upload, publish or drive while interacting with the browser.

No native hosted runner or build image distribution has been provisioned by
this task. The local containers are an available verification environment,
not a reproducibly published CI image. Missing native infrastructure remains a
release blocker even when ordinary hosted CI is green.

## Rebase checklist

1. Review pinned Chromium/Cromite revisions and regenerate/review overlays in order.
2. Rerun loader refusal/idempotency and exact final-source verification.
3. Review frozen list provenance/notices; regenerate converter inputs and run
   parser/trust/fallback negative fixtures without widening privileges.
4. Rerun bootstrap, corruption/interrupted-write recovery, migration, explicit
   opt-out, presets and saved/session ownership/private-scope checks.
5. Rebuild both architectures; verify resources, packaging and all hashes.
6. Rerun installed UI/theme/media/restriction acceptance and relevant physical
   vehicle/live-service/soak gates; record OEM limitations separately.
7. Rebind reviewed release evidence to exact packages. Keep signing/upload in
   their separately authorized workflow and never reuse old approvals by default.
