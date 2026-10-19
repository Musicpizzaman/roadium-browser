# Card 08 - per-site controls and local activity

Implemented and locally verified October 18, 2026. Final packages, installed
acceptance and guarded lab cleanup passed; [verification](verification.json) is
the final record. Physical vehicle and release gates remain open.

## What ships in this overlay

Regular HTTP(S) page information now includes a Shields row. Its panel shows the
current host, global/site exception state, derived Card 07 protection level,
real blocked-request count, readable disable/restore actions and existing local
filter diagnostics/settings. Actions reload the current tab. Controls and count
precede secondary details; both existing palettes were inspected.

| Action/state | Scope | Ownership and persistence |
| --- | --- | --- |
| Disable for this site | Current canonical host and its subdomains, across schemes and ports | Existing saved allowed-domain record |
| Disable for this browser session | Same host scope for this original browser profile | Separate in-memory native vector; never a preference/dictionary entry |
| Remove saved exception | Only the selected covering saved entry, including its explicitly displayed subdomain scope | Does not remove a concurrent temporary entry |
| Remove session exception | Only the selected covering temporary entry | Does not remove a concurrent saved entry |
| Global pause | Takes precedence over either exception | Site restore never enables global or advanced filtering |

The engine routes regular and Incognito filtering through the original profile.
Both saved and temporary choices therefore affect those tabs, after they reload.
The panel is offered in regular tabs; no mutating Shields panel is created in
Incognito. Help text states shared scope, browser-restart expiry, tab-close
behavior and the need to reload other open tabs. Closing a tab does not end a
session exception. Browser-process/configuration destruction does.

This preserves the existing browser-client policy:
`chrome/browser/adblock/adblock_chrome_content_browser_client.cc`,
`GetBrowserContextForEyeoFactories()->GetOriginalProfile()`.
A direct off-record service-factory lookup returning null does **not** mean
private filtering is absent; browser routing happens before that lookup.
[Private scope evidence](private-shared-scope.json) verifies actual inherited
filtering and an exception applied from a regular tab.

The site key is a host, not an automatically widened registrable domain. Matching
requires an exact host or DNS label boundary; siblings remain protected unless
covered by an explicitly selected parent exception. Every covering entry gets a
separate removal action displaying its original host and subdomain scope.
Internal/file/non-HTTP pages and IPv6 literals have no new controls. Existing
independent global/advanced settings and custom manual/subscription rules remain
untouched. Separate cosmetic/advanced per-site toggles are not offered because
those controls are configuration-wide in this implementation.

Current-page hosts use canonical ASCII/punycode. Legacy raw Unicode saved
records are retained, but are not falsely interpreted as working punycode
exceptions: the pinned native domain-option parser rejects non-ASCII values.
The new control can save a valid canonical entry without deleting the old one.
[Before](legacy-record-before.json), [after](legacy-record-after.json),
[actual engine effects](legacy-engine-after-model-fix.json), and
[corrected panel](legacy-unicode-after-model-fix.png) document this regression.
Arbitrary document allow rules in custom lists are not reconstructed by this
settings panel; selected settings and actual list readiness remain separate.

## Engine and lifecycle implementation

The ninth overlay is [0009-roadium-site-controls.patch](../../../../build/roadium/patches/0009-roadium-site-controls.patch).
SHA-256: `c22996e7566fc8e188d5b3f79aead1bae57b238c8d4120a66e296d1d13e8ece2`.
The first eight overlays remain byte-identical. Final cumulative source diff:
`341ddbe7d5d3885f8fc93c68d0e781a6a620200a33c1b7810d7b2db0ae1c6960`.
[Per-file hashes](affected-source-files.json) cover all 24 changed source paths;
full-series verification also checks the complete applied source, not only those paths.

`FilteringConfiguration`/`PersistentFilteringConfiguration` add temporary-domain
get/add/remove methods. Strict native host validation rejects rule/URL injection;
deduplication and missing removals are no-ops. Changed state uses existing
`OnAllowedDomainsChanged` and custom-filter conversion. The maintainer converts
both saved and temporary hosts using the same ordinary document-allow filter.
No engine, trust-policy, migration or alternate preference store was introduced.
Temporary data is a distinct member vector and never enters `dictionary_`, so
unrelated preference writes cannot accidentally serialize it.

