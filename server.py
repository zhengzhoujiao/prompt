import os
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        # 兼容本地直接访问和 nginx /prompt/ 子路径两种场景
        path = parsed.path.removeprefix('/prompt')
        if not path:
            path = '/'

        if path in ('/', '/index.html'):
            self._serve_file(os.path.join(BASE_DIR, 'index.html'), 'text/html')
        elif path == '/api/data':
            self._serve_json()
        elif path == '/image':
            params = parse_qs(parsed.query)
            img_path = unquote(params.get('path', [''])[0])
            self._serve_image(img_path)
        elif path == '/meta':
            params = parse_qs(parsed.query)
            meta_path = unquote(params.get('path', [''])[0])
            self._serve_meta(meta_path)
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_file(self, filepath, content_type):
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', f'{content_type}; charset=utf-8')
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def _serve_json(self):
        json_path = os.path.join(BASE_DIR, 'prompt_local.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(data.encode('utf-8'))

    def _serve_image(self, img_path):
        # img_path 是相对路径，基于 BASE_DIR 解析
        abs_path = os.path.normpath(os.path.join(BASE_DIR, img_path))
        # 防止路径穿越
        if not abs_path.startswith(BASE_DIR):
            self.send_response(403)
            self.end_headers()
            return
        if not os.path.exists(abs_path):
            self.send_response(404)
            self.end_headers()
            return
        mime_type, _ = mimetypes.guess_type(abs_path)
        with open(abs_path, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', mime_type or 'application/octet-stream')
        self.end_headers()
        self.wfile.write(data)

    def _serve_meta(self, meta_path):
        abs_path = os.path.normpath(os.path.join(BASE_DIR, meta_path))
        if not abs_path.startswith(BASE_DIR):
            self.send_response(403)
            self.end_headers()
            return
        if not os.path.exists(abs_path):
            self.send_response(404)
            self.end_headers()
            return
        with open(abs_path, 'r', encoding='utf-8') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(data.encode('utf-8'))

    def log_message(self, format, *args):
        pass  # suppress request logs


if __name__ == '__main__':
    port = 8080
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'已启动，请访问 http://localhost:{port}')
    server.serve_forever()
