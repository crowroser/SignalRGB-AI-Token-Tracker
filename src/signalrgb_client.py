import urllib.request
import urllib.parse
import json
import time

class SignalRGBClient:
    def __init__(self, host: str = "localhost", port: int = 16034, sender: str = "aitoken"):
        self.host = host
        self.port = port
        self.sender = sender
        self.base_url = f"http://{self.host}:{self.port}/canvas/event"
        self._last_sent_payload = None
        self._last_send_time = 0.0
        self.is_connected = False

    def send_event(self, data: dict) -> bool:
        """Sends a JSON event to SignalRGB's Canvas API."""
        now = time.time()
        
        # Serialize data
        json_str = json.dumps(data)
        
        # Deduplicate identical payloads unless >2 seconds passed (heartbeat)
        if json_str == self._last_sent_payload and (now - self._last_send_time) < 2.0:
            return True

        query = urllib.parse.urlencode({
            "sender": self.sender,
            "event": json_str
        })
        url = f"{self.base_url}?{query}"

        try:
            req = urllib.request.Request(
                url,
                data=b"", # Empty POST body as query params contain sender & event
                headers={"User-Agent": "SignalRGB-AI-Token-Tracker/1.0"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=1.5) as res:
                self.is_connected = (res.status == 200)
                self._last_sent_payload = json_str
                self._last_send_time = now
                return True
        except Exception:
            self.is_connected = False
            return False
