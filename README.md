# Roadium Browser

<img src="assets/branding/roadium-app-icon.png" alt="Roadium Browser icon" width="112">

**A browser built for parked use on Android Automotive OS.**

Roadium brings a vehicle-focused browsing experience, configurable filtering
and its own appearance to cars with Android Automotive OS. The initial test
vehicle is a 2024 Chevrolet Blazer EV running Android 12.

## Built on Cromite

Roadium is independently maintained and uses [Cromite](https://github.com/uazo/cromite)
as its upstream foundation. Cromite provides the Chromium browser base,
privacy features and native filtering engine. We intend to continue bringing
Cromite engine updates, security fixes and privacy improvements into Roadium
through reviewed and tested builds.

Roadium maintains its own Automotive features, settings, branding and releases
on top of that foundation. This repository keeps the upstream patch series
intact and adds a separate Roadium overlay. Development continues on `develop`.
Upstream updates are integrated deliberately; installing Roadium does not
mean a new Cromite release is automatically installed in its place.

## Roadium features

- **Automotive browsing:** Android 12 or later, with media restrictions for
  parked use and support for vehicle controls and the on-screen keyboard.
- **Configurable Shields:** bundled filter data, protection presets, category
  controls, custom rules and filter-update diagnostics.
- **Site controls:** saved and temporary exceptions, plus a local count of
  blocked requests. Exceptions share the browser profile's regular and
  Incognito filtering scope; temporary exceptions last until browser restart.
- **Roadium appearance:** its own icon and colors, system-following light and
  dark appearance, and saved per-site website theme overrides.
- **Automotive privacy choices:** browser sign-in, sync, password saving and
  payment autofill are disabled in the current vehicle build.

## Testing and availability

Roadium is in active development and internal vehicle testing. Emulator and
package checks complement testing on the car; they do not establish behavior
on every vehicle or display. Fullscreen display sizing and preferred 720p
playback remain ongoing work and are not completed features in the current
Shields test build.

Updates use Roadium's own build, signing and Android Automotive OS test-release
process. Cromite downloads are upstream builds, not Roadium updates.

## Project documentation

- [Roadium development notes](ROADIUM.md)
- [Build and artifact verification](build/roadium/README.md)
- [Shields taskers and implementation status](docs/shields/README.md)
- [Regression and release checks](docs/shields/REGRESSION_RUNBOOK.md)
- [Current internal-test signing and Play Console steps](docs/shields/PLAY_CONSOLE_UPDATE_801003722.md)
- [Roadium Bundle Signer](tools/roadium/signer/README.md)
- [Branding assets and attribution](assets/branding/README.md)

## Feedback and development

Use the [Roadium issue tracker](https://github.com/Musicpizzaman/roadium-browser/issues)
for Roadium bugs and feature requests. For vehicle issues, include the model,
year, Android version, Roadium version and steps to reproduce while parked.

Roadium-specific changes and releases are maintained here. Cromite remains
our upstream reference for browser-engine, security and privacy work.

## Credits and licensing

Roadium builds on the work of [Cromite](https://github.com/uazo/cromite),
[Chromium](https://www.chromium.org/) and [Bromite](https://github.com/bromite/bromite),
along with their contributors and third-party projects. Roadium is not
affiliated with or endorsed by those projects.

The repository retains its [GNU GPL v3 license](LICENSE). Individual components
and patches retain their applicable licenses and copyright notices. The
[upstream README reference](docs/UPSTREAM_CROMITE_README.md) preserves Cromite's
original credits and licensing details; source notices and browser open-source
credits remain in place.
