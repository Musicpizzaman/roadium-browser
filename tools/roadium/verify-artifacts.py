#!/usr/bin/env python3
"""Validate completed Roadium artifacts inside a prepared build container."""

from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--arch', choices=('arm64', 'x64'), required=True)
parser.add_argument('--workspace', type=Path, default=os.environ.get('WORKSPACE'))
args = parser.parse_args()
if args.workspace is None:
    parser.error('--workspace or WORKSPACE is required')
workspace = args.workspace.resolve()
src = workspace / 'chromium/src'
arch = args.arch
state = src / f'out/{arch}/roadium-build-status'
attempt = Path((state / 'current-run').read_text().strip())
assert (attempt / 'exit').read_text().strip() == '0'
metadata = json.loads((workspace / 'roadium/build/roadium/baseline.json').read_text())
head_tree = subprocess.check_output(['git', 'rev-parse', 'HEAD^{tree}'], cwd=src, text=True).strip()
assert head_tree == metadata['baseline_source_tree'], (head_tree, metadata['baseline_source_tree'])
from version_code import expected_version_code
expected_code = str(expected_version_code(src, metadata, arch))
actual_gn_code = subprocess.check_output(
    [str(src / 'buildtools/linux64/gn'), 'args', f'out/{arch}',
     '--list=android_override_version_code', '--short'], cwd=src, text=True).strip()
assert actual_gn_code == f'android_override_version_code = "{expected_code}"', actual_gn_code
diff = subprocess.check_output(['git', 'diff', '--binary', 'HEAD'], cwd=src)
assert hashlib.sha256(diff).hexdigest() == metadata['patches'][0]['sha256']
android = '{http://schemas.android.com/apk/res/android}'
bundletool = src / 'third_party/android_build_tools/bundletool/cipd/bundletool.jar'
java = src / 'third_party/jdk/current/bin/java'
sdk_tools = src / 'third_party/android_sdk/public/build-tools/37.0.0'
aapt2 = sdk_tools / 'aapt2'
apksigner = sdk_tools / 'apksigner'
expected_abi = {'arm64': 'arm64-v8a', 'x64': 'x86_64'}[arch]
java_env = dict(os.environ, JAVA_HOME=str(java.parent.parent))
java_env['PATH'] = str(java.parent) + os.pathsep + java_env.get('PATH', '')
bundle = src / f'out/{arch}/apks/ChromePublic.aab'
validation = subprocess.run([str(java), '-jar', str(bundletool), 'validate',
                            '--bundle=' + str(bundle)], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, check=True)
(workspace / f'roadium-{arch}-bundle-validation.txt').write_text(validation.stdout)
modules = {}
browser_entry = False
for name in ('base', 'on_demand', 'stack_unwinder', 'xr', 'chrome'):
    xml = subprocess.check_output([str(java), '-jar', str(bundletool), 'dump',
          'manifest', '--bundle=' + str(bundle), '--module=' + name],
          stderr=subprocess.DEVNULL)
    root = ET.fromstring(xml)
    sdk = root.find('uses-sdk')
    assert sdk is not None
    minimum = sdk.get(android + 'minSdkVersion')
    target = sdk.get(android + 'targetSdkVersion')
    assert minimum == '31' and target == '36', (name, minimum, target)
    assert root.get('package') == 'io.github.musicpizzaman.roadium'
    assert root.get(android + 'versionCode') == expected_code, name
    assert root.get(android + 'versionName') == metadata['chromium_version'], name
    modules[name] = {'min_sdk': int(minimum), 'target_sdk': int(target)}
    app = root.find('application')
    if app is not None:
        assert all(e.get(android + 'supportsPictureInPicture') != 'true'
                   for e in app.findall('activity'))
        assert all(e.get(android + 'value') != 'true' for e in app.iter('meta-data')
                   if e.get(android + 'name') == 'distractionOptimized')
        for entry in list(app.findall('activity')) + list(app.findall('activity-alias')):
            if entry.get(android + 'exported') != 'true':
                continue
            for intent in entry.findall('intent-filter'):
                actions = {e.get(android + 'name') for e in intent.findall('action')}
                categories = {e.get(android + 'name') for e in intent.findall('category')}
                if ('android.intent.action.MAIN' in actions
                        and 'android.intent.category.APP_BROWSER' in categories):
                    browser_entry = True
    if name == 'base':
        feature = next(e for e in root.findall('uses-feature')
                       if e.get(android + 'name') == 'android.hardware.type.automotive')
        assert feature.get(android + 'required') == 'true'
        app = root.find('application')
        assert app.get(android + 'label') == 'Roadium Browser'
        assert all(e.get(android + 'supportsPictureInPicture') != 'true'
                   for e in app.findall('activity'))
        assert all(e.get(android + 'value') != 'true' for e in app.iter('meta-data')
                   if e.get(android + 'name') == 'distractionOptimized')
        (workspace / f'roadium-{arch}-manifest.xml').write_bytes(xml)
