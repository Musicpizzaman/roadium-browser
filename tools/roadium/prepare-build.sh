#!/bin/bash
set -euo pipefail
source_root="${1:?Chromium source directory required}"
cromite_root="${2:?Pinned Cromite checkout required}"
roadium_root="${3:?Roadium checkout required}"
arch="${4:-arm64}"
case "$arch" in arm64|x64) ;; *) echo "Unsupported architecture: $arch" >&2; exit 2;; esac
export PATH="$source_root/third_party/llvm-build/Release+Asserts/bin:$WORKSPACE/depot_tools:/usr/local/go/bin:$WORKSPACE/mtool/bin:$PATH"
python3 "$roadium_root/tools/roadium/apply-overlay.py" "$source_root" "$cromite_root"
cd "$source_root"
test -x third_party/llvm-build/Release+Asserts/bin/clang
test -f "$WORKSPACE/depot_tools/siso.py"
mkdir -p "out/$arch"
expected_code=$(python3 "$roadium_root/tools/roadium/version_code.py" "$source_root" "$roadium_root/build/roadium/baseline.json" "$arch")
gn_args=$(cat "$cromite_root/build/cromite.gn_args" "$roadium_root/build/roadium/gn_args")
gn gen "out/$arch" --args="target_os = \"android\" target_cpu = \"$arch\"
$gn_args
android_override_version_code = \"$expected_code\"
"
actual_cpu=$(gn args "out/$arch" --list=target_cpu --short)
test "$actual_cpu" = "target_cpu = \"$arch\""
printf '%s\n' "$actual_cpu"
actual_code=$(gn args "out/$arch" --list=android_override_version_code --short)
test "$actual_code" = "android_override_version_code = \"$expected_code\""
printf '%s\n' "$actual_code"
gn args "out/$arch" --list=chrome_public_manifest_package --short
gn args "out/$arch" --list=default_min_sdk_version --short
gn args "out/$arch" --list=enable_desktop_android_extensions_cromite --short
