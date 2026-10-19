# Card 02 — Restore bundled, preloaded filter databases

Priority: **P0** · Effort: **Medium** · Milestone: **Reliable protection**
Status: **Implemented and verified — x64 runtime; x64/ARM64 packages**

Owner: Codex  Reviewer: Local Ollama independent review  Issue: __________
Branch/patch: develop / `0003-roadium-bundled-filters.patch`  Start: October 13, 2026  Verified: October 14, 2026

## Outcome

A fresh offline installation blocks fixture advertising using bundled native
filter data. Connectivity later permits an ordinary subscription upgrade
without resetting list selections, custom rules, site exceptions or other
browser settings. Use existing converter/resources, not another database.

## Prerequisites

**Required card dependency:** [Card 01](01-audit-and-diagnostics.md), including
first-run/upgrade audit and a way to prove loaded/active filter origin.

- [x] [PRE-01](README.md#pre-01--safe-patch-series-integration): safe separate overlay.
- [x] [PRE-02](README.md#pre-02--reproducible-verification-environment): converter,
  resource build and disposable offline/upgrade profiles.
- [x] [PRE-03](README.md#pre-03--filter-provenance-and-distribution-records): exact
  immutable inputs, licenses, notices and attribution.
- [x] Confirm converter and FlatBuffers schema compatibility with the pinned
  build. A downloaded snapshot is a candidate until conversion/runtime tests pass.

**Supporting:** Card 03 governs default advanced-filter execution. Bundle
anti-circumvention safely even when that setting is off; do not force it on here.
Card 05 later adds recovery beyond normal bootstrap behavior.

## Source spots

Chromium source:

- `components/adblock/core/resources/BUILD.gn`
- `components/adblock/core/resources/adblock_resources.grd`
- `components/adblock/core/subscription/subscription_config.cc`
- `components/adblock/core/subscription/preloaded_subscription_provider_impl.cc`
- `components/adblock/core/converter/` and existing converter build target.
- `components/adblock/core/subscription/test/` for preloaded/subscription tests.

Fork: separate bundle overlay; a pinned input/provenance manifest and notices
under `build/roadium/`; hash/resource checks under `tools/roadium/`; build
documentation. Exact input placement is a design decision, not an existing API.

## Work breakdown

### A. Freeze and validate input data

- [x] Select EasyList and ABP anti-circumvention snapshots; record input
  version, source URL/revision, bytes, SHA-256, license and attribution.
- [x] Evaluate the October 13 candidates in
  [the preparation record](../SHIELDS_PREPARATION.md). Do not silently update
  these files to moving `pages` content during a release build.
- [x] Keep original source notices and license material. Record any packaging
  transformation, including deterministic compression and its output hash.
- [x] Run the pinned native converter and record accepted/rejected rule counts.
  Confirm the output contains plausible rules and no unauthorized privileges.
- [x] Use canonical Cromite identities for converted metadata. Existing target
  URLs may refer to older ABP locations; do not bundle data under a different
  identity from the active subscription/trusted-list configuration.
- [x] Establish deterministic conversion: fixed inputs, converter/schema,
  options and compression; compare repeat outputs or explain unavoidable
  metadata variation and verify a reproducible normalized result.

### B. Restore existing build/resource wiring

- [x] Restore `make_easylist` and `make_anticv` dependencies with pinned local
  inputs. The existing target names are the integration points.
- [x] Restore `IDR_ADBLOCK_FLATBUFFER_*` entries for those two resources; record
  exact final names/IDs after checking GRIT allocation and generated headers.
- [x] Populate `GetPreloadedSubscriptionConfiguration()` for the same two
  canonical identities and resource IDs.
- [x] Verify app resource packaging retains both FlatBuffers blobs in ARM64
  and x64 builds; make missing resources a build/verification failure.
- [x] Keep `exceptionrules.fb` unbundled and Acceptable Ads exceptions disabled.
- [x] Make a bad hash or missing pinned input fail before compilation/release;
  never recover by downloading an unpinned replacement during the build.

### C. Verify selection, upgrade and offline behavior

- [x] Trace how bootstrap data becomes active on a fresh profile; test actual
  blocking with connectivity disabled before first launch.
- [x] Preserve existing subscription data and settings on upgrade. Do not
  overwrite a newer working downloaded list with older bundled data.
- [x] Confirm ordinary updates replace bootstrap data only after acceptance;
  failed updates leave bootstrap/previous valid data operational.
- [x] Preserve an explicitly unsubscribed/disabled list choice. Record how
  recovery/bootstrap differs from user subscription selection.
- [x] Apply trusted-list and advanced-feature policy to bundled snippets just
  as to downloaded snippets; inclusion in the APK must not grant blanket trust.
- [x] Surface bundled version/origin and subsequent update results through
  Card 01 diagnostics.

## Acceptance and tests

| Scenario | Required result | Evidence spot |
| --- | --- | --- |
| Fresh install with networking unavailable | Bundled EasyList loads and blocks controlled test advertising | [Fresh settings/report and actual probe](evidence/card02/README.md#installed-acceptance) |
| Advanced filtering off | Basic blocking works; both bundles contain only nonprivileged conversion output | [Conversion counts and offline control](evidence/card02/README.md) |
| Return online with newer valid list | Installed online activation preserves settings; controlled native higher-version conversion waits for storage acceptance | [Online evidence and native higher-version test](evidence/card02/README.md) |
| Upgrade with newer downloaded data | Controlled native newer data retained; existing emulator data/settings also preserved | [Native and installed upgrade evidence](evidence/card02/README.md) |
| Upgrade with explicit list opt-out | User choice preserved through restart; no automatic bundle activation | [Opt-out settings and probe](evidence/card02/README.md#installed-acceptance) |
| Missing/wrong-hash source or missing resource | Build/package gates reject missing and changed data | [9 input and 8 package tests](evidence/card02/README.md#automated-verification) |
| Repeat conversion of frozen inputs | FlatBuffers and statistics JSON identical | [Repeat results](evidence/card02/repeat-conversion.json) |
| Corrupt bundled data fixture | Invalid bytes/wrong canonical identity rejected | [22 native tests](evidence/card02/native-results.json) |
| Packaging inspection | Both intended resources, manifest and notices included; exceptionrules absent | [x64](evidence/card02/x64-build-manifest.json), [ARM64](evidence/card02/arm64-build-manifest.json) |

Automated converter/resource/provider tests accompany installed offline and
upgrade checks. Card 05 owns recovery when downloaded storage is also invalid.

## Deliverables and handoff

- [x] Separate preloaded-resource patch, focused tests and deliberate manifest
  checksum update.
- [x] Frozen inputs/provenance manifest, deterministic conversion recipe,
  licenses and attribution distribution record.
- [x] Resource mapping and offline/upgrade evidence for the exact artifact.
- [x] Handoff to Card 05: bootstrap lookup behavior, schema/version and rule
  validity checks, and explicit user selection semantics.

## Decisions, blockers and completion spots

Input storage/compression: frozen local gzip, level 9/mtime 0; LF license/manifest text.
Immutable revision/hashes: [input manifest](../../build/roadium/filters/manifest.json),
Cromite pages `338336d9e640489c648d47d606cb0030064c4e0f`.

Exact resource IDs in verified builds: EasyList 39740, AntiCV 39741,
manifest 39742, notices 39743. Converter options: nonprivileged for both;
schema identity is the pinned generated-header SHA-256 via `CurrentSchemaVersion()`.
First run retains five existing default selections; two have bootstrap resources.
Reproducibility: [repeat conversion](evidence/card02/repeat-conversion.json).

Patch SHA-256: `eb4f85d293ea50d4e69cb25f633f86d1539a8caae71752d44ebbdc3662513df4`.
Full source diff: `a62d66be6d65a766d0adabc6c18b440d245f429a5b679aedd5f747e0aacedaa8`.
Build/source identity, test commands/results, offline/upgrade evidence, attribution
and local review: [complete verification record](evidence/card02/README.md).
Codex verified October 14, 2026; independent local review results are retained there.

Card 05 handoff: bundles are selected-list fallback data only. Working installed
data always takes precedence, independent of its version; bootstrap is not written
as a downloaded subscription. Exact canonical identity and schema are checked.
Selection refresh handles a bundle left after terminal failure, so explicit opt-out
removes it even with no disk/pending entry. Corrupt downloaded-storage recovery
remains separate. Card 03 must establish safe live privileged execution before
changing bundle conversion privileges or the advanced-filter default.

Remaining limits: ARM64 vehicle runtime and production signing are release gates.
The live upstream version matched the bundle during testing; higher-version
replacement/retention used a controlled native fixture, separately from installed
online activation. No advanced scriptlet or YouTube effectiveness result is claimed.
