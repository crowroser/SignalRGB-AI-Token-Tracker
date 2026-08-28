"""
SignalRGB AI Token Tracker - Consolidated Bridge
Monitors AI token usage from various providers and streams live data to SignalRGB.
"""

import os
import sys
import glob
import json
import time
import re
import shutil
import tempfile
import sqlite3
import urllib.request
import urllib.parse
import ctypes
import argparse
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict


# =====================================================================
# Path Utilities
# =====================================================================

def get_base_dir() -> str:
    """Get the directory containing the executable or script."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_dir() -> str:
    """Get directory containing bundled resources (PyInstaller MEIPASS or script directory)."""
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return get_base_dir()


def install_effect() -> bool:
    """Copies the effect HTML+PNG from bundled resource path to Documents/WhirlwindFX/Effects/AI Token Tracker/"""
    user_profile = os.environ.get("USERPROFILE", "")
    if not user_profile:
        user_profile = os.path.expanduser("~")

    target_dir = os.path.join(user_profile, "Documents", "WhirlwindFX", "Effects", "AI Token Tracker")
    os.makedirs(target_dir, exist_ok=True)

    res_dir = get_resource_dir()
    possible_dirs = [
        os.path.join(res_dir, "effects", "AI Token Tracker"),
        os.path.join(res_dir, "AI Token Tracker"),
        res_dir,
    ]

    src_html = None
    src_png = None
    for d in possible_dirs:
        h = os.path.join(d, "AI Token Tracker.html")
        if os.path.exists(h):
            src_html = h
            p = os.path.join(d, "AI Token Tracker.png")
            if os.path.exists(p):
                src_png = p
            break

    if not src_html:
        print(f"[❌ Error] Could not find 'AI Token Tracker.html' in resource path: {res_dir}")
        return False

    dst_html = os.path.join(target_dir, "AI Token Tracker.html")
    shutil.copy2(src_html, dst_html)
    print(f"[+] Installed effect HTML to: {dst_html}")

    if src_png:
        dst_png = os.path.join(target_dir, "AI Token Tracker.png")
        shutil.copy2(src_png, dst_png)
        print(f"[+] Installed preview image to: {dst_png}")

    print("[SUCCESS] AI Token Tracker effect installed successfully into SignalRGB!")
    return True


def hide_console():
    """Hides the console window on Windows using ctypes."""
    if sys.platform == "win32":
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)


# =====================================================================
# Data Models & Base Provider
# =====================================================================

@dataclass
class UsageSnapshot:
    provider_name: str
    daily_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_tokens: int = 0
    session_tokens: int = 0
    five_hour_tokens: int = 0
    five_hour_percent: Optional[float] = None
    is_active_now: bool = False
    last_activity_time: float = 0.0
    model_name: str = ""
    cost_estimate: float = 0.0
    extra: dict = field(default_factory=dict)


class BaseProvider:
    def __init__(self, name: str):
        self.name = name

    def is_available(self) -> bool:
        """Returns True if the provider's data files exist on this machine."""
        raise NotImplementedError

    def scan(self) -> UsageSnapshot:
        """Scans local logs and returns a UsageSnapshot."""
        raise NotImplementedError


# =====================================================================
# Providers
# =====================================================================

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


class GrokCliProvider(BaseProvider):
    def __init__(self):
        super().__init__("Grok CLI")
        self.user_profile = os.environ.get("USERPROFILE", "")
        self.sessions_dir = os.path.join(self.user_profile, ".grok", "sessions")
        self._last_active_threshold_sec = 6.0

    def is_available(self) -> bool:
        return os.path.exists(self.sessions_dir)

    def scan(self) -> UsageSnapshot:
        snapshot = UsageSnapshot(provider_name="Grok CLI")
        if not self.is_available():
            return snapshot

        now = time.time()
        today_str = datetime.now().strftime("%Y-%m-%d")

        update_files = glob.glob(os.path.join(self.sessions_dir, "**", "updates.jsonl"), recursive=True)
        latest_mtime = 0.0

        for file_path in update_files:
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

        snapshot.model_name = "Grok 3"
        return snapshot


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


