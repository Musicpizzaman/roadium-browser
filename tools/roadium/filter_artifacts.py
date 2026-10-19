"""Check actual packaged native filter resources against frozen build outputs."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import re
import struct
import zipfile

RESOURCE_NAMES = ('IDR_ADBLOCK_FLATBUFFER_EASYLIST',
                  'IDR_ADBLOCK_FLATBUFFER_ANTICV',
                  'IDR_ADBLOCK_BUNDLED_MANIFEST',
                  'IDR_ADBLOCK_FILTER_NOTICES')


def read_pak(data):
    if len(data) < 9:
        raise ValueError('Truncated Chromium resource pack')
    version, = struct.unpack_from('<I', data)
    if version == 4:
        count, _ = struct.unpack_from('<IB', data, 4)
        aliases, header = 0, 9
    elif version == 5:
        if len(data) < 12: raise ValueError('Truncated v5 pack header')
        _, count, aliases = struct.unpack_from('<BxxxHH', data, 4)
        header = 12
    else:
        raise ValueError(f'Unsupported resource pack version {version}')
    table_end = header + (count + 1) * 6 + aliases * 4
    if count > 65535 or table_end > len(data):
        raise ValueError('Resource pack table exceeds its data')
    entries = [struct.unpack_from('<HI', data, header + i * 6) for i in range(count + 1)]
    resources = {}
    for i, (identifier, offset) in enumerate(entries[:-1]):
        end = entries[i + 1][1]
        if identifier in resources or not table_end <= offset <= end <= len(data):
            raise ValueError('Invalid resource pack offsets or duplicate identity')
        resources[identifier] = data[offset:end]
    for i in range(aliases):
        identifier, index = struct.unpack_from('<HH', data, header + (count + 1) * 6 + i * 4)
        if index >= count or identifier in resources:
            raise ValueError('Invalid resource alias')
        resources[identifier] = resources[entries[index][0]]
    return resources


def verify_filter_package(package, source, output):
    source = Path(source)
    generated = Path(output) / 'gen/components/adblock/core/resources'
    manifest_bytes = (generated / 'roadium-bundled-manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    paths = source / 'components/adblock/core/resources/roadium'
    notices = (paths / 'NOTICES.txt').read_bytes()
    expected = dict(zip(RESOURCE_NAMES, [(generated/'easylist.fb').read_bytes(),
        (generated/'anticv.fb').read_bytes(), manifest_bytes, notices]))
    defines = {}
    for name, expression in re.findall(
            r'^#define\s+(IDR_ADBLOCK_[A-Z0-9_]+)[ \t]+([^\r\n]+)',
            (generated/'grit/adblock_resources.h').read_text(), re.MULTILINE):
        plain = re.fullmatch(r'\s*(\d+)\s*', expression)
        wrapped = re.fullmatch(
            r'\(::ui::AllowlistedResource<(\d+)>\(\),\s*(\d+)\)\s*', expression)
        if plain:
            defines[name] = int(plain[1])
        elif wrapped and wrapped[1] == wrapped[2]:
            defines[name] = int(wrapped[1])
        else:
            raise ValueError(f'Unsupported generated filter resource definition: {name}')
    if 'IDR_ADBLOCK_FLATBUFFER_EXCEPTIONRULES' in defines:
        raise ValueError('Acceptable Ads resource must remain unbundled')
    if not all(name in defines for name in expected):
        raise ValueError('Required generated filter resource identity is missing')
    identifiers = {defines[name]: name for name in expected}
    found = {name: [] for name in expected}
    with zipfile.ZipFile(package) as archive:
        for info in archive.infolist():
            # Android may append the mmap-alignment marker to asset names.
            if not re.search(r'\.pak(?:\+\d+\+)?$', info.filename): continue
            if info.file_size > 128 * 1024 * 1024:
                raise ValueError('Packaged resource pack exceeds verification limit')
            resources = read_pak(archive.read(info))
            for identifier, name in identifiers.items():
                if identifier not in resources: continue
                actual = resources[identifier]
                if actual.startswith(b'\x1f\x8b'):
                    with gzip.GzipFile(fileobj=io.BytesIO(actual)) as packed:
                        actual = packed.read(len(expected[name]) + 1)
                if actual != expected[name]:
                    raise ValueError(f'Wrong packaged filter resource: {name} in {info.filename}')
                found[name].append(info.filename)
    missing = [name for name, packages in found.items() if not packages]
    if missing: raise ValueError('Missing packaged filter resources: ' + ', '.join(missing))
    for item, name in zip(manifest['inputs'], RESOURCE_NAMES[:2]):
        if (len(expected[name]) != item['flatbuffer_bytes'] or
                hashlib.sha256(expected[name]).hexdigest() != item['flatbuffer_sha256']):
            raise ValueError(f'Generated filter manifest checksum mismatch: {name}')
    if hashlib.sha256(notices).hexdigest() != manifest['notices_sha256']:
        raise ValueError('Generated filter notices checksum mismatch')
    return {'revision': manifest['revision'], 'resources': found,
            'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(),
            'notices_sha256': manifest['notices_sha256']}
