import os
import glob
import json
import time
from datetime import datetime
from .base import BaseProvider, UsageSnapshot

class ClaudeCodeProvider(BaseProvider):
    def __init__(self):
        super().__init__("Claude Code")
        self.user_profile = os.environ.get("USERPROFILE", "")
        self.projects_dir = os.path.join(self.user_profile, ".claude", "projects")
        self._last_active_threshold_sec = 6.0

    def is_available(self) -> bool:
        return os.path.exists(self.projects_dir)

    def scan(self) -> UsageSnapshot:
        snapshot = UsageSnapshot(provider_name="Claude Code")
        if not self.is_available():
            return snapshot

        now = time.time()
        today_str = datetime.now().strftime("%Y-%m-%d")
        five_hour_cutoff = now - (5 * 3600)

        jsonl_files = glob.glob(os.path.join(self.projects_dir, "**", "*.jsonl"), recursive=True)
        latest_mtime = 0.0
        seen_messages = set()

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
                            msg_id = item.get("id") or item.get("message_id")
                            if msg_id:
                                if msg_id in seen_messages:
                                    continue
                                seen_messages.add(msg_id)

                            usage = item.get("usage")
                            created_at = item.get("timestamp") or item.get("created_at", "")
                            
                            if usage and isinstance(usage, dict):
                                inp = usage.get("input_tokens", 0) or 0
                                out = usage.get("output_tokens", 0) or 0
                                cache_read = usage.get("cache_read_input_tokens", 0) or 0
                                cache_create = usage.get("cache_creation_input_tokens", 0) or 0
                                tot = inp + out + cache_read + cache_create

                                if today_str in str(created_at) or (not created_at and mtime >= (now - 86400)):
                                    snapshot.daily_tokens += tot
                                    snapshot.input_tokens += inp
                                    snapshot.output_tokens += out
                                    snapshot.cache_tokens += (cache_read + cache_create)

                                if mtime >= five_hour_cutoff:
                                    snapshot.five_hour_tokens += tot
                        except Exception:
                            continue
            except Exception:
                continue

        snapshot.last_activity_time = latest_mtime
        if (now - latest_mtime) <= self._last_active_threshold_sec:
            snapshot.is_active_now = True

        snapshot.model_name = "Claude 3.7 Sonnet / Opus"
        return snapshot
