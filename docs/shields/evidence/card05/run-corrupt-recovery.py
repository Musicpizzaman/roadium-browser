from runtime import *
from importlib.machinery import SourceFileLoader
restore=SourceFileLoader('restore_runtime',str(W/'restore-runtime.py')).load_module().restore
restore();mode('both-fail','203001020009','corrupt-current-recovery')
directory=storage_dir()
changed=[]
for url in URLS[:2]:
 prefix='roadium-'+hashlib.sha256(url.encode()).hexdigest()
 record=json.loads(adb('exec-out','cat',directory+'/'+prefix+'.current.json'))
 file=record['file']
 assert re.fullmatch(prefix+r'-[0-9A-Fa-f]{32}\.fb',file)
 remote=directory+'/'+file
 adb('shell','sh','-c',"'printf broken > "+remote+"'")
 assert adb('exec-out','cat',remote)==b'broken'
 changed.append(file)
capture('corrupt-current-before-restart')
launch()
subprocess.run([__import__('sys').executable,str(W/'capture-scenario.py'),'previous-version-recovery'],check=True)
(E/'corrupt-current-injection.json').write_text(json.dumps(dict(files=changed,method='Own-user stopped-app file corruption; original previous records untouched'),indent=2)+'\n',encoding='utf-8')