The existing site-info extension factory creates `ShieldsPageInfoController`.
It captures the displayed URL, checks it before actions, and attaches a
`WebContentsObserver` only while its subpage exists. Navigation/destruction
invalidates the panel; removal detaches the observer and closes its separate
read-only diagnostics dialog. Existing site-info ownership handles tab changes.
There is no session-long Java resource observer or background history collector.

`EyeoPageInfo` owns a saturating integer counter on the actual `content::Page`.
Both request and response classification dispatch sites capture a
`WeakDocumentPtr`. Only real block decisions for a still-valid dispatching
document increment its page, before invoking the completion callback. A reused
frame cannot attribute a late completion to the new document. Filtering
classification and delivery remain unchanged.

Counts include frame-backed network blocks in embedded frames. They count block
decisions/attempts, not unique URLs or hidden advertisements. Detached workers,
popups and cosmetic changes are excluded. Reload/new-document navigation starts
a new count; same-document navigation and a retained cached page keep its count.
The panel reads a synchronous snapshot; Refresh updates it. No request URLs,
rule text, visit history or attribution event list is retained by this feature.
Rule/list attribution is explicitly unavailable in this snapshot, rather than
inferred from list names. No report submission or automatic upload was added.

## Tests and installed acceptance

| Check | Result/evidence |
| --- | --- |
| Native configuration, persistence, validation and existing regressions | 231 passed; [result](post-review-native.json), [passing command/log](card08-post-review-native-retry.log) |
| Java diagnostics, presets and site model | 54 executions passed (27 tests on two API configurations); [final result](final-java.json), [command/log](card08-final-java.log) |
| Existing media regressions | 26 executions passed; [result](media.json), [command/log](card08-media.log) |
| Overlay loader / packaged filter resources | 16 / 8 passed |
| Upgrade from Card 07 | Custom list/manual rule/saved exception/homepage and advanced opt-out preserved; [record](upgrade-preservation.json) |
| Temporary disable, other tab protection, subdomains and restore | [Record](session-controls.json), [unrelated protected tab](session-other-protected.json) |
| Saved restart, session expiry and both concurrent-removal orders | [Record](persistence-and-ownership.json) |
| Global pause, site restore and Strict/Balanced changes | [Record](global-and-preset-state.json), [paused screenshot](global-paused-strict.png) |
| Unicode navigation, canonical IDN and child scope | [Record](idn-and-redirects.json) |
| Cross-site redirect | Destination stays protected; [effect](redirect-destination-protected.json) |
| Actual activity refresh and frames | Count 2 -> 3 -> 5; [record](activity-and-lifecycle.json), [screenshot](panel-activity-final.png) |
| Navigation, reload, tab ownership, diagnostics teardown | [Record](activity-and-lifecycle.json); new document returns to 2 |
| Legacy Unicode false-off regression | [Before](legacy-record-before.json), [after](legacy-record-after.json), [final normal controls](final-normal-controls.json) |
| Private/shared original-profile scope | [Record](private-shared-scope.json), [no private controls](incognito-policy.json) |
| Internal regular page | [Record](internal-page-policy.json) |
| Light/dark, readable labels and large controls | [Light](panel-controls-final-light.png), [dark](panel-controls-final-dark.png); physical focus/touch remains open |

Total focused coverage is **311 executions**, plus the 16 loader and eight
resource checks. [Runner commands](run-tests.sh) and raw logs retain exact flags.
Native/media code remained unchanged after their passing review reruns. The final
Java guard was rebuilt and all 54 executions passed. The later scope change is
text only; both architectures are rebuilt and the installed caption is checked.

Independent local analysis/reviews were advisory. Codex checked actual source,
applied changes, built and tested. Records cover [native](local-native-review.json),
[Java](local-java-review.json), [UI lifecycle](local-final-ui-review.json),
[UI order](local-ui-reorder-review.json), [domain audit](local-domain-audit.json),
[domain fix](local-domain-review.json) and [shared private scope](local-private-scope-audit.json).
No concrete unresolved finding remains. Speculative mutex advice was rejected
because existing configuration operations are UI-thread serialized. The mixed
ASCII/Unicode test requested by a review is present and passed.

