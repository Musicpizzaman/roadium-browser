#!/usr/bin/env python3
"""Exercise overlay refusal paths without touching the real Chromium checkout."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import overlay_series

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


    def make_series(self, keep_prefix=False):
        self.apply()
        prefix_tree = self.git(self.source, "write-tree").decode().strip()
        self.target.write_text("Roadium Shields\n")
        self.new_file = self.source / "diagnostics.txt"
        self.new_file.write_text("local diagnostics\n")
        self.git(self.source, "add", ".")
        second = self.git(self.source, "diff", "--cached", "--binary", prefix_tree)
        self.expected_series = overlay.source_diff(self.source)
        self.second_patch = self.patch.with_name("diagnostics.patch")
        self.second_patch.write_bytes(second)
        self.meta["patches"].append({
            "path": "build/roadium/patches/diagnostics.patch",
            "sha256": hashlib.sha256(second).hexdigest(),
        })
        # This checkout is a disposable fixture owned entirely by the test.
        self.git(self.source, "reset", "--hard", "HEAD")
        if keep_prefix:
            self.git(self.source, "apply", "--index", str(self.patch))
        self.save_meta()

    def test_overlapping_series_and_new_file_are_repeatable(self):
        self.make_series()
        self.apply()
        self.assertEqual("Roadium Shields\n", self.target.read_text())
        self.assertEqual("local diagnostics\n", self.new_file.read_text())
        self.assertEqual(self.expected_series, overlay.source_diff(self.source))
        self.apply()
        with overlay_series.VerifiedSeries(self.source, self.fork, self.meta) as plan:
            self.assertEqual(hashlib.sha256(self.expected_series).hexdigest(),
                             plan.verify_applied())

    def test_verified_staged_foundation_can_be_extended(self):
        self.make_series(keep_prefix=True)
        self.apply()
        self.assertEqual(self.expected_series, overlay.source_diff(self.source))

    def test_later_bad_checksum_preserves_existing_prefix(self):
        self.make_series(keep_prefix=True)
        before = overlay.source_diff(self.source)
        self.second_patch.write_bytes(self.second_patch.read_bytes() + b"tampered")
        with self.assertRaises(ValueError):
            self.apply()
        self.assertEqual(before, overlay.source_diff(self.source))
        self.assertFalse(self.new_file.exists())

    def test_invalid_later_patch_is_preflighted_before_mutation(self):
        self.make_series()
        data = self.second_patch.read_bytes().replace(b"-Roadium\n", b"-wrong context\n")
        self.second_patch.write_bytes(data)
        self.meta["patches"][1]["sha256"] = hashlib.sha256(data).hexdigest()
        self.save_meta()
        with self.assertRaises(subprocess.CalledProcessError):
            self.apply()
        self.assertEqual(b"", overlay.source_diff(self.source))
        self.assertFalse(self.new_file.exists())

    def test_untracked_collision_is_preserved(self):
        self.make_series()
        self.new_file.write_text("user-owned file\n")
        with self.assertRaises(subprocess.CalledProcessError):
            self.apply()
        self.assertEqual("user-owned file\n", self.new_file.read_text())
        self.assertEqual(b"", overlay.source_diff(self.source))

    def test_malformed_duplicate_and_escaping_entries_are_refused(self):
        variants = [[], [self.meta["patches"][0]] * 2,
                    [{"path": "../escape.patch", "sha256": "0" * 64}],
                    [{"path": "C:/escape.patch", "sha256": "0" * 64}],
                    [{"path": "build/roadium/patches/foundation.patch", "sha256": 4}]]
        for entries in variants:
            with self.subTest(entries=entries):
                self.meta["patches"] = entries
                self.save_meta()
                with self.assertRaises(ValueError):
                    self.apply()
                self.assertEqual(b"", overlay.source_diff(self.source))

    def test_artifact_check_rejects_only_foundation_prefix(self):
        self.make_series(keep_prefix=True)
        with overlay_series.VerifiedSeries(self.source, self.fork, self.meta) as plan:
            with self.assertRaises(ValueError):
                plan.verify_applied()

    def test_write_failure_restores_only_transaction_paths_and_index(self):
        self.make_series(keep_prefix=True)
        before = overlay.source_diff(self.source)
        index_before = (self.source / ".git/index").read_bytes()
        unrelated = self.source / "unrelated-untracked.txt"
        unrelated.write_text("preserve\n")
        real_git = overlay_series.git

        def failing_git(source, *args, **kwargs):
            result = real_git(source, *args, **kwargs)
            if args[:3] == ("apply", "--index", "--binary"):
                raise subprocess.CalledProcessError(1, "injected write failure")
            return result

        with mock.patch.object(overlay_series, "git", side_effect=failing_git):
            with self.assertRaises(subprocess.CalledProcessError):
                self.apply()
        self.assertEqual(before, overlay.source_diff(self.source))
        self.assertEqual(index_before, (self.source / ".git/index").read_bytes())
        self.assertFalse(self.new_file.exists())
        self.assertEqual("preserve\n", unrelated.read_text())


if __name__ == "__main__":
    unittest.main()
