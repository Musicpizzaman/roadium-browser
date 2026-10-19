# Roadium Shields update: Google Play Console steps

This is an **internal vehicle-test candidate**, not a production-ready release.
It contains the implemented Shields work from Cards 01-08 and Card 09 regression
tooling. **Card 10's fullscreen geometry fix and default 720p are not implemented
in this candidate.** Physical vehicle, live-service and extended-soak acceptance
remain open. Internal testing is used to obtain that evidence, not to mark those
gates passed. Do not promote this candidate to production on these results.

Vehicle baseline: the user's About-screen photo confirms Android 12 and the
April 5, 2024 security patch. Android 12 meets this build's API31 minimum; the
photo alone does not prove native display bounds, installed browser version,
vehicle ABI or Play eligibility.

## 1. Sign the prepared update

Keep Docker Desktop running. Open the existing **Roadium Bundle Signer** desktop
shortcut, or:

`E:\Android Auto Projects\RoadiumBuild\RoadiumBundleSigner\RoadiumBundleSigner.exe`

1. Click **Browse** and select:
   `E:\Android Auto Projects\RoadiumBuild\artifacts\153.0.8010.37-roadium-shields-internal-arm64\Roadium-Browser-801003722-arm64-unsigned.aab`
2. Click **Save as** and choose a new file beside it:
   `Roadium-Browser-801003722-arm64-signed.aab`
3. Enter the saved password for the **existing Roadium upload key** in the two
   masked fields. Do not send the password in chat. This is the upload-key
   password used previously, not a Google or GitHub password.
4. Click **Sign bundle** and wait for **Signed and verified**. If signing fails,
   keep the exact error and stop; do not create a replacement key.

The signer preserves the unsigned original, verifies input/package identity,
requires strict signature verification against the existing key, validates the
signed Android bundle, and checks the exported file hash. It does not publish.
No password is stored in this guide and no signed output is claimed before this
step succeeds. The existing signing key stays in its retained container.

## 2. Upload in the existing Automotive internal track

1. Open [Google Play Console](https://play.google.com/console/) and select the
   existing **Roadium Browser** app. Do not create another app or package.
2. Go to **Test and release → Testing → Internal testing**.
3. Select the same **Android Automotive OS** form factor/track used for your
   existing car test. Do not change the established form-factor configuration.
4. Choose **Create new release**, or edit the intended unpublished internal
   draft if Console requires resolving an existing draft first.
5. Upload **Roadium-Browser-801003722-arm64-signed.aab** only.
6. Verify Console reports package `io.github.musicpizzaman.roadium` and version
   code **801003722**. The previous documented design release was **801003712**.
   If Console already has a release with code 801003722 or higher, stop and keep
   that exact message; do not modify the bundle or try to reuse the old code.
7. Suggested release name: **Roadium Shields internal test 801003722**.

Suggested release notes:

> Improved built-in filtering, update recovery, protection presets and per-site
> controls, with local blocked-request information. Internal vehicle test;
> fullscreen sizing and preferred 720p remain under investigation.

## 3. Review and roll out the internal test yourself

1. Save and review the release. Resolve blocking Console errors. Preserve any
   compatibility/signing/version error exactly instead of replacing the key or
   changing package identity.
2. Reconfirm **Android Automotive OS → Internal testing** and the intended
   existing tester list before choosing the final internal rollout action.
3. On the car, while parked, open the existing Roadium Play listing using the
   tester account and choose **Update** when the new version becomes available.
   Preserve the existing install and its settings; do not uninstall to force it.
4. Confirm the installed version code is **801003722** where available, then
   check ordinary browsing, filtering, global pause, presets, site exceptions,
   keyboard, and parked video controls. Keep observations about the right-hand
   gap separate: this candidate does not claim to repair it.

Google's current documentation describes internal testing as a way to distribute
early quality-assurance builds and notes that availability can take time.
See [internal-testing guidance](https://support.google.com/googleplay/android-developer/answer/9845334?hl=en)
and [dedicated form-factor tracks](https://support.google.com/googleplay/android-developer/answer/13295490?hl=en).
Browser requirements for other tracks still apply; see
[Android Automotive browser guidance](https://developer.android.com/training/cars/parked/browser).

## Verification records

The [candidate evidence directory](evidence/release-801003722/README.md) records
the exact source, package hashes, new version codes, focused test results,
packaging validation and remaining limits. Signing, upload and rollout are
user-operated steps, and remain pending until independently confirmed.
