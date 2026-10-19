#!/usr/bin/env python3
"""Check a reviewable release evidence bundle; never sign, upload or authorize."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

from regression_checks import FORK, check_results, digest, inside, offline, read_json


def evaluate(root):
    current = offline()
    plan = read_json(FORK / 'tools/roadium/regression-plan.json')
    suite = read_json(root / 'suite.json')
    if suite.get('status') != 'passed' or suite.get('mode') != 'full' or suite.get('integrity') != current:
        raise ValueError('Missing, failed, offline-only or stale full-suite evidence')
    spec = importlib.util.spec_from_file_location('roadium_runner', FORK / 'tools/roadium/run-regressions.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    if suite['tools'] != runner.tool_identity():
        raise ValueError('Suite tooling changed since execution')
    for name, row in plan['suites'].items():
        data = (root / (name + '.json')).read_bytes()
        if digest(data) != suite['results'][name]['sha256']:
            raise ValueError('Test result changed: ' + name)
        if check_results(json.loads(data), row['tests']) != suite['results'][name]['executions']:
            raise ValueError('Test execution count changed: ' + name)
    from youtube_inventory import attach_native_results, collect
    attach_native_results(collect(), read_json(root / 'native.json'))
    binding = dict(source_patch_sha256=suite['source_patch_sha256'],
                   source_overlay_tree=suite['source_overlay_tree'],
                   baseline_sha256=current['baseline_sha256'], artifacts={})
    blockers = []
    for arch in ('x64', 'arm64'):
        manifest = read_json(root / (arch + '-build-manifest.json'))
        baseline = current['baseline']
        for key in ('baseline_source_tree', 'cromite_commit'):
            if manifest[key] != baseline[key]:
                raise ValueError('Artifact baseline mismatch: ' + key)
        if (manifest['source_patches'] != baseline['patches'] or manifest['architecture'] != arch
                or manifest['source_patch_sha256'] != suite['source_patch_sha256']
                or manifest['source_overlay_tree'] != suite['source_overlay_tree']
                or manifest['version'] != baseline['chromium_version']
                or manifest['roadium_version_code_offset'] != baseline['roadium_version_code_offset']
                or manifest['compiler_exit'] != 0 or manifest['bundletool_exit'] != 0
                or manifest['bundletool_validation'] != 'passed'
                or manifest['package'] != 'io.github.musicpizzaman.roadium'
                or manifest['required_automotive'] is not True or manifest['picture_in_picture'] is not False
                or manifest['target_sdk'] != 36):
            raise ValueError('Artifact verification/source mismatch: ' + arch)
        artifacts = manifest['artifacts']
        if len(artifacts) != 2 or {a['file'] for a in artifacts} != {'ChromePublic.apk', 'ChromePublic.aab'}:
            raise ValueError('Missing or duplicate APK/AAB')
        binding['artifacts'][arch] = {}
        for item in artifacts:
            path = inside(root / arch, item['file'])
            import hashlib
            hasher = hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    hasher.update(chunk)
            sha = hasher.hexdigest()
            if sha != item['sha256'] or path.stat().st_size != item['bytes'] or item['zip_crc'] != 'passed':
                raise ValueError('Artifact bytes changed: ' + str(path))
            if not item.get('bundled_filters', {}).get('resources'):
                raise ValueError('Missing packaged resource verification')
            if item['file'].endswith('.apk') and item.get('apk_signature_verification') != 'passed':
                raise ValueError('APK signature verification missing')
            if item['file'].endswith('.apk') and item.get('certificate_sha256') == '32a2fc74d731105859e5a85df16d95f102d85b22099b8064c5d8915c61dad1e0':
                blockers.append(arch + ': diagnostic APK certificate; production signing remains separate')
            if item['file'].endswith('.aab') and item.get('jar_signature_status') != 'verified':
                blockers.append(arch + ': AAB upload signature not verified')
            binding['artifacts'][arch][item['file']] = sha
    approvals = read_json(root / 'approvals.json')
    if approvals.get('scope') != plan['scope'] or approvals.get('excluded_cards') != plan['excluded_cards']:
        blockers.append('release scope must explicitly match the reviewed plan')
    if approvals.get('binding') != binding:
        blockers.append('manual acceptance must bind these exact source and package hashes')
    for gate in plan['manual_gates']:
        approval = approvals.get('gates', {}).get(gate, {})
        if (approval.get('status') != 'passed' or not approval.get('reviewer') or not approval.get('date')
                or not approval.get('evidence')):
            blockers.append(gate)
            continue
        evidence = inside(root, approval['evidence'])
        if digest(evidence.read_bytes()) != approval.get('sha256'):
            blockers.append(gate + ': evidence digest mismatch')
    return dict(format=1, status='blocked' if blockers else 'evidence_complete',
                authorization='No release authorization, signing or upload is performed',
                scope=plan['scope'], excluded_cards=plan['excluded_cards'], binding=binding, blockers=blockers)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = evaluate(args.evidence.resolve())
    except Exception as error:
        result = dict(format=1, status='blocked', blockers=[str(error)])
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'evidence_complete' else 1


if __name__ == '__main__':
    sys.exit(main())
