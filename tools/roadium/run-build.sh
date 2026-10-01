#!/bin/bash
set -euo pipefail
arch="${ROADIUM_ARCH:-arm64}"
case "$arch" in arm64|x64) ;; *) echo "Unsupported architecture: $arch" >&2; exit 2;; esac
build_script="${1:-$WORKSPACE/roadium/tools/roadium/compile.sh}"
state_dir="${2:-$WORKSPACE/chromium/src/out/$arch/roadium-build-status}"
mkdir -p "$state_dir"
exec 9>"$state_dir/build.lock"
if ! flock -n 9; then
  printf '%s\n' 'A build already holds the output lock.' >&2
  exit 75
fi
attempt=$(mktemp -d "$state_dir/run.XXXXXXXX")
printf '%s\n' "$$" > "$attempt/pid"
cat /proc/sys/kernel/random/boot_id > "$attempt/boot-id"
date -u +%FT%TZ > "$attempt/started-utc"
sha256sum "$build_script" > "$attempt/recipe.sha256"
printf '%s\n' "$attempt" > "$state_dir/current-run.$$.tmp"
mv "$state_dir/current-run.$$.tmp" "$state_dir/current-run"
if bash "$build_script" > "$attempt/build.log" 2>&1; then
  result=0
else
  result=$?
fi
printf '%s\n' "$result" > "$attempt/exit.tmp"
mv "$attempt/exit.tmp" "$attempt/exit"
exit "$result"