One native rerun hit test-harness cleanup timeout; the [failed log](card08-post-review-native.log)
is retained separately from its passing rerun. The initial Java test still
expected legacy Unicode to count as active and failed on both API configurations;
[that failed expectation](domain-old-expectation-java.json) was corrected and the
final 54 executions passed. A formatting helper initially used the wrong formatter
for `.gni`; GN rejected it before acceptance, and the file was restored with only
the intended source addition. No rejected candidate is presented as a final build.

## Controlled fixtures and evidence limits

Installed checks used the final development x64 APK on a read-only API 33
Automotive emulator, 1280x720 at density 160, in owned user 11 `ShieldsCard08`.
Only that disposable browser profile was read. A real Card 07 APK initialized it
before upgrade. Lab-only first-run/DNS/certificate-pin flags, an owned UI helper,
loopback TLS fixture server, one devtools forward and one reverse were used.
This establishes controlled runtime behavior, not live website/ad-format success.

[Fixture manifest](fixture-manifest.json) records byte-identical
[HTML](../../../../tools/roadium/fixtures/shields-site.html) and
[custom list](../../../../tools/roadium/fixtures/shields-site-filters.txt).
The script-dependent fixture fails when filtered, works when excepted, and is
filtered again after restore. Ordinary content remains visible. A cosmetic target
checks full-site scope without being counted as a network request. Six existing
list snapshots were served from their already recorded immutable inputs; no new
list is bundled or granted privilege by this card.

The owned TLS certificate/key are test fixtures outside Git. Synthetic hosts use
`.card08.invalid`; canonical list requests are mapped to loopback. No external
account, production signing key or original user profile was used.

The maintained BadBlock Lite snapshot contains `||xn--$document` with exclusions.
It blocked a punycode fixture after restore, which is existing list policy.
[Observed policy](idn-list-policy.json) is retained. IDN scope was therefore
isolated under Standard with the owned custom list, then Balanced was restored.
No interstitial bypass was clicked and the maintained rule was not changed.

Early fixture probes could read the previous completed DOM during reload.
Accepted probes require the active exact fixture URL and a fresh document
`performance.timeOrigin`; fragments are retained correctly. Restart checks wait
for custom-list activation and explicitly reload, rather than treating a page
opened before custom data loads as active-filter evidence. Preference-restart
checks wait for the existing delayed preference writer before forced termination.
[Runtime revision notes](runtime-revision-notes.json) distinguish the UI layout,
parser-guard and final text-only revisions without erasing earlier evidence.

## Builds, cleanup and handoff

Pinned Chromium `153.0.8010.37`, Cromite
`11507ac1061b5ea227806f5e84db5a57df6ccf6a`, baseline tree
`56400c5406d8f83533c151e122b19f3f745c0892`; version offset 10 is unchanged.
[x64 manifest](x64-build-manifest.json) and [ARM64 manifest](arm64-build-manifest.json)
record final source tree/diff, package hashes, signature checks, ABI/minimum SDK,
bundled resources and bundle validation. Build-time runtime-pending fields remain
as historical build state; [final verification](verification.json) supplies later
installed acceptance. Historical candidate manifests are explicitly named.

Final development packages are under
`E:/Android Auto Projects/RoadiumBuild/artifacts/153.0.8010.37-roadium-shields-card08-x64`
and the corresponding `-arm64` directory. APKs retain the diagnostic development
certificate; AABs are unsigned. No production signing or publication was done.
[Installed package verification](installed-final-package.json) checks the actual
installed APK against the final manifest. [Cleanup](cleanup.json) records owned
profiles/helpers/ports/server/emulator removal and original state restoration.

Card 09 should integrate the site-state model, exact temporary lifetime and
concurrent ownership, shared private scope and reload boundaries, native
page-counter/stale-document behavior, deterministic fixtures and privacy checks.
Physical Android 12 2024 Blazer EV focus/touch/rotary and parked-only regression,
production signing/release integration and extended update/storage soak remain
open. Existing Card 06 live-service gates and Card 10 geometry/preferred 720p
implementation are separate and remain open.
