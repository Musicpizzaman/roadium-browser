from pathlib import Path
import subprocess,sys
for case in sys.argv[1:]:
 subprocess.run([sys.executable,str(Path(__file__).with_name('run-recovery-cases.py')),case],check=True)
