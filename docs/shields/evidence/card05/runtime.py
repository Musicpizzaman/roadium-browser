"""Own read-only emulator session/user11 only; no other profile file access."""
from pathlib import Path
import subprocess,json,hashlib,time,re,xml.etree.ElementTree as ET
W=Path(__file__).parent
E=Path(r'E:\Android Auto Projects\roadium-browser\docs\shields\evidence\card05')
ADB=r'E:\Android Auto Projects\AndroidSdk\platform-tools\adb.exe'
PKG='io.github.musicpizzaman.roadium'
USER='11'
ROOT='/data/user/11/'+PKG
PREF=ROOT+'/app_chrome/Default/Preferences'
URLS=['https://uazo.github.io/cromite/filters/easylist.txt',
      'https://uazo.github.io/cromite/filters/abp-filters-anti-cv.txt',
      'https://custom.card05.invalid/list.txt']
PAGE='http://127.0.0.1:8766/card05.html'
def adb(*a,timeout=45):return subprocess.check_output([ADB,'-s','emulator-5554',*a],timeout=timeout)
def guard():
 assert adb('shell','getprop','ro.product.device').strip()==b'emulator_car64_x86_64'
 assert b'ShieldsCard05' in adb('shell','pm','list','users')
 assert adb('shell','getenforce').strip()==b'Enforcing'
def prefs():return json.loads(adb('exec-out','cat',PREF))
def write_prefs(data):
 guard();stop()
 local=W/'preferences-private.json'
 local.write_text(json.dumps(data),encoding='utf-8',newline='\n')
 adb('push',str(local),'/data/local/tmp/roadium-card05-preferences.json')
 adb('shell','cat /data/local/tmp/roadium-card05-preferences.json > '+PREF)
 adb('shell','rm','-f','/data/local/tmp/roadium-card05-preferences.json')
def stop():adb('shell','am','force-stop','--user',USER,PKG)
def launch():
 guard()
 adb('shell','am','switch-user',USER)
 adb('shell','am','start','-W','--user',USER,'-a','android.intent.action.VIEW','-d',PAGE,'-p',PKG)
def mode(name,version,label):
 (W/'tls-mode.json').write_text(json.dumps(dict(mode=name,version=version,phase=label))+'\n',encoding='utf-8')
def expire():
 data=prefs()
 for url in URLS[:2]:
  metadata=data['adblock'].setdefault('subscription_metadata',{}).setdefault(url,{})
  metadata['expiration_time']='0'
 write_prefs(data)
def storage_dir():
 paths=adb('shell','find',ROOT+'/app_chrome/Default','-type','f','-name','roadium-*.current.json').decode().splitlines()
 if not paths:
  directory=ROOT+'/app_chrome/Default/adblock_subscriptions'
  assert subprocess.run([ADB,'shell','test','-d',directory],capture_output=True).returncode==0
  return directory
 dirs={str(Path(p).parent).replace('\\','/') for p in paths}
 assert len(dirs)==1
 return next(iter(dirs))
def capture(label):
 assert re.fullmatch('[a-z0-9-]+',label)
 guard();E.mkdir(exist_ok=True,parents=True)
 data=prefs()
 selected={k:v for k,v in data.items() if k in ['adblock','filtering']}
 (E/(label+'-profile.json')).write_text(json.dumps(selected,indent=2)+'\n',encoding='utf-8',newline='\n')
 directory=storage_dir()
 names=adb('shell','find',directory,'-maxdepth','1','-type','f').decode().splitlines()
 record=[]
 for path in names:
  assert path.startswith(directory+'/')
  if path.endswith('.json') and '/roadium-' in path:
   content=adb('exec-out','cat',path)
   try:details=json.loads(content)
   except ValueError:details={'corrupt_bytes':len(content)}
   record.append(dict(file=path.rsplit('/',1)[-1],sha256=hashlib.sha256(content).hexdigest(),record=details))
 files=[]
 for path in names:
  if path.endswith('.fb'):
   digest=adb('shell','sha256sum',path).decode().split()[0]
   files.append(dict(file=path.rsplit('/',1)[-1],sha256=digest))
 (E/(label+'-storage.json')).write_text(json.dumps(dict(directory=directory,records=record,files=files),indent=2)+'\n',encoding='utf-8',newline='\n')
 return selected
def wait_version(version,count=2,timeout=35):
 end=time.monotonic()+timeout
 while time.monotonic()<end:
  data=prefs()
  metadata=data['adblock'].get('subscription_metadata',{})
  actual=[metadata.get(url,{}).get('version') for url in URLS[:2]]
  if actual.count(version)>=count:return data
  time.sleep(.5)
 raise RuntimeError('Version not activated: '+str(actual))
