"""Remove only the resumed Card06 lab user, hooks and read-only emulator."""
from runtime import *
import sys
assert sys.argv[1:]==['--execute']
guard()
users=adb('shell','pm','list','users').decode()
assert 'UserInfo{11:ShieldsCard06Resume:' in users
assert 'UserInfo{0:' in users and 'UserInfo{10:' in users
state=json.loads((W/'runtime-state.json').read_text())
assert state['user']==11 and state['original_foreground_user']==10 and state['read_only_avd_session']
assert not state['original_forwards'].strip() and not state['original_reverses'].strip()
assert adb('exec-out','cat','/data/local/chrome-command-line')==(W/'developer-command-line.txt').read_bytes()
assert hashlib.sha256(adb('exec-out','cat','/data/local/tmp/roadium-card06-capture.jar')).hexdigest()==hashlib.sha256((W/'capture.jar').read_bytes()).hexdigest()
stop()
for path in ['/data/local/chrome-command-line','/data/local/tmp/roadium-card06-capture.jar','/data/local/tmp/roadium-card06-preferences.json']:
    adb('shell','rm','-f',path)
for port,target in [('443','8844'),('8766','8766'),('8886','8886')]:
    assert any(row.split()[-2:]==['tcp:'+port,'tcp:'+target] for row in adb('reverse','--list').decode().splitlines())
    adb('reverse','--remove','tcp:'+port)
assert 'tcp:9223 localabstract:chrome_devtools_remote' in adb('forward','--list').decode()
adb('forward','--remove','tcp:9223')
for key,service in [('wifi','wifi'),('mobile_data','data')]:
    adb('shell','svc',service,'enable' if state[key]=='1' else 'disable')
adb('shell','am','switch-user','10')
end=time.monotonic()+20
while time.monotonic()<end:
    if adb('shell','am','get-current-user').strip()==b'10' and b'RUNNING_UNLOCKED' in adb('shell','am','get-started-user-state','10'):break
    time.sleep(.5)
else:raise RuntimeError('Original user did not unlock')
adb('shell','am','stop-user','-w','11')
assert b'Success' in adb('shell','pm','remove-user','11')
users=adb('shell','pm','list','users').decode()
assert 'ShieldsCard06' not in users and 'UserInfo{11:' not in users and 'UserInfo{0:' in users and 'UserInfo{10:' in users
assert not adb('forward','--list').strip() and not adb('reverse','--list').strip()
assert adb('shell','getenforce').strip()==b'Enforcing'
for key in ['wifi_on','mobile_data']:
    assert adb('shell','settings','get','global',key).decode().strip()==state['wifi' if key=='wifi_on' else key]
for path in ['/data/local/chrome-command-line','/data/local/tmp/chrome-command-line','/data/local/tmp/roadium-card06-capture.jar']:
    assert subprocess.run([ADB,'-s','emulator-5554','shell','test','-e',path],capture_output=True).returncode==1
(W/'device-cleanup.json').write_text(json.dumps(dict(own_user_removed=True,original_users_preserved=True,original_foreground_restored=10,network_restored=True,flags_helper_ports_removed=True,selinux='Enforcing',vehicle_properties_modified=False),indent=2)+'\n',encoding='utf-8')
adb('emu','kill')
end=time.monotonic()+20
while time.monotonic()<end:
    if 'emulator-5554' not in subprocess.check_output([ADB,'devices']).decode():break
    time.sleep(.5)
else:raise RuntimeError('Own emulator did not exit')
print('PASS: owned user/hooks removed, original users/network restored, read-only emulator closed')
