#!/bin/bash
set -eu
umask 077
job="$1"
key="$2"
alias="$3"
jdk="$4"
bundletool="$5"
expected_package="$6"
expected_sha="$7"
# The app supplies only its unique, private directory and fixed positional arguments.
[[ "$job" =~ ^/tmp/roadium-sign-[a-f0-9]{32}$ ]] || exit 40
IFS= read -r password || exit 42
trap 'unset password' EXIT
[ -r "$key" ] || exit 45
[ -x "$jdk/jarsigner" ] && [ -x "$jdk/java" ] && [ -r "$bundletool" ] || exit 46
printf 'STAGE:validate\n'
actual_sha=$(sha256sum -- "$job/input.aab")
[ "${actual_sha%% *}" = "$expected_sha" ] || exit 40
"$jdk/java" -jar "$bundletool" validate --bundle="$job/input.aab" >/dev/null 2>&1 || exit 40
"$jdk/java" -jar "$bundletool" dump manifest --bundle="$job/input.aab" --module=base >"$job/manifest.xml" 2>/dev/null || exit 40
python3 - "$job/manifest.xml" "$expected_package" <<'PY' || exit 41
import sys
import xml.etree.ElementTree as ET
sys.exit(0 if ET.parse(sys.argv[1]).getroot().get('package') == sys.argv[2] else 1)
PY
printf 'STAGE:sign\n'
ROADIUM_SIGN_PASSWORD="$password" "$jdk/jarsigner" \
  -keystore "$key" -storetype PKCS12 -storepass:env ROADIUM_SIGN_PASSWORD \
  -keypass:env ROADIUM_SIGN_PASSWORD -digestalg SHA-256 -sigalg SHA256withRSA \
  -signedjar "$job/signed.aab" "$job/input.aab" "$alias" >/dev/null 2>&1 || exit 42
printf 'STAGE:verify\n'
ROADIUM_SIGN_PASSWORD="$password" "$jdk/jarsigner" \
  -verify -strict -verbose:summary -certs -keystore "$key" -storetype PKCS12 \
  -storepass:env ROADIUM_SIGN_PASSWORD "$job/signed.aab" "$alias" >/dev/null 2>&1 || exit 43
"$jdk/java" -jar "$bundletool" validate --bundle="$job/signed.aab" >/dev/null 2>&1 || exit 44
unset password
signed_sha=$(sha256sum -- "$job/signed.aab")
printf 'SIGNED_SHA256:%s\n' "${signed_sha%% *}"
printf 'STAGE:verified\n'
