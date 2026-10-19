#!/usr/bin/env python3
"""Generate or verify the frozen Card 07 native converter test inputs."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path


def generate(snapshots):
    manifest = json.loads((snapshots / 'manifest.json').read_text(encoding='utf-8'))
    if manifest['format'] != 1 or len(manifest['inputs']) != 2:
        raise ValueError('Expected the two reviewed category snapshots')
    parts = ['// Generated test-only inputs; immutable source/hash/license records accompany Card07 evidence.\n']
    for index, row in enumerate(manifest['inputs']):
        name = row['file']
        if Path(name).name != name or not name.endswith('.txt.gz'):
            raise ValueError('Snapshot must be a local gzip filename')
        compressed = (snapshots / name).read_bytes()
        if hashlib.sha256(compressed).hexdigest() != row['gzip_sha256']:
            raise ValueError(f'Compressed snapshot hash mismatch: {name}')
        with gzip.open(snapshots / name, 'rb') as stream:
            data = stream.read(5 * 1024 * 1024 + 1)
        if len(data) > 5 * 1024 * 1024 or len(data) != row['bytes']:
            raise ValueError(f'Snapshot size mismatch: {name}')
        if hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError(f'Snapshot text hash mismatch: {name}')
        parts.append(f'constexpr const char* kCategoryLines{index}[] = {{\n')
        parts.extend('    ' + json.dumps(line, ensure_ascii=False) + ',\n'
                     for line in data.decode('utf-8-sig').splitlines())
        parts.append('};\n')
    parts.append('struct CategoryInput { const char* url; const char* sha256; base::span<const char* const> lines; };\nconstexpr CategoryInput kCategoryInputs[] = {\n')
    for index, row in enumerate(manifest['inputs']):
        parts.append('    {' + json.dumps(row['canonical_url']) + ', '
                     + json.dumps(row['sha256']) + f', kCategoryLines{index}' + '},\n')
    parts.append('};\n')
    return ''.join(parts).encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshots', type=Path, default=Path(__file__).with_name('preset-snapshots'))
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--output', type=Path)
    action.add_argument('--check-include', type=Path)
    args = parser.parse_args()
    expected = generate(args.snapshots)
    if args.check_include:
        if args.check_include.read_bytes() != expected:
            parser.error('Native test include differs from verified snapshot data')
        print('Verified byte-exact native category inputs')
    else:
        args.output.write_bytes(expected)


if __name__ == '__main__':
    main()
