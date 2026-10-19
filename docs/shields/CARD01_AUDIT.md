# Card 01 audit and implementation evidence

Card 01 implementation and x64 emulator verification completed October 13, 2026.
ARM64 packaging and physical-car release checks remain pending. Other Shields
cards remain on hold. See the [evidence index](evidence/card01/README.md).

## Source and environment

- Branch: `develop`; Chromium `153.0.8010.37` and the pinned Cromite source.
- Retained x64 source diff matches foundation SHA-256
  `3f0fedee04363332ccfe8fb2bbd2ba1f4ed8127e187f04c5bd2104a33debd0df`.
- Baseline emulator package: `io.github.musicpizzaman.roadium`, version code
  `801003718`, min SDK 31, target SDK 36.
- Read-only API 33 Automotive AVD session; the saved AVD is preserved.
- Existing app profile: emulator user 10. Fresh disposable profile: user 11.
- Fresh profile completed first run with emulator networking disabled.
- Current parked driving state was confirmed as 0. No physical vehicle was used.

## Observations before implementation

Both profiles select these five canonical subscription identities:

1. `https://uazo.github.io/cromite/filters/easylist.txt`
2. `https://uazo.github.io/cromite/filters/badblock_lite.txt`
3. `https://uazo.github.io/cromite/filters/badmojr-1Hosts-master-Lite-adblock.txt`
4. `https://uazo.github.io/cromite/filters/abp-filters-anti-cv.txt`
5. `https://raw.githubusercontent.com/uazo/cromite/master/tools/filters/experimental-cromite-filters.txt`

| Observation | Existing profile | Fresh offline profile |
| --- | --- | --- |
| Global blocking preference | Enabled | Enabled |
| Selected subscriptions | Five above | Five above |
| Advanced preference stored explicitly | Absent; registered default is false | Absent; registered default is false |
| First-run subscription flag | False after prior first run | False after this first run |
| Subscription metadata records | Five | Zero |
| Stored EasyList version | `202610010932` | None recorded |
| Stored anti-circumvention version | `202610010932` | None recorded |
| FlatBuffers signature records | Five in prior snapshot | Zero |
| Actual engine activation / fixture blocking | Not yet verified | Not yet verified |

These observations establish persisted selection and metadata, not actual
execution. The fresh profile demonstrates why selection must be displayed
separately from installed/active data. Card 01 must expose the deficiency;
it does not implement Card 02's offline resources or Card 03's new defaults.

The existing metadata interface documents `download_count` as including
successful HEAD-only requests, and `error_count` as consecutive failures that
reset after success. They must not be labeled activated-filter count or total
lifetime errors. Installation time must not be relabeled last successful update
unless the relevant event is proven and tracked separately.

## Audit and implementation evidence

- [x] Trace first-run installation independently of scheduled routine updates.
- [x] Verify operational engine state with deterministic rule-specific fixtures.
- [x] Verify diagnostic behavior with an explicitly stored advanced opt-out.
- [x] Record native lifecycle/error schema and manual batch completion design.
- [x] Record converter accepted/rejected counts and reason accounting.
- [x] Record safe separate overlay integration and provenance tests.
- [x] Build/test the reviewed implementation and record the exact artifact.
- [x] Verify visible fresh/upgrade/failure diagnostics and privacy; cancellation via native tests.

Source references and full acceptance requirements are in
[Card 01](01-audit-and-diagnostics.md).

## Implementation and focused verification

The draft is a separately pinned `0002-roadium-shields-diagnostics.patch`.
The foundation patch remains byte-for-byte unchanged. Ordered patch loading
preflights all verified bytes with a disposable Git index, verifies the exact
cumulative source diff and preserves unrelated files/index changes. Sixteen
loader tests passed, including overlap, prefix extension, later-patch failure,
untracked collision and transaction rollback cases.

Diagnostics retain one latest attempt and one last successful activation per
existing subscription metadata record. Error text is capped at 160 bytes and
transport display strings at 2048 bytes. Conversion counters saturate and
retain neither individual rule text nor browsing requests. Inline transport
payloads are omitted from diagnostic fields/display. Existing filter identity
and stored configuration remain authoritative.

The immutable converter sidecar reports accepted input rules and rejection
counts for parser rejection, unsupported commands, prohibited privilege,
unsafe arguments and unsupported/no-operation options. A compound snippet
with an unsupported command remains wholly rejected. No FlatBuffers schema
change or scriptlet allowlist expansion is introduced.

The manual check wraps the existing maintainer lifecycle, joins an existing
installation and completes only after storage/current-engine activation,
failure, cancellation or a 45-second result deadline. A deadline does not stop
the existing automatic retry/backoff policy. Each batch retains per-list
outcome/error snapshots, including a list removed while checking; subsequent
automatic success cannot rewrite a completed manual timeout result.

