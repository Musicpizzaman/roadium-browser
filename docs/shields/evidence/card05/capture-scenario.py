from runtime import *
import sys
label=sys.argv[1]
guard()
processes=adb('shell','ps','-A','-o','USER,PID,NAME').decode().splitlines()
mains=[line.split() for line in processes if line.split()[-1:]==[PKG]]
assert len(mains)==1 and mains[0][0]=='u11_a204',mains
capture(label)
subprocess.run([sys.executable,str(W/'open-and-capture-report.py'),'11',label+'-report'],check=True)
launch()
reload=json.loads(subprocess.check_output(['node',str(W/'probe-fallback.mjs'),'reload'],timeout=30))
probe=json.loads(subprocess.check_output(['node',str(W/'probe-fallback.mjs'),'advertising'],timeout=30))
(E/(label+'.json')).write_text(json.dumps(dict(reload=reload,probe=probe),indent=2)+'\n',encoding='utf-8',newline='\n')
print(label,probe['state'],probe.get('advertisingFailures'))
