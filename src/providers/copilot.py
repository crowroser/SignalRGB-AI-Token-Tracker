import os
import sqlite3
import time
from datetime import datetime
from .base import BaseProvider, UsageSnapshot

class CopilotCliProvider(BaseProvider):
    def __init__(self):
        super().__init__("Copilot CLI")
        self.user_profile = os.environ.get("USERPROFILE", "")
        self.db_path = os.path.join(self.user_profile, ".copilot", "session-store.db")
        self._last_active_threshold_sec = 6.0

    def is_available(self) -> bool:
        return os.path.exists(self.db_path)

    def scan(self) -> UsageSnapshot:
        snapshot = UsageSnapshot(provider_name="Copilot CLI")
        if not self.is_available():
            return snapshot

        now = time.time()
        today_str = datetime.now().strftime("%Y-%m-%d")

        try:
            mtime = os.path.getmtime(self.db_path)
            snapshot.last_activity_time = mtime
            if (now - mtime) <= self._last_active_threshold_sec:
                snapshot.is_active_now = True

            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            cur = conn.cursor()
            # Check if assistant_usage_events table exists
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assistant_usage_events'")
            if cur.fetchone():
                cur.execute("SELECT input_tokens, output_tokens, created_at FROM assistant_usage_events")
                for inp, out, created_at in cur.fetchall():
                    tot = (inp or 0) + (out or 0)
                    if today_str in str(created_at):
                        snapshot.daily_tokens += tot
                        snapshot.input_tokens += (inp or 0)
                        snapshot.output_tokens += (out or 0)
            conn.close()
            snapshot.model_name = "GitHub Copilot"
        except Exception:
            pass

        return snapshot
