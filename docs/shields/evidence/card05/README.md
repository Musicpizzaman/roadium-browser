# Card 05 verification record

Card 05 is implemented and verified on the installed x64 Automotive build.
Atomic publication retains a valid previous generation; restart selects valid
current, previous or eligible bundled data under the user's current choices.
The x64 and ARM64 APKs and bundles passed artifact verification. Main-repository
changes remain uncommitted. Cards 06–09 remain on hold.

## Source and packages

The sixth overlay is
[`0006-roadium-last-known-good-recovery.patch`](../../../../build/roadium/patches/0006-roadium-last-known-good-recovery.patch),
SHA-256 `8a878985e390b893f7987f800e9824838ae570389ef420c7cbf5046ce5738004`.
The first five overlays are unchanged. Chromium `153.0.8010.37`, Cromite
`11507ac1061b5ea227806f5e84db5a57df6ccf6a` and version-code offset `10` remain pinned.
The exact cumulative source diff is
`4864d222f1e7fbb8fc0d58e3f612420501b1582015f270ad89c8cc44e3c061c5`;
the resulting tree is `ea096fd60e709acd07be89f125dabb13a481585f`.
All [14 affected source files](affected-source-files.json) are byte-identical
between the isolated development checkout and both full build checkouts.

The [x64 manifest](x64-build-manifest.json) and
[ARM64 manifest](arm64-build-manifest.json) verify source, ABI, SDK manifests,
required Automotive declaration, APK signatures, ZIP integrity, bundletool
validation and the actual bundled resource bytes. Bundle provenance remains
the frozen Cromite pages revision `338336d9e640489c648d47d606cb0030064c4e0f`.
The packages are exported under
`E:/Android Auto Projects/RoadiumBuild/artifacts/153.0.8010.37-roadium-shields-card05-{x64,arm64}/`.

| Package | SHA-256 |
| --- | --- |
| x64 APK | `002c2eb636653496fdd1804958f92bcc66fcf5a4293f7e8585d56987acf2ce6b` |
| x64 AAB | `bc11d292e0438c2425eee535723a62553f5475e67c2dcb9c2a833ceb1bc98e84` |
| ARM64 APK | `f05cbafdc2ce1719c64a9ef5b1be56b66ff21fd91dfa3a636d882f5d3c4539e4` |
| ARM64 AAB | `f6f126a3302719251b6f50943ca0ffda0be658be6f4913b40acb090756f9e407` |

APKs use the existing development certificate; AABs are unsigned. These are
verified development artifacts, not production-signed distribution packages.

## Transaction, retention and recovery

The implementation extends the existing Eyeo persistent storage and maintainer.
It preserves canonical subscription identities, transport policy, GPL notices,
selection semantics and Card 03's live privilege gate.

1. Validate complete FlatBuffers structure, current schema, canonical identity,
   trust-sensitive indexes and actual supported indexes. One-rule lists remain
   valid; no arbitrary shrink or minimum-size heuristic is used.
2. Write a fresh immutable candidate, flush its file and sync its directory.
   Recheck stored bytes, structure, identity and SHA-256 before publication.
3. Flush the validated prior generation and atomically publish its previous
   record, using an owned pending file, file flush, rename and directory sync.
4. Publish the new current record with the same ordering. Only then may the
   main callback swap active state and publish success counters/history.
5. Prune unreferenced owned generations after success and on startup. Failed
   work keeps the prior active collection. An interrupted candidate cannot be
   inferred to be committed just because its bytes parse.

Each identity has independently validated current and previous JSON records.
They bind exact owned basenames to identity, schema, digest, generation time,
actual source, conversion policy and bounded rule counters. New commit authority
is independent of asynchronously saved preference signatures. Legacy files
require their original preference signature and full structural/schema checks;
duplicate migration chooses deterministically by modification time and filename.

Restart tries current, then recorded previous. If neither is usable, the
existing provider supplies compatible bundled data only for eligible selected
identities. Other selected lists report unavailable. Configuration is preserved;
recovery never restores an intentionally removed list or enables scriptlets
against the current setting. The existing periodic schedule remains unchanged;
recovery adds no retry loop. Card 04's approved-transport bounds still apply,
and legacy custom-bootstrap retry behavior is unchanged.

