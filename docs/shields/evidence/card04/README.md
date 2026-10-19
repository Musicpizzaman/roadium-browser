# Card 04 verification — October 15, 2026 (Central)

Card 04 is implemented and verified on the installed x64 Automotive build.
Both x64 and ARM64 APK/AAB builds passed artifact verification. Cards 05–09
remain on hold. [Acceptance JSON](verification.json) binds the final source,
packages, tests, installed cases and cleanup. Physical ARM64 Android 12 vehicle
acceptance and production upload-key signing remain release gates.

## Source and packages

The separate fifth overlay is `0005-roadium-approved-filter-fallback.patch`,
SHA-256 `ebdbd3da426e96ab7ab49aaf4e04c1c3512c4edd23e1c0d35455304052f96552`.
The four previously accepted overlays are byte-identical. The cumulative
source diff is
`40951ab23f981e0978178293af7f0705cbfbf1eabc5cf11daddb0236f039496b`;
the final Chromium tree is `a33a2961c7502d487058c810b1084f7c66aa1fd5`.
Chromium/Cromite pins and version-code offset remain unchanged.

[x64 provenance](x64-build-manifest.json) and
[ARM64 provenance](arm64-build-manifest.json) record successful compiler runs,
exact source, ABI, SDK manifests, required Automotive declaration, APK
development certificate, ZIP integrity, bundletool validation and actual
packaged filter/manifest/notices bytes. The frozen bundle bytes remain the
Card 03 versions. [Exported hashes](exported-packages.json) were checked again
after copying all four artifacts. The installed x64 APK SHA-256 is
`f416a8962b9ede8b1cd7c21a5042471792ac886616b4e57a23cb574be52766ad`.
AABs are unsigned. Generated build manifests retain their runtime-pending
field; this record supplies subsequent installed acceptance.

## Mapping, identity and policy

The [mapping inventory](fallback-mapping-inventory.json) records **31 exact
canonical/transport pairs**, checked against pinned configuration and frozen
upstream revision `338336d9e640489c648d47d606cb0030064c4e0f`.
[All literal pairs match](mapping-verification.json); native tests also check
the complete known-subscription inventory. This is frozen mapping evidence,
not a claim that a mutable remote branch will remain available forever.

Canonical prefix: `https://uazo.github.io/cromite/filters/`.
Approved transport prefix:
`https://raw.githubusercontent.com/uazo/cromite/pages/filters/`.
The implementation enumerates complete GURLs; it does not construct a fallback
for arbitrary files on those hosts. Queries, fragments, credentials, unexpected
ports, unknown filenames and look-alike sources do not match the reviewed map.

EasyPrivacy has no approved fallback evidence. Acceptable Ads exception rules,
manual/custom filters, test subscriptions and the existing raw/master
experimental identity also have no automatic mapping. The experimental list's
existing exact trust classification is preserved.

Transport is separate from the subscription key, converter identity, callback
and metadata identity. Privileged conversion still requires current advanced
policy and the existing exact trusted identity. The trusted canonical AntiCV
URL and the existing raw/master experimental identity remain unchanged;
raw/pages AntiCV entered directly as a custom subscription gains no trust.
Header filters stay disabled and the scriptlet command/argument allowlist is
unchanged. Card 03's live snapshot gate and reentrant refresh handling remain
in force.

## Bounded update and validation contract

- Every new mapped logical update starts at the primary, followed by at most
  one approved fallback. A successful primary never requests fallback.
- Each approved transport has a **60-second total deadline**, starting before
  offline/throttle waiting, and a **32 MiB decoded download/input limit**.
  Offline attempts fail immediately. Mapped requests use `DoNotRetry`; the
  two transports do not multiply an internal retry loop.
- The existing updater checks on its **11–13 hour cadence** (12 hours with
  ±60 minute jitter). It is retained, rather than replaced by another updater.
  Custom/unmapped legacy transport behavior is unchanged. Long-running live
  connectivity soak was not performed; deterministic clock tests cover the
  changed deadlines, queues and absence of inner retries.
- Card 01's manual result window remains **45 seconds**, explicitly reporting
  that an update may continue. This differs from the per-transport deadline;
  it does not falsely cancel or claim activation of ongoing work.
- Approved requests omit credentials and reject all HTTP redirects before
  following them. The pinned SimpleURLLoader API permits destruction in the
  redirect callback. Filter-declared redirects are rejected too.
