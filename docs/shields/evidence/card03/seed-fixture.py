"""Developer-only cached-list fixture in the backed-up, task-owned user13 profile."""
from pathlib import Path
import base64, hashlib, json, subprocess, sys, time

WORK = Path(__file__).parent
ADB = r'E:\Android Auto Projects\AndroidSdk\platform-tools\adb.exe'
PKG = 'io.github.musicpizzaman.roadium'
ROOT = '/data/user/13/' + PKG + '/app_chrome/Default'
PREF = ROOT + '/Preferences'
NAME = 'C03C03C03C03C03C03C03C03C03C03C03.fb'
mode = sys.argv[1]
assert mode in ['trusted', 'untrusted', 'manual']
owner = json.loads((WORK / 'fresh-profile-owner.json').read_text(encoding='utf-8'))
assert owner['user'] == 13 and owner['reset_after_validated_backups']
def adb(*args):
    return subprocess.check_output([ADB, *args], timeout=45)
assert adb('shell', 'am', 'get-current-user').strip() == b'13'
adb('shell', 'am', 'force-stop', '--user', '13', PKG)
data = json.loads(adb('exec-out', 'cat', PREF))
original = WORK / 'fresh-preferences-private.json'
if not original.exists():
    original.write_text(json.dumps(data), encoding='utf-8')
ab = data['adblock']
assert ab['last_used_schema_version'] == 'Apu+MU09OCFx11xibV1gU0afrAVCmbvSp8K2NKDV2Yc='
assert set(ab.get('subscription_signatures', {})) <= {NAME}, 'Unexpected downloaded lists'
ab['install_first_run_subscriptions'] = False
ab['privilegedfilters_enabled'] = True
config = data['filtering']['configurations']['adblock']
config.update(enabled=True, domains=[], filters=[], temp_filters=[], subscriptions=[])
adb('shell', 'mkdir', '-p', ROOT + '/adblock_subscriptions')
files = adb('shell', 'ls', '-1', ROOT + '/adblock_subscriptions').decode().splitlines()
assert set(files) <= {NAME}, files
adb('shell', 'rm', '-f', ROOT + '/adblock_subscriptions/' + NAME)
ab['subscription_signatures'] = {}
ab['subscription_metadata'] = {}
if mode == 'manual':
    config['filters'] = ['127.0.0.1#$#override-property-read roadiumProbe undefined',
                         '127.0.0.1##.card03-ad', '||pagead2.googlesyndication.com^']
else:
    url = ('https://uazo.github.io/cromite/filters/abp-filters-anti-cv.txt' if mode == 'trusted'
           else 'https://raw.githubusercontent.com/uazo/cromite/pages/filters/abp-filters-anti-cv.txt')
    config['subscriptions'] = [url]
    fb = WORK / (mode + '-fixture.fb')
    ab['subscription_signatures'][NAME] = base64.b64encode(hashlib.sha256(fb.read_bytes()).digest()).decode()
    now = str(int((time.time() + 11644473600) * 1000000))
    ab['subscription_metadata'][url] = dict(version='203001010003',
        expiration_time=str(int(now) + 365*86400*1000000), last_installation_time=now,
        download_count=1, error_count=0, roadium_diagnostics=dict(stage=4,
        active_privileged=True, parsed_privileged=True, source=url, last_success_source=url,
        last_success=now))
    adb('push', str(fb), '/data/local/tmp/roadium-card03-fixture.fb')
    adb('shell', 'cp', '/data/local/tmp/roadium-card03-fixture.fb', ROOT + '/adblock_subscriptions/' + NAME)
    uid = adb('shell', 'stat', '-c', '%u:%g', PREF).decode().strip()
    adb('shell', 'chown', uid, ROOT + '/adblock_subscriptions', ROOT + '/adblock_subscriptions/' + NAME)
    adb('shell', 'chmod', '700', ROOT + '/adblock_subscriptions')
    adb('shell', 'chmod', '600', ROOT + '/adblock_subscriptions/' + NAME)
    # restorecon on this emulator assigns the owner user0 category; inherit
    # the existing user13 profile label instead, without relaxing SELinux.
    context = adb('shell', 'stat', '-c', '%C', PREF).decode().strip()
    assert context.startswith('u:object_r:app_data_file:s0:')
    adb('shell', 'chcon', '-R', context, ROOT + '/adblock_subscriptions')
payload = WORK / 'fixture-preferences-private.json'
payload.write_text(json.dumps(data), encoding='utf-8', newline='\n')
adb('push', str(payload), '/data/local/tmp/roadium-card03-preferences.json')
adb('shell', 'cat /data/local/tmp/roadium-card03-preferences.json > ' + PREF)
adb('shell', 'rm', '-f', '/data/local/tmp/roadium-card03-preferences.json', '/data/local/tmp/roadium-card03-fixture.fb')
print('Seeded only task-owned user13:', mode)
