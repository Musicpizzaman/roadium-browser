# Card 07 — Add protection levels and filter categories

Priority: **P1** · Effort: **Medium** · Milestone: **User customization**
Status: **Implemented and locally verified October 18, 2026 — physical vehicle,
production signing and extended soak remain release gates**

Final record: [Card 07 evidence](evidence/card07/README.md) and
[verification](evidence/card07/verification.json).

Owner: Codex  Reviewer: independent local Ollama reviews  Issue: not created
Branch: develop (uncommitted)  Patch: `0008-roadium-protection-presets.patch`
Start/verification: October 18, 2026  Target: local implementation complete

## Outcome

Users choose Standard, Balanced, Strict or Custom using existing subscription
settings. They can control eligible categories, add compatible custom lists
and manual rules, and restore managed defaults without losing saved custom
data, per-site exceptions or unrelated browser settings.

## Prerequisites

**Required card dependencies:** [Card 01](01-audit-and-diagnostics.md) and
[Card 03](03-advanced-filtering-defaults.md).

- [x] [PRE-01](README.md#pre-01--safe-patch-series-integration) and
  [PRE-02](README.md#pre-02--reproducible-verification-environment).
- [x] Exact supported subscription inventory and existing subscribe/unsubscribe,
  custom list/manual rule and preference persistence APIs documented.
- [x] [PRE-03](README.md#pre-03--filter-provenance-and-distribution-records) for
  any list added to the eligible catalog: syntax, provenance and attribution.
- [x] Define category membership and overlaps before implementing labels.
  Verify tracking/cookie/notification lists exist and are compatible; do not
  promise a category without an actual supported subscription.

**Supporting:** Cards 02/04/05 make list installation robust and are a release
integration gate for a preset claiming reliable protection. This card may
develop its selection model earlier using deterministic subscription fixtures.

## Source spots

Chromium source, under
`chrome/browser/adblock/android/java/src/org/chromium/chrome/browser/adblock/settings/`:

- `AdblockSettingsFragment.java`
- `AdblockFilterListsFragment.java` and `AdblockFilterListsAdapter.java`
- `AdblockCustomFilterListsFragment.java`
- `AdblockCustomFiltersFragment.java`
- Existing preference resources under `chrome/browser/adblock/android/java/res/`.
- `components/adblock/android/java/src/org/chromium/components/adblock/AdblockController.java`
- `components/adblock/core/subscription/subscription_config.cc` and existing
  selection/configuration persistence.

Fork: separate preset/settings overlay, catalog/selection tests and user help.

## Implemented preset contract

| Preset | Managed list intent | User-facing expectation |
| --- | --- | --- |
| Standard | Basic advertising; minimal extra categories | Lighter additional filtering |
| Balanced, new-profile default | Ads, trusted anti-circumvention and compatible tracking protection | Recommended general protection |
| Strict | Balanced plus Social and Notifications | More site breakage may require exceptions |
| Custom | Deviations within the six managed list identities | Exact active selection shown |

Advanced-scriptlet execution remains an independently visible setting governed
by Card 03. Presets never modify advanced or global enabled state. Custom is
derived from managed selection deviations; nonmanaged records are preserved.
List membership alone is not proof the data is active. Existing diagnostics
retain separate download/conversion/activation/failure reporting.

Catalog/mapping spots:

| Category | Exact canonical subscriptions | Included presets | Overlap/risks | Compatibility/provenance |
| --- | --- | --- | --- | --- |
| Advertising | `easylist.txt` | Standard/Balanced/Strict | Basic advertising | Existing catalog/bundle provenance |
| Circumvention | `abp-filters-anti-cv.txt` | Balanced/Strict | May affect site behavior | Existing trusted policy unchanged |
| Tracking/domain blocking | `badblock_lite.txt`, `badmojr-1Hosts-master-Lite-adblock.txt` | Balanced/Strict | Both required for checked category; count shows partial state | Existing Card 06 frozen inputs |
| Social annoyances | `fanboy-social.txt` | Strict | May hide social widgets | CC BY 3.0; full converter verified |
| Notifications | `fanboy-notifications.txt` | Strict | May hide notification prompts | CC BY 3.0; full converter verified |
| Cookie-banner annoyances | None eligible | Unavailable | Explanation only, no selectable control | No supported dedicated list |

All filenames above use the exact prefix `https://uazo.github.io/cromite/filters/`.
EasyPrivacy was excluded after its canonical endpoint returned 404. No privilege
is granted to the added Social/Notifications selections. Frozen inputs, notices,
full conversion counts and independent reviews are linked in the final evidence.

## Work breakdown

### A. Define selection and persistence

- [x] Map each preset to existing list identities; reuse supported engine
  selections instead of creating another filtering engine/settings store.
- [x] Define the catalog-owned set versus user-created list/rule records.
  Switching presets must not delete custom URLs or handwritten filters.
- [x] Decide whether Custom is explicitly saved, derived from deviations, or
  both. Keep label and actual selections synchronized after independent edits.
- [x] Define new-profile Balanced initialization and existing-profile migration.
  Preserve existing custom/disabled settings; do not reset upgrades to Balanced.
- [x] Define advanced-feature interaction, global blocking disabled behavior,
  overlapping category membership and absent/unavailable list handling.
- [x] Restore managed defaults with explicit scope. Preserve custom records and
  per-site exceptions; explain resulting custom/active selections truthfully.
- [x] Apply a multi-list preset consistently through existing configuration
  updates. Handle interrupted changes without deleting state or falsely showing
  all intended lists as loaded.

### B. Extend existing Android settings

- [x] Add protection selection and eligible category/list toggles to existing
  fragments; retain custom URL import, manual rule and allowed-domain paths.
- [x] Show selected, pending/failed and actively filtering states using Card 01.
  Explain overlapping categories and Strict breakage implications simply.
- [x] Provide large accessible targets, focus order, labels and meaningful
  summaries in both existing Roadium palettes; avoid dense controls.
  Physical vehicle touch/focus remains a release gate.
- [x] Preserve independent advanced-filtering control and a clear route to
  restore managed defaults without clearing unrelated browser data.
- [x] Validate custom list input through existing supported formats/parser;
  reject unusable lists, diagnose unsupported rules and keep them untrusted.

### C. Verify side effects and compatibility

- [x] Exercise every preset transition and repeated application with custom
  data present. Ensure unsubscribe changes selection without deleting custom
  saved records needed for later re-enabling.
- [x] Verify active engine selection agrees with UI after restart and an update
  failure. Preserve old valid data only for lists still selected.
- [x] Verify no added category grants privilege based on name, provider,
  hostname or transport. Only existing exact trusted policy applies.
- [x] Verify site exceptions and global blocking preference remain independent.

## Acceptance and tests

| Scenario | Required result | Evidence spot |
| --- | --- | --- |
| Fresh profile | Balanced managed selections; independent advanced setting as specified | [Record](evidence/card07/fresh-defaults.json) |
| Upgrade with custom/disabled selections | Existing intent preserved and label truthful | [Record](evidence/card07/installed-preservation.json) |
| All preset transitions/repeated same preset | Defined selections applied consistently and persist | [Record](evidence/card07/preset-transitions.json) |
| Toggle eligible list/category independently | UI reflects actual membership and Custom/deviation policy | [Record](evidence/card07/category-controls.json) |
| Import compatible custom list/add manual rule | Works through existing engine; survives preset changes | [Record](evidence/card07/fresh-custom-import.json) |
| Invalid custom URL / untrusted source policy | UI rejects bad URL; native trust tests forbid new category privilege | [Record](evidence/card07/invalid-custom-url.json) |
| Explicit advanced opt-out followed by preset change | Opt-out preserved unless user explicitly changes it | [Record](evidence/card07/installed-preservation.json) |
| Restore defaults | Managed defaults restored; custom records/exceptions/browser data retained | [Record](evidence/card07/restore-and-restart.json) |
| Failed list install/offline transition | Pending/degraded state shown; no false active claim | [Record](evidence/card07/recovery-check.json) |
| Emulator light/dark/labels and ordering | Passed locally; physical touchscreen/focus remains open | [Record](evidence/card07/theme-checks.json) |

## Deliverables and handoff

- [x] Separate preset/settings patch and selection/persistence tests.
- [x] Exact category/preset mapping with supported list provenance and risks.
- [x] Documented migration, Custom label and restore-defaults scope.
- [x] Installed settings evidence, including custom data survival.
- [x] Handoff to Card 08: global/preset/site-state model and available exception
  APIs so per-site controls reuse the same settings.

## Decisions and completion record

- Balanced is the unchanged four-list new-profile default; no upgrade migration
  resets user choices. Custom is derived, with the existing list editor as its
  entry point. Partial tracking selection is reported as a count.
- Restore managed defaults applies Balanced only to the six managed identities.
  Custom URLs, regional/legacy opt-ins, rules, exceptions, homepage, global pause
  and advanced opt-out survive. Atomic full-set validation avoids partial presets.
- All nine source-to-target transitions and repeats, direct category switches,
  individual-list edits, fresh/default and upgrade behavior, UI custom import,
  actual controlled filtering, failure/restart and exception effects passed.
- Patch SHA-256: `1802559fa9a5123f2568963d52909679f2fd4d08621981bd0861ab75b6ca8b53`.
  [Source/package identity and tests](evidence/card07/verification.json) records
  294 focused executions, 16 loader, eight resource and six integrity checks.
- Final x64/ARM64 APK/AAB packages verified; development APK certificate and
  unsigned AAB status are explicit in the manifests. No release published.
- [Evidence](evidence/card07/README.md) contains commands, reviews, screenshots,
  exact mapping/provenance, fixture limitations, cleanup and Card 08 handoff.

### Remaining release checks

- [ ] Physical Android 12 2024 Blazer EV focus/touch, layout and parked-only regression.
- [ ] Production signing/release integration and extended update/storage soak.
- [ ] Applicable open live-service gates from Card 06; Card 10 geometry/720p is separate.
