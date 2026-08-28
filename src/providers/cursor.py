import os
import sqlite3
import json
import time
from datetime import datetime
from .base import BaseProvider, UsageSnapshot

class CursorProvider(BaseProvider):
    def __init__(self):
        super().__init__("Cursor")
        appdata = os.environ.get("APPDATA", "")
        self.db_path = os.path.join(appdata, "Cursor", "User", "globalStorage", "state.vscdb")
        self._last_active_threshold_sec = 6.0

    def is_available(self) -> bool:
        return os.path.exists(self.db_path)

    def scan(self) -> UsageSnapshot:
        snapshot = UsageSnapshot(provider_name="Cursor")
        if not self.is_available():
            return snapshot

        now = time.time()
        today_str = datetime.now().strftime("%Y-%m-%d")
        five_hour_cutoff = now - (5 * 3600)

        try:
            mtime = os.path.getmtime(self.db_path)
            snapshot.last_activity_time = mtime
            if (now - mtime) <= self._last_active_threshold_sec:
                snapshot.is_active_now = True

            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            cur = conn.cursor()
            cur.execute("SELECT value FROM cursorDiskKV WHERE key LIKE 'bubbleId:%'")
            
            total_input = 0
            total_output = 0
            five_h_tokens = 0
            latest_model = ""

            for (val_str,) in cur.fetchall():
                if not val_str:
                    continue
                try:
                    data = json.loads(val_str)
                    token_count = data.get("tokenCount")
                    created_at = data.get("createdAt", "")
                    
                    if data.get("modelInfo") and isinstance(data["modelInfo"], dict):
                        latest_model = data["modelInfo"].get("modelName", latest_model)

                    if token_count and isinstance(token_count, dict):
                        inp = token_count.get("inputTokens", 0) or 0
                        out = token_count.get("outputTokens", 0) or 0
                        tot = inp + out
                        
                        if today_str in created_at:
                            total_input += inp
                            total_output += out
                            
                        # Check 5h window if parseable timestamp
                        if created_at:
                            try:
                                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                                if dt.timestamp() >= five_hour_cutoff:
                                    five_h_tokens += tot
                            except Exception:
                                pass
                except Exception:
                    continue

            conn.close()

            snapshot.input_tokens = total_input
            snapshot.output_tokens = total_output
            snapshot.daily_tokens = total_input + total_output
            snapshot.five_hour_tokens = five_h_tokens
            snapshot.model_name = latest_model or "Claude 3.5 Sonnet / GPT-4o"
        except Exception:
            pass

        return snapshot
