import os
import sqlite3
import time
from datetime import datetime
from .base import BaseProvider, UsageSnapshot

class HermesProvider(BaseProvider):
    def __init__(self):
        super().__init__("Hermes Agent")
        self.user_profile = os.environ.get("USERPROFILE", "")
        self.db_path = os.path.join(self.user_profile, ".hermes", "state.db")
        self._last_active_threshold_sec = 6.0

    def is_available(self) -> bool:
        return os.path.exists(self.db_path)

    def scan(self) -> UsageSnapshot:
        snapshot = UsageSnapshot(provider_name="Hermes Agent")
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
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='sessions' OR name='messages')")
            tables = [r[0] for r in cur.fetchall()]

            if "sessions" in tables:
                cur.execute("SELECT total_tokens, updated_at FROM sessions")
                for tokens, updated_at in cur.fetchall():
                    if today_str in str(updated_at):
                        snapshot.daily_tokens += (tokens or 0)
            conn.close()
            snapshot.model_name = "Hermes 3"
        except Exception:
            pass

        return snapshot
