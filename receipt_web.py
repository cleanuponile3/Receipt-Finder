import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from Receiptfinder import RECEIPTS, find_nearest_receipt, find_receipt


class ReceiptRequestHandler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            page = Path(__file__).with_name("receiptfinder.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)
        elif self.path == "/api/receipts":
            self.send_json(200, RECEIPTS)
        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/api/search":
            self.send_json(404, {"error": "Not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 1024:
                raise ValueError
            payload = json.loads(self.rfile.read(content_length))
        except (ValueError, json.JSONDecodeError):
            self.send_json(400, {"error": "Send a JSON object with a timestamp."})
            return

        if not isinstance(payload, dict) or not isinstance(payload.get("time"), str):
            self.send_json(400, {"error": "A timestamp is required."})
            return

        try:
            target_datetime = datetime.fromisoformat(payload["time"])
            if target_datetime.tzinfo is not None:
                raise ValueError
            target_time = target_datetime.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            self.send_json(400, {"error": "Enter a valid local date and time."})
            return

        receipt, peeks = find_receipt(RECEIPTS, target_time)
        if receipt is not None:
            self.send_json(200, {
                "receipt": receipt,
                "peeks": peeks,
                "exact": True,
                "seconds_away": 0,
            })
            return

        try:
            receipt, distance_seconds, nearest_peeks = find_nearest_receipt(RECEIPTS, target_time)
        except ValueError:
            self.send_json(400, {"error": "Enter a valid local date and time."})
            return

        self.send_json(200, {
            "receipt": receipt,
            "peeks": peeks + nearest_peeks,
            "exact": False,
            "seconds_away": distance_seconds,
        })


if __name__ == "__main__":
    address = ("127.0.0.1", 8000)
    print(
        f"Receipt Finder is serving {len(RECEIPTS)} events at "
        f"http://{address[0]}:{address[1]}"
    )
    ThreadingHTTPServer(address, ReceiptRequestHandler).serve_forever()
