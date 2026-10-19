"""Verify ordered Roadium overlays using an isolated Git index."""
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile


def git(source, *args, env=None, input=None):
    return subprocess.check_output(
        ["git", "-C", str(source), *args], env=env, input=input)


def source_diff(source):
    return git(source, "diff", "--no-ext-diff", "--no-color", "--binary", "HEAD")


class VerifiedSeries:
    """Preflight every verified patch; never use the checkout's real index."""

    def __init__(self, source, fork, metadata):
        self.source = source.resolve()
        self._temp = tempfile.TemporaryDirectory(prefix="roadium-series-")
        try:
            root = Path(self._temp.name)
            self.env = dict(os.environ, GIT_INDEX_FILE=str(root / "index"))
            entries = metadata.get("patches")
            if not isinstance(entries, list) or not entries:
                raise ValueError("Roadium requires a nonempty ordered patch series.")
            self.entries = []
            paths = set()
            for entry in entries:
                if not isinstance(entry, dict):
                    raise ValueError("Invalid patch entry.")
                name, digest = entry.get("path"), entry.get("sha256")
                if not isinstance(name, str) or not isinstance(digest, str):
                    raise ValueError("Patch path and SHA-256 must be strings.")
                path = PurePosixPath(name)
                if (path.is_absolute() or "\\" in name or ":" in name
                        or any(part in ("..", ".") for part in name.split("/"))
                        or name != path.as_posix() or path.suffix != ".patch"):
                    raise ValueError("Patch path must be a normalized relative .patch path.")
                full_path = (fork / name).resolve()
                if not full_path.is_relative_to(fork.resolve()):
                    raise ValueError("Patch path must stay inside the Roadium checkout.")
                if full_path in paths:
                    raise ValueError("Duplicate patch path.")
                paths.add(full_path)
                if not re.fullmatch(r"[0-9a-f]{64}", digest):
                    raise ValueError("Invalid patch SHA-256.")
                data = full_path.read_bytes()
                if hashlib.sha256(data).hexdigest() != digest:
                    raise ValueError("Roadium patch checksum mismatch; no source changes applied.")
                # Apply the verified bytes, not a path that could change after hashing.
                self.entries.append(({"path": name, "sha256": digest}, data))
            git(self.source, "read-tree", "HEAD", env=self.env)
            self.trees = [self._tree()]
            self.diffs = [b""]
            for _, data in self.entries:
                git(self.source, "apply", "--cached", "--binary", "-",
                    env=self.env, input=data)
                self.trees.append(self._tree())
                self.diffs.append(git(
                    self.source, "diff", "--no-ext-diff", "--no-color",
                    "--cached", "--binary", "HEAD", env=self.env))
        except BaseException:
            self.close()
            raise

    def _tree(self):
        return git(self.source, "write-tree", env=self.env).decode().strip()

    def close(self):
        self._temp.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def remaining_diff(self, prefix):
        return git(self.source, "diff", "--no-ext-diff", "--no-color",
                   "--cached", "--binary", self.trees[prefix], env=self.env)

    def verify_applied(self):
        if source_diff(self.source) != self.diffs[-1]:
            raise ValueError("Applied source differs from the verified complete overlay series.")
        return hashlib.sha256(self.diffs[-1]).hexdigest()

    def apply(self):
        current = source_diff(self.source)
        staged = git(self.source, "diff", "--no-ext-diff", "--no-color",
                     "--cached", "--binary")
        unstaged = git(self.source, "diff", "--no-ext-diff", "--no-color", "--binary")
        if staged and (staged != current or unstaged):
            raise ValueError("Source index contains unrelated changes.")
        if current == self.diffs[-1]:
            print("The verified Roadium overlay series is already applied.")
            return
        matches = [i for i, diff in enumerate(self.diffs) if diff == current]
        if not matches or (current and not staged):
            raise ValueError("Source has unrelated or unstaged partial changes; refusing to alter it.")
        prefix = max(matches)
        delta = self.remaining_diff(prefix)
        # One combined application, after every later patch has passed preflight.
        git(self.source, "apply", "--index", "--check", "--binary", "-", input=delta)
        touched = git(self.source, "diff", "--cached", "--name-only", "-z",
                      self.trees[prefix], env=self.env).split(b"\0")
        backup = []
        for name in filter(None, touched):
            path = self.source / os.fsdecode(name)
            if not path.resolve().is_relative_to(self.source) or path.is_symlink():
                raise ValueError("Overlay transaction cannot modify escaping or symlink paths.")
            backup.append((path, path.read_bytes() if path.exists() else None,
                           path.stat().st_mode if path.exists() else None))
        index = Path(git(self.source, "rev-parse", "--git-path", "index").decode().strip())
        if not index.is_absolute():
            index = self.source / index
        index_bytes = index.read_bytes()
        try:
            git(self.source, "apply", "--index", "--binary", "-", input=delta)
            self.verify_applied()
        except BaseException:
            # Restore only transaction-owned paths and the initial index, never
            # reset/clean an entire source checkout or delete unrelated files.
            for path, data, mode in backup:
                if data is None:
                    if path.exists():
                        path.unlink()
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
                    path.chmod(mode)
            index.write_bytes(index_bytes)
            raise
        print(f"Applied {len(self.entries) - prefix} verified Roadium patch(es).")
