"""Toggle only observed Roadium master/advanced checkboxes in standalone settings."""
from pathlib import Path
import re, subprocess, sys, time, xml.etree.ElementTree as ET
WORK=Path(__file__).parent
ADB=r'E:\Android Auto Projects\AndroidSdk\platform-tools\adb.exe'
PKG='io.github.musicpizzaman.roadium'
which,value=sys.argv[1:]
assert which in ['advanced','global'] and value in ['true','false']
def adb(*args): return subprocess.check_output([ADB,*args],timeout=40)
assert adb('shell','am','get-current-user').strip()==b'11'
adb('shell','am','start','-W','--user','11','-n',PKG+'/org.chromium.chrome.browser.settings.SettingsActivity',
    '--es','show_fragment','org.chromium.chrome.browser.adblock.settings.AdblockSettingsFragment',
    '--ez','show_fragment_standalone','true')
subprocess.run([sys.executable,str(WORK/'ui.py')],check=True)
root=ET.fromstring((WORK/'last-ui.xml').read_bytes())
nodes=[n for n in root.iter('node') if n.get('package')==PKG and n.get('checkable')=='true']
assert len(nodes)>=2
nodes.sort(key=lambda n:int(re.findall(r'\d+',n.get('bounds'))[1]))
node=nodes[1 if which=='advanced' else 0]
assert node.get('enabled')=='true'
if node.get('checked')!=value:
    x1,y1,x2,y2=map(int,re.findall(r'\d+',node.get('bounds')))
    adb('shell','input','tap',str((x1+x2)//2),str((y1+y2)//2))
    time.sleep(1)
adb('shell','input','keyevent','4')
print('UI toggle:',which,value)
