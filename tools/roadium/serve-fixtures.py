#!/usr/bin/env python3
"""Serve local emulator fixtures and collect playback events (development only)."""
import argparse
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

parser = argparse.ArgumentParser()
parser.add_argument("directory", type=Path)
parser.add_argument("--events", required=True, type=Path)
parser.add_argument("--port", type=int, default=8765)
args = parser.parse_args()
directory = args.directory.resolve()
for name in ("index.html", "tone.wav", "bear.mp4"):
    if not (directory / name).is_file():
        parser.error(f"Missing fixture: {directory / name}")
lock = threading.Lock()
args.events.parent.mkdir(parents=True, exist_ok=True)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *values, **kwargs):
        super().__init__(*values, directory=str(directory), **kwargs)

    def do_POST(self):
        if self.path != "/events":
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 65536:
                raise ValueError("Invalid event size")
            event = json.loads(self.rfile.read(size))
            if not isinstance(event, dict):
                raise ValueError("Event must be an object")
        except (ValueError, UnicodeDecodeError):
            self.send_error(400)
            return
        record = {"receivedUtc": datetime.now(timezone.utc).isoformat(), "event": event}
        with lock, args.events.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record) + "\n")
        self.send_response(204)
        self.end_headers()


print(f"Fixture ready: http://127.0.0.1:{args.port}/", flush=True)
ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
