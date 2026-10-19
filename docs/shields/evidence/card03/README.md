# Card 03 verification — October 14, 2026

Card 03 is implemented and verified on the installed x64 Automotive build.
Both x64 and ARM64 APK/AAB builds passed artifact verification. Cards 04–09
remain on hold. [Machine-readable acceptance](verification.json) records the
final source identities, package hashes, profile comparisons and runtime cases.
Physical ARM64 Android 12 vehicle checks and production signing remain release
gates; these development artifacts are not Play release uploads.

## Source and artifacts

The fourth overlay is `0004-roadium-advanced-filtering.patch`, SHA-256
`fa0e7a57e72696158efca236c66666b52dda20449a6a4ab77c7344d2d46f2b69`.
The first three patches are byte-identical to their accepted versions.
The cumulative source diff is
`eb6fbe801190d11fb9a5303033540fe8ed33316bc658d476b1b8a3079cb09f4f`;
the resulting Chromium tree is
`827c5751427f01b0ac1dca82a66886bb1dbf2e29`.

[x64 provenance](x64-build-manifest.json) and
[ARM64 provenance](arm64-build-manifest.json) bind the builds to Chromium
153.0.8010.37, Cromite `11507ac1061b5ea227806f5e84db5a57df6ccf6a`, all four
overlays and the final artifacts. The installed x64 APK SHA-256 is
`3c1aee8bb2036b44f82c39582f276e2f5e71d6c7b5248621991800db1331f91a`.
All four exported package hashes were rechecked. Package verification covered
source identity, actual APK/AAB bundled resources, ZIP integrity, ABI, SDK
manifests, required Automotive declaration, APK development certificate and
bundletool validation. AABs are unsigned. Build manifests retain their original
runtime-pending field; this record supplies subsequent installed acceptance.

## Preference provenance and migration

The pinned production code registers `kAllowPrivilegedFilters` and writes it
through the explicit configuration setter. No old automatic write of `false`
was found. Changing its registered default to `true` therefore changes new and
existing unset profiles without writing a value or adding a migration marker.
Every stored false/true is preserved, including any historical false whose
intent cannot be established. Repeated startup cannot rewrite the choice.

| Installed case | Result | Evidence |
| --- | --- | --- |
| Fresh profile, offline | No stored advanced override, zero downloaded signatures; advanced enabled and both bundles loaded | [Preferences](fresh-offline-profile.json), [report](fresh-offline-report.txt), [screenshot](fresh-offline-report.png) |
| Upgrade with inherited default | Still unset on disk, effectively enabled; old basic AntiCV truthfully awaits trusted refresh | [Before](upgrade-inherited-before.json), [after](upgrade-inherited-after.json), [report](upgrade-inherited-report.txt) |
| Upgrade with explicit false | Still disabled | [Before](upgrade-explicit-false-before.json), [after](upgrade-explicit-false-after.json), [report](upgrade-explicit-false-report.txt) |
| Upgrade with explicit true and global blocker off | Advanced remains true, global remains off | [Before](upgrade-explicit-true-global-off-before.json), [after](upgrade-explicit-true-global-off-after.json), [report](upgrade-explicit-true-global-off-report.txt) |
| Change after upgrade | Advanced can be toggled off/on while global remains off | [Disabled preference](global-off-advanced-disabled.json), [independent switch](global-off-independent-switch.png) |
| Restart after opting out | Explicit false remains persisted with cached data | [Preferences](trusted-disabled-restart-profile.json) |

The three upgrade comparisons assert identical complete filtering
configurations and cached-list signature maps: list selections, custom rules,
site exceptions and global state were retained. Reports were recaptured on the
final APK after its UI correction. The earlier inherited switch screenshot is
supplementary; final report/profile evidence governs acceptance.

## Lifecycle and trust contract

The persistent configuration observes preference changes. A shared atomic gate
also updates existing subscription snapshots immediately. On newly processed
documents, snippets and privileged inline styles require both current policy
and the exact existing trusted subscription identity. Global blocking remains
an independent outer gate. This does not undo JavaScript already executed in a
previous document; reload/new-document behavior is tested below.

Trusted identities remain the canonical AntiCV URL
`https://uazo.github.io/cromite/filters/abp-filters-anti-cv.txt` and the existing
exact experimental URL
`https://raw.githubusercontent.com/uazo/cromite/master/tools/filters/experimental-cromite-filters.txt`.
The raw/pages AntiCV look-alike gains no trust. Manual `adblock:custom`, unknown
subscriptions and forged privileged cached data cannot bypass the runtime
gate. The pre-existing debug localhost exception is unchanged and is excluded
by the official release build. Header filters remain disabled and the scriptlet
command/argument allowlist is unchanged.

Changing the switch does not add/remove selected lists, enable global blocking
or force every list to download. Trusted selected data previously converted
without privileges is refreshed through the existing scheduler. Working basic
data stays available. Active conversion policy is recorded only after storage
activation. A policy mismatch discards stale conversion results; a single
pending refresh survives active download/storage work. Downloader terminal
state is cleared before callbacks so a reentrant refresh cannot reuse an old
request. Unsubscription clears pending work. No Card 04 fallback/timeouts are
included.

Readiness requires global and advanced settings, current trust and active
privileged data. Old/unknown basic cache reports pending refresh. The freshly
converted privileged AntiCV bundle is usable offline; EasyList remains
nonprivileged. Disabling advanced filtering retains those bytes but stops
privileged execution.

