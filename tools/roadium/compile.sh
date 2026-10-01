#!/bin/bash
set -euo pipefail
arch="${1:-${ROADIUM_ARCH:-arm64}}"
jobs="${ROADIUM_JOBS:-12}"
case "$arch" in arm64|x64) ;; *) echo "Unsupported architecture: $arch" >&2; exit 2;; esac
if ! [[ "$jobs" =~ ^[0-9]+$ ]] || (( jobs < 1 || jobs > 12 )); then
  echo 'ROADIUM_JOBS must be between 1 and 12.' >&2
  exit 2
fi
export PATH="$WORKSPACE/chromium/src/third_party/llvm-build/Release+Asserts/bin:$WORKSPACE/depot_tools:/usr/local/go/bin:$WORKSPACE/mtool/bin:$PATH"
cd "$WORKSPACE/chromium/src"
test -f "out/$arch/args.gn"
python3 "$WORKSPACE/depot_tools/siso.py" ninja -C "out/$arch" --offline --local_jobs="$jobs" chrome_public_apk chrome_public_bundle
