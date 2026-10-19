#!/usr/bin/env python3
"""Apply the pinned Roadium patch series without overwriting unrelated work."""
import json
from pathlib import Path
import subprocess
import sys

from overlay_series import VerifiedSeries, source_diff


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def apply(source, cromite, fork):
    meta = json.loads((fork / "build/roadium/baseline.json").read_text())
    if git(cromite, "rev-parse", "HEAD").decode().strip() != meta["cromite_commit"]:
        raise ValueError("Cromite checkout does not match the pinned release.")
    if git(cromite, "status", "--porcelain", "--untracked-files=no").strip():
        raise ValueError("Pinned Cromite checkout has tracked local changes.")
    if git(source, "rev-parse", "HEAD^{tree}").decode().strip() != meta["baseline_source_tree"]:
        raise ValueError("Chromium+Cromite baseline source tree mismatch.")
    version = dict(
        line.split("=", 1) for line in (source / "chrome/VERSION").read_text().splitlines()
        if "=" in line
    )
    actual_version = ".".join(version[k] for k in ("MAJOR", "MINOR", "BUILD", "PATCH"))
    if actual_version != meta["chromium_version"]:
        raise ValueError("Chromium version does not match the pinned release.")
    with VerifiedSeries(source, fork, meta) as series:
        series.apply()


if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            raise ValueError("Usage: apply-overlay.py CHROMIUM_SOURCE CROMITE_CHECKOUT")
        apply(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(),
              Path(__file__).resolve().parents[2])
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Roadium overlay error: {exc}", file=sys.stderr)
        sys.exit(1)
