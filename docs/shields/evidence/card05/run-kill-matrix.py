from pathlib import Path
import subprocess,sys
for stage in sys.argv[1:]:
 subprocess.run([sys.executable,str(Path(__file__).with_name('run-boundary.py')),stage],check=True)
