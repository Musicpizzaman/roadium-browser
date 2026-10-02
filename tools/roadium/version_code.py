#!/usr/bin/env python3
"""Derive Roadium's upload version code without changing the pinned engine version."""
import argparse
import json
from pathlib import Path
import sys

def expected_version_code(source, metadata, arch):
    if arch not in ("arm64", "x64"):
        raise ValueError("Unsupported Roadium architecture")
    offset = metadata.get("roadium_version_code_offset", 0)
    if type(offset) is not int or offset < 0 or offset % 10:
        raise ValueError("Roadium version-code offset must be a nonnegative multiple of 10")
    sys.path.insert(0, str(Path(source) / "build/util"))
    import android_chrome_version
    _, _, build, patch = map(int, metadata["chromium_version"].split("."))
    code = int(android_chrome_version.GenerateVersionCodes(build, patch, arch)["CHROME_VERSION_CODE"]) + offset
    if not 0 < code <= 2_100_000_000:
        raise ValueError("Roadium version code is outside Google Play's supported range")
    return code

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("arch", choices=("arm64", "x64"))
    args = parser.parse_args()
    print(expected_version_code(args.source, json.loads(args.baseline.read_text()), args.arch))

if __name__ == "__main__":
    main()
