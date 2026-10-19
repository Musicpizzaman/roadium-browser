#!/bin/bash
set -euo pipefail
export WORKSPACE=/home/lg/working_dir
export PATH="$WORKSPACE/depot_tools:$PATH"
export DEPOT_TOOLS_UPDATE=0
export ADB_SERVER_SOCKET=tcp:host.docker.internal:5037
cd "$WORKSPACE/chromium/src"
evidence=out/x64/card04-test-results
mkdir -p "$evidence"
vpython3 out/x64/bin/run_roadium_shields_unit_tests -d emulator-5554 --test-launcher-retry-limit 0 --json-results-file "$evidence/native.json"
vpython3 out/x64/bin/run_roadium_shields_junit_tests --json-results-file "$evidence/diagnostics-junit.json"
vpython3 out/x64/bin/run_roadium_media_junit_tests --json-results-file "$evidence/media-junit.json"
