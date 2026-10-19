# Card 07 — protection levels and categories

Implemented and locally verified October 18, 2026. Physical vehicle and release
checks remain open. [Verification](verification.json) is the final acceptance
record; package manifests retain their original build-time runtime-pending field.

## Selection contract

All managed identities use `https://uazo.github.io/cromite/filters/`.

| Category | Exact managed filename | Standard | Balanced | Strict |
| --- | --- | --- | --- | --- |
| Advertising | `easylist.txt` | Yes | Yes | Yes |
| Circumvention | `abp-filters-anti-cv.txt` | No | Yes | Yes |
| Tracking/domain blocking | `badblock_lite.txt`, `badmojr-1Hosts-master-Lite-adblock.txt` | No | Both | Both |
| Social | `fanboy-social.txt` | No | No | Yes |
| Notifications | `fanboy-notifications.txt` | No | No | Yes |
| Cookie banners | No supported dedicated list | Unavailable | Unavailable | Unavailable |

Balanced matches the existing four-list fresh-profile default. Upgrades never
reset selection. Custom is derived from deviations within the six-list managed
set; nonmanaged subscriptions do not change that label. Selecting Custom opens
the existing individual-list editor. Category switches represent all members;
partial tracking selection shows its selected count and yields Custom. Switching
that category on selects both members; off clears both.

Presets and Restore managed defaults change only the managed set. They preserve
custom and regional subscriptions, explicit legacy experimental selections,
manual rules, saved exceptions, homepage, global enabled state and advanced
filtering. Restore selects Balanced. Global pause and advanced opt-out remain
independent and visible. Selection summaries are separate from downloaded,
parsed and active state, exposed through existing diagnostics. Strict can break
site features; saved exceptions continue to work.

`SetFilterLists` validates the full batch before mutation, deduplicates stable
input and makes one persisted dictionary update/observer notification when
changed. Invalid batches leave existing selection intact; repeated sets are
no-ops. JNI/controller wrappers reuse the existing configuration and engine.
No extra preference store, trust expansion or migration reset was added.

## Source, provenance and review

The eighth overlay is [0008-roadium-protection-presets.patch](../../../../build/roadium/patches/0008-roadium-protection-presets.patch).
SHA-256: `1802559fa9a5123f2568963d52909679f2fd4d08621981bd0861ab75b6ca8b53`.
First seven overlay bytes were preserved. Final cumulative diff:
`3003050b25932d470862bd2b4e083bc81c95cf9e8279ca672a3b5ff0df08727e`;
applied tree `17fed1c823d47df5c3372fee66b44110c963acde`.
Both full pinned source trees matched the [17 affected file hashes](affected-source-files.json).
Chromium `153.0.8010.37`, Cromite `11507ac1061b5ea227806f5e84db5a57df6ccf6a`,
base tree `56400c5406d8f83533c151e122b19f3f745c0892`, version offset 10.

Social and Notifications reuse exact existing catalog entries, without privileged
filtering permission. [Frozen provenance and notices](../../../../tools/roadium/preset-snapshots/README.md)
record revision, versions, sizes, hashes, EasyList authors and CC BY 3.0 license.
Full pinned-converter validation accepted 13,868 Social and 1,372 Notifications
rules with zero rejected/unsafe/unsupported/prohibited results:
[conversion results](category-conversion.json). Generated inputs are native-test
only, not extra packaged lists. EasyPrivacy was excluded because its canonical
endpoint returned 404. No unsupported cookie-banner switch was invented.

The local worker supplied advisory analysis; Codex checked and applied source.
Independent reviews cover [native](local-review-native.json),
[model](local-review-model.json), [UI](local-review-ui.json),
[final UI ordering](local-review-ui-order.json) and
[snapshot tooling](local-review-inventory.json). No concrete unresolved finding.
Suggested mixed-invalid/protocol and ordering cases were checked against existing
tests. The installed initial UI exposed preference-order collisions; the final
patch fixes ordering and was rebuilt, reviewed and retested. A later flaky tap
was resolved by waiting for UI idle; settled row and switch-widget activation
both passed. No unsupported behavioral change was made for that automation issue.

## Verification

