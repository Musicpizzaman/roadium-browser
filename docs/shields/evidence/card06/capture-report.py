from pathlib import Path
import subprocess,xml.etree.ElementTree as ET,sys,re
w=Path(__file__).parent;e=Path(r"E:\Android Auto Projects\roadium-browser\docs\shields\evidence\card06");adb=r"E:\Android Auto Projects\AndroidSdk\platform-tools\adb.exe"
label=sys.argv[1];assert re.fullmatch("[a-z0-9-]+",label)
subprocess.run([sys.executable,str(w/"ui.py")],stdout=subprocess.DEVNULL,check=True)
raw=(w/"last-ui.xml").read_bytes();report=max((n.get("text","") for n in ET.fromstring(raw).iter("node")),key=len)
assert "Ad blocking:" in report and "Advanced filtering:" in report
assert "Latest source:" in report and "Loaded version:" in report, 'Full diagnostic dialog was not captured'
(e/(label+".xml")).write_bytes(raw);(e/(label+".txt")).write_text(report+"\n",encoding="utf-8",newline="\n")
(e/(label+".png")).write_bytes(subprocess.check_output([adb,"exec-out","screencap","-p"]))
print("\n".join(report.splitlines()[:7]))
