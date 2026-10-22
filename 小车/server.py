from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os

# ---------- 小车的状态（权威版本存在后端，前端只是显示器） ----------
COLS, ROWS = 10, 8
car = {"x": 1, "y": 1}
START = (1, 1)

def move_car(command):
    x, y = car["x"], car["y"]
    if command == 'w': y -= 1
    if command == 's': y += 1
    if command == 'a': x -= 1
    if command == 'd': x += 1
    if 0 <= x < COLS and 0 <= y < ROWS:      # 边界检查：不允许走出地图
        car["x"], car["y"] = x, y
    return dict(car)

def reset_car():
    car["x"], car["y"] = START
    return dict(car)

# ---------- HTTP 部分 ----------
class Handler(BaseHTTPRequestHandler):
    def reply(self, body, ctype, code=200):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def reply_json(self, obj, code=200):
        self.reply(json.dumps(obj).encode('utf-8'), 'application/json; charset=utf-8', code)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == '/api/move':
            qs = parse_qs(url.query)
            command = (qs.get('command') or [''])[0].lower()
            if command in ('w', 'a', 's', 'd'):
                self.reply_json(move_car(command))
            else:
                self.reply_json({"error": "command 只能是 w/a/s/d"}, 400)
        elif url.path == '/api/reset':
            self.reply_json(reset_car())
        elif url.path in ('/', '/index.html'):
            page = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
            with open(page, 'rb') as f:
                self.reply(f.read(), 'text/html; charset=utf-8')
        else:
            self.reply(b'Not Found', 'text/plain; charset=utf-8', 404)

    def log_message(self, fmt, *args):       # 每个请求都在黑窗口留一行记录
        print('[请求]', self.address_string(), fmt % args)

if __name__ == '__main__':
    print('小车后端已启动: http://127.0.0.1:8000  (Ctrl+C 停止)')
    HTTPServer(('127.0.0.1', 8000), Handler).serve_forever()