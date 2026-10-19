# Card 05 — Implement last-known-good filtering and atomic updates

Priority: **P0** · Effort: **Medium** · Milestone: **Reliable protection**
Status: **Implemented and verified — installed x64 Automotive; x64/ARM64 packages verified**

Owner: Codex  Reviewer: Local Ollama advisory review  Issue: local task (no external issue assigned)
Branch/patch: develop / 0006-roadium-last-known-good-recovery.patch  Completed: October 17, 2026 (Central)

## Outcome

An interrupted, invalid or failed update cannot remove the last working
filtering state. Restart selects valid current/previous data, then eligible
bundled data when necessary, while preserving all user configuration.
Use existing persistent subscription storage and validation.

## Prerequisites

**Required card dependencies:** [Card 02](02-bundled-filter-databases.md) supplies
validated bootstrap resources; [Card 04](04-approved-github-fallback.md)
supplies canonical identity, transport completion and temporary-data contracts.

- [x] Card 01 diagnostic/error contract available through those dependencies.
- [x] [PRE-01](README.md#pre-01--safe-patch-series-integration) and
  [PRE-02](README.md#pre-02--reproducible-verification-environment).
- [x] Storage audit identifies file writes, metadata publication, active
  collection swap, obsolete-file deletion and restart loading order.
- [x] Fault injection can interrupt each boundary and simulate write/rename,
  metadata and validation failures without touching production app data.

**Supporting:** Card 03 trust/preference policy must be integrated before
Milestone 1 acceptance; valid cached data never overrides a current opt-out.

## Source spots

Chromium source:

- `components/adblock/core/subscription/subscription_persistent_storage_impl.cc`
  and `.h`
- `components/adblock/core/subscription/subscription_persistent_metadata_impl.cc`
  and `.h`
- `components/adblock/core/subscription/subscription_validator_impl.cc` and `.h`
- `components/adblock/core/subscription/subscription_downloader_impl.cc`
- `components/adblock/core/subscription/preloaded_subscription_provider_impl.cc`
- `components/adblock/core/subscription/subscription_collection_impl.cc`
- `components/adblock/core/subscription/subscription_storage_transaction.cc` and `.h`
- `components/adblock/core/subscription/filtering_configuration_maintainer_impl.cc`
- `components/adblock/test/shields_recovery_unittest.cc`
- `components/adblock/core/subscription/test/` for storage/validator/restart tests.

Fork: separate recovery overlay; storage/crash fixtures and an evidence record.

## Work breakdown

### A. Define the actual storage transaction

- [x] Identify existing safety guarantees before adding storage. Unique
  filenames alone do not prove atomic metadata publication or crash durability.
- [x] Define candidate, current and previous valid versions under the original
  subscription identity, with a documented bound on retained versions.
- [x] Specify ordered boundaries: download temporary input → convert → validate
  complete output → durably store candidate → publish metadata/active version
  → update diagnostics → clean obsolete files after success.
- [x] Select atomic replacement or equivalent safe existing storage transaction.
  Account for file/metadata ordering and supported platform durability semantics.
- [x] Preserve current active data and at least one prior valid version until
  the new version can survive reload. Do not publish success counters/version
  before the logical transaction has succeeded.
- [x] Handle asynchronous storage/activation failure without leaking candidates
  or allowing an older callback to replace a newer accepted version.

Transaction/fault-boundary spots:

| Boundary | Durable state after interruption | Recovery expectation | Injection/evidence |
| --- | --- | --- | --- |
| Partial download | Current/previous unchanged | Ignore candidate | [Actual partial-response force-stop](evidence/card05/force-stop-download-boundary.json), [fresh filtering](evidence/card05/force-stop-download-report.txt) |
| Conversion/validation | Current/previous unchanged | Reject incomplete output | 17 native recovery tests plus [both-source invalid HTTP 200 rejection](evidence/card05/invalid-retention-report.txt) and [schema rejection](evidence/card05/schema-recovery-report.txt) |
| Candidate persisted, unpublished | Old metadata/current intact | Ignore or safely reconcile orphan | [Actual paused candidate/force-stop](evidence/card05/force-stop-candidate-boundary.json), [unpublished orphan](evidence/card05/orphan-cleanup.json) |
| Metadata publication | Consistent valid pointer or recoverable previous record | Select valid version | [Previous published](evidence/card05/force-stop-previous-boundary.json), [current published before callback](evidence/card05/force-stop-published-boundary.json) |
| Activation/obsolete cleanup | Current valid, prior retained | No empty filter state | [Activation/restart](evidence/card05/activation-restart-report.txt), [repeated cycles](evidence/card05/repeated-update-recovery-report.txt) |

### B. Validate before activation

- [x] Verify entire FlatBuffers integrity, schema compatibility, canonical
  subscription identity and policy-sensitive metadata.
- [x] Verify supported-rule conversion succeeded and accepted rules are
  plausible for that list. Define baseline/threshold exceptions explicitly;
  arbitrary global rule-count cutoffs can break small valid subscriptions.
- [x] Reject corrupt, truncated, wrong-format, unauthorized privilege and
  incompatible-schema candidates before they replace active data.
- [x] Preserve local error details through Card 01 and keep old active version
  visibly separate from rejected candidate information.

### C. Recover safely on restart

- [x] Validate current data at load. If invalid/unavailable, try recorded
  last-known-good data, then eligible bundled data from Card 02.
- [x] Reapply current selected-list/advanced/trust policy to any recovered data;
  do not resurrect intentionally unsubscribed or disabled subscriptions.
- [x] Recover missing/stale metadata and orphan candidate files according to
  the documented transaction. Clean only owned, verified subscription paths.
- [x] Handle schema-version changes by rejecting incompatible data and using
  compatible previous/bootstrap data or scheduling a bounded refresh.
- [x] Retain per-site exceptions, list configuration, custom URLs and manual
  rules. Recovery is not a profile reset or cache-clearing operation.
- [x] Define behavior when no valid data exists: honest degraded status and
  bounded update scheduling; never label an empty engine as operational.
- [x] Bound disk use and keep cleanup off the critical path where possible.

## Acceptance and tests

| Scenario | Required result | Evidence spot |
| --- | --- | --- |
| Force-stop at each transaction boundary | Restart loads valid current/previous/bootstrap data | Four actual stopped update boundaries, native interruption matrix, and [accepted activation/restart](evidence/card05/activation-restart-report.txt) |
| Bad download/conversion/FlatBuffers/schema | Candidate rejected; known working filtering survives | [Invalid input retention](evidence/card05/invalid-retention-report.txt), [schema recovery](evidence/card05/schema-recovery-report.txt), native corrupt/invalid candidate tests |
| Disk full/write/replace/metadata failure | Failure reported; prior data remains usable | Native write/rename/publication failure paths and [actual installed metadata write error](evidence/card05/storage-error-retention-report.txt); literal device ENOSPC remains a release stress check |
| Current corrupt, prior valid | Prior version selected with recovery diagnostic | [Loaded previous versions and actual filtering](evidence/card05/previous-version-recovery-report.txt) |
| Downloaded versions invalid, bundle valid | Eligible bundled baseline filters offline | [Offline bundled blocking](evidence/card05/offline-bundled-recovery-report.txt), live unavailable custom-list state |
| Missing data or stale/orphan metadata | Deterministic recovery; no unauthorized file deletion | [Missing metadata](evidence/card05/missing-bundled-recovery-report.txt), [orphan cleanup and unrelated-file preservation](evidence/card05/orphan-cleanup.json) |
| Explicit unsubscribed/advanced-disabled profile | Recovery respects current choices and trust policy | [Explicit removal](evidence/card05/explicit-removal-recovery-report.txt), [cached privileged previous data under opt-out](evidence/card05/previous-version-recovery-report.txt) |
| Concurrent update/cancel or reversed callbacks | No old-version regression or duplicate terminal result | Native expired permit, during-commit cancellation, production retire/discard and stale-discard/newer-publication tests; one sequenced I/O runner |
| Repeat recovery/update cycles | Bounded storage and preserved custom settings | [Repair after previous recovery](evidence/card05/repair-after-recovery-report.txt), three installed restart/update cycles, native 12-update bound test |

Use automated boundary/fault tests plus force-stop/restart on an installed
build. Demonstrate actual fixture blocking after recovery; valid file existence
alone does not prove the engine loaded it.

## Deliverables and handoff

- [x] Separate recovery patch and failure/restart tests.
- [x] Written transaction, retention, schema and orphan-cleanup policy.
- [x] Installed force-stop, invalid-input and storage-error evidence.
- [x] Milestone 1 integrated checks across Cards 01–05.
- [x] Handoff to Card 09: reproducible fault boundaries and expected recovery
  version/origin without resetting preferences.

## Decisions and completion record

**Transaction:** the existing Eyeo persistent storage owns immutable generation
files and independent current/previous JSON records. Flush the candidate and
directory, validate stored bytes, publish previous, then atomically publish
current with file flush/rename/directory sync. Only accepted active state counts
as success. Preferences remain configuration/advisory history; new commit
authority is independent of delayed preference signatures.

**Retention and validation:** two reachable generations per identity, each at
most 128 MiB of converted data, plus one transient candidate. Records/pending
records are each at most 16 KiB. Check full FlatBuffers, current schema, canonical
identity, hash, trust-sensitive indexes and actual supported indexes; small lists
remain valid. Old mapped snapshots may retain unlinked blocks until destroyed,
so this is a retained-file bound rather than a universal live-lease disk quota.

**Recovery:** current → previous → eligible compatible bundle under current
configuration and live privilege policy. Missing custom data is honestly
unavailable. Legacy migration requires its original signature and full checks.
Unpublished new orphans/pending records never establish trust. Cleanup is
nonrecursive and confined to exact owned paths, with symlink checks; unrelated
files are preserved. No user configuration is reset. Existing scheduling and
custom-bootstrap retry behavior are retained; recovery adds no retry loop.

**Validation:** 74 native passes including 17 recovery tests, 28 diagnostics and
26 media executions (128 focused executions), loader 16 and package-resource
gate eight passed on final post-review source. Both architectures built and
passed package verification. Twenty installed cases demonstrate actual blocking,
four forced-stop boundaries, previous/bundled recovery, rejected input/schema,
storage failure, no premature success counts, bounded retention and preserved
custom URL/manual rules/site exception. One case repairs recovered prior data
and successfully updates/reloads it. Raw preference snapshots can lag the live
engine; accepted versions/origins use live diagnostics and backing-file hashes.

**Patch:** `0006-roadium-last-known-good-recovery.patch`, SHA-256
`8a878985e390b893f7987f800e9824838ae570389ef420c7cbf5046ce5738004`.
First five overlays unchanged. Full source tree:
`ea096fd60e709acd07be89f125dabb13a481585f`.

**Review and cleanup:** independent local transaction/integration/test/diagnostic
and cleanup reviews completed without blocking findings. The additional real
guard/retire/discard regression addresses a review gap. The disposable user,
protected flags, helper, ports and own local servers are removed, original user
10/network settings restored, and the own read-only emulator closed without a
snapshot save. No other profile files or vehicle properties were modified.

Milestone 1's automated/x64 integration and both package architectures are
verified. Physical ARM64 Android 12 vehicle/driving checks, production upload-key
signing, literal device ENOSPC, abrupt power loss, mapped-view disk pressure and
extended connectivity/I/O stress remain release checks. Main changes are
uncommitted. Cards 06–09 remain on hold.

Acceptance: Codex verification, October 17, 2026 (Central), with advisory local
Ollama review. [Detailed policy, commands, evidence and Card 09 handoff](evidence/card05/README.md),
[verification manifest](evidence/card05/verification.json).
