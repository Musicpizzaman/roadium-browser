from pathlib import Path
import subprocess,xml.etree.ElementTree as ET
ADB=r'E:\Android Auto Projects\AndroidSdk\platform-tools\adb.exe'
raw=subprocess.check_output([ADB,'shell','CLASSPATH=/data/local/tmp/roadium-card06-capture.jar',
    'app_process','/system/bin','RoadiumUiDump'],timeout=40)
root=ET.fromstring(raw)
Path(__file__).with_name('last-ui.xml').write_bytes(raw)
for node in root.iter('node'):
    text=node.get('text') or node.get('content-desc')
    if text:print(repr(text),node.get('bounds'),'checked='+node.get('checked',''),'enabled='+node.get('enabled',''))