All storage I/O uses one sequenced runner. Cancellation permits prevent obsolete
work from publishing where possible; a cancelled post-publication callback can
discard only its exact current candidate and cannot roll back newer work.
Retirement preserves previous data, explicit unsubscribe removes both versions,
and discard restores the recorded prior. Success is counted after acceptance
into current state. A storage failure increments one logical failure; recovery
does not invent a download success.

Steady state retains at most two reachable generations per identity, each capped
at **128 MiB** of converted data. There can be one additional candidate during
commit. This binary limit is separate from Card 04's **32 MiB plaintext** limit.
Records and fixed pending records are each limited to **16 KiB**. Older mapped
snapshots can retain unlinked blocks until their references are destroyed; the
two-file bound is not an absolute quota on all live memory-mapped leases.

Cleanup is nonrecursive and checks exact owned filename grammar and symlinks.
JSON cannot supply an arbitrary or traversing path. Legacy pruning additionally
requires a real signature and valid canonical data. Unrelated files remain.
The installed orphan test verifies that preservation explicitly.

## Automated verification and review

The final post-review [native results](native-results.json) contain **74 passes**,
including 17 storage/recovery tests. [Diagnostics](diagnostics-results.json)
passed **28 executions**, and [media](media-results.json) passed **26 executions**
across API 29/36. All **128 focused executions** passed without retries.
The overlay loader's **16 tests** and package-resource gate's **eight tests**
also passed. The full older SDK test suite is not claimed as passing.

Native cases exercise all publication boundaries on a real temporary filesystem,
real parsing/filtering, current and record corruption, identity/schema mismatch,
invalid candidates, write/rename/publication failures, cancellation, stale
discard, legacy migration, preference-independent reload and repeated bounds.
The existing Cards 01–04 lifecycle, trust, bundle, transport and media checks
continue to pass. See [run-tests.sh](run-tests.sh) for the focused commands.

Local workers were advisory. Independent reviews covered
[transactions](review-transaction.json), [integration](review-integration.json),
[tests](review-tests.json), the added
[production guard/retire/discard regression](review-guard-test.json),
[loaded-data diagnostics](review-loaded-diagnostics.json) and
[cleanup](review-cleanup.json). No blocking findings remained. The production
guard test was added in response to the review. Suggestions to invoke the raw
transaction helper concurrently conflict with its single-sequence contract;
real asynchronous requests are serialized. Empty/boilerplate review fields and
claims about nullable `std::string` values were not treated as defects.

## Installed checks

The exact verified x64 APK was installed on API 33 Automotive in this task's
read-only `RoadiumAAOS33` session. Original saved users were 0 and 10. A new
`ShieldsCard05` user 11 held all fault data; no other profile files were edited.
The profile selected EasyList, Anti-Circumvention and a custom HTTPS subscription,
plus one manual rule and one site exception.

The temporary root-owned command-line file was labelled only for that app/user
with SELinux **Enforcing**. Host resolution and one specific temporary SPKI
routed controlled HTTPS responses through the stock APK; no production mapping,
trust store or native allowlist was weakened. The own custom subscription stayed
untrusted and received no fallback mapping. The HTTP page used only fixed local
probes; downloaded advertising code was never executed.

The [installed verifier](installed-verification.json) checks **20 scenarios**.
Every report has a corresponding XML/PNG, sanitized configuration snapshot,
storage records/hashes and a fresh-document probe. All cases demonstrated actual
`ERR_BLOCKED_BY_ADMINISTRATOR` filtering. Ordinary fixture cosmetics remained
hidden for downloaded-list cases; the generic fixture selector is not in the
real bundle, so bundled recovery is established by actual network blocking.

