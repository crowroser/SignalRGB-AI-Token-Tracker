import os
import json

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
    def __init__(self, config_path: str = "config.json"):
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
