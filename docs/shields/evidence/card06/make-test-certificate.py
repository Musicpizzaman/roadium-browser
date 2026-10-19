"""Generate only an ephemeral developer TLS fixture, never a release key."""
from pathlib import Path
import subprocess,hashlib,base64,json
root=Path('/tmp/roadium-card06-test-tls')
root.mkdir(exist_ok=False)
subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','3',
    '-keyout',str(root/'fixture.key'),'-out',str(root/'fixture.crt'),
    '-subj','/CN=Roadium Card06 developer fixture',
    '-addext','subjectAltName=DNS:uazo.github.io,DNS:raw.githubusercontent.com',
    '-addext','basicConstraints=critical,CA:FALSE'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
public=subprocess.check_output(['openssl','x509','-in',str(root/'fixture.crt'),'-pubkey','-noout'])
der=subprocess.check_output(['openssl','pkey','-pubin','-outform','DER'],input=public)
data=dict(spki_sha256_base64=base64.b64encode(hashlib.sha256(der).digest()).decode(),
          certificate_sha256=hashlib.sha256((root/'fixture.crt').read_bytes()).hexdigest(),
          purpose='Ephemeral local developer TLS injection; not a production signing key')
(root/'public.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data))
