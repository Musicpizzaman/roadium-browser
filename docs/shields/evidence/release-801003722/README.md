# Shields internal-test candidate 801003722

This candidate is prepared for the existing **user-operated Google Play Console
internal-testing workflow**. It is not signed, uploaded or rolled out by Codex.
Use the [step-by-step signing and Play guide](../../PLAY_CONSOLE_UPDATE_801003722.md).

## Scope

Included browser work: Cards 01-08, with Card 09 checks/tooling. Card 06 retains
its documented live-service limits. **Card 10 fullscreen geometry and preferred
720p are not implemented in this candidate.** The Android 12 photo confirms
software details but cannot establish native content/window bounds or ownership
of the photographed gap. See [the updated vehicle record](../card10/device-software-2026-10-18.json).

This is a vehicle-test handoff with known open acceptance gates. No production
release readiness or successful OEM behavior is inferred from emulator results.
No existing manual gate has been marked passed to make the release checker green.
The user clarification changes deployment to instructions and user-operated
signing/upload, not direct Play publishing by the agent.

## Final local results

- [Verification summary](verification.json): both builds and artifact validators
  passed. [Full regression run](suite.json): 311 focused executions plus 16
  loader, eight packaged-resource and eight gate tests, **343 total**. The
  [Windows offline run](windows-offline-suite.json) also passed.
- [Installed update smoke](installed-update.json): actual x64 install from
  801003718 to 801003728, successful launch and rendered settings, with global
  pause, advanced opt-out, saved host, custom rule, subscriptions and homepage
  preserved. [Settings screenshot](installed-update-settings.png) was visually
  inspected. This is not physical-car/media/720p acceptance.
- [ARM64 manifest](arm64-build-manifest.json) and
  [x64 manifest](x64-build-manifest.json) record exact new APK/AAB hashes.
  All seven ARM64 native libraries passed [ELF16K checks](arm64-alignment.log),
  APK zipalign passed, and [bundle config](bundle-config.json) declares
  `PAGE_ALIGNMENT_16K`. ARM64 application manifest is non-debuggable and not
  test-only. The AAB remains unsigned, ready for the user's existing signer.
- Unsigned ARM64 AAB SHA256:
  `4c4f157683b535055c71c2ff7eaed027811728faa98ca9d1d6b7a390f30a6837`.
- [Production release checker](release-status.json) returns blocked as expected.
  No pending manual evidence was relabeled passed for this internal test.
- The owned read-only emulator PID98284 and new `ShieldsRelease722` user11 were
  guarded and removed/stopped. Original users0/10, shared host ADB and build
  containers were preserved. Developer flags and temporary preference staging
  files are absent; the emulator transport disappeared after shutdown.

The first installed-profile probe expected initialized filtering before the
ordinary first-run UI had been completed. It stopped and was not counted as a
pass. The actual Welcome/search-engine flow was then completed in the disposable
user, task flags removed, and the update test passed. No product change was
made to bypass first-run or to conceal that probe failure.

## Version and source

The prior documented design upload and initial Shields package both used ARM64
version code 801003712. The reviewed metadata-only offset increase from 10 to 20
produces **801003722 ARM64** and **801003728 x64**, while preserving engine
version **153.0.8010.37** and all nine overlay bytes. Both GN outputs explicitly
confirmed the new codes before builds. Existing overlay source remains:

- Cromite `11507ac1061b5ea227806f5e84db5a57df6ccf6a`.
- Baseline tree `56400c5406d8f83533c151e122b19f3f745c0892`.
- Cumulative overlay SHA256 `341ddbe7d5d3885f8fc93c68d0e781a6a620200a33c1b7810d7b2db0ae1c6960`.
- Applied source tree `6aa2d7a3c56cc89cdc401ac116481b80ab01d93b`.

The synthetic release-check test fixture now derives its offset from the current
baseline instead of assuming the historical Card 08 value. This changes test
data only; actual artifact checks and pending manual gates are unchanged.
Read-only local Ollama analysis reviewed the version path; independent
`gemma-4-12b-qat:latest` diff review approved the two-line metadata/test adjustment.
Missing required offset metadata continues to fail rather than adding the
reviewer's optional fallback suggestion.

## Local reproduction

Both prepared containers used the existing `prepare-build.sh` to regenerate GN
from pinned Cromite arguments plus Roadium overrides, followed by `run-build.sh`
and `verify-artifacts.py`. The full Card 09 runner is repeated on the new baseline
and requires all 311 focused browser tests plus 16 loader, eight resource and
eight gate tests. Actual package metadata/hashes, result status and owned
read-only emulator cleanup are recorded in the final verification JSON.

Historical Card 08/09 evidence is retained unchanged. Do not reuse its hashes or
old `suite.json` as acceptance for the newly versioned packages. New result and
build records belong here. Production signatures, Play upload/rollout, physical
car behavior, installed release UI/live-service/soak checks and hosted/native CI
provisioning remain independently tracked.
