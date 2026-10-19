"""Loopback-only TLS subscription fixture; no production trust/mapping changes."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json,re,ssl,threading,time
WORK=Path(__file__).parent
MODE=WORK/'tls-mode.json'
LOG=WORK/'tls-requests.jsonl'
LOCK=threading.Lock()
NAMES={'easylist.txt','abp-filters-anti-cv.txt'}

class Handler(BaseHTTPRequestHandler):
    protocol_version='HTTP/1.1'
    def log_message(self,*args): pass
    def do_GET(self):
        host=self.headers.get('Host','').removesuffix(':443')
        mode=json.loads(MODE.read_text(encoding='utf-8'))
        assert mode['mode'] in ['fallback','primary','both-fail','redirect','html','metadata-redirect','invalid','slow']
        assert re.fullmatch(r'20300102[0-9]{4}',mode['version'])
        primary=host=='uazo.github.io' and self.path.startswith('/cromite/filters/')
        fallback=host=='raw.githubusercontent.com' and self.path.startswith('/uazo/cromite/pages/filters/')
        custom=host=='custom.card05.invalid' and self.path=='/list.txt'
        name=self.path.rsplit('/',1)[-1]
        status=200
        content_type='text/plain; charset=utf-8'
        location=None
        if custom:
            body=('[Adblock Plus 2.0]\n! Title: Roadium Card05 custom subscription\n'
                  '! Version: 203001020001\n! Expires: 365 days\n'
                  '||custom.ads.card05.invalid^\n')
        elif not (primary or fallback) or name not in NAMES:
            status=404
            body='Unapproved test path\n'
        elif mode['mode']=='invalid':
            content_type='text/html'
            body='<!doctype html><title>Rejected update</title>'
        elif mode['mode']=='both-fail' or (primary and mode['mode']=='fallback'):
            status=503
            body='Controlled unavailable transport\n'
        elif primary and mode['mode']=='redirect':
            status=302
            location='https://uazo.github.io/cromite/filters/not-approved.txt'
            body='Controlled redirect\n'
        elif primary and mode['mode']=='html':
            content_type='text/html'
            body='<!doctype html><title>Controlled HTTP 200 error page</title>'
        elif primary and mode['mode']=='metadata-redirect':
            body='[Adblock Plus 2.0]\n! Redirect: https://uazo.github.io/cromite/filters/not-approved.txt\n||pagead2.googlesyndication.com^\n'
        else:
            body=('[Adblock Plus 2.0]\n! Title: Roadium Card05 controlled list\n'
                  '! Version: '+mode['version']+'\n! Expires: 365 days\n'
                  '||pagead2.googlesyndication.com^\n127.0.0.1##.card05-ad\n')
            if name=='abp-filters-anti-cv.txt':
                body+='127.0.0.1#$#override-property-read roadiumProbe undefined\n'
        payload=body.encode('utf-8')
        record=dict(time_unix=time.time(),phase=mode['phase'],mode=mode['mode'],host=host,path=self.path,
                    transport='primary' if primary else 'fallback' if fallback else 'custom' if custom else 'unapproved',
                    status=status,bytes=len(payload),had_cookie='Cookie' in self.headers,
                    had_authorization='Authorization' in self.headers)
        with LOCK:
            with LOG.open('a',encoding='utf-8',newline='\n') as stream:
                stream.write(json.dumps(record)+'\n')
        self.send_response(status)
        self.send_header('Content-Type',content_type)
        self.send_header('Content-Length',str(len(payload)))
        self.send_header('Cache-Control','no-store')
        if location:self.send_header('Location',location)
        self.end_headers()
        if mode['mode']=='slow':
            self.wfile.write(payload[:len(payload)//2])
            self.wfile.flush()
            (WORK/'slow-response.json').write_text(json.dumps(record),encoding='utf-8')
            time.sleep(40)
            try:self.wfile.write(payload[len(payload)//2:])
            except (BrokenPipeError,ConnectionResetError):pass
        else:self.wfile.write(payload)

assert MODE.is_file()
server=ThreadingHTTPServer(('127.0.0.1',8844),Handler)
context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(WORK/'tls/fixture.crt',WORK/'tls/fixture.key')
context.set_alpn_protocols(['http/1.1'])
server.socket=context.wrap_socket(server.socket,server_side=True)
print('Card05 developer TLS fixture listening only on 127.0.0.1:8844',flush=True)
server.serve_forever()
