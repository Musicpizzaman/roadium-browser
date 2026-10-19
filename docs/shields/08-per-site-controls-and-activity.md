# Card 08 â€” Add per-site controls and a filter activity panel

Priority: **P1** Â· Effort: **Mediumâ€“high** Â· Milestone: **User customization**
Status: **Planned â€” implementation on hold**

Owner: Codex  Reviewer: independent local Ollama reviews  Issue: not created
Branch: develop (uncommitted)  Patch: `0009-roadium-site-controls.patch`
Start/local verification: October 18, 2026  Target: local implementation complete

## Outcome

Users open Shields from the existing address-bar/site-information surface,
inspect current-site protection, disable it persistently or temporarily, reload
and restore it without changing protection for unrelated sites. Activity stays
local and reports only counters/attribution actually available from the engine.

## Prerequisites

**Required card dependencies:** [Card 01](01-audit-and-diagnostics.md) and
[Card 07](07-protection-levels-and-categories.md).

- [x] [PRE-01](README.md#pre-01--safe-patch-series-integration) and
  [PRE-02](README.md#pre-02--reproducible-verification-environment).
- [x] Verify current allowed-domain scope, matching/normalization and engine
  application across frames/navigation before defining a UI site key.
- [x] Identify an existing safe address-bar/site-information integration spot
  and the current tab/WebContents lifetime APIs in the pinned Chromium revision.
- [x] Audit existing counters, request classification observers and attribution
  fields. Missing rule attribution is a limitation to expose, not fabricate.
- [x] Choose temporary exception lifetime and an engine-supported overlay
  mechanism that does not rewrite permanent exceptions.

**Supporting:** Cards 04/05 supply reliable source/recovery state. Independent
per-site cosmetic or advanced controls are conditional on verified existing
engine support and are not required if they would need a broad rewrite.

## Source spots

Chromium source:

- `AdblockAllowedDomainsFragment.java` under
  `chrome/browser/adblock/android/java/src/org/chromium/chrome/browser/adblock/settings/`.
- `components/adblock/android/java/src/org/chromium/components/adblock/AdblockController.java`
- `components/adblock/android/java/src/org/chromium/components/adblock/FilteringConfiguration.java`
- `components/adblock/android/java/src/org/chromium/components/adblock/ResourceFilteringCounters.java`
- `components/adblock/android/java/src/org/chromium/components/adblock/ResourceClassificationNotifier.java`
- `components/adblock/content/browser/` and existing browser tests.
- Existing Chromium site-information/address-bar Java and native entry points;
  confirm exact files during the integration audit rather than inventing a fork.

Fork: separate per-site/activity overlay, navigation/lifetime/privacy tests,
controlled broken-site fixtures and user help.

## Work breakdown

### A. Define current-site and exception semantics

- [x] Match engine normalization for host/site scope, subdomains, international
  domains and navigation; explain the actual scope to users.
- [x] Define precedence among global blocking, selected preset/lists, permanent
  allowed domain and temporary exception. Global-off must remain apparent;
  Restore on this site cannot falsely imply global protection is on.
- [x] Implement persistent Disable on this site using existing allowed domains,
  with reload behavior and a route to inspect/remove the saved exception.
- [x] Choose temporary lifetime explicitly: current tab/navigation/session or
  another bounded supported scope. State it in the control's label/help.
- [x] Keep temporary exceptions separately owned and nonpersistent. Do not add
  a permanent domain and later remove it, which could erase a user's exception.
- [x] Define Restore protection precisely, including a permanent and temporary
  exception present together. Remove only the selected exception(s) with clear
  scope; preserve other sites and custom rules.
- [x] Define behavior for unsupported internal/file pages, incognito, tab switch,
  cross-site redirects and browser restart.

Behavior/ownership spots:

| Action/state | Scope and lifetime | Storage/owner | Reload/result |
| --- | --- | --- | --- |
| Disable on this site | Canonical host and subdomains, both HTTP(S) schemes and all ports | Existing permanent allowed domains | Reload current tab; other tabs apply on reload |
| Disable temporarily | Original-profile browser session, including regular and Incognito tabs | Separate in-memory configuration vector; never prefs | Reload current tab; expires on browser restart |
| Restore protection | Remove one explicitly displayed covering domain and subdomain scope | Saved and temporary records have separate removal controls | Reload; other ownership/global pause remains authoritative |
| Global blocking off | Global state remains authoritative | Existing global pref | Site restore never enables global or advanced filtering |

### B. Implement the Shields panel

- [x] Add a Shields entry to an existing site-info/address-bar menu and keep
  Android Automotive activity/input restrictions intact.
- [x] Show effective current-site protection, the reason it is off, selected
  protection level and real operational/degraded state from Card 01.
- [x] Offer persistent disable, temporary disable and restore with readable
  targets and a clear reload action/result.
- [x] Connect to existing allowed-domains settings so site controls and settings
  stay synchronized across observers, tabs and restarts.
- [x] Show blocked request count from existing counters; define per-navigation
  versus tab lifetime, reset rules and whether cosmetic actions are counted.
- [x] Show matching list/rule only when actually available and accurate. Indicate
  unknown attribution honestly; never infer a rule from the subscription title.
- [x] Add a useful troubleshooting route: disable/reload/restore, inspect local
  diagnostics and reach existing help/report information. No automatic upload
  or external report submission is part of this card.

### C. Preserve local privacy and lifecycle behavior

- [x] Keep activity ephemeral/local and bounded. Avoid a stored browsing-history
  log; report any existing data lifetime accurately.
- [x] If a later explicit export/report is designed, define redaction/preview
  separately. This panel does not transmit visited URLs or matching requests.
- [x] Detach observers on tab/view destruction and ignore stale callbacks for
  previously selected tabs or navigations.
- [x] Verify temporary exceptions expire as defined, never persist after the
  chosen boundary and never remove a concurrent permanent user choice.
- [x] Add separate cosmetic/advanced site toggles only if the engine can scope
  them correctly without a broad rewrite; otherwise document the capability
  limit and deliver the required whole-site controls.

## Acceptance and tests

| Scenario | Required result | Evidence spot |
| --- | --- | --- |
| Protected fixture breaks due to filtering | Disable on site and reload fixes fixture; unrelated site stays protected | [Record](evidence/card08/session-controls.json) |
| Restore that site | Same rule-specific fixture is filtered again | [Record](evidence/card08/saved-restored.json) |
| Permanent exception after restart | Persists and settings/panel agree | [Record](evidence/card08/persistence-and-ownership.json) |
| Temporary exception lifetime boundary | Expires as documented; no permanent preference written | [Record](evidence/card08/persistence-and-ownership.json) |
| Temporary plus concurrent permanent exception | Expiry does not remove user's permanent choice | [Record](evidence/card08/persistence-and-ownership.json) |
| Global-off/preset change | Effective state and restore behavior remain truthful | [Record](evidence/card08/global-and-preset-state.json) |
| Subdomain/IDN/redirect/tab/incognito cases | Matches documented engine scope; no exception leakage | [Record](evidence/card08/idn-and-redirects.json) |
| Navigation and tab switching | Correct counters/state; stale callbacks discarded | [Record](evidence/card08/activity-and-lifecycle.json) |
| Rule/list attribution unavailable | Count can be shown; attribution explicitly unavailable | [Record](evidence/card08/activity-and-lifecycle.json) |
| Panel/privacy/Automotive checks | No history transmission; local lifetime bounded; safety unchanged | [Record](evidence/card08/private-shared-scope.json) |

## Deliverables and handoff

- [x] Separate per-site/activity patch and state/lifecycle/exception tests.
- [x] Exact site scope, precedence, transient lifetime and counter semantics.
- [x] Installed broken-site disable/reload/restore evidence plus unrelated-site
  protection and restart/expiry evidence.
- [x] Handoff to Card 09: deterministic fixtures, temporary exception boundary,
  available attribution limits and privacy checks.

## Decisions and completion record

- Entry: existing PageInfo `createAdditionalRowViews` in
  `ChromePageInfoControllerDelegate.java`, with `ShieldsPageInfoController.java`.
  HTTP(S) DNS/IPv4 hosts only; internal/file/IPv6 pages have no new controls.
- Engine scope: exact host plus its subdomains, across schemes/ports, without
  automatic registrable-domain widening. Canonical ASCII/punycode entries match
  the engine. Legacy raw Unicode records remain saved but are not falsely
  reported as working exceptions; the pinned parser rejects their domain options.
- Temporary lifetime: native configuration/browser-process lifetime. The
  `temporary_allowed_domains_` vector is separate from persisted dictionary data.
  Duplicates/missing removals are no-ops and never change permanent ownership.
- Private scope: the existing browser client routes filtering to the original
  profile, so exceptions also affect Incognito tabs after reload. Controls are
  offered only in regular PageInfo. Help states shared scope and reload/lifetime
  boundaries. No new private-mode engine or settings store was introduced.
- Precedence: global pause, covering saved exception, covering session exception,
  then filtering enabled with readiness/coverage limits. Removing one entry
  leaves other covering entries, unrelated settings and advanced opt-out intact.
- Activity: real frame-backed block decisions in `content::Page`, including
  embedded frames; saturating integer and dispatch-time `WeakDocumentPtr`.
  New documents/reload reset; same-document/cached pages retain. No request/rule
  history, popup/cosmetic count, detached-worker attribution or automatic upload.
  Refresh reads a snapshot; matching rule/list details are not retained.
- Reviews, source/package identities, actual engine fixtures and 311 focused
  executions are recorded in the evidence, plus 16 loader/eight resource checks.
  Installed checks cover restart/expiry, both concurrent-removal orders, global
  pause/presets, IDN/subdomain/redirect/private scope, actual counters/lifecycle,
  light/dark and the legacy Unicode regression.
- Overlay SHA-256: `c22996e7566fc8e188d5b3f79aead1bae57b238c8d4120a66e296d1d13e8ece2`.
  First eight overlays unchanged. x64/ARM64 APK/AAB builds are development
  artifacts; no production signing or publication was performed.
- Handoff: [Card 09](09-regression-and-release-gates.md) should integrate these
  fixtures, exact lifetimes, current-tab ownership and shared private-mode scope.

### Remaining release checks

- [ ] Physical Android 12 2024 Blazer EV focus/touch/rotary, layout and parked-only regression.
- [ ] Production signing/release integration and extended update/storage soak.
- [ ] Applicable existing Card 06 live-service gates; Card 10 geometry/720p remains separate.

## Card 07 implementation handoff â€” October 18, 2026

[Card 07 evidence](evidence/card07/README.md) and its eighth overlay provide
`ShieldsPresets`, derived managed-set selection, atomic selected-list controller
wrappers, and independent global/advanced controls. Existing allowed-domain
exceptions were verified against controlled filtering and survived reset/restart.
Reuse these APIs and diagnostics; do not create a separate filtering store.
Current-tab lifecycle, site normalization/frame matching, temporary disable scope
and available activity counters/attribution still require this card's audit.
Card 08 uses a memory-only original-profile session exception alongside existing
saved allowed domains. Original-profile routing shares filtering state with
Incognito; controls are offered in regular PageInfo and that scope is explicit.
