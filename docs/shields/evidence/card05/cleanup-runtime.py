"""Remove only verified Card05 hooks, own lab user and own read-only emulator."""
from runtime import *
import socket,sys
def ps(command):
 return subprocess.check_output(['powershell.exe','-NoProfile','-Command',command],timeout=20).decode('utf-8-sig').strip()
def listener(port):
 lines=subprocess.check_output(['netstat','-ano','-p','tcp'],timeout=15).decode().splitlines()
 owners={int(row.split()[-1]) for row in lines if len(row.split())==5 and
         row.split()[1]=='127.0.0.1:'+str(port) and row.split()[3]=='LISTENING'}
 assert len(owners)==1,(port,owners)
 return next(iter(owners))
def process(pid):
 assert isinstance(pid,int) and pid>0
 raw=ps("Get-CimInstance Win32_Process -Filter 'ProcessId="+str(pid)+"' | Select-Object ProcessId,ExecutablePath,CommandLine,CreationDate | ConvertTo-Json -Compress")
 return json.loads(raw)
def prepare():
 guard()
 state=json.loads((W/'runtime-state.json').read_text())
 assert state['user']==11 and state['created_user_name']=='ShieldsCard05'
 assert state['read_only_avd_session'] and state['original_foreground_user']==10
 assert state['original_forwards'].strip()==state['original_reverses'].strip()==''
 assert adb('exec-out','cat','/data/local/chrome-command-line')==(W/'developer-command-line.txt').read_bytes()
 assert hashlib.sha256(adb('exec-out','cat','/data/local/tmp/roadium-card05-capture.jar')).hexdigest()==hashlib.sha256((W/'capture.jar').read_bytes()).hexdigest()
 processes=[]
 for port in [8844,8766]:
  info=process(listener(port))
  assert str(info['ExecutablePath']).lower()==r'c:\python313\python.exe'
  line=info['CommandLine'].lower()
  if port==8844:assert str(W/'tls-fixture-server.py').lower() in line
  else:assert 'http.server' in line and '8766' in line and str(W/'public').lower() in line
  processes.append(dict(port=port,**info))
 emulator=json.loads(ps("Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('emulator.exe','qemu-system-x86_64.exe') } | Select-Object ProcessId,ExecutablePath,CommandLine | ConvertTo-Json -Compress"))
 if isinstance(emulator,dict):emulator=[emulator]
 owned=[p for p in emulator if 'RoadiumAAOS33' in (p.get('CommandLine') or '') and
        '-read-only' in p['CommandLine'] and '-no-snapshot-save' in p['CommandLine']]
 assert owned,'No verified own read-only emulator process'
 return state,processes,owned
state,servers,emulator=prepare()
if sys.argv[1:]!=['--execute']:
 print(json.dumps(dict(check='passed',own_server_pids=[p['ProcessId'] for p in servers],
                      own_read_only_emulator_pids=[p['ProcessId'] for p in emulator])))
 raise SystemExit(0)
stop()
for path in ['/data/local/chrome-command-line','/data/local/tmp/roadium-card05-capture.jar',
 '/data/local/tmp/roadium-card05-base.tar','/data/local/tmp/roadium-card05-fault.dat',
 '/data/local/tmp/roadium-card05-preferences.json']:
 adb('shell','rm','-f',path)
for port,target in [('443','8844'),('8766','8766')]:
 mappings=adb('reverse','--list').decode()
 assert any(row.split()[-2:]==['tcp:'+port,'tcp:'+target] for row in mappings.splitlines())
 adb('reverse','--remove','tcp:'+port)
assert 'tcp:9223 localabstract:chrome_devtools_remote' in adb('forward','--list').decode()
adb('forward','--remove','tcp:9223')
for key,service in [('wifi','wifi'),('mobile_data','data')]:
 adb('shell','svc',service,'enable' if state[key]=='1' else 'disable')
assert adb('shell','getenforce').strip()==b'Enforcing'
for path in ['/data/local/chrome-command-line','/data/local/tmp/chrome-command-line',
             '/data/local/tmp/roadium-card05-capture.jar']:
 assert subprocess.run([ADB,'shell','test','-e',path],capture_output=True).returncode==1
assert not adb('reverse','--list').strip() and not adb('forward','--list').strip()
assert adb('shell','settings','get','global','wifi_on').decode().strip()==state['wifi']
assert adb('shell','settings','get','global','mobile_data').decode().strip()==state['mobile_data']
adb('shell','am','switch-user','10')
end=time.monotonic()+20
while time.monotonic()<end:
 if (adb('shell','am','get-current-user').strip()==b'10' and
     b'RUNNING_UNLOCKED' in adb('shell','am','get-started-user-state','10')):break
 time.sleep(.5)
else:raise RuntimeError('Original user did not resume')
adb('shell','am','stop-user','-w','11')
assert b'ShieldsCard05' in adb('shell','pm','list','users')
assert b'Success' in adb('shell','pm','remove-user','11')
users=adb('shell','pm','list','users').decode()
assert 'ShieldsCard05' not in users and 'UserInfo{11:' not in users
assert 'UserInfo{0:' in users and 'UserInfo{10:' in users
assert adb('shell','am','get-current-user').strip()==b'10'
for server in servers:
 # Recheck exact process birth and command immediately before terminating it.
 assert process(server['ProcessId'])=={k:v for k,v in server.items() if k!='port'}
 ps('[System.Diagnostics.Process]::GetProcessById('+str(server['ProcessId'])+').Kill()')
for port in [8844,8766]:
 with socket.socket() as sock:
  sock.settimeout(1)
  assert sock.connect_ex(('127.0.0.1',port))!=0
adb('emu','kill')
end=time.monotonic()+15
while time.monotonic()<end:
 if 'emulator-5554' not in subprocess.check_output([ADB,'devices']).decode():break
 time.sleep(.5)
else:raise RuntimeError('Own emulator did not exit')
result=dict(status='passed',own_user_removed=True,original_users_preserved=True,
 foreground_restored_before_shutdown=10,flags_removed=True,helper_removed=True,
 port_mappings_removed=True,host_fixture_servers_stopped=True,
 network_settings_restored=True,selinux='Enforcing',own_read_only_emulator_closed=True,
 avd_snapshot_saved=False,vehicle_properties_modified=False,
 saved_avd_disk_verification='Read-only/no-snapshot-save launch verified; byte-for-byte pre-launch disk hash was not captured',
 production_signing_material_accessed=False,private_backups_kept_outside_repository=True)
(E/'cleanup-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Verified Card05 cleanup; original users preserved, own emulator closed without snapshot save')