# =====================================================================
# Configuration
# =====================================================================

DEFAULT_CONFIG = {
    "daily_token_budget": 500000,
    "five_hour_token_quota": 200000,
    "mode": "remaining",  # "remaining" (100% down to 0%) or "usage" (0% up to 100%)
    "poll_interval_seconds": 1.0,
    "signalrgb_host": "localhost",
    "signalrgb_port": 16034,
    "active_providers": [
        "Antigravity",
        "Claude Code",
        "Codex",
        "Cursor",
        "Gemini CLI",
        "Copilot CLI",
        "Grok CLI",
        "Pi Agent",
        "Hermes Agent",
        "OpenRouter"
    ],
    "openrouter_api_key": ""
}


class Config:
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.path.join(get_base_dir(), "config.json")
        self.config_path = config_path
        self.data = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except Exception as e:
                print(f"[Config] Error loading {self.config_path}: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"[Config] Error saving {self.config_path}: {e}")

    def __getattr__(self, item):
        return self.data.get(item)


# =====================================================================
# Token Scanner
# =====================================================================

class TokenScanner:
    def __init__(self, config: Config):
        self.config = config
        self.providers: List[BaseProvider] = [
            AntigravityProvider(),
            ClaudeCodeProvider(),
            CodexProvider(),
            CursorProvider(),
            GeminiCliProvider(),
            CopilotCliProvider(),
            GrokCliProvider(),
            PiAgentProvider(),
            HermesProvider(),
            OpenRouterProvider(api_key=config.openrouter_api_key)
        ]
        
        self.available_providers = [p for p in self.providers if p.is_available()]
        self._prev_daily_tokens = 0
        self._prev_scan_time = time.time()
        self._tokens_per_sec = 0.0

    def scan_all(self) -> Dict:
        """Runs scan on all available providers and computes aggregated metrics."""
        now = time.time()
        total_daily_tokens = 0
        total_5h_tokens = 0
        is_generating_any = False
        active_provider_name = ""
        active_model_name = ""
        provider_details = {}

        for provider in self.available_providers:
            if provider.name not in self.config.active_providers:
                continue

            try:
                snapshot: UsageSnapshot = provider.scan()
                total_daily_tokens += snapshot.daily_tokens
                total_5h_tokens += snapshot.five_hour_tokens
                
                provider_details[provider.name] = {
                    "daily": snapshot.daily_tokens,
                    "5h": snapshot.five_hour_tokens,
                    "is_active": snapshot.is_active_now,
                    "model": snapshot.model_name
                }

                if snapshot.is_active_now:
                    is_generating_any = True
                    active_provider_name = snapshot.provider_name
                    active_model_name = snapshot.model_name
            except Exception as e:
                pass

        # Calculate Tokens per second
        dt = max(0.1, now - self._prev_scan_time)
        if self._prev_daily_tokens > 0 and total_daily_tokens >= self._prev_daily_tokens:
            diff = total_daily_tokens - self._prev_daily_tokens
            if diff > 0:
                self._tokens_per_sec = round(diff / dt, 1)
            elif not is_generating_any:
                self._tokens_per_sec = 0.0
        self._prev_daily_tokens = total_daily_tokens
        self._prev_scan_time = now

        # Calculate percentage
        budget = max(1, self.config.daily_token_budget)
        used_ratio = total_daily_tokens / budget
        
        if self.config.mode == "usage":
            percentage = min(100.0, max(0.0, used_ratio * 100.0))
        else: # "remaining" mode
            remaining_ratio = max(0.0, 1.0 - used_ratio)
            percentage = min(100.0, max(0.0, remaining_ratio * 100.0))

        remaining_tokens = max(0, budget - total_daily_tokens)

        # Fallback provider display
        if not active_provider_name and self.available_providers:
            active_provider_name = self.available_providers[0].name

        return {
            "percentage": round(percentage, 1),
            "used_tokens": total_daily_tokens,
            "remaining_tokens": remaining_tokens,
            "total_tokens": budget,
            "daily_tokens": total_daily_tokens,
            "five_hour_tokens": total_5h_tokens,
            "is_generating": is_generating_any,
            "tokens_per_sec": self._tokens_per_sec,
            "provider": active_provider_name,
            "model": active_model_name,
            "providers_detected": len(self.available_providers),
            "details": provider_details
        }


# =====================================================================
# SignalRGB Client
# =====================================================================

class SignalRGBClient:
    """Bridges token data into SignalRGB via two methods:
    1. Direct HTML state injection (Free + Pro) — rewrites the state defaults
       inside the effect HTML so SignalRGB picks them up on every render reload.
    2. Canvas API POST (Pro only) — sends events to onCanvasApiEvent.
    Both methods run in parallel; whichever one works, works.
    """

    def __init__(self, host: str = "localhost", port: int = 16034, sender: str = "aitoken"):
        self.host = host
        self.port = port
        self.sender = sender
        self.base_url = f"http://{self.host}:{self.port}/canvas/event"
        self._last_sent_payload = None
        self._last_send_time = 0.0
        self.is_connected = False

        # HTML injection path — the installed effect file
        user_profile = os.environ.get("USERPROFILE", "")
        if not user_profile:
            user_profile = os.path.expanduser("~")
        self.effect_html_path = os.path.join(
            user_profile, "Documents", "WhirlwindFX", "Effects",
            "AI Token Tracker", "AI Token Tracker.html"
        )
        self._last_injected_state = None
        self._last_inject_time = 0.0
        # Minimum interval between HTML rewrites (seconds) to avoid thrashing
        self._inject_interval = 2.0

    def send_event(self, data: dict) -> bool:
        """Sends token data to SignalRGB via both HTML injection and Canvas API."""
        now = time.time()

        # 1. Always inject into the HTML file (works with Free edition)
        self._inject_state_into_html(data, now)

        # 2. Also try Canvas API POST (works only with Pro)
        self._send_canvas_api(data, now)

        return True

    def _inject_state_into_html(self, data: dict, now: float):
        """Atomically rewrites the state defaults in the effect HTML."""
        if not os.path.exists(self.effect_html_path):
            return

        # Throttle writes
        if (now - self._last_inject_time) < self._inject_interval:
            return

        pct = data.get("percentage", 100)
        used = data.get("used_tokens", 0)
        remaining = data.get("remaining_tokens", 0)
        daily = data.get("daily_tokens", 0)
        is_gen = "true" if data.get("is_generating", False) else "false"
        tps = data.get("tokens_per_sec", 0)
        provider = data.get("provider", "")
        model = data.get("model", "")

        new_state_block = (
            f'  // Live State from Python Bridge or Test Mode\n'
            f'  let state = {{\n'
            f'    percentage: {pct},\n'
            f'    used_tokens: {used},\n'
            f'    remaining_tokens: {remaining},\n'
            f'    daily_tokens: {daily},\n'
            f'    is_generating: {is_gen},\n'
            f'    tokens_per_sec: {tps},\n'
            f'    provider: "{provider}",\n'
            f'    model: "{model}",\n'
            f'    last_update_time: Date.now()\n'
            f'  }};\n'
            f'\n'
            f'  let currentPercentage = {pct};'
        )

        # Check if identical to last write
        if new_state_block == self._last_injected_state:
            return

        try:
            with open(self.effect_html_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Replace the state block using regex
            pattern = (
                r'  // Live State from Python Bridge or Test Mode\n'
                r'  let state = \{[^}]+\};\n'
                r'\n'
                r'  let currentPercentage = [^;]+;'
            )
            replacement = new_state_block

            new_content, count = re.subn(pattern, replacement, content)
            if count == 0:
                return  # Pattern not found, skip

            # Atomic write: write to temp file then rename
            dir_name = os.path.dirname(self.effect_html_path)
            fd, tmp_path = tempfile.mkstemp(suffix=".html", dir=dir_name)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as tmp_f:
                    tmp_f.write(new_content)
                # On Windows, need to remove target first
                if os.path.exists(self.effect_html_path):
                    os.replace(tmp_path, self.effect_html_path)
                else:
                    shutil.move(tmp_path, self.effect_html_path)
            except Exception:
                # Clean up temp file on failure
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                raise

            self._last_injected_state = new_state_block
            self._last_inject_time = now
            self.is_connected = True
        except Exception:
            pass

    def _send_canvas_api(self, data: dict, now: float):
        """Sends event via Canvas API POST (Pro only)."""
        json_str = json.dumps(data)

        # Deduplicate identical payloads unless >2 seconds passed
        if json_str == self._last_sent_payload and (now - self._last_send_time) < 2.0:
            return

        query = urllib.parse.urlencode({
            "sender": self.sender,
            "event": json_str
        })
        url = f"{self.base_url}?{query}"

        try:
            req = urllib.request.Request(
                url,
                data=b"",
                headers={"User-Agent": "SignalRGB-AI-Token-Tracker/1.0"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=1.5) as res:
                if res.status == 200:
                    self.is_connected = True
                self._last_sent_payload = json_str
                self._last_send_time = now
        except Exception:
            pass


# =====================================================================
# Main Application
# =====================================================================

def print_banner():
    print("=" * 65)
    print("  🟢 SignalRGB AI Token Tracker Bridge")
    print("  💡 Real-time RGB LED Visualizer for AI Coding & LLM Tokens")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="SignalRGB AI Token Tracker Bridge")
    parser.add_argument("--install", action="store_true", help="Install the SignalRGB effect files into WhirlwindFX Effects directory")
    parser.add_argument("--background", action="store_true", help="Hide console window on Windows and run in background")
    parser.add_argument("--config", type=str, default=None, help="Path to config.json file")
    args = parser.parse_args()

    if args.install:
        install_effect()
        return

    if args.background:
        hide_console()

    print_banner()
    config = Config(config_path=args.config)
    scanner = TokenScanner(config)
    client = SignalRGBClient(
        host=config.signalrgb_host,
        port=config.signalrgb_port,
        sender="aitoken"
    )

    detected = [p.name for p in scanner.available_providers]
    print(f"[🔍 Providers] Detected {len(detected)} active AI tools:")
    for name in detected:
        print(f"   • {name}")
    print("-" * 65)
    print(f"[⚙️  Config] Daily Budget: {config.daily_token_budget:,} tokens | Mode: {config.mode.upper()}")
    print(f"[📡 Target] SignalRGB: http://{config.signalrgb_host}:{config.signalrgb_port}/canvas/event")
    print("-" * 65)
    print("Running background monitor... (Press Ctrl+C to stop)\n")

    last_print = 0.0

    try:
        while True:
            metrics = scanner.scan_all()
            
            # Send payload to SignalRGB
            sent = client.send_event(metrics)

            now = time.time()
            if (now - last_print) >= 2.0 or metrics["is_generating"]:
                gen_badge = "⚡ [GENERATING]" if metrics["is_generating"] else "💤 [IDLE]"
                conn_badge = "🟢 Linked" if client.is_connected else "⚪ Waiting SignalRGB"
                
                pct = metrics["percentage"]
                daily = metrics["daily_tokens"]
                rem = metrics["remaining_tokens"]
                
                sys.stdout.write(
                    f"\r\033[K[{conn_badge}] {gen_badge} "
                    f"Quota: {pct:>5.1f}% | Today: {daily:>8,} tok | Rem: {rem:>8,} tok | Active: {metrics['provider']}"
                )
                sys.stdout.flush()
                last_print = now

            time.sleep(config.poll_interval_seconds)
    except KeyboardInterrupt:
        print("\n\n[🛑 Stopped] Exiting AI Token Tracker bridge. Goodbye!")


if __name__ == "__main__":
    main()
