# Card 02 verification — October 14, 2026

Card 02 restores native offline bootstrap data for EasyList and ABP
Anti-Circumvention. Cards 03 and 04 are excluded. The advanced-filter default
remains unchanged; both bundles convert without privileged rules. No Acceptable
Ads exception list is packaged.

## Exact source and artifacts

Chromium `153.0.8010.37`, Cromite
`11507ac1061b5ea227806f5e84db5a57df6ccf6a`. The immutable foundation and Card 01
patch hashes are preserved. The separate Card 02 patch is
`build/roadium/patches/0003-roadium-bundled-filters.patch`, SHA-256
`eb4f85d293ea50d4e69cb25f633f86d1539a8caae71752d44ebbdc3662513df4`.
The cumulative source diff is
`a62d66be6d65a766d0adabc6c18b440d245f429a5b679aedd5f747e0aacedaa8`,
and the resulting source tree is `69ac49b1e34f3a63c9a965d65ecfd15140dea799`.

Both architecture builds and package verification passed. These manifests bind
the exact APK/AAB hashes, ABI, package, SDK levels, certificate, source series,
build attempt and all four actual packaged resources:

- [x64 provenance](x64-build-manifest.json), version code `801003718`.
- [ARM64 provenance](arm64-build-manifest.json), version code `801003712`.

The installed x64 APK SHA-256 is
`16a0bca66a2451fb66fc450c362aab12541c1e7ab8b4d489ce25e9329b857441`.
The ARM64 APK SHA-256 is
`917c5f7ff094734013b201b922e4e61ba299564dd7bb5bde5da3d8af33f5e22e`.
Artifacts remain in the local `RoadiumBuild/artifacts/153.0.8010.37-roadium-shields-card02-x64`
and corresponding `-arm64` directories. APKs use the diagnostic development
certificate; AABs are unsigned. No release signing, upload or physical-car run
is claimed. The raw build manifests retain their initial runtime-pending field;
the installed evidence below supplies the separate x64 runtime result.

## Frozen inputs and conversion

[The generated manifest](bundled-manifest.json) records immutable Cromite pages
revision `338336d9e640489c648d47d606cb0030064c4e0f`, source and compressed hashes,
canonical identities, attribution, notices and converted output hashes. Source
text, including original notices, remains inside deterministic gzip archives.
The GPL license and distribution notice use LF line endings. Canonical list
URLs retain their existing Cromite identities.

| Bundle | Version | Accepted | Parser rejected | Privilege rejected | Converted bytes |
| --- | --- | ---: | ---: | ---: | ---: |
| EasyList | 202610130952 | 81,698 | 5 | 37 | 8,184,160 |
| ABP Anti-Circumvention | 202610130952 | 2,492 | 48 | 1,915 | 309,424 |

Other rejection categories are zero for these bundled conversions. Privilege
rejection is intentional in Card 02. This does not establish advanced scriptlet
support or YouTube effectiveness. Counts describe conversion, not advertising
coverage. [Repeat conversion](repeat-conversion.json) produced identical
FlatBuffers and statistics JSON with the pinned native converter.

The runtime checks FlatBuffers structure, exact canonical URL and
`CurrentSchemaVersion()` (the base64 SHA-256 of the generated schema header).
Selected bundles remain active when downloads fail; any accepted installed
subscription takes precedence, and explicit list removal drops bootstrap data.
Corrupt downloaded-storage recovery is Card 05 work.

The generated resource IDs in these builds are EasyList `39740`, AntiCV
`39741`, manifest `39742`, notices `39743`. They survive both APK and AAB
allowlists. Package verification compares decompressed bytes with the exact
generated files, including Android `.pak+40064988+` asset names and wrapped
`AllowlistedResource` definitions. The resource reader was also compared with
Chromium's reader for all 327 actual APK resource packs.

## Automated verification

| Check | Result | Evidence |
| --- | --- | --- |
| Frozen input integrity, identity, missing/corrupt files and manifest merge | 9 tests passed | `components/adblock/core/resources/roadium/test_verify_inputs.py` |
| APK/AAB resource gates using Chromium's actual GRIT writer | 8 tests passed | `tools/roadium/test-filter-artifacts.py` |
| Safe ordered overlay transaction, collisions and rollback | 16 tests passed | `tools/roadium/test-apply-overlay.py` |
| Native lifecycle, bundle/provider and conversion tests | 22 passed, API 33 Automotive | [Results](native-results.json) |
| Android diagnostics | 20 executions passed, API 29/36 | [Results](diagnostics-results.json) |
| Existing media regressions | 26 executions passed, API 29/36 | [Results](media-results.json) |

The added lifecycle tests use the real bundle provider and maintainer with
controlled network/storage callbacks. They prove that terminal failure retains
the bundle, opt-out removes it, a newer `203001010001` conversion replaces it
only after storage acceptance, and newer installed data survives update failure.
That future version is a synthetic native test fixture. The live upstream served
the same version as the bundle during installed testing, so installed online
activation and the higher-version native tests are distinct evidence.

In the pinned source, with depot_tools on PATH and updates disabled:

```sh
python3 "$WORKSPACE/depot_tools/siso.py" ninja -C out/x64 --offline --local_jobs=12 roadium_shields_unit_tests roadium_shields_junit_tests roadium_media_junit_tests
ADB_SERVER_SOCKET=tcp:host.docker.internal:5037 vpython3 out/x64/bin/run_roadium_shields_unit_tests -d emulator-5554 --test-launcher-retry-limit 0 --json-results-file out/x64/card02-test-results/native.json
vpython3 out/x64/bin/run_roadium_shields_junit_tests --json-results-file out/x64/card02-test-results/diagnostics-junit.json
vpython3 out/x64/bin/run_roadium_media_junit_tests --json-results-file out/x64/card02-test-results/media-junit.json
CHROMIUM_SOURCE="$WORKSPACE/chromium/src" python3 "$WORKSPACE/roadium/tools/roadium/test-filter-artifacts.py"
python3 "$WORKSPACE/roadium/tools/roadium/verify-artifacts.py" --arch x64
python3 "$WORKSPACE/roadium/tools/roadium/verify-artifacts.py" --arch arm64
```

## Installed acceptance

The exact x64 APK ran on the API 33 Automotive emulator. Wi-Fi and mobile data
were disabled before first launch of disposable user13. Existing users10/11
were retained as upgrade fixtures. The saved AVD disk remains preserved through
the read-only emulator session.

| Scenario | Observation | Evidence |
| --- | --- | --- |
| Fresh first launch offline | Both intended bundles loaded, zero downloaded signatures, advanced default off | [Settings](fresh-offline-settings.json), [report](fresh-offline-diagnostics.txt), [screen](fresh-offline-diagnostics.png) |
| Fresh actual blocking | Fixed advertising fetch blocked by the engine | [Probe](fresh-offline-enabled-probe.json), [screen](fresh-offline-blocked.png) |
| EasyList isolated, no custom rules | `ERR_BLOCKED_BY_ADMINISTRATOR` with blocking enabled | [Probe](easylist-only-offline-enabled.json) |
| Same offline page with blocking disabled | `ERR_INTERNET_DISCONNECTED`, establishing the control | [Probe](easylist-only-offline-disabled.json) |
| All lists explicitly removed, then restarted | Empty selection preserved; request reaches the offline network failure | [Settings](offline-unsubscribed-settings.json), [probe](offline-unsubscribed-probe.json) |
| Existing downloaded data on APK upgrade | Existing lists remain Installed, including October 1 data; selections/signatures unchanged | [Report](upgrade-user10-diagnostics.txt), [screen](upgrade-user10-diagnostics.png), [comparison](upgrade-preservation.json) |
| Explicit advanced opt-out, manual rule and exception on upgrade | Preserved in user11 | [Before](upgrade-user11-before.json), [after](upgrade-user11-after.json), [comparison](upgrade-preservation.json) |
| Restore connectivity and check updates | Five accepted activations; bundle origin changes to canonical network source | [Report](online-activated-diagnostics.txt), [screen](online-activated-diagnostics.png) |
| Settings through ordinary online activation | All selections, custom rule, exception and explicit advanced false retained | [Before](online-transition-before.json), [after](online-transition-after.json) |
| Downloaded data restarted offline | Actual advertising fetch remains blocked | [Probe](downloaded-data-offline-probe.json) |
| Offline manual update times out | Five lists remain Installed; signatures/settings unchanged; actual blocking continues | [Report](offline-timeout-retention.txt), [screen](offline-timeout-retention.png), [settings](offline-after-timeout-settings.json), [probe](offline-after-timeout-probe.json) |

The probe fetches bytes from one fixed advertising URL without executing the
downloaded script. It operates solely on the controlled local fixture. After the
initial untouched fresh-profile observation, test-only root preference edits
reconfigured stopped disposable user13 for isolated selection, disabled control,
unsubscribe and settings-preservation cases. They are not a release feature.
Existing users10/11 were read and launched for comparisons, without root edits.
Native tests separately exercise the live selection-change path and completed
download/storage failures.

[The installed APK hash](installed-artifact.json) matches the verified x64
artifact. Wi-Fi/mobile data were restored to their original enabled state,
Park was restored, the disposable browser was force-stopped and task-owned
ADB forwarding was removed. No firewall rules or production networking
exceptions were introduced. The pre-existing local fixture server was retained.

## Review and fixes

The original three broad local requests timed out. Smaller bounded local
analysis and independent reviews succeeded; their advisory results are retained
as `analysis-*.json` and `review-*.json`. Claimed URL mismatch, missing transitive
verification dependency and missing length check were rejected against actual
source. A proposal to purge working data on failed update was rejected because
it violated retention requirements. Python integers do not overflow; existing
pack header bounds already reject short input.

Compilation identified the restored converter's moved logging-settings header
and the populated configuration vector's exit-time destructor; both were fixed.
An added integration test caught stale bundle state after terminal failure and
opt-out; refreshing the provider on selection change fixed it. Actual artifact
checks caught wrapped GRIT IDs, suffixed Android asset names and pruning of
unreferenced notices/manifest resources. Supported explicit resource references
and the corrected inspector fixed those gaps. The corrected 22 native tests and
both architecture package checks passed afterward.

Physical ARM64 vehicle acceptance and production signing remain release gates.
Advanced default/execution policy, fallback transport and broader recovery stay
with their respective later cards.