| Check | Result / evidence |
| --- | --- |
| Native selection, persistence, trust and inventories | 228 pass; [post-review result](post-review-native.json), [command/log](card07-post-review-native.log) |
| Java diagnostics and presets | 40 executions pass (20 tests on two API configurations); [post-review result](post-review-junit.json), [command/log](card07-post-review-junit.log) |
| Existing media regressions | 26 executions pass; [result](media-junit.json), [command/log](card07-media-junit.log) |
| Overlay loader / packaged resources | 16 / 8 pass in the configured source environment |
| Snapshot integrity | Six checks pass including hash/size/include tampering; [record](snapshot-integrity-checks.json) |
| Upgrade/custom/paused/advanced disabled | [Final installed preservation](installed-preservation.json), [initial upgrade](upgrade-initial.json) |
| Every actual source-to-target preset transition and repetition | All nine pass; [record](preset-transitions.json) |
| Categories, partial selection, Custom editor and direct switches | [Record](category-controls.json), [partial tracking screenshot](partial-tracking.png) |
| Managed reset and process restart | [Record](restore-and-restart.json) |
| Invalid custom URL actually submitted | Rejected through existing UI; [record](invalid-custom-url.json) |
| Fresh profile | Balanced four defaults, independent enabled advanced setting; [record](fresh-defaults.json) |
| Valid custom list and manual rule added through UI | Survive Strict and restore; [record](fresh-custom-import.json), [actual effects](fresh-filtering.json) |
| Light/dark, labels and grouped ordering | [Record](theme-checks.json), [light](strict-enabled-light.png), [dark](strict-enabled-dark.png), [categories](categories-dark.png) |

Native and Java checks were rerun after review. The final UI-order-only change
was subsequently compiled, built on both architectures and exercised installed.
The snapshot tool's six integrity checks followed its independent review.
Exact generated test runner commands and raw results are in the linked logs.
For standalone loader/resource checks, use `python3 tools/roadium/test-apply-overlay.py`
and, with `CHROMIUM_SOURCE` pointing to the pinned full source,
`python3 tools/roadium/test-filter-artifacts.py`. Run the latter in the configured
build environment; an initial unconfigured host invocation could not find source.
Verify the generated native input with
`python3 tools/roadium/preset_inventory.py --check-include <source>/components/adblock/test/shields_category_inputs.inc`.

## Installed filtering and failure checks

The final development APK ran on a disposable read-only API 33 x64 Automotive
AVD at 1280x720, density 160, using only owned users 11 and 13. An old Card 06
profile fixture upgraded with custom/experimental selections, manual rule,
allowed site, homepage, global pause and advanced opt-out preserved.
No original profile data was inspected.

Controlled HTTPS hosts `custom.card07.invalid` and `preserved.card07.invalid`
served an ordinary element, Social/Notifications selectors, and custom-list/manual
selectors. Canonical list requests were mapped to loopback and served exact
frozen snapshots using an owned test certificate pin. Lab-only first-run/DNS/SPKI
flags and a UI capture helper were removed afterwards. No account or live-service
acceptance is implied. Early HTTP probes did not establish filtering and were
superseded by these successful HTTPS checks.

- [Strict](strict-filtering.json): Social, Notifications, custom subscription and
  manual rule hide their examples; ordinary content remains visible.
- [Balanced](balanced-filtering.json) and [Standard](standard-filtering.json):
  Social/Notifications examples remain visible; custom/manual effects remain.
- [Saved exception](exception-filtering.json): all fixture examples remain visible.
- After HTTP 503 list-update failures and a browser restart, [last valid Strict
  filtering](recovered-filtering.json) remains effective; [recovery assertion](recovery-check.json),
  [failure metadata](failed-update-metadata.json), [diagnostics screenshot](failed-update-summary.png).

Advanced filtering stayed off during the upgraded-profile ordinary filtering
checks. All six managed sources loaded. The separately retained legacy
experimental fixture failed activation and was not counted as active; presets
never select it. The later fresh profile imported its custom URL and rule through
the existing UI and verified both effects after restore.

[Cleanup](cleanup.json): original foreground user and night mode restored;
owned users, command-line flags, UI helper, forwards/reverses and fixture servers
removed; owned read-only emulator stopped. Existing users 0/10 and build
containers retained. Private test key/profile files remain outside this repo.

## Packages and handoff

Final x64 and ARM64 APK/AAB builds and full artifact verification passed:
[x64 manifest](x64-build-manifest.json), [ARM64 manifest](arm64-build-manifest.json).
APK certificate remains the diagnostic development certificate; AABs are unsigned.
Badging, signing and bundle-validation records accompany the manifests.
The initial x64 UI build manifest is retained explicitly as historical evidence.

Package directories under `E:/Android Auto Projects/RoadiumBuild/artifacts/`:
`153.0.8010.37-roadium-shields-card07-x64` and
`153.0.8010.37-roadium-shields-card07-arm64`. Exact sizes and SHA-256 values are
in the manifests. No production signing, publishing or release was performed.

Card 08 can reuse the global/advanced controls, selected-list wrappers, derived
preset model and existing allowed-domain APIs; site matching, temporary scope,
activity attribution and current-tab lifecycle still require its own audit.
Card 09 must integrate these regressions and verify physical Android 12 Blazer EV
focus/touch, parked-only behavior, production signing and extended storage/update
soak. Card 06 live ad-format gates remain open. Card 10 geometry and preferred
720p behavior remain unimplemented; this card does not close them.
