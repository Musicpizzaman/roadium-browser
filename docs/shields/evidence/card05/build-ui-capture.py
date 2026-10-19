from pathlib import Path
import subprocess
ROOT=Path('/home/lg/working_dir/chromium/src')
WORK=Path('/tmp/roadium-card05-ui-helper')
WORK.mkdir(exist_ok=True)
sdk=ROOT/'third_party/android_sdk/public'
android=sdk/'platforms/android-37.0/android.jar'
jdk=ROOT/'third_party/jdk/current/bin'
subprocess.run([str(jdk/'javac'),'--release','8','-classpath',str(android),'-d',str(WORK),
                '/tmp/RoadiumUiDump.java'],check=True)
subprocess.run([str(jdk/'java'),'-cp',str(sdk/'build-tools/37.0.0/lib/d8.jar'),
    'com.android.tools.r8.D8','--min-api','28','--lib',str(android),'--output',str(WORK/'capture.jar'),
    str(WORK/'RoadiumUiDump.class')],check=True)
print('Built root-only read-only focused-window helper; browser binaries unchanged.')
