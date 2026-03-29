import argparse
import json
from datetime import datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
MOTD_FILE = DATA_DIR / "motd.txt"


state_lock = Lock()
messages = []
online_users = set()
next_message_id = 1


def build_message(sender, recipient, content):
	global next_message_id
	message = {
		"id": next_message_id,
		"from": sender,
		"to": recipient,
		"text": content,
		"timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
	}
	next_message_id += 1
	return message


class ChatHandler(SimpleHTTPRequestHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

	def do_GET(self):
		parsed = urlparse(self.path)

		if parsed.path == "/api/users":
			with state_lock:
				payload = {"users": sorted(online_users)}
			self._send_json(payload)
			return

		if parsed.path == "/api/messages":
			query = parse_qs(parsed.query)
			username = query.get("username", [""])[0].strip()
			after_id = self._safe_int(query.get("after_id", ["0"])[0], default=0)

			if not username:
				self._send_json({"error": "username is required"}, status=HTTPStatus.BAD_REQUEST)
				return

			with state_lock:
				filtered = [
					msg
					for msg in messages
					if msg["id"] > after_id and (msg["to"] in (username, "all"))
				]
			self._send_json({"messages": filtered})
			return

		if parsed.path == "/api/motd":
			if not MOTD_FILE.exists():
				self._send_json({"motd": "Welcome to let-s_chat"})
				return
			text = MOTD_FILE.read_text(encoding="utf-8").strip()
			self._send_json({"motd": text})
			return

		# Serve index by default
		if parsed.path == "/":
			self.path = "/index.html"
		return super().do_GET()

	def do_POST(self):
		parsed = urlparse(self.path)
		body = self._read_json_body()

		if body is None:
			self._send_json({"error": "invalid JSON body"}, status=HTTPStatus.BAD_REQUEST)
			return

		if parsed.path == "/api/login":
			username = body.get("username", "").strip()
			if not username:
				self._send_json({"error": "username is required"}, status=HTTPStatus.BAD_REQUEST)
				return

			with state_lock:
				online_users.add(username)
				messages.append(build_message("system", username, f"Welcome, {username}"))
			self._send_json({"ok": True})
			return

		if parsed.path == "/api/logout":
			username = body.get("username", "").strip()
			if not username:
				self._send_json({"error": "username is required"}, status=HTTPStatus.BAD_REQUEST)
				return

			with state_lock:
				online_users.discard(username)
			self._send_json({"ok": True})
			return

		if parsed.path == "/api/send":
			sender = body.get("from", "").strip()
			recipient = body.get("to", "all").strip() or "all"
			content = body.get("text", "").strip()

			if not sender or not content:
				self._send_json(
					{"error": "from and text are required"},
					status=HTTPStatus.BAD_REQUEST,
				)
				return

			with state_lock:
				messages.append(build_message(sender, recipient, content))
			self._send_json({"ok": True})
			return

		self._send_json({"error": "route not found"}, status=HTTPStatus.NOT_FOUND)

	def log_message(self, format, *args):
		# Keep useful logs while reducing noise.
		print(f"[{self.log_date_time_string()}] {self.address_string()} - {format % args}")

	def _read_json_body(self):
		length = self._safe_int(self.headers.get("Content-Length", "0"), default=0)
		if length <= 0:
			return {}

		raw = self.rfile.read(length)
		try:
			return json.loads(raw.decode("utf-8"))
		except (UnicodeDecodeError, json.JSONDecodeError):
			return None

	def _send_json(self, payload, status=HTTPStatus.OK):
		data = json.dumps(payload).encode("utf-8")
		self.send_response(status)
		self.send_header("Content-Type", "application/json; charset=utf-8")
		self.send_header("Content-Length", str(len(data)))
		self.end_headers()
		self.wfile.write(data)

	@staticmethod
	def _safe_int(value, default=0):
		try:
			return int(value)
		except (TypeError, ValueError):
			return default


def run_server(host, port):
	DATA_DIR.mkdir(exist_ok=True)
	STATIC_DIR.mkdir(exist_ok=True)
	server = ThreadingHTTPServer((host, port), ChatHandler)
	print(f"Chat server running on http://{host}:{port}")
	print("Open that URL in any browser on your network")
	server.serve_forever()


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Browser chat server")
	parser.add_argument("--host", default="0.0.0.0", help="Host/IP to bind")
	parser.add_argument("--port", type=int, default=8000, help="Port to bind")
	args = parser.parse_args()
	run_server(args.host, args.port)