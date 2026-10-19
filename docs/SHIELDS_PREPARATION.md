# Roadium Shields preparation

Prepared October 13, 2026. Card 01 subsequently started following the user's
go-ahead. No card has been accepted as complete; Cards 02–09 remain on hold.
The preparation findings below describe the baseline before Card 01 changes.

Detailed work packages, prerequisite gates and fill-in tracking/evidence spots
for all nine cards are in [Roadium Shields taskers](shields/README.md).

## Verified starting point

- Repository: Roadium Browser, `develop` (tracking `origin/develop`).
- Chromium: `153.0.8010.37`.
- Pinned Cromite commit: `11507ac1061b5ea227806f5e84db5a57df6ccf6a`.
- Post-Cromite source tree: `56400c5406d8f83533c151e122b19f3f745c0892`.
- Foundation patch SHA-256:
  `3f0fedee04363332ccfe8fb2bbd2ba1f4ed8127e187f04c5bd2104a33debd0df`.
- The retained `roadium-design-x64-153` container's complete source diff
  matches that foundation checksum. Its existing staged foundation changes
  are expected; they must be preserved.
- All eight existing `tools/roadium/test-apply-overlay.py` tests passed.
  This establishes the current loader baseline, not Shields functionality.

The fork stores patches and build tools. The full Chromium source lives in
the compiler container. See [build instructions](../build/roadium/README.md)
and [baseline.json](../build/roadium/baseline.json).

## Agreed implementation boundaries

- Extend the existing native Eyeo engine, updater, FlatBuffers resources,
  scriptlet allowlist and Android settings.
- Preserve the pinned foundation. Use separately reviewed, checksum-pinned
  Shields patches; any patch-series support must retain source verification,
  idempotency and refusal of unrelated edits.
- Treat GitHub Raw as an approved transport for exact known subscriptions.
  Retain the canonical subscription identity for trust, conversion and metadata.
- Preserve explicit user choices, custom filters, allowed domains and
  subscription data during upgrades and recovery.
- Keep Acceptable Ads exceptions disabled, diagnostics local, GPL-3.0
  compatibility and filter attribution intact.
- Preserve parked-only media restrictions. YouTube improvements must pass the
  existing media regressions as well as new filtering tests.

## Preparation completed

Relevant subscription, network, converter and Android bridge/settings source
was copied to the local build scratch area for future bounded worker analysis.
Two candidate offline input snapshots were downloaded outside the repository.
No filter snapshot has been integrated into the browser or release build.

Both snapshots are from Cromite's `pages` commit
`338336d9e640489c648d47d606cb0030064c4e0f`, with filter version `202610130952`:

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| `easylist.txt` | 2147920 | `1e2a42fcfc24642be33392385c6912179fc96b068c39b21a6b9601aea4343bce` |
| `abp-filters-anti-cv.txt` | 496681 | `2fcfb54891e7f7880909f5438d9691d4233dcde4b00b105d7bd315e6a0fad51a` |

The immutable source URLs use
`https://raw.githubusercontent.com/uazo/cromite/338336d9e640489c648d47d606cb0030064c4e0f/filters/`
followed by the exact input filename. Their availability and hashes do not
establish parser compatibility or successful offline filtering.

EasyList's [licence page](https://easylist.to/pages/licence.html) offers
GPL-3.0-or-later as one licensing option. The
[anti-circumvention project's licence page](https://gitlab.com/eyeo/anti-cv/abp-filters-anti-cv/-/blob/master/LICENSE)
identifies GPL-3.0-only. Preserve full notices and verify attribution and
component terms before bundling.

Local Ollama returned preliminary proposals for patch-series support,
bootstrap/defaults, fallback/recovery and diagnostics. They remain unaccepted
advisory material. In particular, a sequential patch loop alone does not
provide rollback or verify the resulting combined source diff. Unique
subscription filenames alone do not establish durable atomic updates or
last-known-good recovery. Review the affected source and tests before edits.

## Starting order when implementation is authorized

1. Card 01: audit fresh and upgraded profiles, then expose operational and
   update-result diagnostics. Establish which native/JNI fields already exist.
2. Prepare safe ordered-patch application and artifact verification before
   adding a second browser overlay. Verify failure rollback and collisions.
3. Cards 02 and 03: restore reproducible native bootstrap resources, validate
   the snapshots with the real converter, and preserve explicit advanced-filter
   opt-outs while changing defaults.
4. Cards 04 and 05: add bounded fallback with unchanged trust identity, then
   validate storage transactions and recovery with fault injection.
5. Card 06: inventory and test YouTube syntax against the current parser and
   scriptlet library before changing rules. Preserve compound-rule semantics.
6. Cards 07 and 08: build presets and per-site controls on existing settings
   and allowed domains; establish engine support before adding finer controls.
7. Card 09: add focused tests throughout development and use them as release
   gates, including Roadium CI that needs no upstream release credentials.

## Verification to prepare for implementation

- Loader: ordered patches, full reapplication, tampered later patches,
  malformed paths, unrelated edits, new-file collisions and partial failures.
- Native subscription tests: offline startup, downloaded versus active state,
  preference migration, bounded retries, bad data, malicious redirects,
  trust identity, storage errors and restart recovery.
- Android tests: update results, existing custom settings, presets and
  persistent versus temporary site exceptions.
- Converter tests: supported and rejected YouTube commands. The experimental
  list contains `simulate-mouse-event`, commented as unsupported in the pinned
  serializer; do not automatically remove commands from compound rules.
- Build/resource checks: pinned input hashes, converter output, resource IDs,
  source overlay provenance, attribution, APK/AAB packaging and version codes.
- Runtime checks: fresh install and upgrade; YouTube pre-roll, mid-roll, Shorts,
  embeds, fullscreen, captions, seeking and tab changes; Automotive media
  restrictions and recovery. Emulator and physical-car evidence are separate.

No Shields native/Android tests, converter validation, APK/AAB builds or
runtime acceptance tests have been run. The installed app has not changed.
