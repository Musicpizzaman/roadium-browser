from pathlib import Path
import hashlib,json,subprocess,tempfile
root=Path('/home/lg/working_dir/chromium/src')
out=root/'out/x64'
resource=root/'components/adblock/core/resources/roadium'
generated=out/'gen/components/adblock/core/resources'
results=[]
with tempfile.TemporaryDirectory(prefix='roadium-card03-repeat-') as temp:
    for name,source,url,privileged in [
        ('easylist.fb','easylist.txt.gz','https://uazo.github.io/cromite/filters/easylist.txt',False),
        ('anticv.fb','abp-filters-anti-cv.txt.gz','https://uazo.github.io/cromite/filters/abp-filters-anti-cv.txt',True)]:
        target=Path(temp)/name
        args=[str(out/'clang_x64/adblock_flatbuffer_converter'),str(resource/source),url,str(target),
              '--statistics-output='+str(target)+'.json']
        if privileged: args.append('--allow-privileged')
        subprocess.run(args,check=True)
        value=target.read_bytes()
        assert value==(generated/name).read_bytes()
        stats=json.loads(Path(str(target)+'.json').read_text())
        assert stats==json.loads((generated/(name+'.json')).read_text())
        results.append(dict(file=name,sha256=hashlib.sha256(value).hexdigest(),bytes=len(value),
                            identical=True,allow_privileged=privileged,statistics=stats))
Path('/tmp/roadium-card03-repeat.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
