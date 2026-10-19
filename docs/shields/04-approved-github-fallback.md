# Card 04 — Add automatic approved GitHub fallback downloads

Priority: **P0** · Effort: **Medium–high** · Milestone: **Reliable protection**
Status: **Implemented and verified — x64 Automotive; x64/ARM64 packages verified**

Owner: Codex  Reviewer: Local Ollama independent review  Issue: local task (no external issue assigned)
Branch/patch: develop / 0005-roadium-approved-filter-fallback.patch  Verification completed: October 15, 2026 (Central)

## Outcome

When a known Cromite subscription's primary transport fails or produces
unusable data, Roadium attempts an approved same-list GitHub transport,
validates it and reports the source used. Original identity and privilege
policy remain unchanged, and failure of both transports retains working data.

## Prerequisites

**Required card dependency:** [Card 01](01-audit-and-diagnostics.md), including
real update completion/error reporting and source diagnostic contracts.

- [x] [PRE-01](README.md#pre-01--safe-patch-series-integration) for the overlay.
- [x] [PRE-02](README.md#pre-02--reproducible-verification-environment) for mock
  transport, conversion and lifecycle tests without live network dependency.
- [x] Enumerate exact known Cromite identities/filenames from the pinned
  configuration; identify which have a valid same-list fallback.
- [x] Trace transport redirects/retries/timeouts and converter identity inputs.
  Distinguish HTTP redirects from list metadata subscription redirects.

**Supporting:** Card 03 adds default policy tests. Card 05 strengthens storage
and restart recovery. This card must preserve existing valid data on failure
even before Card 05; an identified retention defect blocks acceptance.

## Source spots

Chromium source:

- `components/adblock/core/subscription/subscription_config.cc` and `.h`
- `components/adblock/core/subscription/subscription_downloader_impl.cc` and `.h`
- `components/adblock/core/subscription/subscription_persistent_metadata_impl.cc`
- `components/adblock/core/net/adblock_resource_request_impl.cc` and `.h`
- `components/adblock/core/subscription/subscription_validator_impl.cc`
- `components/adblock/core/subscription/test/subscription_downloader_impl_test.cc`
- `components/adblock/core/net/test/` for transport/redirect behavior.

Fork: separate fallback overlay; fixed mapping/release checks and deterministic
fixtures under `tools/roadium/`; update source documentation.

## Source and identity contract

Primary distribution prefix: `https://uazo.github.io/cromite/filters/`

Fallback prefix: `https://raw.githubusercontent.com/uazo/cromite/pages/filters/`

Use a reviewed mapping of exact canonical identity to exact approved transport
URL. These prefixes are not permission to construct a fallback for every
custom URL or trust every file on either host. The GitHub `pages` branch is
the runtime update transport; immutable revisions are used for bundled inputs.

| Canonical identity | Exact fallback transport | Privilege classification | Mapping evidence |
| --- | --- | --- | --- |
| Known EasyList identity | Approved `easylist.txt` path | Existing nonprivileged policy | [Exact pair](evidence/card04/fallback-mapping-inventory.json); native inventory and installed primary/fallback cases |
| Known anti-circumvention identity | Approved `abp-filters-anti-cv.txt` path | Existing trusted policy plus advanced setting | [Installed canonical identity and current policy](evidence/card04/installed-verification.json) |
| Other known subscription | Reviewed exact filename/path only | Existing policy | 31 reviewed pairs; headerless BadBlock/1Hosts format explicitly scoped; [inventory](evidence/card04/fallback-mapping-inventory.json) |
| Custom/unknown identity | No automatic mapping | Untrusted | Native exact-identity/look-alike/raw/manual tests; no mapping for custom, test, AA, EasyPrivacy or experimental raw/master |

## Work breakdown

### A. Specify bounded primary/fallback state

- [x] Primary is always the first attempt for a new update request. On network,
  timeout, HTTP, invalid content or conversion/validation failure, attempt the
  mapped fallback once within the existing bounded retry system.
- [x] Keep transport URL separate from the map key, canonical converter URL,
  callback identity, metadata identity and privileged-list decision.
- [x] Avoid calling ordinary `StartDownload(fallback_url)` in a way that creates
  a second subscription or changes trust. Audit every identity consumer.
- [x] Preserve cancellation ownership and prevent stale primary/conversion
  callbacks from racing a fallback or a replacement update.
- [x] Define finite timeout, retry count, maximum bytes and backoff. Record
  values/reasons after inspecting existing transport behavior; do not multiply
  retries independently at multiple layers or retry continuously offline.
- [x] Clean temporary files on every failure/cancel path; invoke completion
  exactly once for the original subscription.

### B. Enforce approved transport and validate content

- [x] Require HTTPS, expected host, exact repository/branch/directory/filename,
  expected port and no credentials. Reject URL variations that leave the
  approved mapping, including traversal and unauthorized paths/queries.
- [x] Disallow fallback redirects to arbitrary domains or unapproved files.
  Configure transport redirect policy before fetching redirected content,
  rather than detecting an unauthorized destination only after consuming it.
- [x] Apply equivalent policy to filter-declared redirects. Do not let a
  `Redirect` directive turn fallback bytes into a newly trusted identity.
- [x] Check response length/limits and supported downloaded format. Reject
  HTML error pages, empty/oversized/truncated data and unsupported input.
- [x] Run actual parsing/conversion and FlatBuffers validation. HTTP 200,
  content type and a text-looking header alone do not establish usability.
- [x] Check canonical embedded identity and meaningful accepted rules where
  appropriate. Define per-list plausibility policy without rejecting legitimate
  small lists or quietly dropping unsupported rules from compound semantics.
- [x] Recheck current privilege preference at activation; fallback can never
  expand the existing trusted-list or scriptlet command policy.

### C. Preserve working data and expose results

- [x] Keep the prior installed list active until a new validated version is
  successfully stored/activated. Both-source failure must not uninstall it.
- [x] Record primary failure category, fallback attempt/outcome, last successful
  source and active source/version separately through Card 01.
- [x] Count one logical update result consistently; decide how transport-level
  attempts relate to existing lifetime counters and document those semantics.
- [x] Preserve existing subscription selection and future automatic update
  schedule. Do not replace the updater or permanently rewrite canonical URLs.

## Acceptance and tests

| Scenario | Required result | Evidence spot |
| --- | --- | --- |
| Valid primary | Activates accepted data; fallback not requested | [Installed report](evidence/card04/primary-success-report.txt), exactly two primary requests and no fallback |
| Network/HTTP/timeout primary failure | Bounded mapped fallback succeeds under canonical identity | Real-loader deadline/offline tests, native fallback control flow, [installed primary 503/fallback success](evidence/card04/fallback-opt-out-report.txt) |
| HTTP 200 HTML/invalid conversion primary | Fallback attempted; bad primary never activates | [Installed HTML rejection](evidence/card04/html-rejected-report.txt), native real-converter validation tests |
| Both sources unusable | One terminal failure; prior valid list continues filtering | [Failure](evidence/card04/both-transports-fail-report.txt), [fresh-document filtering](evidence/card04/both-transports-fail.json), [restart](evidence/card04/failure-restart.json) |
| Fallback cross-host/path redirect or metadata redirect | Rejected before unauthorized activation/trust | Native pre-follow cross-host test; [installed HTTP redirect](evidence/card04/redirect-rejected-report.txt) and [metadata redirect](evidence/card04/metadata-redirect-rejected-report.txt), no target fetch |
| Unknown/custom URL or lookalike mapped URL | No approved fallback or privilege gained | Native complete inventory, exact URL variations, untrusted redirect and raw/manual privilege tests |
| Untrusted list with copied privileged rule | Snippet remains rejected even through transport fixtures | Native untrusted text/cached/manual scriptlet tests; canonical fallback preserves trust policy |
| Oversized/truncated/empty payload | Rejected within bounded resources; completion reported | Native real SimpleURLLoader oversize/incomplete-response and strict-converter empty/format/rule-presence tests |
| Cancel/unsubscribe/re-toggle during fallback | No stale activation, callback duplication or temp-file leak | Native stale-response/temporary cleanup, cancelled fallback, replacement, live opt-out and storage cancellation regressions |
| Poor connectivity/repeated scheduled failures | Finite work and measured backoff | Mock-clock 60-second queue/deadline and no-inner-retry checks; unchanged 11–13h cadence audited; extended live soak remains a release gate |

Mocks establish control-flow/security behavior; also run an installed-build
primary-failure/fallback-success check using controlled transport injection
that is absent or inaccessible in release builds. Do not weaken production
allowlists for test servers.

## Deliverables and handoff

- [x] Separate fallback patch and transport/conversion/cancellation tests.
- [x] Exact mapping, timeout/size/retry policy and diagnostic counter semantics.
- [x] Trust identity evidence and real installed-build fallback demonstration.
- [x] Handoff to Card 05: validated-data ownership, terminal failure contract,
  temporary paths and active-source metadata transaction requirements.

## Decisions and completion record

**Mapping:** 31 complete reviewed canonical/transport pairs. No wildcard host,
prefix-based mapping or identity rewrite. EasyPrivacy, Acceptable Ads exception
rules, custom/test subscriptions and the existing raw/master experimental
identity are unmapped. The exact trusted identities and scriptlet allowlist
remain unchanged. [Mapping evidence](evidence/card04/mapping-verification.json).

**Bounds:** primary first, one fallback maximum, 60 seconds per approved
transport including offline/throttle waiting, 32 MiB decoded input, no inner
retries. Existing automatic checks remain 12h ±60min. The existing 45-second
manual result window truthfully says updates may continue. HTTP redirects are
rejected before follow; filter-declared redirects are rejected before a new
identity/fetch. Supported plaintext, actual parsing, canonical embedded identity,
current schema, verified FlatBuffers and at least one supported rule are required.
Only two exact headerless domain-list identities use the reviewed alternate
format. Small valid lists remain supported.

**Ownership and counters:** tokens identify each transport/generation; stale
callbacks cannot activate, converter/loader ownership handles input/partial
files, and stale absolute paths are explicitly discarded. Old data remains
until successful storage activation. Both transport failures yield one terminal
failure per original list; fallback activation is one success. Latest primary
failure/fallback outcome and active last-success source are independent.
Storage failure retains old data; Card 05 owns stronger crash/storage recovery.

**Patch:** `0005-roadium-approved-filter-fallback.patch`, SHA-256
`ebdbd3da426e96ab7ab49aaf4e04c1c3512c4edd23e1c0d35455304052f96552`.
First four overlays unchanged. Final source tree:
`a33a2961c7502d487058c810b1084f7c66aa1fd5`.

**Validation:** 57 native, 28 diagnostics executions and 26 media executions
passed on the final post-review source; loader 16 and package gate 8 passed.
Both architecture APK/AAB builds and verifiers passed. Eight installed cases
and 24 exact fixture requests prove primary/fallback behavior, current-policy
effects, invalid-content/redirect rejection, one-result counters and retained
working data/signatures across failure and restart.

The controlled transport uses protected root-only settings and a temporary
specific SPKI with SELinux enforcing; no release mapping or trust exception was
added. Source, mapping/diagnostic, tests and cleanup local reviews completed
without blocking findings. The detailed record explains setup corrections,
review dispositions, commands and evidence.

**Cleanup:** original Preferences and seven shared-preference files match the
validated backup byte-for-byte; all five cached-list hashes match. Original
choices, rules, exceptions, ownership and labels are restored. Test flags,
ports, capture helper and owned TLS listener are removed. Card 04 did not change
vehicle properties; CarService was unavailable for a new driving-state check.

Acceptance: Codex verification, October 15, 2026 (Central), with advisory local
Ollama review. [Detailed evidence and Card 05 handoff](evidence/card04/README.md),
[acceptance JSON](evidence/card04/verification.json).
Physical ARM64 Android 12 vehicle/driving checks, production upload-key signing
and extended connectivity soak remain release gates. Cards 05–09 remain on
hold. Main-repository changes remain uncommitted.
