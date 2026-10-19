from runtime import *
guard()
assert not (W/'runtime-state.json').exists(), 'Do not overwrite preflight record'
assert adb('shell','stat','-c','%u:%g',ROOT).strip()==b'1110204:1110204'
for path in ['/data/local/chrome-command-line','/data/local/tmp/chrome-command-line']:
 result=subprocess.run([ADB,'shell','test','-e',path],capture_output=True,timeout=15)
 assert result.returncode==1, 'Existing developer flags require preservation'
state=dict(user=11,created_user_name='ShieldsCard05',read_only_avd_session=True,
 original_foreground_user=10,profile_uid='1110204:1110204',
 context=adb('shell','stat','-c','%C',ROOT).decode().strip(),
 wifi=adb('shell','settings','get','global','wifi_on').decode().strip(),
 mobile_data=adb('shell','settings','get','global','mobile_data').decode().strip(),
 original_forwards=adb('forward','--list').decode(),original_reverses=adb('reverse','--list').decode(),
 flags_existed=False,selinux='Enforcing')
(W/'runtime-state.json').write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
spki=json.loads((W/'tls/public.json').read_text())['spki_sha256_base64']
flags=('_ --host-resolver-rules="MAP uazo.github.io 127.0.0.1, MAP raw.githubusercontent.com 127.0.0.1, '
       'MAP custom.card05.invalid 127.0.0.1, MAP pagead2.googlesyndication.com 127.0.0.1" '
       '--ignore-certificate-errors-spki-list='+spki+' --disable-quic --no-first-run --disable-fre\n')
local=W/'developer-command-line.txt';local.write_text(flags,encoding='utf-8',newline='\n')
remote='/data/local/chrome-command-line'
adb('push',str(local),remote)
adb('shell','chown','0:0',remote);adb('shell','chmod','644',remote)
adb('shell','chcon',state['context'],remote)
assert adb('shell','stat','-c','%u:%g:%a',remote).strip()==b'0:0:644'
for remote_port,host_port in [('443','8844'),('8766','8766')]:
 adb('reverse','tcp:'+remote_port,'tcp:'+host_port)
adb('forward','tcp:9223','localabstract:chrome_devtools_remote')
print('Prepared protected own-user TLS flags and own fixture ports with SELinux enforcing')
