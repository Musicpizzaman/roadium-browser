"""Serve byte-exact frozen filter snapshots only to this own lab profile."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import ssl,json,time,hashlib,threading
W=Path(__file__).parent
LOCK=threading.Lock()
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        host=self.headers.get('Host','').removesuffix(':443')
        key=(host,self.path)
        paths={('uazo.github.io','/cromite/filters/'+name):name for name in ['easylist.txt','abp-filters-anti-cv.txt','badblock_lite.txt','badmojr-1Hosts-master-Lite-adblock.txt']}
        paths[('raw.githubusercontent.com','/uazo/cromite/master/tools/filters/experimental-cromite-filters.txt')]='experimental-cromite-filters.txt'
        mode=json.loads((W/'tls-mode.json').read_text())
        assert mode['mode'] in ['frozen','controlled']
        name=paths.get(key)
        if name and mode['mode']=='frozen':
            payload=(W/'lists'/name).read_bytes();status=200
        elif name and mode['mode']=='controlled':
            payload=(W/'controlled-list.txt').read_bytes() if name=='abp-filters-anti-cv.txt' else b'[Adblock Plus 2.0]\n! Version: 203001060001\n||unused.card06.invalid^\n';status=200
        elif host=='custom.card06.invalid' and self.path=='/list.txt':
            payload=(W/'controlled-list.txt').read_bytes();status=200
        else:payload=b'Unapproved lab path\n';status=404
        record=dict(time_unix=time.time(),phase=mode['phase'],host=host,path=self.path,status=status,bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest(),had_cookie='Cookie' in self.headers,had_authorization='Authorization' in self.headers)
        with LOCK:
            with (W/'tls-requests.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
        self.send_response(status);self.send_header('Content-Type','text/plain; charset=utf-8');self.send_header('Content-Length',str(len(payload)));self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(payload)
context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(W/'tls/fixture.crt',W/'tls/fixture.key')
server=ThreadingHTTPServer(('127.0.0.1',8844),Handler)
server.socket=context.wrap_socket(server.socket,server_side=True)
print('Own Card06 frozen-list TLS server on127.0.0.1:8844',flush=True)
server.serve_forever()
