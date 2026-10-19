# Roadium Shields taskers

Latest release preparation: [Shields internal-test candidate 801003722](evidence/release-801003722/README.md)
and [user-operated signing/Play Console steps](PLAY_CONSOLE_UPDATE_801003722.md).
This candidate excludes the unfinished Card 10 fullscreen/720p changes and is
not a claim of production release acceptance.

Planning date: October 13, 2026; Card 05 verification completed October 17.
Cards 01â€“05 are implemented and verified on the x64 Automotive emulator.
Cards 02â€“05 also have verified x64 and ARM64 packages. The latest
[Card 05 evidence](evidence/card05/README.md) records atomic publication,
current/previous/bundled recovery, actual forced-stop and storage-error checks,
current-policy behavior and configuration preservation. Physical vehicle,
production signing and extended storage/soak checks remain release gates.
Card06 is implemented with explicit open live acceptance gates; [its evidence](evidence/card06/README.md) records145 rule outcomes,278 focused executions and the maintained-default change.
Card 07 is implemented and locally verified October 18: protection presets,
category controls and preserved custom settings, with 294 focused executions
and verified x64/ARM64 packages. [Evidence](evidence/card07/README.md) records
installed filtering, failures, reviews and open physical/release gates.
Cards 08 and 09 are implemented and locally verified; physical/release acceptance remains open. See [Card 09 results](evidence/card09/README.md).
Empty checkboxes and evidence fields remain open until the associated work
has been performed and verified.
Card 10 was added and authorized October 17 for fullscreen display geometry and
preferred 720p playback. [Investigation and diagnostic tooling](evidence/card10/README.md)
are in progress; the geometry fix and quality preference remain open. The original
card numbers remain unchanged.

## Task index and prerequisites

| Card | Tasker | Priority | Required card dependencies | Effort |
| --- | --- | --- | --- | --- |
| 01 | [Audit and diagnostics](01-audit-and-diagnostics.md) | P0 | None | Smallâ€“medium |
| 02 | [Bundled filter databases](02-bundled-filter-databases.md) | P0 | 01 | Medium |
| 03 | [Advanced filtering defaults](03-advanced-filtering-defaults.md) | P0 | 01 | Smallâ€“medium |
| 04 | [Approved GitHub fallback](04-approved-github-fallback.md) | P0 | 01 | Mediumâ€“high |
| 05 | [Last-known-good recovery](05-last-known-good-recovery.md) | P0 | 02, 04 | Medium |
| 06 | [YouTube rule compatibility](06-youtube-rule-compatibility.md) | P1 | 03, 04, 05 | Mediumâ€“high |
| 07 | [Protection levels and categories](07-protection-levels-and-categories.md) | P1 | 01, 03 | Medium |
| 08 | [Per-site controls and activity](08-per-site-controls-and-activity.md) | P1 | 01, 07 | Mediumâ€“high |
| 09 | [Regression and release gates](09-regression-and-release-gates.md) | P0 for release | All cards included in the release | Mediumâ€“high |
| 10 | [Fullscreen video and preferred 720p](10-fullscreen-video-and-720p-default.md) | P1 â€” investigation open | PRE-01/02; existing media/viewport baseline | Mediumâ€“high |

Recommended implementation order is 01 â†’ 02 â†’ 03 â†’ 04 â†’ 05, then 06,
then 07 â†’ 08. Card 09 starts with test infrastructure and grows with every
implemented card; do not defer all testing until the end.
Card 09 now assembles the focused suites, fork CI and explicit release blockers. Card 10 remains the next feature implementation.
Card 10 remains open for
geometry and preferred 720p implementation; its investigation can use Card 06
media evidence without waiting for the open ad-format checks. Physical Chevy
verification remains a Card 10 release gate; Card 09 includes those checks if it ships.

**Required** means a prerequisite must be satisfied before the dependent
implementation can be accepted. **Supporting** means useful preparation may
run earlier, but cannot establish the dependent feature's acceptance.
**Release gate** means the feature may be developed before that check, but
cannot be included in a releasable artifact until it passes.

## Baseline and source locations

Use `develop` and the pinned baseline in
[baseline.json](../../build/roadium/baseline.json). See the
[preparation record](../SHIELDS_PREPARATION.md) for the verified source tree,
foundation hash and candidate filter snapshots. The preparation record's
eight passing loader tests do not establish that Shields works.

This repository stores overlays and tools, not a full Chromium checkout.
Paths beginning `components/` or `chrome/` in the taskers refer to the pinned
Chromium source inside the build environment. Paths beginning
`build/roadium/`, `tools/roadium/`, `docs/` or `.github/` refer to this fork.
Verify affected source against the pinned tree before accepting a draft.

## Shared prerequisites

### PRE-01 â€” Safe patch-series integration

**Required before applying any additional browser overlay.** This is supporting
build work, not a numbered feature card. It can be prepared alongside Card 01.

The loader now verifies ordered patch entries and the exact cumulative source diff using a disposable index, including overlapping paths. Card 01 supplies PRE-01; its 16 tests pass.

- [x] Preserve `0001-roadium-aaos-foundation.patch` byte-for-byte.
- [x] Specify ordered patch entries, per-patch hashes and exact final-source
  verification. Record how overlapping patches and new files are handled.
