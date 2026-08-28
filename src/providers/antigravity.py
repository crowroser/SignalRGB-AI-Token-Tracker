import os
import glob
import json
import time
from datetime import datetime, timezone
from .base import BaseProvider, UsageSnapshot

class AntigravityProvider(BaseProvider):
    def __init__(self):
        super().__init__("Antigravity")
        self.user_profile = os.environ.get("USERPROFILE", "")
        self.cli_brain_path = os.path.join(self.user_profile, ".gemini", "antigravity-cli", "brain")
        self.ide_dbs_path = os.path.join(self.user_profile, ".gemini", "antigravity-ide", "conversations")
        self.core_dbs_path = os.path.join(self.user_profile, ".gemini", "antigravity", "conversations")
        self._last_active_threshold_sec = 6.0

    def is_available(self) -> bool:
        return (
            os.path.exists(self.cli_brain_path) or
            os.path.exists(self.ide_dbs_path) or
            os.path.exists(self.core_dbs_path)
        )

    def scan(self) -> UsageSnapshot:
        snapshot = UsageSnapshot(provider_name="Antigravity")
        now = time.time()
        today_date_str = datetime.now().strftime("%Y-%m-%d")

        # 1. Scan Antigravity CLI Transcripts
        transcript_pattern = os.path.join(
            self.cli_brain_path, "*", ".system_generated", "logs", "transcript*.jsonl"
        )
        transcript_files = glob.glob(transcript_pattern)

        latest_mtime = 0.0
        daily_chars = 0
        five_hour_chars = 0
        five_hour_cutoff = now - (5 * 3600)

        for file_path in transcript_files:
            try:
                mtime = os.path.getmtime(file_path)
                if mtime > latest_mtime:
                    latest_mtime = mtime

                # Skip files older than 24 hours for daily tally
                if (now - mtime) > 86400 * 2:
                    continue

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            item = json.loads(line)
                            created_at_str = item.get("created_at", "")
                            # Check if today
                            if today_date_str in created_at_str:
                                # Estimate token usage from text fields
                                text_len = 0
                                if "content" in item and item["content"]:
                                    text_len += len(str(item["content"]))
                                if "thinking" in item and item["thinking"]:
                                    text_len += len(str(item["thinking"]))
                                if "tool_calls" in item and item["tool_calls"]:
                                    text_len += len(str(item["tool_calls"]))
                                
                                daily_chars += text_len
                                if mtime >= five_hour_cutoff:
                                    five_hour_chars += text_len
                        except Exception:
                            continue
            except Exception:
                continue

        # Convert characters to tokens (approx 4 chars per token)
        snapshot.daily_tokens = max(1, daily_chars // 4)
        snapshot.five_hour_tokens = max(1, five_hour_chars // 4)
        snapshot.last_activity_time = latest_mtime

        # Active generation detection
        if (now - latest_mtime) <= self._last_active_threshold_sec:
            snapshot.is_active_now = True

        # Compute 5h block percent based on typical quota (e.g. 1,000,000 tokens / 5h limit)
        quota_5h = 1_000_000
        snapshot.five_hour_percent = min(100.0, (snapshot.five_hour_tokens / quota_5h) * 100.0)
        snapshot.model_name = "Gemini / Claude Pro"

        return snapshot