- Primary network/HTTP/timeout, unusable content and conversion/structural
  validation failures can trigger fallback. HTML, empty/oversized input,
  incomplete network bodies, unsupported format, invalid FlatBuffers, wrong
  schema/embedded identity and zero supported rules cannot activate.
- Plaintext ABP headers are validated, including BOM handling. Only the two
  reviewed headerless domain-list identities (BadBlock and 1Hosts) may use the
  title/domain format. Real parsing and conversion are still mandatory.
  A single accepted rule is sufficient; no arbitrary large minimum or shrink
  heuristic rejects legitimate small lists. Comment-only/unsupported-only
  candidates are not usable updates.
- New tokens distinguish transports and replacement updates. Stale responses
  cannot convert/activate; stale absolute temporary paths are discarded.
  SimpleURLLoader owns partial download cleanup and the converter removes its
  input on every result path. Terminal state is erased before client callbacks.
- A privilege change invalidates incompatible conversion without trying to
  bypass policy through fallback. Cancellation remains owned by the existing
  maintainer/manual batch. Working installed or bundled data stays active until
  validated replacement data is successfully stored and activated.

Structural/content validation occurs before storage. A later storage failure
retains old working data and reports failure; retrying transport does not repair
a disk/storage failure. Card 05 retains ownership of stronger crash/storage
transaction recovery.

## Diagnostics and counters

The bounded local sidecar adds `primary_failure`, `fallback_attempted` and
`fallback_outcome`. It persists latest attempt, cancellation/interruption,
parsed-awaiting-storage and activation outcomes separately from last successful
source and active data. Captured manual entries retain their fallback details
when a list is removed. No rule contents or browsing activity are added.

One terminal failed logical download increments the consecutive failure count
once, including when both transports fail. A primary failure followed by a
valid activated fallback is one success, with the primary failure still
visible. Parsing alone is not activation. Existing successful-request counters
include historical HEAD requests; the controlled cases below use GET. Storage
failures remain separately reported and do not masquerade as network success.

## Installed demonstration

The **same verified x64 APK** was installed with `-r`. Testing used the
task-created Android user13 after a validated profile/shared-preference backup.
It used the real network request, parser, converter, validator, storage,
activation, JNI report and page engine.

