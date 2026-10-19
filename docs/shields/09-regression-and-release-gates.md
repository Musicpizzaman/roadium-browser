# Card 09 — Build automated regressions and release checks

Priority: **P0 for release** · Effort: **Medium–high** · Milestone: **Release gate**
Status: **Automation implemented and locally verified October 18, 2026; release acceptance blocked by explicit pending gates**

Owner: __________  Reviewer: __________  Issue: __________
Branch/patch: __________  Start: __________  Target: __________

## Outcome

Roadium's pipeline detects missing filter resources, unsafe fallback/trust
mappings, invalid filter conversion and regressions before an APK/AAB is
released. Tests cover fresh/upgrade/offline/failure/user-control behavior and
preserve browser playback, packaging and parked-only restrictions.

## Prerequisites and staged start

**Required for full acceptance:** Every card included in the intended release
has implemented interfaces and evidence. Record explicitly which cards are in
scope; a Milestone 1 release need not claim Cards 06–08 are complete.
The added [Card 10](10-fullscreen-video-and-720p-default.md) is also conditional
on explicit release scope; adding its tasker does not start implementation.

**Supporting work can start early:** test fixtures, target inventory, CI design
and a requirements-to-test matrix. Every implementation card owns its focused
tests; this card assembles integration and release gates throughout development.

