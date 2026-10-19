"""Own lab CONNECT relay: host DNS workaround, no TLS interception.

Bound to loopback and reached only by this emulator's own adb reverse port.
Allowed external names are YouTube playback dependencies. Frozen subscription
names route to the existing lab TLS fixture. Records contain host/outcome only.
"""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import socket,select,json,time,threading
W=Path(__file__).parent
LOCK=threading.Lock()
DOMAINS=('youtube.com','youtube-nocookie.com','googlevideo.com','ytimg.com','ggpht.com','googleusercontent.com','googleapis.com','gstatic.com')
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_CONNECT(self):
        host,sep,port=self.path.rpartition(':')
        local=host in ['uazo.github.io','raw.githubusercontent.com','custom.card06.invalid']
        allowed=sep and port=='443' and (local or any(host==d or host.endswith('.'+d) for d in DOMAINS))
        outcome='denied';remote=None
        try:
            if not allowed:self.send_error(403);return
            remote=socket.create_connection(('127.0.0.1',8844) if local else (host,443),timeout=15)
            outcome='connected';self.send_response(200);self.end_headers()
            sockets=[self.connection,remote]
            while True:
                ready,_,_=select.select(sockets,[],[],30)
                if not ready:break
                for source in ready:
                    payload=source.recv(65536)
                    if not payload:return
                    (remote if source is self.connection else self.connection).sendall(payload)
        except OSError as error:
            outcome=type(error).__name__
            if remote is None:self.send_error(502)
        finally:
            if remote:remote.close()
            with LOCK:
                with (W/'live-proxy.jsonl').open('a',encoding='utf-8') as f:
                    f.write(json.dumps(dict(time=time.time(),host=host,port=port,outcome=outcome,lab_subscription=local))+'\n')
    def do_GET(self):self.send_error(403)
print('Own loopback DNS relay127.0.0.1:8886; TLS remains end to end',flush=True)
ThreadingHTTPServer(('127.0.0.1',8886),Handler).serve_forever()