Settings provide a local diagnostics report, active-versus-pending summaries,
full-width request counters and real manual-check results. Polling runs only
while the corresponding settings surface is active and is removed on pause
or stop. Historical information missing in older builds is displayed as not
recorded. Counters are not presented as proof of activation.

Focused execution before installed-app verification:

- 15 native tests passed on the API 33 Automotive emulator: real converter,
  metadata, downloader, maintainer and service with controlled storage and
  transport boundaries. These cover stale conversion tokens, trust, timeout,
  cancellation, old-data retention and the disabled recommended installer
  remaining independent of routine scheduled updates.
- 20 Android test executions passed across API 29 and API 36 (10 cases on
  each): truthful state/unknown-history handling, batch outcomes, removed-list
  snapshots, diagnostics privacy and full counter semantics.
- Independent local Ollama reviews completed for loader, diagnostic data,
  lifecycle, Android and tests. No concrete bugs were reported. The reviewers'
  suggested coverage checks were compared with the actual tests; full
  installed UI/native/storage verification was completed for the scenarios below.

The exact x64 APK/AAB build succeeded and packaging/provenance validation passed.
Installed observations are recorded below; these results do not establish
physical-car compatibility or release readiness.

## Source audit conclusions and handoff

Recommended first-run installation is disabled in the pinned configuration;
routine updates still run for selected subscriptions. The native test
`RoutineUpdatesRunWithoutRecommendedInstaller` establishes this distinction.
The preloaded subscription collection is empty, so a fresh offline profile has
five selections and no installed data. Card 02 owns restoration of bundled data.

Advanced filtering's registered default remains false, and explicit false
survives upgrade. Card 03 owns the proposed new default/migration. The trusted
anti-circumvention list can be loaded while privileged rules are ineligible.
The observed online conversion rejected 1,915 anti-circumvention rules for
prohibited privilege; 2,492 rules were accepted. That explains one constraint
on current protection, without claiming a complete diagnosis of every ad.

The downloader records transport and conversion boundaries; the maintainer
records storage and collection activation. Request generation tokens reject
stale conversion callbacks. Installed-subscription state remains the authority
for active data, independent of latest attempt failure. The original response
identity still drives conversion/trust; final transport URL is display-only.
Card 04 can populate transport provenance through the same diagnostic event;
Card 05 can report validation/storage/recovery results while keeping active
old data independent of the latest attempt. Neither card is implemented here.

JNI now exposes local snapshots and true 64-bit request counters. Legacy
successful-download counts include HEAD checks; consecutive failures reset on
success. Old installation time is kept separate from new last-success history.
Old buffers lack rejection statistics and display “not recorded”; new immutable
sidecars record bounded totals without changing FlatBuffers wire schemas.

## Installed build verification

The APK/AAB build completed successfully; the exact installed development APK
SHA-256 is `748899dd401759d2b430f4445bad336ec98c839799e7fd5ca68bb2039a34fd68`.
The cumulative applied source diff is
`0eaf8d4da1259c2e26befa338bcfd44aebc6d677b096638aa3ad51e65adffae0`;
the final overlay tree is `8c8e3e4d12be47954492fd8a3df3c4ef12eaa489`.
The original foundation bytes remain unchanged.

Fresh offline UI showed selected but inactive data and five finite manual-check
timeouts. Online checks then reported five activations and showed EasyList and
anti-circumvention loaded. Temporary transport rejection produced five explicit
`ERR_CONNECTION_REFUSED` failures while those lists remained loaded with their
prior installed versions and active-rule counts. Networking was restored.

The existing user10 profile retained all configuration and old installed
versions after upgrade. User11 retained explicit advanced false, its custom
manual rule, site exception and five subscriptions. Global-off UI correctly
showed EasyList paused. Opening/dismissing/leaving the report and reopening
settings did not crash or produce perpetual checking state. Lifecycle-scoped
polling and batch tests supply the stronger callback/state evidence.

A controlled advertising-resource fetch with only EasyList selected was blocked
with `net::ERR_BLOCKED_BY_ADMINISTRATOR`. The identical fetch completed when
global blocking was disabled. The downloaded code was never executed. This
establishes actual list operation beyond persisted selection or metadata.

All 26 existing media test executions passed after rebuilding their target
against current source. In the installed emulator, parked HTML audio/video
started and WebAudio ran. Driving restrictions displayed the lock screen and
paused HTML audio/video; returning to Park did not auto-resume them. WebAudio
context state alone does not prove audible output, and no speaker/speech or
physical-car verification is claimed.

Full result JSONs, screenshots, review records, commands and limitations are in
[the evidence directory](evidence/card01/README.md). All sixteen loader tests
passed again after installed checks. Cards 02–09 remain on hold.
