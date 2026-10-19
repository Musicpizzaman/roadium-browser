# Card 06 — Modernize YouTube filtering using the existing engine

Priority: **P1** · Effort: **Medium–high** · Milestone: **Better YouTube support**
Status: **Implemented — default policy, audit and regression checks verified; live format and vehicle acceptance gates remain open**

Owner: Codex. Reviewer: independent local Gemma4 12B review (approved). Issue: local Card06 task.
Branch: develop (uncommitted). Patch: seventh overlay. Implementation/verification: October17,2026.

## Outcome

Every enabled YouTube-specific rule has a recorded compatibility result.
Maintained upstream rules take priority; permitted supported rules execute,
rejected rules are diagnosable and normal playback remains usable. Improve
supported ad handling without promising that all future YouTube ads are blocked.

## Prerequisites

**Required card dependencies:** [Card 03](03-advanced-filtering-defaults.md),
[Card 04](04-approved-github-fallback.md), and
[Card 05](05-last-known-good-recovery.md). Trust, reliable updates and recovery
must work before a live YouTube result can be attributed to rule changes.

- [x] [PRE-01](README.md#pre-01--safe-patch-series-integration) and
  [PRE-02](README.md#pre-02--reproducible-verification-environment).
- [x] Exact installed anti-circumvention and experimental versions and selection
  recorded through Card 01. Inventory installed data, not only current URLs.
- [x] Pinned parser/serializer command allowlist, arguments and snippet library
  dependency behavior available for inspection and test execution.
- [x] Baseline ordinary media/Automotive tests available; controlled local
  video/DOM/JSON fixtures and an installed-build live playback test plan ready.

**Supporting:** Rule inventory can be prepared before prerequisite acceptance.
It is not evidence that live rules execute. Confirm the experimental list's
revision/maintenance history rather than assuming a date from its filename.

## Source spots

Fork input: `tools/filters/experimental-cromite-filters.txt`, frozen installed
list inventories, compatibility report/fixtures under `tools/roadium/`.

Chromium source:

- `components/adblock/core/converter/serializer/flatbuffer_serializer.cc`
- `components/adblock/core/converter/parser/`, including snippet tokenization.
- `components/adblock/core/converter/parser/test/` and serializer tests.
- `components/adblock/content/browser/element_hider_impl.cc`
- `components/adblock/core/resources/snippets/`
- Existing adblock browser tests under `components/adblock/content/browser/test/`.

Separate rule/compatibility overlay and focused tests; library changes require
specific justification and corresponding trust/argument validation tests.

## Work breakdown

### A. Inventory all relevant rules

- [x] Freeze versions/hashes for anti-circumvention, experimental and any other
  enabled YouTube rules. Record domain applicability, source line and rule text
  or stable local identifier without recording personal browsing activity.
- [x] Classify each rule as network, cosmetic or scriptlet; identify compound
  sequences, dependencies, frames/world and targeted YouTube surface.
- [x] Check `skip-video`, `json-prune`, `override-property-read` and every other
  command present against this build's parser, arguments and runtime library.
- [x] Record both syntax support and actual trust/advanced-setting eligibility.
  A supported command on an untrusted list is still prohibited.
- [x] Classify outcome: supported/accepted, unsupported, rejected by policy or
  parsing, or superseded. Superseded requires a named maintained replacement,
  not simply a guess that a newer list contains similar code.

Compatibility report spots:

| Rule ID/source version | Domains/surface | Commands and arguments | Parser/policy result | Runtime evidence | Replacement/decision |
| --- | --- | --- | --- | --- | --- |
| Five frozen sources /145 stable source-line IDs | Exact domain options and generated calls in the inventory | Full command/argument text retained | 137 accepted,8 unsupported | Native calls plus scoped installed fixtures | Maintained defaults; named duplicate replacements; no unsafe rewrite |

### B. Resolve outdated rules conservatively

- [x] Prioritize maintained compatible upstream rules and avoid duplicate
  experimental behavior that fights the same playback/JSON state.
- [x] Investigate compound rules containing `simulate-mouse-event`, which the
  pinned serializer marks unsupported. Determine whether the entire rule is
  rejected and what its original ordering/control semantics require.
- [x] Split or rewrite only when the remaining supported behavior is separately
  correct and tested. Do not automatically strip unknown commands or preserve
  control tokens whose partner operations no longer exist.
- [x] Leave unsupported commands rejected unless a narrowly scoped implementation
  and security/compatibility justification is reviewed. Such added support
  must not enable arbitrary JavaScript or broaden trusted identities.
- [x] Avoid whole-media-domain blocking, including blanket `googlevideo.com`
  blocks that would break legitimate streams.
- [x] Make rejected/superseded results visible in the local compatibility report
  and appropriate Card 01 diagnostics.

### C. Verify real execution and playback

- [x] Use deterministic local fixtures to exercise expected DOM/JSON/property
  behavior and negative cases for missing elements, malformed arguments,
  multiple players, delayed state and repeated execution.
- [x] Verify allowed scriptlets run in intended documents/frames; blocked or
  untrusted rules have no observable privileged effects.
- [x] Test actual desktop/mobile YouTube surfaces used by Roadium, including
  pre-roll, mid-roll, Shorts, embeds and fullscreen. Record account/session
  conditions, date, exact filter versions and whether an ad opportunity occurred.
- [x] Validate captions, seeking, pause/resume, quality changes, background/tab
  transitions and ordinary non-YouTube HTML audio/video/WebAudio.
- [x] Run existing Automotive restriction/recovery checks; filter scripts cannot
  restart restricted playback or require bypassing parked-only enforcement.
- [x] Record baseline comparison and reproducible regressions. A session that
  showed no ads is inconclusive about a particular ad format's blocking.

## Acceptance and tests

| Scenario | Required result | Evidence spot |
| --- | --- | --- |
| Inventory of every enabled YouTube rule | Source/version, parser/policy outcome and decision recorded | [145 explicit references from all four loaded defaults plus optional experimental](evidence/card06/compatibility.json); generic rules covered by full-list playback |
| Supported snippet fixtures | Intended effect, argument handling and execution lifecycle verified | [Installed assertions](evidence/card06/installed-verification.json) |
| Unsupported/compound rule fixtures | Safe rejection or explicitly justified tested rewrite | [Native results](evidence/card06/native.json), [rule decisions](evidence/card06/rule-decisions.json) |
| Untrusted copied YouTube snippet | No privileged execution | [Untrusted copied-command fixture](evidence/card06/untrusted-final-trigger.json) |
| Pre-roll/mid-roll/Shorts/embed/fullscreen | Observed behavior reported accurately; normal video remains usable | [Live conditions and open format gates](evidence/card06/README.md#live-conditions-and-limits) |
| Captions/seek/quality/tab transitions | No regression from approved baseline | [Captions/quality](evidence/card06/fresh-live-features.json), [tab return](evidence/card06/tab-returned-ordinary.json), [seek](evidence/card06/fresh-live-desktop-controls.json) |
| Standard audio/video/WebAudio | Existing media behavior retained | [Installed assertions](evidence/card06/installed-verification.json) |
| Moving/restricted then parked | Playback stays restricted; ordinary recovery behavior preserved | [Background restriction/recovery](evidence/card06/background-trigger.json) and26 media executions pass; actual vehicle-motion acceptance remains pending |

Live YouTube is a changing external system: use deterministic regression tests
for supported behavior and record live outcomes/limits rather than making an
unstable live ad appearance the sole CI pass criterion.

## Deliverables and handoff

- [x] Complete versioned compatibility inventory and justified rule decisions.
- [x] Separate patch where behavior changes are needed; if all maintained rules
  already work, deliver the audit/tests without manufacturing engine changes.
- [x] Converter/runtime fixtures and installed playback/Automotive evidence.
- [x] Handoff to Card 09: parser cases, live test conditions and observed limits
  to recheck after upstream changes.

## Implementation and remaining acceptance

Fresh profiles prefer maintained Anti-Circumvention rules. The legacy experimental
list remains visible/trusted/selectable and existing choices are preserved. No
parser, scriptlet command, library or trust identity was broadened. Unsupported
compound sequences remain rejected as complete rules.

The [145-row inventory](evidence/card06/RULE_OUTCOMES.md) covers all four loaded
default snapshots plus optional experimental rules:137 accepted,8 unsupported.
[Full compatibility data](evidence/card06/compatibility.json) binds source text,
versions/hashes, domain applicability, policy and actual native generated calls.
Named maintained replacements are recorded for exact experimental duplicates;
scope/value differences remain explicit. The accepted `[-]` JSON-removal syntax
has a demonstrated runtime gap and was not unsafely rewritten.

224 native +28 diagnostics +26 media executions passed after independent local
review; loader16 and packaged-resource8 checks pass. Final x64/ARM64 APK/AAB builds,
source/patch provenance, actual installed APK hash, fresh defaults, upgrade
selection/advanced-opt-out preservation, command/frame effects, audio/video/
WebAudio, background restriction, foreground/tab recovery and live desktop/mobile/
embed controls have recorded evidence. See the [verification record](evidence/card06/verification.json)
and [detailed report](evidence/card06/README.md). Cleanup passed.

The checked work items above mean the work/test attempt was performed; they do
not turn inconclusive live formats into successful ad blocking. Acceptance remains:

| Acceptance item | Recorded status |
| --- | --- |
| Inventory, converter/policy, safe compound rejection | Passed for frozen145 rules |
| Supported command fixtures, trusted/untrusted, advanced opt-out | Passed |
| Desktop/mobile/embed playback, captions, seeking, quality, fullscreen, tab return | Passed in recorded lab conditions |
| Ordinary media and activity-background restrictions/recovery | Passed; actual vehicle motion was not simulated |
| Shorts | Attempted; did not buffer, also failed advanced-off baseline; open |
| Pre-roll/mid-roll effectiveness | No observed ad opportunity; inconclusive |
| `json-prune` array removal `[-]` | Accepted syntax has unsupported runtime semantics; upstream compatibility gate |
| Physical Android12 ARM64 vehicle and extended soak | Release gate; pending |

No release signing/publishing, main commit or push was performed. The first six
overlays remain unchanged. Card Nine inherits these exact fixtures, parser rows,
live conditions and open gates. Cards Seven–Nine remain on hold.
