import os
import glob
import json
import time
from datetime import datetime
from .base import BaseProvider, UsageSnapshot

class PiAgentProvider(BaseProvider):
    def __init__(self):
        super().__init__("Pi Agent")
        self.user_profile = os.environ.get("USERPROFILE", "")
        self.sessions_dir = os.path.join(self.user_profile, ".pi", "agent", "sessions")
        self._last_active_threshold_sec = 6.0

    def is_available(self) -> bool:
        return os.path.exists(self.sessions_dir)

    def scan(self) -> UsageSnapshot:
        snapshot = UsageSnapshot(provider_name="Pi Agent")
        if not self.is_available():
            return snapshot

        now = time.time()
        today_str = datetime.now().strftime("%Y-%m-%d")

        session_files = glob.glob(os.path.join(self.sessions_dir, "**", "*.jsonl"), recursive=True)
        latest_mtime = 0.0

        for file_path in session_files:
            try:
                mtime = os.path.getmtime(file_path)
                if mtime > latest_mtime:
                    latest_mtime = mtime

                if (now - mtime) > 86400 * 2:
                    continue

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            item = json.loads(line)
                            usage = item.get("usage") or {}
                            inp = usage.get("input_tokens", 0) or 0
                            out = usage.get("output_tokens", 0) or 0
                            tot = inp + out
                            if today_str in str(item.get("timestamp", "")):
                                snapshot.daily_tokens += tot
                                snapshot.input_tokens += inp
                                snapshot.output_tokens += out
                        except Exception:
                            continue
            except Exception:
                continue

        snapshot.last_activity_time = latest_mtime
        if (now - latest_mtime) <= self._last_active_threshold_sec:
            snapshot.is_active_now = True

        snapshot.model_name = "Pi Agent"
        return snapshot
