import urllib.request
import urllib.parse
import json
import time
import os
import re
import shutil
import tempfile
import http.server
import threading


class TokenHttpHandler(http.server.BaseHTTPRequestHandler):
    """Serves real-time token metrics to the SignalRGB HTML canvas."""

    def log_message(self, format, *args):
        # Suppress standard logging to prevent cluttering the terminal
        pass

    def do_GET(self):
        if self.path.startswith("/api/tokens"):
            client_ref = getattr(self.server, "client_ref", None)
            if client_ref:
                client_ref.last_client_poll_time = time.time()
                client_ref.is_connected = True
                payload = client_ref.latest_data or {}
            else:
                payload = {}

            data = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()


class SignalRGBClient:
    """Bridges token data into SignalRGB via two robust methods:
    1. Built-in Local HTTP API Server (port 16035) — SignalRGB HTML effect polls
       real-time metrics directly from Python. Works universally on Free & Pro editions.
    2. Canvas API POST (port 16034) — sends events to SignalRGB onCanvasApiEvent (Pro only).
    """

    def __init__(self, host: str = "localhost", port: int = 16034, sender: str = "aitoken", local_http_port: int = 16035):
        self.host = host
        self.port = port
        self.sender = sender
        self.base_url = f"http://{self.host}:{self.port}/canvas/event"
        self._last_sent_payload = None
        self._last_send_time = 0.0
        self.is_connected = False

        # Live telemetry state
        self.latest_data = {}
        self.last_client_poll_time = 0.0
        self.local_http_port = local_http_port
        self.local_server = None

        # Start local HTTP server thread for SignalRGB effect polling
        self._start_local_server()

        # HTML installation path
        user_profile = os.environ.get("USERPROFILE", "")
        self.effect_html_path = os.path.join(
            user_profile, "Documents", "WhirlwindFX", "Effects",
            "AI Token Tracker", "AI Token Tracker.html"
        )

    def _start_local_server(self):
        try:
            class ThreadedServer(http.server.HTTPServer):
                allow_reuse_address = True

            self.local_server = ThreadedServer(("127.0.0.1", self.local_http_port), TokenHttpHandler)
            self.local_server.client_ref = self
            server_thread = threading.Thread(target=self.local_server.serve_forever, daemon=True)
            server_thread.start()
        except Exception:
            pass

    def send_event(self, data: dict) -> bool:
        """Publishes token data to the local HTTP server and SignalRGB Canvas API."""
        now = time.time()
        self.latest_data = data

        # Check if SignalRGB HTML canvas has polled recently
        if (now - self.last_client_poll_time) < 3.5:
            self.is_connected = True
        else:
            self.is_connected = False

        # Also try Canvas API POST (Pro edition)
        self._send_canvas_api(data, now)

        return True

    def _send_canvas_api(self, data: dict, now: float):
        """Sends event via Canvas API POST (Pro only)."""
        json_str = json.dumps(data)

        # Deduplicate identical payloads unless >2 seconds passed
        if json_str == self._last_sent_payload and (now - self._last_send_time) < 2.0:
            return

        query = urllib.parse.urlencode({
            "sender": self.sender,
            "event": json_str
        })
        url = f"{self.base_url}?{query}"

        try:
            req = urllib.request.Request(
                url,
                data=b"",
                headers={"User-Agent": "SignalRGB-AI-Token-Tracker/1.0"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=1.5) as res:
                if res.status == 200:
                    self.is_connected = True
                self._last_sent_payload = json_str
                self._last_send_time = now
        except Exception:
            pass
