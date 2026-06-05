from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse
import sys


bind = sys.argv[1]
port = int(sys.argv[2])
web_root = Path(sys.argv[3]).resolve()
assets_root = Path(sys.argv[4]).resolve()


class IntranetPreviewHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        requested_path = unquote(urlparse(path).path)
        if requested_path == "/":
            requested_path = "/index.html"

        if requested_path.startswith("/web/"):
            root = web_root
            relative = requested_path[len("/web/") :]
        elif requested_path.startswith("/assets/"):
            root = assets_root
            relative = requested_path[len("/assets/") :]
        else:
            root = web_root
            relative = requested_path.lstrip("/")

        resolved = (root / relative).resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            return str(web_root / "__not_found__")

        return str(resolved)

    def end_headers(self):
        self.send_header("X-Robots-Tag", "noindex, nofollow")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


ThreadingHTTPServer((bind, port), IntranetPreviewHandler).serve_forever()
