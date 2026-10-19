from pathlib import Path
import subprocess
import sys
import time
import re
import xml.etree.ElementTree as ET

WORK = Path(__file__).parent
ADB = r'E:\Android Auto Projects\AndroidSdk\platform-tools\adb.exe'
PACKAGE = 'io.github.musicpizzaman.roadium'
user = str(int(sys.argv[1]))
assert user in ['11','13']

def adb(*args):
    return subprocess.run([ADB, *args], check=True, capture_output=True, timeout=40)

adb('shell', 'am', 'switch-user', user)
for _ in range(30):
    if b'RUNNING_UNLOCKED' in adb('shell', 'am', 'get-started-user-state', user).stdout:
        break
    time.sleep(.5)
else:
    raise RuntimeError('Test user did not unlock')
adb('shell', 'am', 'start', '-W', '--user', user, '-a', 'android.intent.action.VIEW',
    '-d', 'http://127.0.0.1:8766/card06.html', '-p', PACKAGE)
adb('shell', 'am', 'start', '-W', '--user', user, '-n',
    PACKAGE + '/org.chromium.chrome.browser.settings.SettingsActivity',
    '--es', 'show_fragment', 'org.chromium.chrome.browser.adblock.settings.AdblockSettingsFragment',
    '--ez', 'show_fragment_standalone', 'true')

def ui():
    for _ in range(3):
        result = subprocess.run([sys.executable, str(WORK / 'ui.py')], capture_output=True)
        if result.returncode == 0:
            return ET.fromstring((WORK / 'last-ui.xml').read_bytes())
        time.sleep(.5)
    raise RuntimeError('No fresh settings hierarchy available')

def bounds(node):
    return list(map(int, re.findall(r'\d+', node.get('bounds'))))

for _ in range(5):
    root = ui()
    diagnostics = [node for node in root.iter('node')
                   if node.get('package') == PACKAGE and node.get('text') == 'Filter diagnostics'
                   and bounds(node)[3] - bounds(node)[1] >= 20]
    if diagnostics:
        x1, y1, x2, y2 = bounds(diagnostics[0])
        adb('shell', 'input', 'tap', str((x1+x2)//2), str((y1+y2)//2))
        for attempt in range(5):
            dialog = ui()
            if any(node.get('text') == 'Local filter diagnostics' for node in dialog.iter('node')):
                subprocess.run([sys.executable, str(WORK / 'capture-report.py'), sys.argv[2]], check=True)
                break
            # A preference refresh can race the first tap; use a fresh observed row.
            retry = [node for node in dialog.iter('node')
                     if node.get('package') == PACKAGE and node.get('text') == 'Filter diagnostics']
            if retry:
                a,b,c,d = bounds(retry[0])
                adb('shell', 'input', 'tap', str((a+c)//2), str((b+d)//2))
            time.sleep(.5)
        else:
            raise RuntimeError('Diagnostic dialog did not open')
        break
    scroll = [node for node in root.iter('node')
              if node.get('package') == PACKAGE and node.get('scrollable') == 'true'
              and bounds(node)[2] - bounds(node)[0] > 400]
    assert scroll, 'No observed settings scroller'
    x1, y1, x2, y2 = bounds(scroll[0])
    adb('shell', 'input', 'swipe', str((x1+x2)//2), str(y2-40),
        str((x1+x2)//2), str(y1+60), '400')
else:
    raise RuntimeError('Diagnostics entry not reached')