- [ ] [PRE-01](README.md#pre-01--safe-patch-series-integration): complete patch
  series and final-source provenance verification.
- [ ] [PRE-02](README.md#pre-02--reproducible-verification-environment): confirmed
  native/Android commands, image, fixtures, emulator and physical-car plan.
- [ ] [PRE-03](README.md#pre-03--filter-provenance-and-distribution-records):
  bundle versions/hashes/source URLs, resource mapping, licenses and notices.
- [ ] Choose fork-owned CI runners/build-image access and artifact storage;
  identify feasibility before assuming full Chromium builds on hosted runners.
- [ ] Establish the approved media/theme baseline and exact release artifacts.
  Build success, artifact validation and runtime acceptance are separate checks.

## Source spots

Fork:

- `tools/roadium/` for deterministic checks/fixtures and build/test entry points.
- `build/roadium/` for pinned manifest, overlays, resources and evidence records.
- `.github/workflows/` for Roadium-specific CI without upstream release secrets.
- `tools/roadium/test-apply-overlay.py`, `apply-overlay.py`, `verify-artifacts.py`.
- `build/roadium/README.md` for current build and focused media/theme commands.
- Existing verification records in `build/roadium/` for baseline references.

Chromium source: existing native subscription/net/converter/browser test
directories; existing Android settings/JNI tests; confirmed focused Roadium
media/theme targets. Add a Shields-focused target only if existing targets
cannot provide reliable scoped coverage; record actual GN target/run commands.

Separate test overlay where Chromium tests/targets change. Fork-side scripts,
CI and documentation accompany it without altering the foundation patch.

## Work breakdown

### A. Establish a traceable regression suite

- [x] Map each implemented requirement to a test ID, level, deterministic fixture,
  assertion and evidence owner. Identify manual-only checks explicitly.
- [ ] Create clean, upgraded, explicit opt-out and custom-configured profile
  fixtures. Preserve production profile and signing data.
- [x] Provide primary/fallback response fixtures for network/HTTP/timeouts,
  HTML 200, truncation, oversize, malformed rules and corrupt FlatBuffers.
- [x] Provide trusted/untrusted scriptlet fixtures using real supported commands
  with observable effects; test canonical identity through every transport.
- [x] Provide storage fault boundaries, schema mismatch and interrupted-write
  restart fixtures from Card 05.
- [x] Provide protected/allowlisted/broken-site fixtures and selected-preset
  transitions from Cards 07/08 if those features are in the release.
- [x] Carry converter compatibility fixtures and live playback conditions from
  Card 06 if included. CI must not rely on unpredictable live YouTube ads.
- [ ] Preserve existing media restriction and website-theme coverage; filtering
  changes must not weaken previously verified browser behavior.
- [ ] If Card 10 is included, carry its viewport measurements, supported-player
  matrix, multi-rendition/no-720p fixtures, manual overrides and network fallbacks
  into the suite. Keep affected physical Chevy verification as a separate gate.

Coverage matrix to populate:

The populated [SH-01 through SH-14 matrix](evidence/card09/README.md#requirement-to-test-matrix) maps every scenario to actual targets, fixtures, historical installed evidence and pending release gates. The [test plan](../../tools/roadium/regression-plan.json) names all 311 required focused executions.

### B. Add Roadium-owned CI

- [x] Create a workflow that runs for relevant Roadium changes/PRs; do not
  rely on inherited workflows restricted to `uazo/cromite`.
- [x] Run lightweight loader, manifest/hash, mapping and fixture checks in
  ordinary fork CI. Native/Android/full-build jobs use the confirmed available
  environment and declare infrastructure prerequisites.
- [ ] Use pinned source/image/tool inputs or documented reproducibility limits.
  Validate source identity before applying verified overlays.
- [x] Make deterministic failures block the relevant merge/release gate with
  useful logs; distinguish infrastructure failure from a passed test.
- [x] Scope credentials to fork-owned resources. Do not require `PAGE_PUBLISH`,
  Cromite upstream release credentials or the production upload signing key.
- [x] Design untrusted PR jobs with read-only/minimal permissions; isolate any
  privileged runner/release job. Keep signing separate from ordinary tests.
- [x] Archive test results, provenance, fixture versions and failure diagnostics
  with bounded retention; exclude private browsing/signing data.
- [x] Document local reproduction commands and CI limitations. A unavailable
  native runner is an unresolved gate, not a silently skipped passing job.

### C. Add resource and release-artifact checks

- [x] Verify immutable bundled source URLs/revisions, versions, lengths/hashes,
  converter/schema inputs and packaged FlatBuffers/resource IDs.
- [x] Reject missing resources, hash drift, unusable converter output, unauthorized
  fallback mappings and inadvertent Acceptable Ads exception resources.
- [ ] Verify license/attribution records and distributed notices for all bundled
  lists and any newly eligible categories.
- [x] Verify ordered patch hashes and the exact applied source state. Record
  individual patches and final provenance; no first-patch-only verification.
- [x] Run existing artifact validation for package/label, version codes, SDK,
  ABI, archive integrity, APK signature and bundletool AAB validation.
- [x] Record APK and AAB hashes separately, build recipe/source/architecture and
  whether the AAB is unsigned, diagnostic-signed or upload-key-signed.
- [ ] Signing and Play upload require their own authorized release workflow;
  these taskers do not publish or create a production release.

### D. Execute installed and vehicle acceptance

- [ ] Install the exact verified x64 build on an Automotive emulator for fresh,
  upgrade, offline, fallback, recovery and applicable settings/site controls.
- [ ] Run parked HTML audio/video/WebAudio and YouTube controls, including
  fullscreen, captions, seeking and tab transitions where Card 06 applies.
- [ ] Confirm actual vehicle restriction state before moving-state media
  assertions. Repeated script/external playback attempts must not bypass it.
- [ ] Verify parked recovery follows Roadium's established behavior; stronger
  filtering must not freeze the same existing player or auto-start restricted
  media unexpectedly.
- [ ] Record emulator evidence separately from physical Android 12 car behavior.
  Plan physical tests in Park; any restricted-state checks must use a safe
  authorized test setup without interacting with a browser while driving.
- [ ] Verify ARM64 artifact packaging and existing Play internal-testing process
  readiness without claiming emulator results prove OEM/Play compatibility.

## Release checklist and acceptance

| Gate | Required proof | Status/evidence spot |
| --- | --- | --- |
| Included scope | Every included card and prerequisite signed off; omitted cards named | __________ |
| Source/patch provenance | Exact pinned baseline, all patches and final source verified | __________ |
| Offline resources | Versions/hashes/IDs/notices valid; actual offline filtering demonstrated | __________ |
| Update trust/resilience | Primary/fallback/error/redirect/custom-privilege tests pass | __________ |
| Recovery and upgrades | Fault/restart/settings-preservation tests pass | __________ |
| Applicable YouTube/customization | Deterministic tests pass; live limits recorded | __________ |
| Automotive/browser regressions | Relevant prior media/theme tests and installed checks pass | __________ |
| Applicable fullscreen/720p | Card 10 geometry/quality checks and affected physical Chevy evidence pass; OEM/unsupported-player limits explicit | __________ |
| Artifacts | Exact APK/AAB metadata, integrity, signature state and hashes recorded | __________ |
| CI ownership | Roadium checks run without upstream release credentials | __________ |
| Physical/runtime gaps | Pending checks explicitly listed; no false completion claim | __________ |

Acceptance requires the pipeline to catch deliberately broken resource,
fallback/trust and parser fixtures before release, not simply pass a healthy
build. Include negative controls to demonstrate those gates fail usefully.

## Deliverables

- [x] Requirements/test matrix and confirmed reproducible local commands.
- [x] Reviewed automated test/tool patches and Roadium CI workflow.
- [x] Release checker for resources, mappings, parser compatibility and provenance.
- [x] Test/result artifacts and exact APK/AAB verification record.
- [ ] Emulator and physical-car reports, separately scoped with pending limits.
- [x] Maintainer checklist for Chromium/Cromite rebases: rerun patch/source,
  converter/trust, resources, migration/recovery and media/packaging gates.

## Decisions, blockers and completion spots

Release cards included/omitted: __________  CI runners/image access: __________
Confirmed target/build/run commands: __________  Artifact storage/retention: __________
Failure-injection plan: __________  Physical-car plan/owner: __________
Blockers/owner/next action: __________  Patch/tool/workflow revisions: __________
Source identity/artifact hashes: __________  CI/local test evidence: __________
Emulator evidence: __________  Physical-car evidence or pending status: __________
License/resource checklist: __________  Local review/findings/retest: __________
Release acceptance reviewer/date: __________  Remaining limits: __________

## Card06 release integration handoff

Recheck the [frozen145-rule inventory and installed conditions](evidence/card06/README.md)
after upstream changes. Preserve source-policy/native-result binding and whole-rule
rejection. Carry the unsupported `[-]` removal grammar, Shorts buffering and
observed pre-/mid-roll opportunities as open gates. Keep fresh-profile experimental
opt-in behavior, existing selection preservation, media/background/tab controls,
all four default-list snapshots and physical vehicle evidence in the release matrix.

## Card 07 release integration handoff — October 18, 2026

Include [Card 07 verified source and acceptance](evidence/card07/verification.json)
when presets ship. Its 294 focused executions, full-file converter checks,
all preset transitions, fresh/upgrade/custom preservation, actual controlled
filtering and failed-update restart are documented in the evidence directory.
Integrate the 16 overlay-loader, eight packaged-resource and six snapshot
integrity checks. Verify category availability and exact canonical identity,
partial selection, opt-out independence and no privileged expansion.
Physical Android 12 Blazer EV focus/touch and parked-only regression, production
signing and extended update/storage soak remain open. API 33 x64 fixture results
and ARM64 packages do not close those gates. Card 09 automation is now locally verified; release acceptance remains open.

## Card 08 implementation handoff - October 18, 2026

[Card 08 evidence](evidence/card08/README.md) supplies the ninth overlay, 311
focused executions and installed site-control/activity acceptance. Integrate
saved/session ownership and expiry, global pause/preset independence, host/IDN
normalization and the legacy raw-Unicode false-off regression. Use the committed
`shields-site.html`/`shields-site-filters.txt` fixture pair and recorded hashes.

The existing browser client remaps Eyeo factory contexts to `GetOriginalProfile`.
Exceptions affect both regular and Incognito tabs after reload; only regular
PageInfo offers new controls. Do not infer absent private filtering from direct
off-record service-factory lookup. Preserve the shared-scope text and installed
cross-mode regression if routing changes.

Counter assertions must use the dispatching document, not a potentially reused
frame: embedded frames count in their page; reload/new documents reset while
same-document/cached pages retain counts. Validate panel/dialog observer teardown,
explicit unknown attribution and local bounded storage. Test probes must wait for
a fresh committed document and active fixture data. Physical Android 12 Blazer EV
focus/touch/rotary and parked-only behavior, signing and extended soak remain
release gates. Card 09 was authorized and its automation is now locally verified; release acceptance remains open.

## Card 09 implementation and verification - October 18, 2026

Owner/implementation/review: Codex with advisory read-only local Ollama analysis
and two independent diff reviews. No additional browser overlay is required.
All nine existing overlays and exact browser packages remain unchanged.

See [results and coverage matrix](evidence/card09/README.md), the
[reproduction/release runbook](REGRESSION_RUNBOOK.md), the
[full suite record](evidence/card09/suite.json) and the
[machine-readable blocked release status](evidence/card09/release-status.json).
311 focused browser executions, 16 loader, eight resource and eight new gate
tests pass in the prepared environment. Both architecture packaging verifiers
pass for the exact existing Card 08 APK/AAB bytes. Negative controls demonstrate
failure for damaged inputs and incomplete/mismatched evidence.

Fork-owned offline CI is implemented with minimal permissions and bounded log
retention. Hosted execution/branch protection and a published pinned native
runner/image are not provisioned by this local task; they remain release gates.
The local Docker image IDs and owned read-only emulator are recorded separately.
Installed fixture/profile acceptance from prior cards is retained as historical
evidence, not presented as newly rerun Card 09 UI acceptance.

Candidate scope is Cards 01-09, excluding Card 10. Physical Android12 2024 Blazer
EV acceptance, actual parked/restricted media plus theme/tab regressions on the
release candidate, live Card06 limits, extended storage/update soak, production
signing and Play readiness remain open. Every manual gate starts pending;
source/package bindings and reviewer/date/evidence hashes are required. Current
diagnostic APK certificates and unsigned AABs block release independently. No
production signing or upload is performed. Remaining empty acceptance boxes
represent those unresolved gates, not completed checks.
