#!/usr/bin/env python3
"""Offline integrity checks. These do not assert browser/runtime acceptance."""
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

FORK = Path(__file__).resolve().parents[2]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def inside(root, name):
    path = PurePosixPath(name)
    if (not name or path.is_absolute() or '\\' in name or ':' in name
            or any(p in ('', '.', '..') for p in name.split('/'))):
        raise ValueError('Expected normalized relative path: ' + name)
    result = (root / name).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError('Path escapes root: ' + name)
    return result


def patches(fork):
    baseline = read_json(fork / 'build/roadium/baseline.json')
    entries = baseline['patches']
    if not entries or len({r['path'] for r in entries}) != len(entries):
        raise ValueError('Empty or duplicate patch series')
    for row in entries:
        if not row['path'].endswith('.patch'):
            raise ValueError('Expected overlay patch')
        if digest(inside(fork, row['path']).read_bytes()) != row['sha256']:
            raise ValueError('Patch hash mismatch: ' + row['path'])
    return baseline


def snapshots(root):
    manifest = read_json(root / 'manifest.json')
    if manifest.get('format') != 1 or len(manifest['inputs']) != 2:
        raise ValueError('Expected two immutable inputs per snapshot family')
    revision = manifest['revision']
    if not re.fullmatch('[0-9a-f]{40}', revision):
        raise ValueError('Snapshot revision must be immutable')
    urls = set()
    for row in manifest['inputs']:
        name = row['file']
        if '/' in name or not name.endswith('.txt.gz'):
            raise ValueError('Expected local gzip input')
        data = inside(root, name).read_bytes()
        if len(data) > 5 * 1024 * 1024 or digest(data) != row['gzip_sha256']:
            raise ValueError('Compressed snapshot mismatch: ' + name)
        if 'gzip_bytes' in row and len(data) != row['gzip_bytes']:
            raise ValueError('Compressed length mismatch: ' + name)
        with gzip.open(inside(root, name), 'rb') as stream:
            plain = stream.read(5 * 1024 * 1024 + 1)
        if len(plain) != row['bytes'] or len(plain) > 5 * 1024 * 1024 or digest(plain) != row['sha256']:
            raise ValueError('Plain snapshot mismatch: ' + name)
        plain.decode('utf-8-sig')
        canonical = 'https://uazo.github.io/cromite/filters/' + name.removesuffix('.gz')
        source = 'https://raw.githubusercontent.com/uazo/cromite/' + revision + '/filters/' + name.removesuffix('.gz')
        if row['canonical_url'] != canonical or row['source_url'] != source or canonical in urls:
            raise ValueError('Snapshot identity mismatch: ' + name)
        urls.add(canonical)
        if not row['license'].strip() or not row['attribution'].strip():
            raise ValueError('Missing license/attribution: ' + name)
    notices = root / ('NOTICES.txt' if root.name == 'filters' else 'README.md')
    if not notices.is_file() or not notices.read_text(encoding='utf-8').strip():
        raise ValueError('Missing distributed snapshot notices')
    return manifest


def added_file(patch, name):
    """Read a complete new text file; refuse modifications/ambiguous hunks."""
    section = patch.split('diff --git a/' + name + ' b/' + name + '\n')
    if len(section) != 2:
        raise ValueError('Missing/duplicate generated overlay input: ' + name)
    section = section[1].split('diff --git ', 1)[0]
    if '--- /dev/null\n' not in section or section.count('@@ ') != 1:
        raise ValueError('Expected one complete added-file hunk')
    lines = section.splitlines(keepends=True)
    start = next(i for i, line in enumerate(lines) if line.startswith('@@ ')) + 1
    if any(not line.startswith('+') for line in lines[start:]):
        raise ValueError('Unexpected generated input patch content')
    return ''.join(line[1:] for line in lines[start:]).encode('utf-8')


def check_results(data, expected):
    """Reject empty, partial, disabled, duplicated, retried or failed suites."""
    if not expected or set(data['all_tests']) != set(expected) or len(data['all_tests']) != len(expected):
        raise ValueError('Test inventory differs from reviewed plan')
    if data.get('disabled_tests') or len(data['per_iteration_data']) != 1:
        raise ValueError('Disabled tests or unexpected iteration count')
    results = data['per_iteration_data'][0]
    if set(results) != set(expected):
        raise ValueError('Incomplete executed test inventory')
    for name, attempts in results.items():
        if len(attempts) != 1 or attempts[0]['status'] != 'SUCCESS':
            raise ValueError('Failed, skipped or retried test: ' + name)
    return len(results)


def offline(fork=FORK):
    baseline = patches(fork)
    roots = ('build/roadium/filters', 'tools/roadium/youtube-snapshots', 'tools/roadium/preset-snapshots')
    expected_names = ({'easylist.txt.gz', 'abp-filters-anti-cv.txt.gz'},
                      {'badblock_lite.txt.gz', 'badmojr-1Hosts-master-Lite-adblock.txt.gz'},
                      {'fanboy-social.txt.gz', 'fanboy-notifications.txt.gz'})
    for root, names in zip(roots, expected_names):
        manifest = snapshots(fork / root)
        if {row['file'] for row in manifest['inputs']} != names:
            raise ValueError('Snapshot family differs from reviewed scope: ' + root)
    fixture = read_json(fork / 'docs/shields/evidence/card08/fixture-manifest.json')
    if set(fixture['files']) != {'tools/roadium/fixtures/shields-site.html',
                                 'tools/roadium/fixtures/shields-site-filters.txt'}:
        raise ValueError('Missing reviewed site fixture pair')
    for name, row in fixture['files'].items():
        data = inside(fork, name).read_bytes()
        if digest(data) != row['sha256'] or len(data) != row['bytes']:
            raise ValueError('Fixture mismatch: ' + name)
    from preset_inventory import generate
    from youtube_inventory import collect, generate_header
    category = generate(fork / roots[2])
    youtube = generate_header(collect(fork)).encode('utf-8')
    for patch_name, source_name, expected in (
            ('0007-roadium-youtube-compatibility.patch', 'shields_youtube_rules.inc', youtube),
            ('0008-roadium-protection-presets.patch', 'shields_category_inputs.inc', category)):
        patch = (fork / 'build/roadium/patches' / patch_name).read_text(encoding='utf-8')
        if added_file(patch, 'components/adblock/test/' + source_name) != expected:
            raise ValueError('Generated converter input differs from overlay: ' + source_name)
    return dict(baseline=baseline, baseline_sha256=digest((fork / 'build/roadium/baseline.json').read_bytes()),
                snapshot_families=len(roots), fixtures=len(fixture['files']),
                category_include_sha256=digest(category), youtube_include_sha256=digest(youtube))


if __name__ == '__main__':
    print(json.dumps(offline(), indent=2))