| Scenario | Observable result |
| --- | --- |
| [Initial opt-in](initial-advanced-enabled-report.txt) | Accepted v1, basic/cosmetic blocking and supported trusted scriptlet |
| [Second generation](second-generation-report.txt) | Accepted v2; prior retained |
| [Explicit opt-out](advanced-opt-out-baseline-report.txt) | Basic filtering stays active; fresh page has no scriptlet effect |
| [Current corrupt](previous-version-recovery-report.txt) | Previous EasyList v1 and Anti-CV v2 selected; cached privileged bytes still obey opt-out |
| [Stop during download](force-stop-download-report.txt) | Partial response cannot replace working v3 |
| [Stop after candidate persistence](force-stop-candidate-report.txt) | Unpublished v4 ignored; current v3 retained |
| [Stop after previous publication](force-stop-previous-report.txt) | Current v3 survives interrupted current-record publication |
| [Stop after current publication](force-stop-published-report.txt) | Committed v4 loads before a prior callback could count success |
| [Storage failure](storage-error-retention-report.txt) | Actual pending-record write failure retains working v3; one failure |
| [Storage failure restart](storage-error-restart-report.txt) | Working v3 and failure counters persist |
| [Invalid update](invalid-retention-report.txt) | HTTP 200 HTML from both transports rejected; working v3 retained |
| [Invalid update restart](invalid-restart-report.txt) | Same working data and failure state after restart |
| [Unpublished orphan](orphan-recovery-report.txt) | Candidate/pending ignored and pruned; unrelated sentinel preserved |
| [Schema mismatch](schema-recovery-report.txt) | Correctly hashed but incompatible FlatBuffers metadata rejected; previous selected |
| [Explicit removal](explicit-removal-recovery-report.txt) | Anti-CV remains unselected and both cached generations are removed |
| [Activation restart](activation-restart-report.txt) | Accepted v5 reloads with previous retained |
| [Repeated updates](repeated-update-recovery-report.txt) | v6→v7→v8, restart each time, two-generation bound |
| [Both copies corrupt offline](offline-bundled-recovery-report.txt) | Eligible bundles actually block; custom list honestly unavailable |
| [Metadata missing offline](missing-bundled-recovery-report.txt) | Valid but unrecorded files are not trusted; bundles block |
| [Repair after recovery](repair-after-recovery-report.txt) | Recovered previous data can update to v6 and reload normally |

The four forced stops used actual running updates. A partial TLS response pauses
download; root-only FIFO fixtures pause the owning process at candidate,
previous-record and post-current-publication boundaries. After two seconds of
stable pre-callback state, `am force-stop` kills the app, the FIFO is removed,
and restart proves recovery. No release-facing fault switch is added; the native
test callback is per-instance and unbound by the production factory. The
[published-boundary record](force-stop-published-boundary.json) proves the durable
current changed while preference version and success count had not advanced.

Raw preference snapshots precede the live UI reports and can lag asynchronous
persistence. Loaded versions/origins are therefore verified from in-process
diagnostics, backing-file hashes and actual filtering, rather than inferred from
those early snapshots. The generation timestamp restores the accepted data's
time; a crash can leave advisory preference history behind the committed record.

The [request log](transport-requests.jsonl) records only controlled request
metadata and credential-header booleans. Initial default-list/component requests
remain visible and are distinguished by phases; this record does not claim that
every request is one of the accepted filter cases. No cookies or authorization
headers were observed. Two fixture assumptions (FIFO type capitalization and
duplicate schema strings) were corrected before their accepted cases passed.

## Cleanup and remaining limits

[Cleanup verification](cleanup-verification.json) records removal of the test
flags, helper, ports and disposable user, restoration of user 10 and network
settings, closure of the two verified own fixture processes, and shutdown of the
own read-only emulator without saving a snapshot. Original users 0/10 remain.
SELinux stayed enforcing; vehicle properties were not changed. The legacy
PowerShell stop command failed; the same verified PIDs were stopped through
`.NET Process.Kill`, and process/listener exits were confirmed. Private keys and
profile archives remain outside the repository. A pre-launch disk hash was not
captured, so byte-for-byte saved-AVD verification is not claimed.

Android/POSIX file flush and directory fsync provide the publication ordering.
This record proves process interruption and filesystem error handling; it does
not prove survival of hardware that violates fsync or corruption of both copies.
Physical ARM64 Android 12 vehicle/driving checks, production upload-key signing,
literal device ENOSPC, abrupt power loss, long-lived mapped-view disk pressure and
extended connectivity/I/O soak remain release checks. The actual write/replace
error branches were tested without filling a shared filesystem.

Card 09 can reuse the documented boundaries, per-case version/origin assertions,
configuration checks and [verification manifest](verification.json). Cards 06–09
remain on hold.
