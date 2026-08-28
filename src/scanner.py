import time
from typing import List, Dict
from .providers import (
    AntigravityProvider,
    ClaudeCodeProvider,
    CodexProvider,
    CursorProvider,
    GeminiCliProvider,
    CopilotCliProvider,
    GrokCliProvider,
    PiAgentProvider,
    HermesProvider,
    OpenRouterProvider,
    BaseProvider,
    UsageSnapshot
)
from .config import Config

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
