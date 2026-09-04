import os
import glob
import json
import time
import re
from datetime import datetime, timezone
from .base import BaseProvider, UsageSnapshot

class AntigravityProvider(BaseProvider):
    MODEL_PATTERN = re.compile(
        r"Model Selection[`'\"']?\s+from\s+[^`\n\r]+?\s+to\s+[`'\"']?([^`\n\r<]+)",
        re.I
    )

    def __init__(self, gemini_quota_5h: int = 1_150_000, claude_quota_5h: int = 70_000, mode: str = "remaining"):
        super().__init__("Antigravity")
        self.user_profile = os.environ.get("USERPROFILE", "")
        self.cli_brain_path = os.path.join(self.user_profile, ".gemini", "antigravity-cli", "brain")
        self.ide_dbs_path = os.path.join(self.user_profile, ".gemini", "antigravity-ide", "conversations")
        self.core_dbs_path = os.path.join(self.user_profile, ".gemini", "antigravity", "conversations")
        self._last_active_threshold_sec = 6.0
        self.gemini_quota_5h = gemini_quota_5h
        self.claude_quota_5h = claude_quota_5h
        self.mode = mode

    @staticmethod
    def _classify_model_family(model_name: str) -> str:
        low = model_name.lower()
        if any(k in low for k in ["claude", "opus", "sonnet", "haiku", "anthropic", "gpt", "o1", "o3"]):
            return "Claude"
        return "Gemini"

    @staticmethod
    def _clean_model_name(raw: str) -> str:
        clean = re.split(r"(?:\.\s+|\s+No need|\s+Please|\s+Do not|<|`|\.\.\.)", raw, flags=re.I)[0].strip()
        clean = clean.strip("`'\" .")
        if not clean or clean == "..." or len(clean) < 3 or not re.search(r"[a-zA-Z]", clean):
            return ""
        return clean

    def is_available(self) -> bool:
        return (
            os.path.exists(self.cli_brain_path) or
            os.path.exists(self.ide_dbs_path) or
            os.path.exists(self.core_dbs_path)
        )

    def scan(self) -> UsageSnapshot:
        snapshot = UsageSnapshot(provider_name="Antigravity")
        now = time.time()
        today_local_str = datetime.now().strftime("%Y-%m-%d")
        today_utc_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        five_hour_cutoff = now - (5 * 3600)

        # 1. Scan Antigravity CLI Transcripts (use transcript_full to avoid double counting with transcript.jsonl)
        transcript_pattern = os.path.join(
            self.cli_brain_path, "*", ".system_generated", "logs", "transcript_full.jsonl"
        )
        transcript_files = glob.glob(transcript_pattern)
        if not transcript_files:
            transcript_files = glob.glob(
                os.path.join(self.cli_brain_path, "*", ".system_generated", "logs", "transcript.jsonl")
            )

        latest_mtime = 0.0
        latest_model_switch_iso = ""
        latest_model_switch_time = 0.0
        latest_active_model = "Gemini Flash / Pro"

        gemini_daily_chars = 0
        gemini_5h_chars = 0
        claude_daily_chars = 0
        claude_5h_chars = 0

        for file_path in transcript_files:
            try:
                mtime = os.path.getmtime(file_path)
                if mtime > latest_mtime:
                    latest_mtime = mtime

                # Skip files older than 48 hours
                if (now - mtime) > 86400 * 2:
                    continue

                current_file_model = "Gemini Flash / Pro"

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        # Check for authentic model switch event inside system metadata
                        if "<ADDITIONAL_METADATA>" in line and "Model Selection" in line:
                            match = self.MODEL_PATTERN.search(line)
                            if match:
                                raw_model = match.group(1).strip()
                                clean_name = self._clean_model_name(raw_model)
                                if clean_name:
                                    current_file_model = clean_name
                                    try:
                                        item_tmp = json.loads(line)
                                        iso = item_tmp.get("created_at", "")
                                    except Exception:
                                        iso = ""
                                    if iso and iso > latest_model_switch_iso:
                                        latest_model_switch_iso = iso
                                        latest_active_model = clean_name
                                    elif not latest_model_switch_iso and mtime >= latest_model_switch_time:
                                        latest_model_switch_time = mtime
                                        latest_active_model = clean_name

                        try:
                            item = json.loads(line)
                            created_at_str = item.get("created_at", "")
                            if not created_at_str:
                                continue

                            try:
                                item_ts = datetime.fromisoformat(created_at_str).timestamp()
                            except Exception:
                                item_ts = mtime

                            text_len = 0
                            if "content" in item and item["content"]:
                                text_len += len(str(item["content"]))
                            if "thinking" in item and item["thinking"]:
                                text_len += len(str(item["thinking"]))
                            if "tool_calls" in item and item["tool_calls"]:
                                text_len += len(str(item["tool_calls"]))

                            if text_len > 0:
                                fam = self._classify_model_family(current_file_model)

                                # 5-hour rolling sliding window (independent of calendar day)
                                if item_ts >= five_hour_cutoff:
                                    if fam == "Claude":
                                        claude_5h_chars += text_len
                                    else:
                                        gemini_5h_chars += text_len

                                # Daily tokens (matches local today or UTC today)
                                if today_local_str in created_at_str or today_utc_str in created_at_str:
                                    if fam == "Claude":
                                        claude_daily_chars += text_len
                                    else:
                                        gemini_daily_chars += text_len
                        except Exception:
                            continue
            except Exception:
                continue

        # Convert characters to tokens (approx 4 chars per token)
        gemini_daily_tokens = max(0, gemini_daily_chars // 4)
        gemini_5h_tokens = max(0, gemini_5h_chars // 4)
        claude_daily_tokens = max(0, claude_daily_chars // 4)
        claude_5h_tokens = max(0, claude_5h_chars // 4)

        active_family = self._classify_model_family(latest_active_model)

        gemini_percent_5h = min(100.0, (gemini_5h_tokens / self.gemini_quota_5h) * 100.0)
        claude_percent_5h = min(100.0, (claude_5h_tokens / self.claude_quota_5h) * 100.0)

        gemini_rem_pct = max(0.0, 100.0 - gemini_percent_5h)
        claude_rem_pct = max(0.0, 100.0 - claude_percent_5h)

        snapshot.daily_tokens = gemini_daily_tokens + claude_daily_tokens
        snapshot.five_hour_tokens = claude_5h_tokens if active_family == "Claude" else gemini_5h_tokens
        
        # In remaining mode, five_hour_percent represents the active model's remaining quota percentage
        if self.mode == "remaining":
            snapshot.five_hour_percent = round(claude_rem_pct if active_family == "Claude" else gemini_rem_pct, 1)
        else:
            snapshot.five_hour_percent = round(claude_percent_5h if active_family == "Claude" else gemini_percent_5h, 1)

        snapshot.last_activity_time = latest_mtime
        snapshot.model_name = latest_active_model

        # Active generation detection
        if (now - latest_mtime) <= self._last_active_threshold_sec:
            snapshot.is_active_now = True

        # Attach rich dual model telemetry to snapshot.extra
        snapshot.extra = {
            "mode": self.mode,
            "active_family": active_family,
            "active_model": latest_active_model,
            "gemini": {
                "daily_tokens": gemini_daily_tokens,
                "5h_tokens": gemini_5h_tokens,
                "5h_quota": self.gemini_quota_5h,
                "5h_percent": round(gemini_percent_5h, 1),
                "remaining_percent": round(gemini_rem_pct, 1),
                "percent_5h": round(gemini_percent_5h, 1),
            },
            "claude": {
                "daily_tokens": claude_daily_tokens,
                "5h_tokens": claude_5h_tokens,
                "5h_quota": self.claude_quota_5h,
                "5h_percent": round(claude_percent_5h, 1),
                "remaining_percent": round(claude_rem_pct, 1),
                "percent_5h": round(claude_percent_5h, 1),
            }
        }

        return snapshot
