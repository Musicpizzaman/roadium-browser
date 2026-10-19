from pathlib import Path
import subprocess,json,sys,re
adb=r"E:\Android Auto Projects\AndroidSdk\platform-tools\adb.exe"
user=int(sys.argv[1]);label=sys.argv[2]
assert user == 11 and re.fullmatch("[a-z0-9-]+",label)
data=json.loads(subprocess.check_output([adb,"exec-out","cat",f"/data/user/{user}/io.github.musicpizzaman.roadium/app_chrome/Default/Preferences"]))
fields={k:v for k,v in data.items() if k in ["adblock","filtering"]}
e=Path(r"E:\Android Auto Projects\roadium-browser\docs\shields\evidence\card05")
(e/(label+".json")).write_text(json.dumps(fields,indent=2)+"\n",encoding="utf-8",newline="\n")
print(label,"advanced:",fields["adblock"].get("privilegedfilters_enabled","unset"),"blocking:",fields["filtering"]["configurations"]["adblock"]["enabled"],"signatures:",len(fields["adblock"].get("subscription_signatures",{})))
