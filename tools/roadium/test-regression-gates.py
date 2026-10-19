#!/usr/bin/env python3
"""Negative controls for integrity and complete successful test evidence."""
import copy
import gzip
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from regression_checks import FORK, check_results, digest, inside, offline, patches, read_json, snapshots
from youtube_inventory import attach_native_results


class GatesTest(unittest.TestCase):
    def test_repository_integrity(self):
        self.assertEqual(offline()['snapshot_families'], 3)

    def test_path_escape(self):
        for name in ('../key', '/key', 'C:/key', 'a\\key', './key', 'a//key'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                inside(FORK, name)

    def test_patch_tamper_and_duplicate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'build/roadium').mkdir(parents=True)
            (root / 'test.patch').write_bytes(b'reviewed patch')
            row = dict(path='test.patch', sha256=digest(b'reviewed patch'))
            path = root / 'build/roadium/baseline.json'
            path.write_text(json.dumps(dict(patches=[row])), encoding='utf-8')
            patches(root)
            (root / 'test.patch').write_bytes(b'changed patch')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                patches(root)
            path.write_text(json.dumps(dict(patches=[row, row])), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                patches(root)

    def test_snapshot_negative_controls(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            revision = 'a' * 40
            plain = b'[Adblock Plus 2.0]\n||ads.invalid^\n'
            data = gzip.compress(plain, mtime=0)
            rows = [dict(file=name+'.txt.gz', source_url='https://raw.githubusercontent.com/uazo/cromite/'+revision+'/filters/'+name+'.txt',
                         canonical_url='https://uazo.github.io/cromite/filters/'+name+'.txt', bytes=len(plain),
                         sha256=digest(plain), gzip_sha256=digest(data), license='GPL-3.0-or-later', attribution='Fixture')
                    for name in ('one', 'two')]
            manifest = dict(format=1, revision=revision, inputs=rows)
            (root / 'README.md').write_text('Test-only attributed data', encoding='utf-8')
            for row in rows:
                (root / row['file']).write_bytes(data)

            def write(value):
                (root / 'manifest.json').write_text(json.dumps(value), encoding='utf-8')
            write(manifest)
            snapshots(root)
            for field, bad in (('gzip_sha256', '0'*64), ('sha256', '0'*64), ('bytes', 0),
                               ('license', ''), ('attribution', ''), ('source_url', 'https://evil.invalid/'),
                               ('canonical_url', 'https://evil.invalid/'), ('file', '../one.txt.gz')):
                broken = copy.deepcopy(manifest)
                broken['inputs'][0][field] = bad
                write(broken)
                with self.subTest(field=field), self.assertRaises(ValueError):
                    snapshots(root)
            write(manifest)
            (root / rows[0]['file']).write_bytes(data[:-1])
            with self.assertRaises(ValueError):
                snapshots(root)

    def test_incomplete_failed_skipped_retried_results(self):
        good = dict(all_tests=['A', 'B'], disabled_tests=[], per_iteration_data=[dict(A=[dict(status='SUCCESS')], B=[dict(status='SUCCESS')])])
        self.assertEqual(check_results(good, ['A', 'B']), 2)
        mutations = []
        for status in ('FAILURE', 'SKIPPED', 'TIMEOUT', 'CRASH'):
            bad = copy.deepcopy(good)
            bad['per_iteration_data'][0]['A'][0]['status'] = status
            mutations.append(bad)
        for change in ('missing', 'retry', 'disabled', 'empty'):
            bad = copy.deepcopy(good)
            if change == 'missing': del bad['per_iteration_data'][0]['B']
            if change == 'retry': bad['per_iteration_data'][0]['A'] *= 2
            if change == 'disabled': bad['disabled_tests'] = ['B']
            if change == 'empty': bad['all_tests'] = []
            mutations.append(bad)
        for bad in mutations:
            with self.subTest(result=bad), self.assertRaises(ValueError):
                check_results(bad, ['A', 'B'])

    def test_native_audit_identity(self):
        inventory = dict(rules=[dict(id='one', url='https://good.invalid/', rule='||ads.invalid^')])
        for actual in ([], [dict(id='one', url='https://evil.invalid/', rule='||ads.invalid^')],
                       [dict(id='one', url='https://good.invalid/', rule='changed')]):
            output = '\n'.join('ROADIUM_YOUTUBE_AUDIT ' + json.dumps(row) for row in actual)
            native = dict(per_iteration_data=[dict(Test=[dict(status='SUCCESS', output_snippet=output)])])
            with self.subTest(actual=actual), self.assertRaises(ValueError):
                attach_native_results(copy.deepcopy(inventory), native)

    def test_release_rejects_missing_or_offline(self):
        spec = importlib.util.spec_from_file_location('release', Path(__file__).with_name('release-gates.py'))
        release = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(release)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with self.assertRaises(FileNotFoundError):
                release.evaluate(root)
            (root / 'suite.json').write_text(json.dumps(dict(status='passed', mode='offline', integrity=offline())), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'offline-only'):
                release.evaluate(root)

    def test_release_artifact_and_manual_bindings(self):
        # Synthetic successful suites isolate packaging/approval contract tests.
        # These records are never written to real acceptance evidence.
        spec = importlib.util.spec_from_file_location('release_test', Path(__file__).with_name('release-gates.py'))
        release = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(release)
        spec2 = importlib.util.spec_from_file_location('runner_test', Path(__file__).with_name('run-regressions.py'))
        runner = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(runner)
        integrity = offline()
        plan = read_json(Path(__file__).with_name('regression-plan.json'))
        with tempfile.TemporaryDirectory() as temp, mock.patch('youtube_inventory.attach_native_results'):
            root = Path(temp)

            def write(name, value):
                path = root / name
                path.write_text(json.dumps(value), encoding='utf-8')
                return digest(path.read_bytes())
            suite = dict(status='passed', mode='full', integrity=integrity, tools=runner.tool_identity(),
                         source_patch_sha256='a'*64, source_overlay_tree='b'*40, results={})
            for name, row in plan['suites'].items():
                results = dict(all_tests=row['tests'], disabled_tests=[],
                               per_iteration_data=[{test: [dict(status='SUCCESS')] for test in row['tests']}])
                sha = write(name+'.json', results)
                suite['results'][name] = dict(sha256=sha, executions=len(row['tests']))
            write('suite.json', suite)
            for arch in ('x64', 'arm64'):
                manifest = read_json(FORK / 'docs/shields/evidence/card08' / (arch+'-build-manifest.json'))
                manifest.update(source_patch_sha256='a'*64, source_overlay_tree='b'*40,
                                roadium_version_code_offset=integrity['baseline']['roadium_version_code_offset'])
                (root / arch).mkdir()
                for item in manifest['artifacts']:
                    data = (arch + item['file']).encode()
                    (root / arch / item['file']).write_bytes(data)
                    item.update(sha256=digest(data), bytes=len(data))
                write(arch+'-build-manifest.json', manifest)
            write('approvals.json', dict(scope=plan['scope'], excluded_cards=plan['excluded_cards'], gates={}))
            blocked = release.evaluate(root)
            self.assertEqual(blocked['status'], 'blocked')
            self.assertIn('physical_android12_blazer_ev', blocked['blockers'])
            self.assertTrue(any('diagnostic APK' in b for b in blocked['blockers']))
            self.assertTrue(any('AAB upload signature' in b for b in blocked['blockers']))
            approvals = read_json(root / 'approvals.json')
            approvals['binding'] = blocked['binding']
            proof_sha = write('proof.json', dict(test_only=True))
            approvals['gates'] = {gate: dict(status='passed', reviewer='Synthetic', date='2026-10-18',
                                            evidence='proof.json', sha256=proof_sha) for gate in plan['manual_gates']}
            write('approvals.json', approvals)
            # Manual attestations cannot turn diagnostic/unsigned binaries into releases.
            self.assertEqual(release.evaluate(root)['status'], 'blocked')
            for arch in ('x64', 'arm64'):
                manifest = read_json(root / (arch+'-build-manifest.json'))
                for item in manifest['artifacts']:
                    item['certificate_sha256'] = 'c'*64
                    item['jar_signature_status'] = 'verified'
                write(arch+'-build-manifest.json', manifest)
            self.assertEqual(release.evaluate(root)['status'], 'evidence_complete')
            approvals['binding']['source_patch_sha256'] = 'd'*64
            write('approvals.json', approvals)
            self.assertEqual(release.evaluate(root)['status'], 'blocked')
            (root / 'x64/ChromePublic.apk').write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'Artifact bytes changed'):
                release.evaluate(root)


if __name__ == '__main__':
    unittest.main()
