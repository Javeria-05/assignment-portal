import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test-report.json")


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/report":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"[receiver] saved report: {data.get('overall_status')} "
              f"commit {str(data.get('commit_sha'))[:7]}")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"saved": true}')


if __name__ == "__main__":
    print("Receiver listening on http://127.0.0.1:9000/report")
    HTTPServer(("127.0.0.1", 9000), Handler).serve_forever()