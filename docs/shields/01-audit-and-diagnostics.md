# Card 01 — Audit the existing AdBlock system and expose diagnostics

Priority: **P0** · Effort: **Small–medium** · Milestone: **Reliable protection**
Status: **In progress — source audit and diagnostics implementation**

Owner: Codex  Reviewer: Local Ollama independent review  Issue: __________
Branch/patch: `develop` / separate Card 01 overlay  Start: October 13, 2026  Target: Card 01 implementation verified October 13, 2026

## Outcome

An installed Roadium build clearly shows whether EasyList and the trusted
anti-circumvention list are operating and why an update failed. Diagnostics
must distinguish downloaded bytes, accepted filter data and active filtering,
without an external analytics service or browsing-history collection.

## Prerequisites

**Required card dependencies:** None. This is the starting card.

- [x] Access to pinned source and existing settings/bridge APIs; see
  [PRE-02](README.md#pre-02--reproducible-verification-environment).
- [x] Fresh and upgraded disposable profile fixtures, including an explicit
  advanced-filtering opt-out, a site exception and a custom list/manual rule.
- [x] Safe overlay integration under [PRE-01](README.md#pre-01--safe-patch-series-integration)
  before applying the diagnostic implementation.

**Supporting:** PRE-01 can proceed alongside the audit. Cards 02–05 will add
new diagnostic fields/results; agree their contracts here so they reuse the UI.

## Source spots

Chromium source:

- `chrome/browser/adblock/android/java/src/org/chromium/chrome/browser/adblock/settings/AdblockSettingsFragment.java`
- `chrome/browser/adblock/android/java/src/org/chromium/chrome/browser/adblock/settings/AdblockFilterListsAdapter.java`
- `chrome/browser/adblock/android/java/res/layout/adblock_filter_lists_list_item.xml`
- `chrome/browser/adblock/android/java/res/xml/eyeo_adblock_preferences.xml`
- `components/adblock/android/java/src/org/chromium/components/adblock/AdblockController.java`
- `components/adblock/android/adblock_controller_jni.cc`
- `components/adblock/core/subscription/subscription_service_impl.cc`
- `components/adblock/core/subscription/subscription_persistent_metadata_impl.cc`
- `components/adblock/core/subscription/installed_subscription.h`
- `components/adblock/core/converter/` for local conversion rejection accounting.

Fork: `build/roadium/patches/0002-roadium-shields-diagnostics.patch`,
focused tests and audit/evidence records under `tools/roadium/` and `docs/`.
PRE-01 is implemented and its 16 loader tests pass.

## Work breakdown

### A. Establish observed behavior

- [x] Inventory subscriptions on fresh and upgraded profiles: canonical URL,
  enabled selection, installed state/version, resource origin and privilege.
- [x] Trace first-run/recommended installation separately from routine updates
  of already subscribed lists. A disabled installer does not prove a disabled
  updater.
- [x] Record advanced-filtering preference value and whether it is defaulted
  or explicitly stored. Record how anti-circumvention follows that choice.
- [x] Trace download → conversion → validation → storage → collection activation.
  Identify the actual success/failure notification at each boundary.
- [x] Inventory current Java fields, JNI exports and observer callbacks before
  introducing any new API. Existing counters and descriptions may suffice for
  parts of the display; establish what they actually measure.

Audit table spot:

| Profile | List identity | Selected | Installed version/source | Parsed | Active | Advanced setting | Observed failure |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Fresh offline | Five defaults; see audit | Yes | None | No | No | Default false | No network; manual deadline |
| Upgrade | Five defaults; see audit | Yes | EasyList/antiCV 202610010932 | Historical state unknown | Stored data retained | Unset/default false | Offline audit; versions preserved |
| Explicit opt-out | Five defaults; see audit | Yes | EasyList/antiCV 202610130952 after online check | Yes | Loaded | Explicit false retained | Failed later check retained active data |

### B. Define local diagnostic data

- [x] Display canonical URL, selection/state, installed version, installation
  time, last successful update, and latest download/parse/storage error.
- [x] Define timestamp semantics. Installation time is not automatically last
  successful update time; missing history displays as unknown/never.
- [x] Show global ad blocking, advanced-filtering choice, and whether trusted
  anti-circumvention is loaded and eligible to execute supported scriptlets.
- [x] Show last attempted transport/source separately from active data origin.
  Card 04 supplies fallback details; a failed fallback must not appear active.
- [x] Define stable error categories for transport, HTTP, invalid input,
  conversion, validation, storage and cancellation. Include useful local
  details without dumping full downloaded rules or request URLs from browsing.
- [x] Define bounded rejected-rule counts/reason categories during conversion,
  including unsupported syntax and prohibited privileged rules. Count each
  rejected rule consistently; retain no visited-page data.
- [x] Avoid claiming that a selected or downloaded list is operational before
  engine activation. Allow active old data plus failed new update to coexist.

### C. Implement settings and update results

- [x] Extend existing list rows/detail UI and settings summaries; use readable
  labels, accessible controls and suitable targets for a car touchscreen.
- [x] Connect Check for updates now to real completion results. Show in-progress
  state, then per-list outcomes and an aggregate result for that request.
- [x] Handle concurrent automatic/manual updates, repeated taps, mixed list
  outcomes, cancellation and leaving/reopening the fragment without stale UI.
- [x] Track a request/batch identity or equivalent completion contract; changes
  in lifetime counters alone cannot prove the tapped update has completed.
- [x] Manage observers using the fragment/controller lifecycle; no callbacks
  to destroyed views or duplicate registration after configuration changes.
- [x] Keep diagnostic storage bounded and local. Any future export is explicit
  and reviewed; this card does not upload a report.

## Acceptance and tests

| Scenario | Required result | Evidence spot |
| --- | --- | --- |
| Fresh and upgraded profiles | Actual EasyList/anti-circumvention state and settings are visible | Audit, fresh-report.png, online-completed.png; upgrade JSON records |
| Successful manual update | Completion reports the accepted/activated version, not just a toast | online-completed.png and online-conversion-diagnostics.json |
| Transport/HTTP failure | Useful failure category; old working filters still shown as active | failed-update-report.png and failed-update-diagnostics.json; native HTTP failure test |
| Downloaded invalid or rejected data | Download, parse and activation outcomes remain distinct | Native converter, storage and activation tests; Android state tests |
| Mixed success/failure batch | Per-list outcomes and truthful aggregate result | Native batch aggregation test; Android per-list snapshot test |
| No eligible lists/repeated taps/cancellation | Finite truthful result; no perpetual checking state | Native empty/repeated-tap/cancellation/timeout tests; installed fresh timeout |
| Unsupported/untrusted snippet fixture | Rejected count/reason visible locally; snippet never executes | Native unsupported compound/untrusted privilege tests; installed antiCV rejection counts |
| Leave/reopen settings while updating | No crash, leak, duplicate callback or stale completion | Lifecycle-scoped polling verified in source; pause/reopen/global-off installed check; finite native batch contract |
| Privacy inspection | No analytics dependency or transmission of browsing data | Native privacy/bounds test, Android inline-source test and source review; no analytics added |

Use deterministic conversion/network fixtures for automated checks and an
installed build for visible status. Normal browsing is not evidence that a
specific subscription is active; include a rule-specific fixture.

## Deliverables and handoff

- [x] Baseline audit with fresh/upgrade observations and identified deficiencies.
- [x] Reviewed diagnostic patch plus native/JNI/Android tests as applicable.
- [x] Documented diagnostic schema/error semantics and update completion contract.
- [x] Installed-build screenshots and rule-specific operational evidence.
- [x] Handoff to Cards 02–05: resource/source state, preference provenance,
  fallback source, validation/storage errors and recovery fields to populate.

## Decisions, blockers and completion spots

Diagnostic retention: one latest attempt plus one last successful activation per list; bounded errors (160 bytes) and transport strings (2048 bytes). No rule bodies or browsing request history.
Batch completion: maintainer storage/collection activation, failure/cancellation, or 45-second result deadline. Existing retries continue; completed results are immutable per-list snapshots.
Rejected-rule accounting: immutable converter sidecar; counts persisted only after conversion/storage as appropriate; no FlatBuffers schema change.
Patch SHA-256: `9a4a39651200f465f52ffa1e3d0ccade4a035a07fc0a97cd0f0b5745535eff58`.
Build/source identity, commands, independent review and screenshots: [audit](CARD01_AUDIT.md) and [evidence index](evidence/card01/README.md).
Acceptance: Codex source/test review and installed x64 emulator checks, October 13, 2026. Human acceptance remains available.
Remaining release gates: ARM64 packaging and parked physical-car checks; audible WebAudio/speech and live YouTube effectiveness are unverified. Cards 02–09 remain on hold.
