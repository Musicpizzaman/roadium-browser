# Card 03 — Enable advanced filtering by default

Priority: **P0** · Effort: **Small–medium** · Milestone: **Reliable protection**
Status: **Implemented and verified — x64 Automotive; x64/ARM64 packages verified**

Owner: Codex  Reviewer: Local Ollama independent review  Issue: local task (no external issue assigned)
Branch/patch: develop / separate overlay per card  Start: October 13, 2026  Completed verification: October 14, 2026

## Outcome

New profiles start with trusted advanced filtering enabled. Existing profiles
receive the new default where they inherited the old default; explicit user
opt-outs remain disabled. Custom/untrusted lists cannot execute privileged
snippets, and the existing supported-scriptlet allowlist remains enforced.

## Prerequisites

**Required card dependency:** [Card 01](01-audit-and-diagnostics.md), including
preference provenance, list lifecycle audit and diagnostic status fields.

- [x] [PRE-01](README.md#pre-01--safe-patch-series-integration) and applicable
  [PRE-02](README.md#pre-02--reproducible-verification-environment) test fixtures.
- [x] Determine whether the old code stored `false` automatically, only on user
  action, or both. Default value and explicit opt-out must be distinguished.
- [x] Confirm the exact trusted anti-circumvention identity and all entry paths
  to privileged conversion/execution in this source revision.

**Supporting:** Card 02 supplies offline trusted-list data. This card must
also define behavior before first download and with connectivity unavailable.
Cards 04/05 must preserve the policy during fallback and recovery.

## Source spots

Chromium source:

- `components/adblock/core/common/adblock_prefs.cc` and associated declarations.
- `components/adblock/core/subscription/subscription_service_impl.cc`
- `components/adblock/core/subscription/subscription_persistent_metadata_impl.cc`
- `components/adblock/core/subscription/subscription_config.cc`
- `components/adblock/core/subscription/filtering_configuration_maintainer_impl.cc`
- Existing advanced-filter preference in `AdblockSettingsFragment.java` and
  `eyeo_adblock_preferences.xml` under `chrome/browser/adblock/android/`.
- `components/adblock/core/converter/serializer/flatbuffer_serializer.cc`
  for preserving the existing command allowlist.

Fork: a separate default/migration overlay, profile/trust tests and migration
documentation. Identify the existing migration facility before adding one.

## Work breakdown

### A. Specify migration semantics

- [x] Change the registered `kAllowPrivilegedFilters` default to `true` for new
  profiles, after confirming registration and all consumers.
- [x] Verify how unset/default preferences behave in existing profiles. If
  changing the registered default satisfies migration, avoid redundant writes.
- [x] Preserve explicit stored `false`, explicit stored `true` and later user
  changes across restart, repeated migration and upgrades.
- [x] If old automatic writes obscure intent, document the ambiguity and use
  reliable provenance or a conservative preservation rule. Do not relabel all
  stored `false` values as inherited defaults and overwrite them.
- [x] If a migration marker is necessary, define scope, ordering and rerun
  behavior. Record why it cannot reset settings or run twice with new effects.
- [x] Keep ordinary ad blocking independent; enabling advanced filtering must
  not silently re-enable a user's globally disabled blocker.

Migration test matrix spot:

| Profile state | Expected advanced setting | Migration mechanism/evidence |
| --- | --- | --- |
| New/unset | Enabled | No stored override; registered default true; fresh offline report |
| Upgrade, inherited default | Enabled | No stored override before/after; effective enabled |
| Upgrade, explicit false | Disabled | Stored false preserved; installed upgrade and native tests |
| Upgrade, explicit true | Enabled | Stored true preserved, including global-off upgrade |
| Ambiguous historical false | Preserve choice; resolve/document provenance limitation | Preserve every stored false; no reliable intent is inferred |
| User changes after migration | Latest user choice retained | UI off/on, persisted opt-out, no migration marker or writes |

### B. Synchronize list and conversion lifecycle

- [x] Audit existing enable/disable behavior before adding work already done
  by the service or configuration maintainer.
- [x] Ensure the canonical trusted anti-circumvention list is installed and
  processed when advanced filtering is enabled, consistent with supported
  independent list selections.
- [x] Identify which stored lists were converted with different privilege
  settings. Invalidate/reconvert or schedule a bounded re-download only where
  accepted rules need to change; avoid destroying currently working basic data.
- [x] Define offline enable behavior: trusted valid bundled/cached data can be
  used if policy permits; otherwise show pending data without claiming success.
- [x] On disable, remove privileged execution promptly, including already
  installed/cached data. A new preference value alone must not leave stale
  scriptlets running on newly processed documents.
- [x] Handle repeated toggles, in-flight conversions and cancellation so a
  result obtained under old settings cannot bypass the current setting.
- [x] Preserve custom lists, manual rules, site exceptions and unrelated prefs.

### C. Preserve trust and user control

- [x] Keep the accessible independent advanced-filtering switch and explain
  its trusted-scriptlet scope in existing settings.
- [x] Preserve the existing scriptlet command allowlist. This card does not
  add arbitrary JavaScript, new scriptlet commands or trust based on transport.
- [x] Apply identical privilege checks to text conversion, FlatBuffers load,
  preloaded data, custom subscriptions and local/manual filter input paths.
- [x] Show effective setting and anti-circumvention readiness using Card 01.

## Acceptance and tests

| Scenario | Required result | Evidence spot |
| --- | --- | --- |
| New/default-unset profile | Advanced filtering enabled; trusted list lifecycle starts correctly | [Fresh offline report](evidence/card03/fresh-offline-report.txt) |
| Explicit false upgrade | Remains disabled; no privileged execution | [Upgrade report](evidence/card03/upgrade-explicit-false-report.txt); native policy tests |
| Explicit true and repeated upgrade | Retained; migration is idempotent | [Upgrade comparison](evidence/card03/verification.json); default never writes a value |
| Global blocker disabled | Preference migration does not re-enable global blocking | [Upgrade report](evidence/card03/upgrade-explicit-true-global-off-report.txt), [runtime](evidence/card03/trusted-global-off.json) |
| Enable after previous nonprivileged conversion | Relevant trusted rules become available through safe refresh | Native scheduler/conversion tests; installed old cache reports pending, [report](evidence/card03/upgrade-inherited-report.txt) |
| Disable during conversion/update | Old callback cannot activate prohibited privileges | Native stale-conversion, storage race and reentrant-refresh tests |
| Offline enable | Valid permitted data works or pending status is truthful | [Fresh bundles](evidence/card03/fresh-offline-report.txt), [supported effect](evidence/card03/trusted-enabled.json) |
| Custom list copies a privileged snippet | Snippet rejected; ordinary supported rules still behave as intended | Native unknown/manual cache tests; [installed manual rules](evidence/card03/manual-rules.json) |
| Raw/alternate URL masquerades as trusted identity | No trust gained from URL similarity/transport | [Installed untrusted privileged cache](evidence/card03/untrusted-cached.json) |
| Unsupported command on trusted list | Allowlist still rejects it | [Conversion rejection](evidence/card03/trusted-fixture-conversion.json); installed click count zero |

Use real supported snippet fixtures with observable effects, not only checks
that a boolean changed. New and upgraded installed-build evidence supplements
automated profile/lifecycle tests.

## Deliverables and handoff

- [x] Separate default/migration patch with focused tests and evidence.
- [x] Recorded historical preference audit and migration decision.
- [x] Defined enable/disable refresh and stale-result handling contract.
- [x] Handoff to Cards 04–07: canonical trusted identity, current-policy checks,
  diagnostic readiness states and handling of explicit opt-outs.

## Decisions and completion record

**Preference provenance:** the production setter is the only audited writer;
registration now defaults to true. Unset preferences inherit it; every stored
false/true remains intact. No marker or preference rewrite is needed. An
ambiguous stored false is conservatively preserved.

**Refresh contract:** preserve working basic data and independent selections;
refresh only selected trusted data whose active conversion policy needs to
change. The current-policy gate closes immediately, including existing
snapshots. Stale conversions are discarded and one refresh can wait for active
download/storage work. Offline bundled privileged AntiCV is eligible; old basic
cache truthfully awaits refresh. Header filters remain disabled.

**Trust:** retain both exact existing trusted URLs (canonical AntiCV and
raw/master experimental Cromite), exclude manual/custom and unknown identities,
and keep the command/argument allowlist. URL resemblance does not grant trust.
See the [full evidence and Cards 04–07 handoff](evidence/card03/README.md).

**Patch:** `0004-roadium-advanced-filtering.patch`, SHA-256
`fa0e7a57e72696158efca236c66666b52dda20449a6a4ab77c7344d2d46f2b69`.
The first three overlays are unchanged. Final source tree:
`827c5751427f01b0ac1dca82a66886bb1dbf2e29`.

**Verification:** 32 native, 24 diagnostics executions and 26 media executions
passed; loader 16 and package gate 8 passed. Both architecture builds and
artifact verification passed. The final x64 APK was installed and exercised
with real observable supported-scriptlet effects, live UI toggles, global-off
gating, untrusted-cache/manual negatives, fresh offline and upgrade profiles.
Local source, test, readiness and final UI reviews were completed; the evidence
record explains findings, accepted corrections and retests.

**Cleanup:** the task-created Android test profile was restored from validated
backups; original Preferences bytes match exactly. Network settings and test
port mappings were restored. No other user profile was root-edited.

Acceptance: Codex verification, October 14, 2026, with advisory local Ollama
review. [Machine-readable acceptance](evidence/card03/verification.json).
Physical ARM64 Android 12 vehicle checks and production upload-key signing
remain release gates. Cards 04–09 remain on hold. Changes remain uncommitted.
