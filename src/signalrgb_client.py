import urllib.request
import urllib.parse
import json
import time
import os
import re
import shutil
import tempfile

class SignalRGBClient:
    """Bridges token data into SignalRGB via two methods:
    1. Direct HTML state injection (Free + Pro) — rewrites the state defaults
       inside the effect HTML so SignalRGB picks them up on every render reload.
    2. Canvas API POST (Pro only) — sends events to onCanvasApiEvent.
    Both methods run in parallel; whichever one works, works.
    """

    def __init__(self, host: str = "localhost", port: int = 16034, sender: str = "aitoken"):
        self.host = host
        self.port = port
        self.sender = sender
        self.base_url = f"http://{self.host}:{self.port}/canvas/event"
        self._last_sent_payload = None
        self._last_send_time = 0.0
        self.is_connected = False

        # HTML injection path — the installed effect file
        user_profile = os.environ.get("USERPROFILE", "")
        self.effect_html_path = os.path.join(
            user_profile, "Documents", "WhirlwindFX", "Effects",
            "AI Token Tracker", "AI Token Tracker.html"
        )
        self._last_injected_state = None
        self._last_inject_time = 0.0
        # Minimum interval between HTML rewrites (seconds) to avoid thrashing
        self._inject_interval = 2.0

    def send_event(self, data: dict) -> bool:
        """Sends token data to SignalRGB via both HTML injection and Canvas API."""
        now = time.time()

        # 1. Always inject into the HTML file (works with Free edition)
        self._inject_state_into_html(data, now)

        # 2. Also try Canvas API POST (works only with Pro)
        self._send_canvas_api(data, now)

        return True

    def _inject_state_into_html(self, data: dict, now: float):
        """Atomically rewrites the state defaults in the effect HTML."""
        if not os.path.exists(self.effect_html_path):
            return

        # Throttle writes
        if (now - self._last_inject_time) < self._inject_interval:
            return

        pct = data.get("percentage", 100)
        used = data.get("used_tokens", 0)
        remaining = data.get("remaining_tokens", 0)
        daily = data.get("daily_tokens", 0)
        is_gen = "true" if data.get("is_generating", False) else "false"
        tps = data.get("tokens_per_sec", 0)
        provider = data.get("provider", "")
        model = data.get("model", "")

        new_state_block = (
            f'  // Live State from Python Bridge or Test Mode\n'
            f'  let state = {{\n'
            f'    percentage: {pct},\n'
            f'    used_tokens: {used},\n'
            f'    remaining_tokens: {remaining},\n'
            f'    daily_tokens: {daily},\n'
            f'    is_generating: {is_gen},\n'
            f'    tokens_per_sec: {tps},\n'
            f'    provider: "{provider}",\n'
            f'    model: "{model}",\n'
            f'    last_update_time: Date.now()\n'
            f'  }};\n'
            f'\n'
            f'  let currentPercentage = {pct};'
        )

        # Check if identical to last write
        if new_state_block == self._last_injected_state:
            return

        try:
            with open(self.effect_html_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Replace the state block using regex
            pattern = (
                r'  // Live State from Python Bridge or Test Mode\n'
                r'  let state = \{[^}]+\};\n'
                r'\n'
                r'  let currentPercentage = [^;]+;'
            )
            replacement = new_state_block

            new_content, count = re.subn(pattern, replacement, content)
            if count == 0:
                return  # Pattern not found, skip

            # Atomic write: write to temp file then rename
            dir_name = os.path.dirname(self.effect_html_path)
            fd, tmp_path = tempfile.mkstemp(suffix=".html", dir=dir_name)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as tmp_f:
                    tmp_f.write(new_content)
                # On Windows, need to remove target first
                if os.path.exists(self.effect_html_path):
                    os.replace(tmp_path, self.effect_html_path)
                else:
                    shutil.move(tmp_path, self.effect_html_path)
            except Exception:
                # Clean up temp file on failure
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                raise

            self._last_injected_state = new_state_block
            self._last_inject_time = now
            self.is_connected = True
        except Exception:
            pass

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