## Observable installed scriptlet tests

These developer tests use only the task-created, backed-up Android user13.
Real FlatBuffers were produced by the pinned native converter and root-seeded
into its disposable profile while offline. This simulates loaded trusted and
untrusted caches; it does not test network authenticity or grant trust through
a production override. The untrusted buffer deliberately contains privileged
data to test the runtime gate, while manual rules use the normal custom-rule
conversion path.

The [filter fixture](scriptlet-fixture.txt) contains supported
`override-property-read roadiumProbe undefined`, an unsupported
`simulate-mouse-event`, ordinary cosmetic hiding and an ordinary request rule.
Both [trusted](trusted-fixture-conversion.json) and
[untrusted](untrusted-fixture-conversion.json) privileged fixture conversions
accepted three rules and rejected one unsupported command. The local
[page](card03.html) sets the property to `fixture-value`, counts button clicks
and exposes narrow observations to the [developer probe](probe-advanced.mjs).
The fetched advertising bytes are never executed.

| Case | Property read | Ordinary request/cosmetic filtering | Evidence |
| --- | --- | --- | --- |
| Trusted, advanced on | `undefined` | Blocked / hidden | [Result](trusted-enabled.json) |
| Same cache, advanced off through UI | `fixture-value` | Blocked / hidden | [Result](trusted-disabled.json) |
| Advanced reenabled through UI | `undefined` | Blocked / hidden | [Result](trusted-reenabled.json) |
| Global blocker off, advanced still on | `fixture-value` | Offline network error / visible | [Result](trusted-global-off.json) |
| Global blocker restored | `undefined` | Blocked / hidden | [Result](trusted-global-restored.json) |
| Raw/pages look-alike with privileged cache | `fixture-value` | Blocked / hidden | [Result](untrusted-cached.json) |
| Manual copy of the scriptlet | `fixture-value` | Blocked / hidden | [Result](manual-rules.json) |

Every observation followed a new document/reload. Enabled ordinary filtering
produced `ERR_BLOCKED_BY_ADMINISTRATOR`; globally disabled filtering produced
`ERR_INTERNET_DISCONNECTED` under the same offline conditions. The unsupported
button control remained at zero clicks in every case. No YouTube effectiveness
or arbitrary-script support is claimed.

The initial root fixture had incorrect Android SELinux categories and was not
loaded. Matching the existing user13 profile label corrected the test setup;
SELinux remained enforced. The successful results above use the correctly
loaded database. [Seeding](seed-fixture.py), [UI toggles](toggle-setting.py) and
[assertions](save-probe.py) are retained for reproduction in a disposable,
backed-up developer profile, not for use on a personal profile.

Afterward, both original app-profile and shared-preference archives were
restored with their owner and SELinux labels. The restored Preferences bytes
exactly match the original archive, including the original explicit false,
custom rule, exception and five cached lists. Wi-Fi/mobile data were restored
to enabled, the vehicle stayed parked, the app was stopped and test port
mappings were removed. Private full-profile backups remain outside this repo.

## Automated checks and review

- [Native results](native-results.json): **32 passed**, API 33 Automotive.
- [Diagnostics results](diagnostics-results.json): **24 executions passed**,
  API 29/36, including effective-readiness and unknown-state handling.
- [Media results](media-results.json): **26 executions passed**, API 29/36.
- Ordered overlay loader: **16 passed**; package resource gate: **8 passed**.
- Both exact full-source/package builds and `verify-artifacts.py --arch ARCH`
  passed. Final exported bytes and installed APK identity were rechecked.
- [Repeated native conversion](repeat-conversion.json) produced identical
  databases and statistics. [Generated bundle manifest](bundled-manifest.json)
  binds the current output to the frozen licensed inputs.
- Both fork and Chromium overlay `git diff --check` passed.

[Exact native/JUnit commands](run-tests.sh) use the actual generated runners.
Focused tests cover inherited/explicit defaults, global-off independence,
selection retention, current-policy cached snapshots, unknown/raw/manual data,
stale conversion callbacks, reentrancy, storage races, observer lifetime,
metadata persistence and one scheduled refresh of basic trusted data. The
optional older SDK mock-based test batch was incompatible with this revision
and was not retained or counted as passing.

Local worker [policy](analysis-policy.json), [lifecycle](analysis-lifecycle.json)
and [conversion](analysis-conversion.json) analyses were advisory.
Independent reviews covered [source](review-source.json),
[tests](review-tests.json), [readiness](review-readiness.json) and the final
[independent UI switch](review-ui-switch.json). Accepted findings were fixed
and retested. Recommendations to enable header filters or add an allegedly
missing per-subscription check were rejected: header filters are intentionally
disabled, and that check already exists. The conversion analysis also confused
the fixed identity allowlist with mutable preference state; the current-policy
completion check and captured conversion flag govern the actual race.
Review prose implying only
AntiCV is trusted is imprecise; both exact existing identities are listed above.
Review questions about preloaded readiness and global gating were resolved by
the fresh offline report and installed global-off/restored cases. One bounded
analysis retry followed a context-size failure; no failed worker result is
treated as successful evidence.

The final UI-only change leaves the advanced switch interactive when global
blocking is off. Both packages were rebuilt and verified afterward, and its
installed UI/backend behavior passed the cases above. Native/JUnit source did
not change after the passing focused run. Physical vehicle acceptance and
production signing remain open release gates.
