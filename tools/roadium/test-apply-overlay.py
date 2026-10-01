#!/usr/bin/env python3
"""Exercise overlay refusal paths without touching the real Chromium checkout."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("apply-overlay.py")
spec = importlib.util.spec_from_file_location("overlay", SCRIPT)
overlay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(overlay)


class OverlayTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="roadium-overlay-")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.source, self.cromite, self.fork = root / "source", root / "cromite", root / "fork"
        for repo in (self.source, self.cromite):
            repo.mkdir()
            self.git(repo, "init", "-q")
        (self.source / "chrome").mkdir()
        self.version = self.source / "chrome/VERSION"
        self.version.write_text("MAJOR=153\nMINOR=0\nBUILD=8010\nPATCH=37\n")
        self.target = self.source / "browser.txt"
        self.target.write_text("Cromite\n")
        self.other = self.source / "other.txt"
        self.other.write_text("preserve\n")
        (self.cromite / "upstream.txt").write_text("pinned\n")
        for repo in (self.source, self.cromite):
            self.git(repo, "add", ".")
            self.git(repo, "-c", "user.name=Roadium Fixture", "-c",
                     "user.email=fixture@example.invalid", "commit", "-qm", "baseline")
        self.target.write_text("Roadium\n")
        patch = overlay.source_diff(self.source)
        self.target.write_text("Cromite\n")
        (self.fork / "build/roadium/patches").mkdir(parents=True)
        self.patch = self.fork / "build/roadium/patches/foundation.patch"
        self.patch.write_bytes(patch)
        self.meta = {
            "chromium_version": "153.0.8010.37",
            "cromite_commit": self.git(self.cromite, "rev-parse", "HEAD").decode().strip(),
            "baseline_source_tree": self.git(self.source, "rev-parse", "HEAD^{tree}").decode().strip(),
            "patches": [{"path": "build/roadium/patches/foundation.patch",
                         "sha256": hashlib.sha256(patch).hexdigest()}],
        }
        self.save_meta()

    def git(self, repo, *args):
        return subprocess.check_output(["git", "-C", str(repo), *args],
                                       stderr=subprocess.DEVNULL)

    def save_meta(self):
        (self.fork / "build/roadium/baseline.json").write_text(json.dumps(self.meta))

    def apply(self):
        overlay.apply(self.source, self.cromite, self.fork)

    def assert_refused(self):
        before = overlay.source_diff(self.source)
        with self.assertRaises(ValueError):
            self.apply()
        self.assertEqual(before, overlay.source_diff(self.source))

    def test_applies_and_is_idempotent(self):
        self.apply()
        self.assertEqual("Roadium\n", self.target.read_text())
        before = overlay.source_diff(self.source)
        self.apply()
        self.assertEqual(before, overlay.source_diff(self.source))

    def test_new_file_is_staged_and_repeatable(self):
        fresh = self.source / "new-test.txt"
        fresh.write_text("new test\n")
        self.target.write_text("Roadium\n")
        self.git(self.source, "add", "-N", fresh.name)
        patch = overlay.source_diff(self.source)
        self.git(self.source, "update-index", "--force-remove", fresh.name)
        fresh.unlink()
        self.target.write_text("Cromite\n")
        self.patch.write_bytes(patch)
        self.meta["patches"][0]["sha256"] = hashlib.sha256(patch).hexdigest()
        self.save_meta()
        self.apply()
        self.assertEqual("new test\n", fresh.read_text())
        self.assertEqual(patch, self.git(self.source, "diff", "--cached", "--binary"))
        self.apply()

    def test_dirty_source_is_preserved(self):
        self.other.write_text("user edit\n")
        self.assert_refused()
        self.assertEqual("user edit\n", self.other.read_text())

    def test_staged_source_is_preserved(self):
        self.other.write_text("staged edit\n")
        self.git(self.source, "add", "other.txt")
        self.assert_refused()
        self.assertTrue(self.git(self.source, "diff", "--cached").strip())

    def test_wrong_tree_is_refused(self):
        self.meta["baseline_source_tree"] = "0" * 40
        self.save_meta()
        self.assert_refused()

    def test_wrong_cromite_is_refused(self):
        self.meta["cromite_commit"] = "0" * 40
        self.save_meta()
        self.assert_refused()

    def test_wrong_version_is_refused(self):
        self.version.write_text("MAJOR=154\nMINOR=0\nBUILD=8010\nPATCH=37\n")
        self.assert_refused()

    def test_modified_patch_is_refused(self):
        self.patch.write_bytes(self.patch.read_bytes() + b"tampered")
        self.assert_refused()


if __name__ == "__main__":
    unittest.main()
