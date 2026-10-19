# Card 09 verification - October 18, 2026

Regression automation is implemented locally. Release acceptance remains blocked.
The nine browser overlays and browser package bytes are unchanged from Card 08.
No production signing, upload or hosted workflow execution occurred.

## Executed results

- [Final full run](suite.json): passed, exact source diff
  `341ddbe7d5d3885f8fc93c68d0e781a6a620200a33c1b7810d7b2db0ae1c6960`,
  applied tree `6aa2d7a3c56cc89cdc401ac116481b80ab01d93b`.
- [Final Windows offline run](windows-offline-suite.json): passed with the same
  reviewed tooling; Linux full mode also passed all offline prerequisites.
- [Native](native.json): 231; [Shields Java](shields.json): 54;
  [media Java](media.json): 26. Exactly 311 focused executions, every status
  SUCCESS and no retries/disabled tests. [Native inventory audit](youtube-audit.json)
  binds all 145 frozen rule outcomes.
- [Loader](loader.log): 16 tests; [packaged resource negatives](resources.log):
  eight; [new regression gate negatives](gates.log): eight. Total 343 test
  executions including these tooling suites. [Compilation](compile.log)
  confirmed all three targets up to date in the exact verified source.
- Fresh packaging verification passed for [x64](x64-build-manifest.json) and
  [ARM64](arm64-build-manifest.json). Package hashes exactly match final Card 08
  packages; no browser rebuild was needed for fork-only tooling changes.
- [Release checker](release-status.json): expected exit 1, **blocked**, after
  independently hashing all four actual package files. All eight manual gates
  remain pending; diagnostic APK certificates and unverified AAB signatures
  block independently. The empty approval binding is intentional.
- Read-only local Ollama [analysis](local-analysis.json), [initial review](local-review.json)
  and [final review](local-final-review.json) completed. No concrete outstanding
  review findings. The optional filesystem-resolve timeout suggestion was not
  adopted for local files. Absolute pinned SDK/depot paths and command timeouts
  were checked through the actual integrated run; offline collection plus native
  audit cover the real inventory beyond the isolated identity-negative test.

Environment: pinned Chromium 153.0.8010.37 / Cromite
`11507ac1061b5ea227806f5e84db5a57df6ccf6a`; local x64 Docker image
`sha256:596eb1ca970b047031e5f8f0db937ece34c325d9a675e16c711989b07b30182f`,
ARM64 build-container image
`sha256:beb9e3b76915c499722c72be704a71164638da8f2951967d01ab4af59c3833d7`.
These are local image identities, not published reproducible image digests.
The owned API33 x64 RoadiumAAOS33 emulator ran read-only, snapshots/window/audio
disabled, 1280x720 at density160. The full runner requires foreground user0;
the initial ephemeral foreground user10 was switched only on this owned
read-only instance. It was stopped after tests with PID/path/arguments/AVD
identity guards. No extra runtime fixture users, TLS server, profile copies,
developer flags or browser UI fixtures were introduced for Card 09.

Initial container setup failures remain separate from accepted evidence:
[missing fork input](failed-missing-input-suite.json) and
[missing PATH adb](failed-pre-adb-suite.json). Both failed closed; required inputs
were synced and the runner now uses the pinned SDK executable. The earliest
missing-tool bootstrap exposed reporting initialization outside the error handler;
that initialization was moved inside it before final verification. Setup failures
and intermediate passing runs are not aggregated into final passing counts.
Windows lacked an optional external YAML parser; the workflow was independently
reviewed locally, but only a real hosted run can establish GitHub execution.

See the [runbook](../../REGRESSION_RUNBOOK.md) for exact commands, environment,
failure semantics, release-bundle format and rebase checklist. The committed
test plan records every required test name. Ordinary CI is deliberately limited
to fork-owned offline checks; the native suite requires the prepared environment.

## Requirement-to-test matrix