The transport fixture requires protected root-only Chromium command-line
settings, exact host resolution for the two approved origins, and a temporary
certificate's specific SPKI. The flags file remained root-owned and was given
only the task app/user's SELinux category so that this profile could read it.
SELinux stayed **Enforcing**. No production mapping/trust override, localhost
subscription exception, new release test hook, system trust-store change or
global certificate bypass was added. The ordinary release environment cannot
create this protected setup. The [temporary certificate's public metadata](fixture-certificate-public.json)
and harness sources document the injection; its private key is outside the repo.

An initial disconnected emulator network and an unreadable test-flags label
were corrected before accepting controlled results. A system-user browser was
stopped to isolate the shared debug socket. The probe checks the task-owned
browser UID. A read-only [focused-window helper](RoadiumUiDump.java) captures
the secondary user's actual diagnostic dialog and excludes offscreen nodes.
These harness corrections did not change the verified browser binaries.

The loopback TLS server records only phase, approved host/path, status, byte
count and credential-presence booleans. The [24 recorded requests](transport-requests.jsonl)
confirm exact primary/fallback ordering, no credential-bearing requests and
**zero requests to the unapproved redirect target**.

| Installed case | Result | Evidence |
| --- | --- | --- |
| Primary 503, advanced opt-out | Both exact fallbacks activate version `203001010004` under canonical identities; basic request/cosmetic filtering works; privileged rule rejected | [Report](fallback-opt-out-report.txt), [probe](fallback-opt-out.json), [profile](fallback-opt-out-profile.json) |
| Enable advanced through UI | Only AntiCV refreshes through primary/fallback; supported property-read rule becomes observable after activation | [Report](fallback-advanced-enabled-report.txt), [probe](fallback-advanced-enabled.json), [profile](fallback-advanced-enabled-profile.json) |
| Valid primary | Version `203001010005` activates; exactly two primary requests, no fallback | [Report](primary-success-report.txt), [probe](primary-success.json), [profile](primary-success-profile.json) |
| Both transports 503 | One failure per list; prior version, signatures, source, policy and filtering retained | [Report](both-transports-fail-report.txt), [probe](both-transports-fail.json), [profile](both-transports-fail-profile.json) |
| Restart after failure | Failed attempt and working data survive restart; fresh document still filtered | [Report](failure-restart-report.txt), [probe](failure-restart.json), [profile](failure-restart-profile.json) |
| Primary HTTP redirect | Redirect target never fetched; approved fallback activates `203001010006` | [Report](redirect-rejected-report.txt), [probe](redirect-rejected.json) |
| Primary HTTP 200 HTML | HTML never activates; fallback activates `203001010007` | [Report](html-rejected-report.txt), [probe](html-rejected.json) |
| Primary filter-declared redirect | Directive cannot rename identity or fetch its target; fallback activates `203001010008` | [Report](metadata-redirect-rejected-report.txt), [probe](metadata-redirect-rejected.json) |

The [page](card04.html) and [restricted probe](probe-fallback.mjs) observe
`override-property-read roadiumProbe undefined`, ordinary hiding and an
advertising request that fails with `ERR_BLOCKED_BY_ADMINISTRATOR`. Downloaded
advertising code is never executed. With advanced disabled the property stays
`fixture-value`; after the enabled trusted refresh it reads `undefined` on a
new document. Existing basic data keeps working while that refresh is pending.
No YouTube effectiveness claim follows from these tests.

[Installed assertions](installed-verification.json) validate all eight cases.
[Retention assertions](retention-verification.json) compare the cached
signatures, complete filtering configuration, installation/success history and
one-error-per-logical-update counters before failure, afterward and on restart.
Screenshots/XML accompany each report basename.

## Automated checks and independent review

- [Native](native-results.json): **57 passed**, API 33 Automotive.
- [Diagnostics](diagnostics-results.json): **28 passed executions**, API 29/36.
- [Media](media-results.json): **26 passed executions**, API 29/36.
- Ordered overlay loader: **16 passed**; actual-resource package gate: **8 passed**.
- Final post-review, formatted source compiled and reran all 111 focused
  executions successfully. Both complete package builds and artifact verifiers
  passed. [Runner commands](run-tests.sh) use the actual generated targets.
- Both source/fork diff checks and all exported artifact/source hashes passed.

Focused tests cover primary/fallback success and terminal failure, canonical
identity, live policy, stale response/conversion and replacement races,
cancellation, owned temporary cleanup, wrong identity/schema, empty/unusable
conversion, headerless format, exact mappings and diagnostic persistence.
Real SimpleURLLoader tests cover deadline/offline/throttle queues, stale queue
release, pre-follow redirect rejection, oversized/incomplete responses and
destruction. Existing Card 01–03 lifecycle/trust/media checks also pass.

The broad upstream network test support has an incompatible Cromite SSL socket
mock. A narrow **test-only** target compiles the three pinned helper sources
needed here; production networking and existing SDK targets are unchanged.
The first native run exposed two fixture mistakes (inventory exclusions and
raw-header encoding); both were corrected before the final all-pass runs.
The full older SDK test suite is not claimed as passing.

Local analysis was advisory. A proposed broad prefix/filename mapper was
rejected in favor of complete exact pairs. Claims about missing redirect or
retry guards were checked against actual source; existing guards were retained.
Independent reviews cover [production source](review-source.json),
[mapping/diagnostics](review-diagnostics.json), [tests](review-tests.json) and
[cleanup](review-cleanup.json). No blocking findings remained. Suggested extra
401/403 cases were not added to mirror the same non-200 branch; 404 native and
503 installed cases exercise it. Complete known-inventory tests address the
mapping review's coverage question. These approvals are advisory, not authority
to modify or publish anything.

## Cleanup and remaining gates

[Cleanup verification](cleanup-verification.json) confirms original Preferences
and all seven shared-preference files are byte-identical to backup, all five
original cached-list hashes match, and selections/custom rules/exceptions,
explicit advanced opt-out and global state are restored. Owner and SELinux
labels match the original profile. The app is stopped; test flags, capture
helper, port mappings and owned loopback TLS listener are removed. The existing
HTTP fixture server was preserved. Wi-Fi/mobile settings remain enabled and the
existing AndroidWifi network was reconnected. Private backups remain outside
the repo.

Card 04 did not change vehicle properties. CarService was unavailable at
cleanup, so this record does not claim a new parked/driving-state verification.
Physical vehicle checks, extended connectivity soak and release signing remain
release gates. Card 05's crash/storage recovery work is still on hold.
