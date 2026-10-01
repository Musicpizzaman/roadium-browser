#!/usr/bin/env python3
"""Apply the pinned Roadium foundation without overwriting unrelated source work."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def source_diff(source):
    return git(source, "diff", "--no-ext-diff", "--no-color", "--binary", "HEAD")


def apply(source, cromite, fork):
    meta = json.loads((fork / "build/roadium/baseline.json").read_text())
    if len(meta["patches"]) != 1:
        raise ValueError("This foundation loader expects one complete overlay diff.")
    entry = meta["patches"][0]
    patch_path = (fork / entry["path"]).resolve()
    if not patch_path.is_relative_to(fork.resolve()):
        raise ValueError("Patch path must stay inside the Roadium checkout.")
    patch = patch_path.read_bytes()
    if hashlib.sha256(patch).hexdigest() != entry["sha256"]:
        raise ValueError("Roadium patch checksum mismatch; no source changes applied.")
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
    staged = git(source, "diff", "--no-ext-diff", "--no-color", "--cached", "--binary")
    current = source_diff(source)
    if current == patch:
        if staged and (staged != patch or git(source, "diff", "--binary").strip()):
            raise ValueError("Source index contains unrelated changes.")
        print("The verified Roadium overlay is already applied.")
        return
    if staged.strip():
        raise ValueError("Source has staged changes; refusing to alter it.")
    if git(source, "status", "--porcelain", "--untracked-files=no").strip():
        raise ValueError("Source has unrelated tracked changes; refusing to alter it.")
    subprocess.run(["git", "-C", str(source), "apply", "--index", "--check", str(patch_path)], check=True)
    subprocess.run(["git", "-C", str(source), "apply", "--index", str(patch_path)], check=True)
    if source_diff(source) != patch:
        raise ValueError("Applied source diff differs from the pinned overlay; inspect the source.")
    print("Applied the verified Roadium overlay.")


if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            raise ValueError("Usage: apply-overlay.py CHROMIUM_SOURCE CROMITE_CHECKOUT")
        apply(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(),
              Path(__file__).resolve().parents[2])
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Roadium overlay error: {exc}", file=sys.stderr)
        sys.exit(1)
