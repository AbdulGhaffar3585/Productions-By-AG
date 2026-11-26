"""Local preview: python3 serve.py → http://localhost:4173 (mimics Vercel clean URLs)."""
import http.server, os
from pathlib import Path

PUBLIC = Path(__file__).parent / "concept"

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(PUBLIC), **k)

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path != "/" and "." not in Path(path).name and (PUBLIC / (path.lstrip("/") + ".html")).exists():
            self.path = path + ".html" + (self.path[len(path):] if "?" in self.path else "")
        elif path != "/" and not (PUBLIC / path.lstrip("/")).exists():
            self.send_response(404); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write((PUBLIC / "404.html").read_bytes()); return
        super().do_GET()

http.server.ThreadingHTTPServer(("127.0.0.1", int(os.environ.get("PORT", 4173))), H).serve_forever()
