from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

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
