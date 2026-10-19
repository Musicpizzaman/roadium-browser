# Card Six — YouTube compatibility

Card Six changes one production default: fresh profiles no longer automatically
select the legacy Cromite experimental list. The maintained Anti-Circumvention
list remains selected. Existing selections, explicit experimental opt-in, its
visibility and exact trusted identity remain intact. An installed upgrade
[preserved the complete selected configuration and advanced opt-out](upgrade-preservation.json).
The [fresh-profile report](resumed-fresh-default-report.txt) shows all four
default lists actually loaded and the experimental list unselected.

The separate seventh overlay contains that configuration change and focused
tests. The parser, serializer command/value allowlists, snippet library,
injection mechanism, trusted identities, update/recovery implementation and
Automotive media enforcement are unchanged. The first six patches retain their
previous hashes. No experimental compound rule was split or stripped.

## Frozen inventory and decisions

[Compatibility data](compatibility.json) and the [145-row outcome table](RULE_OUTCOMES.md)
record source/version, canonical identity, line, full text, text digest, actual
converter results with and without privilege, current source eligibility and
generated calls for desktop, mobile, Music, Kids, embeds, Shorts and an unrelated
document. Live advanced-off generation is checked for every row. Native results
are bound to exact rule text and identity; stale, missing or duplicate results
are refused. Header regeneration and changed-text/identity negative controls pass.

| Source | Frozen version | Explicit references | Accepted | Unsupported |
| --- | --- | ---: | ---: | ---: |
| EasyList | 202610130952 | 40 | 40 | 0 |
| Anti-Circumvention | 202610130952 | 44 | 39 | 5 |
| Optional experimental | no version supplied | 17 | 14 | 3 |
| BadBlock Lite | 04October2026v1 | 38 | 38 | 0 |
| 1Hosts Lite | no version supplied | 6 | 6 | 0 |
| Total | | 145 | 137 | 8 |

These are explicit YouTube-related references, including exclusions and
incidental third-party names. Generic filters may also affect YouTube and are
exercised by installed full-list playback checks. Accepted syntax does not prove
that every selector, argument grammar or future YouTube surface works.

EasyList/AntiCV retain the existing bundled plaintext hashes and Cromite pages
revision `338336d9e640489c648d47d606cb0030064c4e0f`. The other two default snapshots
are [audit-only gzip inputs](../../../../tools/roadium/youtube-snapshots/README.md),
with independent version/hash/license metadata; they do not add browser resources.
Both are loaded through their original canonical URLs in the lab. 1Hosts supplies
last-modified `2026-09-03T12:23:55.742Z`, not a filter Version. Experimental
installed bytes have SHA256 `4458c790077ede1f985771c911039ccc3529301cd43b389fd4381e59d06b5d46`.
Its [checked commit history](experimental-maintenance.json) contains the September2,
2024 commit `c1b924af3adf31541e6215e49653429f2ec7f0e3`; its filename is not a maintenance date.

Eight complete sequences remain rejected: AntiCV lines3553,3554,3569,3570,3575
and experimental lines4,19,20. Unsupported operations include `event-override`,
`map-override` and `simulate-mouse-event`. A preceding `race`, supported skip or
property override does not partially install when the sequence is rejected.
Existing Card One diagnostics show aggregate reasons; the local inventory gives
the exact rule-level result without adding browsing telemetry.

[Recorded decisions](rule-decisions.json) name maintained replacements for
experimental lines6/7/15/16. Other overlaps have different scopes or values and
are not falsely marked fully superseded. In particular, maintained desktop
`emptyArray` overrides overlap experimental `undefined` overrides. Keeping the
legacy list as an explicit choice preserves existing profiles; preferring the
maintained list for new profiles avoids adding those duplicate hooks by default.

AntiCV line3572 exposes a separate runtime gap: `json-prune` accepts
`entries.[-]...` syntactically, but the pinned library does not remove the array
entry. The [installed fixture](controlled-final-after.json) retains `isAd`.
Replacing removal with `[]` leaf deletion would change semantics, so it was not
done. This remains an upstream compatibility item for Card Nine.

## Deterministic and installed verification

The native suite records 224 successful tests, including145 inventory cases and
whole-rule rejection, arguments, trust, live opt-out, fresh-default metadata and
existing-selection persistence tests. Java diagnostics contribute28 executions
and existing media/Automotive tests26: **278 executions passed after local review**.
See [native](native.json), [diagnostics](diagnostics-junit.json), [media](media-junit.json)
and the [run log](final-tests.log). Loader16 and packaged resource8 checks also pass.
The [independent local review](expanded-local-review.json) reports no findings.

The controlled list uses existing trusted AntiCV identity and domain-adapted
fixtures, not a proposed upstream release. Privileged effects come through normal
engine conversion, per-frame selection and the existing execution wrapper; the
developer probes do not inject scriptlets. JSON/property effects are observable
in the document world and a same-origin child frame. Existing XPath dependencies
and library bytes are preserved.