| ID | Requirement and assertion | Automated coverage / fixture | Installed or manual evidence |
| --- | --- | --- | --- |
| SH-01 | Fresh defaults and upgrade/explicit opt-out preserved | `ShieldsDefaultsTest`, `ShieldsServiceTest`, `ShieldsYoutubeTest`, preset Java/native models | [Card 08 real upgrade](../card08/upgrade-preservation.json); fresh/upgrade release rerun pending |
| SH-02 | Selected bundled data works offline without privilege leakage | `ShieldsBundlesTest`, including corrupt/wrong identity and installed precedence; immutable EasyList/AntiCV inputs | [Card 02](../card02/README.md); offline installed release gate pending |
| SH-03 | One approved fallback preserves canonical identity and bounded completion | `ShieldsFallbackTest`, `ShieldsTransportTest`; mocked primary/fallback HTTP/network responses | [Card 04](../card04/README.md); installed release rerun pending |
| SH-04 | HTML200, oversize, truncation, malformed data, redirects, lookalikes and custom lists cannot activate privileged data | `ShieldsApprovedContentTest`, `ShieldsFallbackMappingTest`, `ShieldsConverterTest`, transport negative fixtures | [Card 04](../card04/README.md), [Card 06](../card06/README.md) |
| SH-05 | Prior/bootstrap recovery survives corruption, schema mismatch, interrupted boundaries and failed storage | `ShieldsRecoveryTest`, `ShieldsLifecycleTest`; real temporary persistent stores and fault boundaries | [Card 05 forced-stop/storage evidence](../card05/README.md); extended soak open |
| SH-06 | Whole-rule parser decisions and trusted/untrusted policy match frozen source | 145 `Frozen/ShieldsYoutubeInventoryTest` cases, `ShieldsYoutubeTest`, converter tests; exact generated include and native audit identity | [Card 06 supported effects/live limits](../card06/README.md); live formats/Shorts remain open |
| SH-07 | Managed presets/category partial state and reset preserve custom/global/advanced choices | Native/Java preset cases; 15,240 accepted frozen category rules; generated input identity | [Card 07](../card07/README.md) |
| SH-08 | Saved/session ownership, restart expiry, IDN and DNS label scope | Native temporary-configuration tests and `ShieldsSiteStateTest` including raw-Unicode false-off regression; committed broken-site fixture hashes | [Card 08](../card08/README.md), including private original-profile sharing, actual document counts and observer teardown; release UI rerun pending |
| SH-09 | Parked video controls, captions, seeking, fullscreen, tabs and theme behavior retained | Existing focused Java media tests cover activity/mute/TTS models, not all playback UI | [Card 06](../card06/README.md) and prior media/theme baseline; installed/live UI release gate pending |
| SH-10 | Automotive restrictions cannot be bypassed; approved parked recovery | Existing Automotive Java lifecycle/mute/TTS tests; actual moving/parked state is separate | Physical Android12 Blazer EV and installed actual restriction-state acceptance pending |
| SH-11 | Immutable inputs, IDs, bytes and notices present; no Acceptable Ads package | Offline six-input checks, exact converter include generation; eight packaged-resource tests including corruption/missing/exception IDs | Both architecture artifact verifiers; attribution-presence checks do not replace license review |
| SH-12 | Ordered complete source and exact APK/AAB packaging | 16 loader tests; `VerifiedSeries`; both `verify-artifacts.py` runs; source-bound full suite and release evidence checker | Development certificate/unsigned AAB and release infrastructure remain blockers |
| SH-13 | Fullscreen available app viewport, no unintended gutter | Excluded Card 10; no claim of passing geometry coverage | [Card 10 investigation](../card10/README.md), implementation/physical measurements open |
| SH-14 | Preferred actual 720p, override and fallback | Excluded Card 10; no quality-preference implementation | Card 10 remains open |

## Scope and remaining acceptance

Cards 01-09 are the explicit candidate scope; Card 10 is excluded. This does not
resolve Card 06 live limits or imply a release is ready. The release checker
requires explicit manual evidence with reviewer/date/hash and an exact source/
package binding. Known development signatures and unsigned AABs block it
independently. No approval records have been marked passed for this task.

New offline negative controls reject changed patch/gzip/plain hashes, size and
identity drift, missing attribution, escaping paths, partial/skipped/timed-out/
retried tests, wrong native audit URL/text, stale source approvals and changed
package bytes. Existing native fixtures supply actual fallback/trust/parser and
storage rejection checks; packaged-resource tests independently exercise missing,
corrupt and forbidden exception resources.

Installed acceptance from earlier cards is linked above as historical evidence.
Card 09 reruns the complete focused suite and packaging checks; it does not claim
new fresh/upgrade/live UI/physical-car execution. The owned read-only emulator
is only used for the focused native test harness. No production profiles or
signing-private data are used. Raw focused results contain public deterministic
fixtures, not browsing history. Logs remain scoped to those tests.
