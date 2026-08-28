import os
import glob
import json
import time
from datetime import datetime
from .base import BaseProvider, UsageSnapshot

class CodexProvider(BaseProvider):
    def __init__(self):
        super().__init__("Codex")
        self.user_profile = os.environ.get("USERPROFILE", "")
        self.sessions_dir = os.path.join(self.user_profile, ".codex", "sessions")
        self._last_active_threshold_sec = 6.0

    def is_available(self) -> bool:
        return os.path.exists(self.sessions_dir)

    def scan(self) -> UsageSnapshot:
        snapshot = UsageSnapshot(provider_name="Codex")
        if not self.is_available():
            return snapshot

        now = time.time()
        today_str = datetime.now().strftime("%Y-%m-%d")
        five_hour_cutoff = now - (5 * 3600)

        jsonl_files = glob.glob(os.path.join(self.sessions_dir, "**", "*.jsonl"), recursive=True)
        latest_mtime = 0.0

        for file_path in jsonl_files:
            try:
                mtime = os.path.getmtime(file_path)
                if mtime > latest_mtime:
                    latest_mtime = mtime

                if (now - mtime) > 86400 * 3:
                    continue

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            item = json.loads(line)
                            # Match token_count events or turn objects
                            if item.get("type") == "token_count" or "tokens" in item or "usage" in item:
                                usage = item.get("usage") or item.get("tokens") or {}
                                inp = usage.get("input_tokens") or usage.get("prompt_tokens", 0) or 0
                                out = usage.get("output_tokens") or usage.get("completion_tokens", 0) or 0
                                tot = inp + out or item.get("total_tokens", 0)

                                created_at = item.get("timestamp") or item.get("created_at", "")
                                if today_str in str(created_at) or (not created_at and mtime >= (now - 86400)):
                                    snapshot.daily_tokens += tot
                                    snapshot.input_tokens += inp
                                    snapshot.output_tokens += out

                                if mtime >= five_hour_cutoff:
                                    snapshot.five_hour_tokens += tot
                        except Exception:
                            continue
            except Exception:
                continue

        snapshot.last_activity_time = latest_mtime
        if (now - latest_mtime) <= self._last_active_threshold_sec:
            snapshot.is_active_now = True

        snapshot.model_name = "o3 / GPT-4o"
        return snapshot
