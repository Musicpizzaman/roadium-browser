#!/usr/bin/env python3
"""Exercise package gates using the pinned Chromium GRIT resource writer.

Run with CHROMIUM_SOURCE pointing to the pinned checkout.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(os.environ['CHROMIUM_SOURCE']) / 'tools/grit'))
from grit.format import data_pack
from filter_artifacts import RESOURCE_NAMES, read_pak, verify_filter_package


class FilterPackageTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.output = self.root / 'output'
        inputs = self.source / 'components/adblock/core/resources/roadium'
        inputs.mkdir(parents=True)
        self.generated = self.output / 'gen/components/adblock/core/resources'
        (self.generated / 'grit').mkdir(parents=True)
        notices = b'Fixture copyright and license\n'
        (inputs / 'NOTICES.txt').write_bytes(notices)
        manifest = {'revision': 'fixture', 'notices_sha256': self.digest(notices),
                    'inputs': []}
        for name, content in [('easylist.fb', b'EasyList fixture'),
                              ('anticv.fb', b'AntiCV fixture')]:
            (self.generated / name).write_bytes(content)
            manifest['inputs'].append({'flatbuffer_bytes': len(content),
                                      'flatbuffer_sha256': self.digest(content)})
        encoded = (json.dumps(manifest) + '\n').encode()
        (self.generated / 'roadium-bundled-manifest.json').write_bytes(encoded)
        self.payloads = dict(enumerate([b'EasyList fixture', b'AntiCV fixture',
                                       encoded, notices], 10020))
        header = ''.join(f'#define {name} (::ui::AllowlistedResource<{10020 + i}>(), {10020 + i})\n'
                         for i, name in enumerate(RESOURCE_NAMES))
        (self.generated / 'grit/adblock_resources.h').write_text(header)
        self.package = self.root / 'test.apk'

    @staticmethod
    def digest(value):
        return hashlib.sha256(value).hexdigest()

    def package_with(self, payloads, path='assets/resources.pak'):
        with zipfile.ZipFile(self.package, 'w') as archive:
            archive.writestr(path, data_pack.WriteDataPackToString(payloads, 0))

    def verify(self):
        return verify_filter_package(self.package, self.source, self.output)

    def test_apk_and_bundle_module_resources(self):
        for path in ['assets/resources.pak', 'base/assets/resources.pak',
                     'assets/resources.pak+40064988+']:
            with self.subTest(path=path):
                self.package_with(self.payloads, path)
                self.assertEqual('fixture', self.verify()['revision'])

    def test_compressed_resources_and_real_grit_aliases(self):
        payloads = {key: gzip.compress(value, mtime=0)
                    for key, value in self.payloads.items()}
        payloads[10100] = payloads[10020]  # GRIT emits an alias for duplicates.
        packed = data_pack.WriteDataPackToString(payloads, 0)
        self.assertEqual(data_pack.ReadDataPackFromString(packed).resources,
                         read_pak(packed))
        self.package_with(payloads)
        self.verify()

    def test_plain_resource_definitions(self):
        path = self.generated / 'grit/adblock_resources.h'
        path.write_text(''.join(f'#define {name} {10020 + i}\n'
                                for i, name in enumerate(RESOURCE_NAMES)))
        self.package_with(self.payloads)
        self.verify()

    def test_each_missing_resource_fails(self):
        for missing in self.payloads:
            with self.subTest(missing=missing):
                self.package_with({key: value for key, value in self.payloads.items()
                                   if key != missing})
                with self.assertRaisesRegex(ValueError, 'Missing packaged'):
                    self.verify()

    def test_changed_and_oversized_compressed_resources_fail(self):
        for bad in [b'changed', gzip.compress(b'x' * 100000, mtime=0)]:
            self.package_with(dict(self.payloads, **{}) | {10020: bad})
            with self.assertRaisesRegex(ValueError, 'Wrong packaged'):
                self.verify()

    def test_generated_manifest_hash_mismatch_fails(self):
        path = self.generated / 'roadium-bundled-manifest.json'
        manifest = json.loads(path.read_text())
        manifest['inputs'][0]['flatbuffer_sha256'] = '0' * 64
        encoded = json.dumps(manifest).encode()
        path.write_bytes(encoded)
        self.package_with(self.payloads | {10022: encoded})
        with self.assertRaisesRegex(ValueError, 'manifest checksum'):
            self.verify()

    def test_exception_resource_definition_fails(self):
        path = self.generated / 'grit/adblock_resources.h'
        path.write_text(path.read_text() +
                        '#define IDR_ADBLOCK_FLATBUFFER_EXCEPTIONRULES 10101\n')
        self.package_with(self.payloads)
        with self.assertRaisesRegex(ValueError, 'Acceptable Ads'):
            self.verify()

    def test_corrupt_grit_offsets_and_aliases_fail(self):
        payloads = self.payloads | {10100: self.payloads[10020]}
        original = data_pack.WriteDataPackToString(payloads, 0)
        count, aliases = struct.unpack_from('<HH', original, 8)
        self.assertGreater(aliases, 0)
        for offset, fmt, value in [(14, '<I', 0),
                                   (12 + (count + 1) * 6 + 2, '<H', count)]:
            corrupted = bytearray(original)
            struct.pack_into(fmt, corrupted, offset, value)
            with self.assertRaises(ValueError):
                read_pak(corrupted)
        for length in [0, 8, 11, 13]:
            with self.assertRaises(ValueError):
                read_pak(original[:length])


if __name__ == '__main__':
    unittest.main()
