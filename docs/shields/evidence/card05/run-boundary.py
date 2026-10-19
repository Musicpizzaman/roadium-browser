"""Freeze real own-user update I/O with root-only FIFO fault fixtures, then kill."""
from runtime import *
from importlib.machinery import SourceFileLoader
import sys
restore=SourceFileLoader('restore_runtime',str(W/'restore-runtime.py')).load_module().restore
stage=sys.argv[1]
assert stage in ['download','candidate','previous','published']
label='force-stop-'+stage
restore();mode('primary','203001020003',label+'-prepare');launch()
def toggle(value):
 subprocess.run([sys.executable,str(W/'toggle-setting.py'),'advanced',value],check=True,stdout=subprocess.DEVNULL)
def wait(predicate,seconds=30):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if predicate():return
  time.sleep(.2)
 raise RuntimeError('Boundary not reached: '+stage)
toggle('true')
wait(lambda: prefs()['adblock']['subscription_metadata'][URLS[1]].get('version')=='203001020003' and
     prefs()['adblock']['subscription_metadata'][URLS[1]]['roadium_diagnostics'].get('active_privileged') is True)
directory=storage_dir()
prefix='roadium-'+hashlib.sha256(URLS[1].encode()).hexdigest()
current=directory+'/'+prefix+'.current.json'
previous=directory+'/'+prefix+'.previous.json'
def record(path):return json.loads(adb('exec-out','cat',path))
before_current=record(current);before_previous=record(previous)
before=prefs()['adblock']['subscription_metadata'][URLS[1]]
before_files=set(adb('shell','find',directory,'-maxdepth','1','-type','f','-name',prefix+'-*.fb').decode().splitlines())
fault=None
if stage!='download':
 if stage=='published':
  fake='roadium-'+hashlib.sha256(b'https://card05.invalid/interrupted-cleanup').hexdigest()
  fault=directory+'/'+fake+'.current.json'
 else:fault=directory+'/'+prefix+('.previous' if stage=='candidate' else '.current')+'.json.pending'
 assert fault.startswith(directory+'/roadium-')
 state=json.loads((W/'runtime-state.json').read_text())
 adb('shell','mkfifo',fault)
 adb('shell','chown',state['profile_uid'],fault)
 adb('shell','chmod','600',fault)
 adb('shell','chcon',state['context'],fault)
 assert b'fifo' in adb('shell','stat','-c','%F',fault).lower()
mode('slow' if stage=='download' else 'primary','203001020004',label)
if stage=='download' and (W/'slow-response.json').exists():(W/'slow-response.json').unlink()
try:
 toggle('false')
 if stage=='download':wait(lambda:(W/'slow-response.json').exists())
 elif stage=='published':wait(lambda:record(current)['file']!=before_current['file'])
 else:
  wait(lambda:len(set(adb('shell','find',directory,'-maxdepth','1','-type','f','-name',prefix+'-*.fb').decode().splitlines())-before_files)>0)
 # Waiting proves the observed pre-callback state is paused, not just a short
 # race caught between ordinary asynchronous operations.
 time.sleep(2)
 checkpoint=prefs()['adblock']['subscription_metadata'][URLS[1]]
 assert checkpoint['version']=='203001020003',checkpoint
 assert checkpoint['download_count']==before['download_count']
 observed_current=record(current);observed_previous=record(previous)
 if stage in ['download','candidate','previous']:
  assert observed_current==before_current
 if stage=='candidate':assert observed_previous==before_previous
 if stage in ['previous','published']:assert observed_previous==before_current
 if stage=='published':assert observed_current['privileged'] is False
 capture(label+'-before-kill')
 stop()
 record_evidence=dict(boundary=stage,method='Actual own-user update paused using a root-only FIFO, then am force-stop' if fault else 'Actual partial HTTP response then am force-stop',
  fifo=fault,current_before=before_current,current_at_kill=observed_current,
  previous_before=before_previous,previous_at_kill=observed_previous,
  preference_version_at_kill=checkpoint['version'],
  success_count_before=before['download_count'],success_count_at_kill=checkpoint['download_count'],
  advanced_at_kill=prefs()['adblock']['privilegedfilters_enabled'])
 (E/(label+'-boundary.json')).write_text(json.dumps(record_evidence,indent=2)+'\n',encoding='utf-8',newline='\n')
finally:
 stop()
 if fault:adb('shell','rm','-f',fault)
mode('both-fail','203001020009',label+'-restart')
launch()
subprocess.run([sys.executable,str(W/'capture-scenario.py'),label],check=True)
