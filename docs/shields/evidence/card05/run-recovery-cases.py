from runtime import *
from importlib.machinery import SourceFileLoader
import sys
restore=SourceFileLoader('restore_runtime',str(W/'restore-runtime.py')).load_module().restore
case=sys.argv[1]
assert case in ['orphan','schema','remove','offline','missing','storage-error','invalid','activation','cycles','repair']
def run(name,*args):subprocess.run([sys.executable,str(W/name),*args],check=True)
def wait(predicate,seconds=35):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if predicate():return
  time.sleep(.3)
 raise RuntimeError('Case did not finish: '+case)
def write(data,path):
 assert path.startswith(ROOT+'/app_chrome/Default/adblock_subscriptions/')
 local=W/'fault-data-private.dat';local.write_bytes(data)
 tmp='/data/local/tmp/roadium-card05-fault.dat'
 adb('push',str(local),tmp)
 adb('shell','cat '+tmp+' > '+path)
 adb('shell','rm','-f',tmp)
 state=json.loads((W/'runtime-state.json').read_text())
 adb('shell','chown',state['profile_uid'],path)
 adb('shell','chcon',state['context'],path)
def connectivity(enabled):
 for service in ['wifi','data']:adb('shell','svc',service,'enable' if enabled else 'disable')
 time.sleep(2)
restore();mode('both-fail','203001020009',case)
directory=storage_dir()
prefix='roadium-'+hashlib.sha256(URLS[1].encode()).hexdigest()
current=directory+'/'+prefix+'.current.json'

if case in ['storage-error','invalid']:
 mode('primary','203001020003',case+'-prepare');launch()
 run('toggle-setting.py','advanced','true')
 wait(lambda:prefs()['adblock']['subscription_metadata'][URLS[1]].get('version')=='203001020003' and
      prefs()['adblock']['subscription_metadata'][URLS[1]]['roadium_diagnostics'].get('active_privileged') is True)
 before=prefs()['adblock']['subscription_metadata'][URLS[1]]
 fault=None
 if case=='storage-error':
  fault=current+'.pending'
  adb('shell','mkdir',fault)
  # Nonempty owned directory makes the pending-record write fail and prevents
  # normal DeleteFile cleanup from silently removing the injected fault.
  write(b'own injected metadata write error',fault+'/fault-sentinel')
 mode('invalid' if case=='invalid' else 'primary','203001020004',case)
 try:
  run('toggle-setting.py','advanced','false')
  wait(lambda:prefs()['adblock']['subscription_metadata'][URLS[1]]['roadium_diagnostics'].get('stage')==5)
  after=prefs()['adblock']['subscription_metadata'][URLS[1]]
  assert after['download_count']==before['download_count']
  assert after['error_count']==before['error_count']+1
  assert after['version']=='203001020003'
  run('capture-scenario.py',case+'-retention')
  (E/(case+'-counters.json')).write_text(json.dumps(dict(before=before,after=after),indent=2)+'\n',encoding='utf-8')
 finally:
  stop()
  if fault:
   adb('shell','rm','-f',fault+'/fault-sentinel')
   adb('shell','rmdir',fault)
 mode('both-fail','203001020009',case+'-restart');launch()
 run('capture-scenario.py',case+'-restart')
elif case=='orphan':
 record=json.loads(adb('exec-out','cat',current))
 orphan=directory+'/'+prefix+'-'+'F'*32+'.fb'
 assert subprocess.run([ADB,'shell','test','-e',orphan],capture_output=True).returncode==1
 write(adb('exec-out','cat',directory+'/'+record['file']),orphan)
 write(json.dumps(record).encode(),current+'.pending')
 sentinel=directory+'/keep-card05-unowned.txt';write(b'preserve unrelated fixture',sentinel)
 capture('orphan-before-restart');launch();run('capture-scenario.py','orphan-recovery')
 for path in [orphan,current+'.pending']:
  assert subprocess.run([ADB,'shell','test','-e',path],capture_output=True).returncode==1
 assert adb('exec-out','cat',sentinel)==b'preserve unrelated fixture'
 (E/'orphan-cleanup.json').write_text(json.dumps(dict(orphan_ignored_and_pruned=True,
  pending_ignored_and_pruned=True,unowned_sentinel_preserved=True),indent=2)+'\n',encoding='utf-8')
elif case=='schema':
 record=json.loads(adb('exec-out','cat',current))
 path=directory+'/'+record['file']
 data=adb('exec-out','cat',path)
 schema=record['schema'].encode();assert data.count(schema)>=1
 incompatible=data.replace(schema,b'0'*len(schema))
 record['sha256']=hashlib.sha256(incompatible).hexdigest()
 write(incompatible,path);write(json.dumps(record).encode(),current)
 capture('schema-before-restart');launch();run('capture-scenario.py','schema-recovery')
elif case=='remove':
 data=prefs();data['filtering']['configurations']['adblock']['subscriptions'].remove(URLS[1])
 write_prefs(data);launch();run('capture-scenario.py','explicit-removal-recovery')
 wait(lambda:not adb('shell','find',directory,'-maxdepth','1','-name',prefix+'*').strip())
 (E/'removed-cache-cleanup.json').write_text('{"both_generations_and_records_removed":true}\n',encoding='utf-8')
elif case in ['offline','missing']:
 if case=='offline':
  for path in adb('shell','find',directory,'-maxdepth','1','-type','f','-name','roadium-*.fb').decode().splitlines():
   write(b'corrupt both downloaded copies',path)
 else:
  for path in adb('shell','find',directory,'-maxdepth','1','-type','f','-name','roadium-*.json').decode().splitlines():
   assert path.startswith(directory+'/roadium-')
   adb('shell','rm','-f',path)
 capture(case+'-before-restart') if case=='offline' else None
 connectivity(False)
 try:
  launch();run('capture-scenario.py',case+'-bundled-recovery')
 finally:
  stop();connectivity(True)
elif case=='activation':
 run('advance-version.py','203001020005','activation-before-stop')
 capture('activation-before-stop');stop();mode('both-fail','203001020009','activation-restart')
 launch();run('capture-scenario.py','activation-restart')
elif case=='cycles':
 for version in ['203001020006','203001020007','203001020008']:
  run('advance-version.py',version,'repeat-'+version)
  stop();launch();wait(lambda:all(prefs()['adblock']['subscription_metadata'][url]['version']==version for url in URLS[:2]))
  capture('repeat-'+version)
  data=json.loads((E/('repeat-'+version+'-storage.json')).read_text())
  for url in URLS:
   p='roadium-'+hashlib.sha256(url.encode()).hexdigest()+'-'
   assert len([f for f in data['files'] if f['file'].startswith(p)])<=2
 run('capture-scenario.py','repeated-update-recovery')
elif case=='repair':
 for url in URLS[:2]:
  p='roadium-'+hashlib.sha256(url.encode()).hexdigest()
  record=json.loads(adb('exec-out','cat',directory+'/'+p+'.current.json'))
  write(b'invalid current before repair',directory+'/'+record['file'])
 launch()
 wait(lambda:all(prefs()['adblock']['subscription_metadata'][url]['roadium_diagnostics'].get('recovery')=='previous' for url in URLS[:2]))
 capture('repair-before-update')
 run('advance-version.py','203001020006','repair-after-recovery')
 stop();mode('both-fail','203001020009','repair-restart');launch()
 run('capture-scenario.py','repair-after-recovery')
