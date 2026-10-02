# Roadium Bundle Signer

A reusable Windows application for signing Roadium Android App Bundles with your **existing** upload key. It verifies both the signature and Android bundle before saving a signed copy. The unsigned original is preserved, and existing output files are never overwritten.

1. Keep Docker Desktop running. Open **RoadiumBundleSigner.exe**.
2. Click **Browse** and select an unsigned `.aab` file. The default signed copy is saved beside it as `<name>-signed.aab`; use **Save as** to choose another location.
3. Enter your saved upload-key password in both masked fields, then click **Sign bundle**. After **Signed and verified**, upload the output `.aab` in Play Console.

Use the password for the key that signed your first Play upload. It is not your Google or GitHub password. The application does not create keys, save passwords, upload files, or publish releases.

## Requirements and settings

Windows x64, .NET 10 Desktop Runtime, Docker Desktop, and the retained `roadium-baseline-153` container containing your original PKCS12 upload key. The runtime is already installed on the development PC. Keep `signer-settings.json` beside the executable. This file contains public paths, container name, alias, and expected app package; edit it if you later move the existing key/toolchain into another container. Never put passwords in this file.

The app starts the existing container if stopped. It uses the JDK and bundletool already in that container. Losing that container also loses access to the key unless you have backed it up: preserve your original key and its password separately.

Passwords travel over redirected UTF-8 standard input to a fixed helper, then in a scoped environment to jarsigner. They never appear in process arguments, helper files, or application logs. Fields are cleared after each attempt; as with any ordinary desktop password entry, the password is briefly present in process memory. CR/LF/NUL are rejected; other characters and spaces are passed unchanged. The PKCS12 store and key must share the same password, as in the original signing guide.

The app creates private, uniquely named temporary folders, validates a stable input snapshot and package, signs with SHA-256/RSA, requires strict verification against the existing key and successful bundletool validation, then checks the exported SHA-256 before an atomic move. Failed attempts do not produce a final signed file. A crash or Docker outage can leave a temporary job directory; the private key is never copied into a job directory or deleted.

## Build and verify

From this directory, with the .NET 10 SDK:

~~~powershell
dotnet publish RoadiumBundleSigner.csproj -c Release -o 'E:\Android Auto Projects\RoadiumBuild\RoadiumBundleSigner'
.\bin\Release\net10.0-windows\RoadiumBundleSigner.exe --self-test 'E:\Android Auto Projects\RoadiumBuild\signer-test-results'
~~~

The dependency-free self-tests exercise validation, password transport, output races, cleanup, and hidden UI layout at normal and simulated 2× scale. An integration-test entry point is also available for developers: `--integration-test <test-settings.json> <public-unsigned.aab> <output-directory>`. It is deliberately restricted to an isolated `roadium-signer-test-*` container with a disposable key under `/tmp/roadium-signer-fixture/`; it never accepts the production container/key. It generates test reports and signed fixtures only in the chosen test output directory.
