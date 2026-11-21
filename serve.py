#!/usr/bin/env python3
"""Local server for the gift tracker: serves index.html and reads/writes people.json.

Listens on 127.0.0.1 only. Port from GIFTS_PORT (default 8765).
Keeps one backup per day in backups/ (last 30 days).
"""
import json
import os
import shutil
from datetime import date
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "people.json"
BACKUPS = ROOT / "backups"
KEEP_BACKUPS = 30
HOST = "127.0.0.1"
PORT = int(os.environ.get("GIFTS_PORT", "8765"))
ALLOWED_HOSTS = {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}


def backup():
    if not DATA.exists():
        return
    BACKUPS.mkdir(exist_ok=True)
    target = BACKUPS / f"people-{date.today().isoformat()}.json"
    if not target.exists():
        shutil.copy2(DATA, target)
    for old in sorted(BACKUPS.glob("people-*.json"))[:-KEEP_BACKUPS]:
        old.unlink()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_json(self, code, body):
        raw = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def trusted(self):
        # Blocks other websites (DNS rebinding, cross-origin posts) from touching the data.
        if self.headers.get("Host") not in ALLOWED_HOSTS:
            return False
        origin = self.headers.get("Origin")
        return origin is None or origin.removeprefix("http://") in ALLOWED_HOSTS

    def do_GET(self):
        if not self.trusted():
            return self.send_error(403)
        if self.path == "/api/people":
            doc = json.loads(DATA.read_text()) if DATA.exists() else {"people": []}
            return self.send_json(200, doc)
        if self.path in ("/", "/index.html", "/icon.svg"):
            return super().do_GET()
        self.send_error(404)

    def do_PUT(self):
        if not self.trusted():
            return self.send_error(403)
        if self.path != "/api/people":
            return self.send_error(404)
        try:
            length = int(self.headers.get("Content-Length", 0))
            doc = json.loads(self.rfile.read(length))
            if not isinstance(doc, dict) or not isinstance(doc.get("people"), list):
                raise ValueError("expected {\"people\": [...]}")
        except ValueError as e:
            return self.send_json(400, {"error": str(e)})
        backup()
        tmp = DATA.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
        os.replace(tmp, DATA)
        self.send_json(200, {"ok": True})

    # sendBeacon (used when the tab closes mid-save) can only POST.
    do_POST = do_PUT


if __name__ == "__main__":
    print(f"Gift tracker on http://{HOST}:{PORT}/")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