- [x] Validate all entries before mutation: schema, duplicate entries, path
  containment, expected patch files and every checksum.
- [x] Prove clean application and exact full-series reapplication are safe.
- [x] Define partial-series behavior. Reject ambiguous existing state or
  recover only a verified prefix; never infer that unrelated edits belong.
- [x] Prove a later failure cannot strand newly applied changes. Prefer
  staging/verification in an isolated disposable workspace before a safe
  transaction; do not use blanket cleanup against an unrelated working tree.
- [x] Refuse unrelated staged/unstaged changes and untracked file collisions.
- [x] Update `apply-overlay.py`, its tests, `verify-artifacts.py`, build
  documentation and provenance records together.
- [x] Verify a failed or tampered later patch leaves initial source and index
  unchanged; preserve the current eight loader refusal/idempotency cases.

Owner: Codex. Design/evidence: [Card 01 audit](CARD01_AUDIT.md), ordered loader tests and exact build manifest.

### PRE-02 â€” Reproducible verification environment

**Required for implementation acceptance; environment inspection can precede
implementation.** See [build instructions](../../build/roadium/README.md).

- [x] Confirm the exact pinned image/source tree and identify existing source
  edits before touching a retained container.
- [x] Choose isolated development source/output locations. Preserve existing
  output volumes, installed app data and production signing material.
- [x] Confirm the native and Android test targets available in this revision;
  record exact build/run commands rather than inventing target names.
- [x] Prepare fresh, upgraded, explicitly disabled and custom-configured
  profile fixtures using copies or disposable profiles.
- [x] Prepare deterministic local network/filter fixtures and storage-failure
  injection. Unit tests must not depend on current public endpoint content.
- [x] ARM64 packaging coverage verified alongside x64 Automotive runtime checks;
  physical Android 12 vehicle/driving checks remain release gates.

Source/image record: [pinned source/image audit](CARD01_AUDIT.md) and
[latest exact source/package manifests](evidence/card05/verification.json).
Fixtures/commands/results: [Card 05 recovery record](evidence/card05/README.md),
[focused test commands](evidence/card05/run-tests.sh). Device plan: verified
read-only API 33 Automotive x64 session, cleaned up after testing; physical
ARM64 Android 12 vehicle/driving checks remain release gates.

### PRE-03 â€” Filter provenance and distribution records

**Required for bundling or adding an eligible subscription; full release
records are a release gate.** Card 02 owns initial bundle integration.

- [ ] Record canonical identity, immutable source revision, input version,
  byte count, SHA-256, license and attribution for each bundled input.
- [ ] Validate candidate snapshots with the actual pinned converter and
  trusted-list policy before calling them known-good.
- [ ] Decide where source inputs and license notices live and how reproducible
  conversion outputs and notices reach the distributed artifact.
- [ ] Record syntax support and ownership for every list added to presets.
- [ ] Keep GPL-3.0 compatibility and Acceptable Ads exceptions disabled.

Provenance manifest: __________  Attribution record: __________
Converter evidence: __________  Distribution review: __________

## Shared engineering rules

Use the existing Eyeo engine, subscription updater, FlatBuffers, permitted
scriptlets and settings. Preserve Roadium's architecture and Automotive
safety behavior. GitHub fallback is transport only; it must not create a new
trusted subscription or broaden privileged execution for custom lists.

For substantial engineering work, follow the project's Ollama workflow:
identify minimum files with lightweight searches; use `delegate_code_task`
with `gemma4:26b` and file batches below 48 KiB; include relevant architecture
rules; request concise proposals. Smaller work and independent review can use
`gemma-4-12b-qat:latest`. Workers are advisory and cannot edit repository files.
Codex verifies affected source, applies accepted changes, builds and tests,
obtains the diff, runs `review_code_diff` for substantive changes, fixes valid
findings and retests. Worker failure requires reporting and user direction
before independent implementation. Do not cancel a running request merely
because it is slow; the permitted total runtime is three hours including its
bounded retry, with manual user cancellation available.

Each feature card produces a separate reviewed Roadium patch, focused tests
and evidence. Supporting fork tooling/test changes may accompany the card.
Patch filenames in taskers are proposed until the series design is approved;
update `baseline.json` checksums deliberately as integration proceeds.

## Common completion requirements

- [ ] Required prerequisites have evidence, not just links to open cards.
- [ ] Affected source and JNI/resource/build interfaces have been checked.
- [ ] Existing settings, custom filters and relevant upgrade behavior survive.
- [ ] Acceptance checks and failure tests pass on the exact reviewed source.
- [ ] Local independent review findings are resolved and tests rerun.
- [ ] Patch hash, test commands/results, build identity and limitations are
  recorded in the tasker's evidence fields.
- [ ] Applicable license/attribution and parked-only regression gates pass.
- [ ] Unmet runtime checks are marked pending; mocked success is not recorded
  as real-world YouTube or physical-car success.

## Project tracking spots

Project owner: __________  Implementation start decision: __________
Milestone 1 target: __________  Milestone 2 target: __________
Milestone 3 target: __________  Release candidate: __________
Integration branch: __________  Issue tracker links: __________
Cross-card decisions/blockers: __________