assert browser_entry, "Missing exported MAIN + APP_BROWSER entry"
artifacts = []
for name in ('ChromePublic.apk', 'ChromePublic.aab'):
    path = src / f'out/{arch}/apks/{name}'
    item = {'file': name}
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        library_paths = [entry for entry in z.namelist() if entry.endswith('.so')]
        assert library_paths, (name, 'no native libraries')
        packaged_abis = set()
        for entry in library_paths:
            match = re.fullmatch(r'(?:[^/]+/)?lib/([^/]+)/[^/]+\.so', entry)
            assert match, (name, 'unexpected native library path', entry)
            packaged_abis.add(match.group(1))
        assert packaged_abis == {expected_abi}, (name, packaged_abis, expected_abi)
        item.update(native_abis=sorted(packaged_abis), native_library_count=len(library_paths))
        if name.endswith('.aab'):
            signing_entries = [entry for entry in z.namelist()
                               if re.fullmatch(r'META-INF/[^/]+\.(?:SF|RSA|DSA|EC)',
                                               entry, re.IGNORECASE)]
            item['jar_signing_entries'] = signing_entries
            item['jar_signature_status'] = ('entries present; signature not verified'
                                            if signing_entries else 'unsigned')
    if name.endswith('.apk'):
        badging = subprocess.check_output([str(aapt2), 'dump', 'badging', str(path)], text=True)
        (workspace / f'roadium-{arch}-badging.txt').write_text(badging)
        package_line = next(line for line in badging.splitlines() if line.startswith('package: '))
        fields = dict(re.findall(r"(\w+)='([^']*)'", package_line))
        assert fields['name'] == 'io.github.musicpizzaman.roadium', fields
        assert fields['versionName'] == metadata['chromium_version'], fields
        assert fields['versionCode'] == expected_code, fields
        assert "application-label:'Roadium Browser'" in badging.splitlines()
        assert "minSdkVersion:'31'" in badging.splitlines()
        assert "targetSdkVersion:'36'" in badging.splitlines()
        abi_line = next(line for line in badging.splitlines() if line.startswith('native-code:'))
        assert re.findall(r"'([^']*)'", abi_line) == [expected_abi], abi_line
        signature = subprocess.check_output([str(apksigner), 'verify', '--verbose',
                                            '--print-certs', str(path)], text=True, env=java_env)
        (workspace / f'roadium-{arch}-signing.txt').write_text(signature)
        certificates = re.findall(r'certificate SHA-256 digest: ([0-9a-fA-F]{64})$',
                                  signature, re.MULTILINE)
        assert len(certificates) == 1 and 'Number of signers: 1' in signature.splitlines()
        assert 'Verified using v2 scheme (APK Signature Scheme v2): true' in signature.splitlines()
        item.update(apk_signature_verification='passed', apk_signature_v2=True,
                    certificate_sha256=certificates[0].lower(), min_sdk=31, target_sdk=36)
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(1024 * 1024), b''):
            h.update(data)
    item.update(bytes=path.stat().st_size, sha256=h.hexdigest(), zip_crc='passed')
    artifacts.append(item)
result = {
    'project': 'Roadium Browser', 'architecture': arch,
    'package': 'io.github.musicpizzaman.roadium',
    'version': metadata['chromium_version'], 'version_code': int(expected_code),
    'roadium_version_code_offset': metadata.get('roadium_version_code_offset', 0),
    'baseline_source_tree': metadata['baseline_source_tree'],
    'cromite_commit': metadata['cromite_commit'],
    'source_patch_sha256': metadata['patches'][0]['sha256'],
    'compiler_exit': 0, 'build_attempt': attempt.name,
    'started_utc': (attempt / 'started-utc').read_text().strip(),
    'native_toolchain_min_sdk': 29, 'target_sdk': 36,
    'required_automotive': True, 'picture_in_picture': False,
    'signing': 'APK verified with diagnostic development certificate; AAB status recorded per artifact',
    'bundle_modules': modules, 'bundletool_validation': 'passed',
    'bundletool_exit': validation.returncode, 'packaged_abi': expected_abi,
    'artifacts': artifacts,
    'emulator_runtime_verification': 'pending',
    'physical_car_verification': 'pending'
}
(workspace / f'roadium-{arch}-build-manifest.json').write_text(
    json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
