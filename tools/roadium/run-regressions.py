#!/usr/bin/env python3
"""Run fork checks or focused tests in the pinned prepared Chromium environment."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

from regression_checks import FORK, check_results, digest, offline, read_json


def tool_identity():
    names = ('regression_checks.py', 'run-regressions.py', 'release-gates.py',
             'regression-plan.json', 'test-regression-gates.py', 'test-apply-overlay.py',
             'test-filter-artifacts.py', 'overlay_series.py', 'filter_artifacts.py',
             'preset_inventory.py', 'youtube_inventory.py', 'verify-artifacts.py')
    return {name: digest((FORK / 'tools/roadium' / name).read_bytes()) for name in names}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New directory; existing results never reused')
    parser.add_argument('--source', type=Path, help='Pinned, already applied Chromium checkout; enables full suite')
    parser.add_argument('--device', help='Explicit owned test emulator serial, required for full suite')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    out = args.output.resolve()
    report = dict(format=1, status='failed', mode='full' if args.source else 'offline',
                  started_utc=datetime.now(timezone.utc).isoformat())
    env = dict(os.environ, PYTHONIOENCODING='utf-8')

    def run(name, command, cwd=FORK, timeout=1800):
        with (out / (name + '.log')).open('wb') as log:
            subprocess.run(command, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=timeout)

    try:
        report['tools'] = tool_identity()
        report['integrity'] = offline()
        run('loader', [sys.executable, str(FORK / 'tools/roadium/test-apply-overlay.py')])
        run('gates', [sys.executable, str(FORK / 'tools/roadium/test-regression-gates.py')])
        if args.source:
            if not args.device:
                raise ValueError('--device must identify an owned disposable emulator')
            source = args.source.resolve()
            from overlay_series import VerifiedSeries, git
            baseline = report['integrity']['baseline']
            if git(source, 'rev-parse', 'HEAD^{tree}').decode().strip() != baseline['baseline_source_tree']:
                raise ValueError('Wrong Chromium baseline')
            with VerifiedSeries(source, FORK, baseline) as series:
                report['source_patch_sha256'] = series.verify_applied()
                report['source_overlay_tree'] = series.trees[-1]
            for name, key in (('shields_category_inputs.inc', 'category_include_sha256'),
                              ('shields_youtube_rules.inc', 'youtube_include_sha256')):
                if digest((source / 'components/adblock/test' / name).read_bytes()) != report['integrity'][key]:
                    raise ValueError('Compiled fixture source mismatch: ' + name)
            env['CHROMIUM_SOURCE'] = str(source)
            run('resources', [sys.executable, str(FORK / 'tools/roadium/test-filter-artifacts.py')])
            depot = source.parents[1] / 'depot_tools'
            env['PATH'] = str(depot) + os.pathsep + env.get('PATH', '')
            env['DEPOT_TOOLS_UPDATE'] = '0'
            adb = source / 'third_party/android_sdk/public/platform-tools/adb'
            boot = subprocess.check_output([str(adb), '-s', args.device, 'shell', 'getprop', 'sys.boot_completed'], env=env, timeout=30)
            if boot.strip() != b'1':
                raise ValueError('Owned emulator is not booted; no test was counted as passing')
            current_user = subprocess.check_output([str(adb), '-s', args.device, 'shell', 'am', 'get-current-user'], env=env, timeout=30).decode().strip()
            if current_user != '0':
                raise ValueError('Focused native harness requires foreground test user 0 on the owned read-only emulator')
            report['device'] = dict(serial=args.device, foreground_user=current_user,
                                    adb_server=env.get('ADB_SERVER_SOCKET', 'default local server'))
            plan = read_json(FORK / 'tools/roadium/regression-plan.json')
            run('compile', [sys.executable, str(depot / 'siso.py'), 'ninja', '-C', 'out/x64',
                            '--offline', '--local_jobs=8', *[row['target'] for row in plan['suites'].values()]], source, timeout=10800)
            report['results'] = {}
            for name, row in plan['suites'].items():
                result = out / (name + '.json')
                command = ['vpython3', str(source / 'out/x64/bin' / row['runner']),
                           '--json-results-file', str(result)]
                if name == 'native':
                    command += ['-d', args.device, '--test-launcher-retry-limit', '0']
                run(name, command, source)
                count = check_results(read_json(result), row['tests'])
                report['results'][name] = dict(executions=count, sha256=digest(result.read_bytes()))
            from youtube_inventory import attach_native_results, collect
            audit = attach_native_results(collect(), read_json(out / 'native.json'))
            (out / 'youtube-audit.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
            # Confirm test execution did not alter the verified browser source.
            with VerifiedSeries(source, FORK, baseline) as series:
                series.verify_applied()
        report['status'] = 'passed'
    except Exception as error:
        report['error'] = str(error)
        print(str(error), file=sys.stderr)
    finally:
        report['completed_utc'] = datetime.now(timezone.utc).isoformat()
        (out / 'suite.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(status=report['status'], mode=report['mode'], report=str(out / 'suite.json'))))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    sys.exit(main())
