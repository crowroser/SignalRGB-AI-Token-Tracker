import urllib.request
import json
import time
from .base import BaseProvider, UsageSnapshot

class OpenRouterProvider(BaseProvider):
    def __init__(self, api_key: str = ""):
        super().__init__("OpenRouter")
        self.api_key = api_key
        self._last_scan_time = 0.0
        self._cached_snapshot = UsageSnapshot(provider_name="OpenRouter")

    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def scan(self) -> UsageSnapshot:
        if not self.is_available():
            return self._cached_snapshot

        # Rate limit external API checks to once every 30 seconds
        now = time.time()
        if (now - self._last_scan_time) < 30.0:
            return self._cached_snapshot

        try:
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/auth/key",
                headers={
                    "Authorization": f"Bearer {self.api_key.strip()}",
                    "User-Agent": "SignalRGB-AI-Token-Tracker/1.0"
                }
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    key_data = data.get("data", {})
                    limit = key_data.get("limit") or 0.0
                    usage = key_data.get("usage") or 0.0
                    
                    snapshot = UsageSnapshot(provider_name="OpenRouter")
                    snapshot.cost_estimate = usage
                    snapshot.last_activity_time = now
                    
                    if limit > 0:
                        remaining_percent = max(0.0, min(100.0, ((limit - usage) / limit) * 100.0))
                        snapshot.five_hour_percent = 100.0 - remaining_percent # used %
                        snapshot.extra["remaining_percent"] = remaining_percent
                        snapshot.extra["limit"] = limit
                        snapshot.extra["usage"] = usage

                    snapshot.model_name = "OpenRouter Multi-LLM"
                    self._cached_snapshot = snapshot
                    self._last_scan_time = now
        except Exception:
            pass

        return self._cached_snapshot
