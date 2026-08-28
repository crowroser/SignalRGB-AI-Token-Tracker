import os
import glob
import json
import time
from datetime import datetime
from .base import BaseProvider, UsageSnapshot

class GeminiCliProvider(BaseProvider):
    def __init__(self):
        super().__init__("Gemini CLI")
        self.user_profile = os.environ.get("USERPROFILE", "")
        self.tmp_dir = os.path.join(self.user_profile, ".gemini", "tmp")
        self._last_active_threshold_sec = 6.0

    def is_available(self) -> bool:
        return os.path.exists(self.tmp_dir)

    def scan(self) -> UsageSnapshot:
        snapshot = UsageSnapshot(provider_name="Gemini CLI")
        if not self.is_available():
            return snapshot

        now = time.time()
        today_str = datetime.now().strftime("%Y-%m-%d")
        chat_files = glob.glob(os.path.join(self.tmp_dir, "**", "chats", "*.json*"), recursive=True)
        latest_mtime = 0.0

        for file_path in chat_files:
            try:
                mtime = os.path.getmtime(file_path)
                if mtime > latest_mtime:
                    latest_mtime = mtime

                if (now - mtime) > 86400 * 2:
                    continue

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    # If JSON or JSONL
                    lines = content.strip().split("\n")
                    for line in lines:
                        if not line.strip():
                            continue
                        try:
                            item = json.loads(line)
                            usage = item.get("usageMetadata") or item.get("usage") or {}
                            inp = usage.get("promptTokenCount", 0) or usage.get("prompt_tokens", 0)
                            out = usage.get("candidatesTokenCount", 0) or usage.get("completion_tokens", 0)
                            tot = usage.get("totalTokenCount", 0) or (inp + out)
                            if tot == 0:
                                # Estimate from text length
                                text = str(item.get("parts") or item.get("content") or "")
                                tot = max(1, len(text) // 4)

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

        snapshot.model_name = "Gemini 2.5 Flash / Pro"
        return snapshot