| Installed case | Result/evidence |
| --- | --- |
| JSON.parse, Response.json, array paths, missing paths, malformed JSON | [Supported effects and preserved content](controlled-final-after.json) |
| Property override, abort-on-write, XPath DOM hiding, same-origin child | [Normal engine execution](controlled-final-after.json) |
| Missing ad marker, delayed marker, two video players | [Before](controlled-final-before.json), [after](controlled-final-after.json); ordinary player unaffected |
| Unsupported compound and unsafe override value | Probe properties remain unchanged in [trusted fixture](controlled-final-after.json) |
| Current advanced opt-out and re-enable | [Off](advanced-off-final-trigger.json), [restored](advanced-restored-final-trigger.json) |
| Copied untrusted list | [No privileged effects](untrusted-final-trigger.json), [diagnostics](custom-final-report.txt) |
| Ordinary audio/video/WebAudio | [Audio](controlled-audio.json), [video](controlled-final-ordinary.json), [WebAudio](controlled-final-webaudio.json) |
| Backgrounded scriptlet playback attempt | [Trigger](background-trigger.json), [stable paused state](background-state.json) |
| Foreground recovery | [Visible document](resumed-state.json), [ordinary playback](resumed-ordinary.json) |
| Tab change and return | [Hidden document](tab-away.json), [scriptlet attempt](tab-hidden-trigger.json), [returned playback](tab-returned-ordinary.json) |

The short local WebM seeks settle at keyframe0 with advanced filtering on and off;
exact local seek accuracy is not claimed. Live YouTube seek-to10seconds succeeds.
Background checks prove activity/lifecycle restriction, not an actual moving
vehicle state. Vehicle properties were not changed.

## Live conditions and limits

Live checks ran October17,2026 America/Chicago on a temporary signed-out profile,
API33 x64 Automotive emulator, final APK SHA256
`d18d2781075d5bb788341788894680814f45f9575f948ee328a952dbd0325a4b`.
The resumed fresh-profile runs use all four actual default lists and no
experimental subscription. Earlier controlled/upgrade evidence uses the same
APK bytes in a separate read-only session. Original saved profiles were not read
or edited. No account was signed in.

The emulator initially failed external DNS despite connected AndroidWifi. A
loopback CONNECT relay uses host DNS and preserves end-to-end TLS for YouTube;
some ancillary hosts are denied. Its [host-only trace](live-relay-hosts.jsonl)
records this constraint. Frozen filter downloads use an ephemeral developer TLS
fixture and a specific SPKI exception in a protected own-user command-line file.
No OS trust store, production trust identity or certificate policy was changed.
[Subscription logs](subscription-requests.jsonl) record served plaintext hashes
and show no Cookie/Authorization headers at those fixture endpoints.

Desktop and mobile ordinary playback/pause/seek, English captions, actual144p
quality selection, iframe embed playback and fullscreen have recorded results:
[desktop](fresh-live-desktop-controls.json), [mobile](fresh-live-mobile-controls.json),
[captions/quality](fresh-live-features.json), [embed](fresh-live-embed-controls.json),
[fullscreen](fresh-live-fullscreen.json), [embed fullscreen](fresh-live-embed-fullscreen.json).
Public test clips are Blender's `aqz-KE-bpKQ` and YouTube Developers'
`M7lc1UVf-VE`. Desktop/mobile UA overrides are scoped to their CDP navigation
session; subsequent observations record the actual current UA.

Shorts reached a real Shorts URL but did not buffer in this lab; earlier advanced-off
baseline also failed. [The result](fresh-live-shorts-features.json) remains open
acceptance, not a passed format or demonstrated filtering regression. No pre-roll
or mid-roll ad opportunity was observed. Those formats remain inconclusive,
especially given the relay constraints. No claim that all YouTube ads are blocked
is made. Extended tab/long-session behavior and physical ARM64 Android12 vehicle
restriction/recovery remain release gates.

[Installed assertions](installed-verification.json) pass while preserving these
open live gates. [Cleanup verification](cleanup-verification.json) confirms the
resumed lab user, flags/helper, ports, fixture/relay processes and read-only
emulator were removed; original users/network were restored. The build containers
remain available. No saved-AVD disk hash comparison is claimed.

## Reproduction and handoff

Generate `inventory-inputs.json` and the test `.inc` with
`tools/roadium/youtube_inventory.py --inventory ... --header ...`.
Build/run `roadium_shields_unit_tests`, `roadium_shields_junit_tests` and
`roadium_media_junit_tests` using the pinned environment; retain native runner
JSON. Then regenerate `compatibility.json` with `--native-results native.json`.
The tool refuses incomplete or changed-rule output. The `.inc` remains test data.

Recorded [fixture](card06.html), [frame](card06-frame.html), [filter list](controlled-list.txt)
and [probes](probe.mjs) are lab references with explicit ownership guards.
Adapt/verify device IDs, user identity and ports before rerunning them. TLS keys,
private Preferences and backup archives remain outside Git. Ordinary media input
files came from the pinned Chromium media test data and are not duplicated here.

Final source/package manifests are [x64](x64-build-manifest.json) and
[ARM64](arm64-build-manifest.json); [affected source hashes](affected-source-files.json)
match the isolated source and both full build checkouts. APKs use the diagnostic
certificate; AABs remain unsigned. No publishing, production signing, commit or
push was performed. Card Nine inherits145 parser/policy rows, the `[-]` gap,
Shorts and observed-ad-opportunity checks, and physical/lifecycle release gates.
Cards Seven–Nine remain on hold.
