# Signing app verification

Verified on the development PC on 2026-10-02 with .NET SDK 10.0.401 and Windows Desktop runtime 10.0.12.

- Release build and publish: zero warnings/errors, no external NuGet package dependencies.
- 74 self-test assertions passed: exact password confirmation, empty/control-character rejection, Unicode/metacharacter preservation, malformed settings, unsigned ZIP checks, already signed input rejection, unchanged source, stopped-container start, no password in command arguments, error handling for each signing/verification stage, output collision/race protection, exported hash mismatch rejection, missing Docker, and cleanup.
- Hidden native form render and bounds/accessibility checks passed at normal and simulated 2× scale. Password fields are masked; the Open output folder action fits and is cleared when a new output/attempt is selected. Actual monitor DPI transitions were not exercised.
- 10 real integration assertions passed using a disposable RSA PKCS12 key in a separate `roadium-signer-test-20261002` container: UTF-8 stdin transport, incorrect-password rejection/no output, successful signing with spaces/quotes/shell metacharacters in the fixture password, strict jarsigner verification, bundletool validation, unchanged public unsigned Roadium AAB, signature entries, already signed input rejection, wrong package, missing key, and removed job directories.
- The disposable signed output and test container were removed after verification. The existing production upload key was not accessed by tests; no production-signed bundle was created or uploaded.
- Independent local Ollama review completed for the backend/UI and tests/build/docs. A separate focused UI audit found a clipped action button and stale success action after retries; both were corrected before the final test run.

The installed app is framework dependent. Keep its executable, DLL, JSON runtime files, and public signer settings together in the published folder.
