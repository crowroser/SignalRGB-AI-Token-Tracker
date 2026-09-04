import time
import sys
import os

class NullWriter:
    def write(self, *args, **kwargs): pass
    def flush(self): pass

if sys.stdout is None:
    sys.stdout = NullWriter()
elif hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if sys.stderr is None:
    sys.stderr = NullWriter()
elif hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from .config import Config
from .scanner import TokenScanner
from .signalrgb_client import SignalRGBClient

def print_banner():
    print("=" * 65)
    print("  🟢 SignalRGB AI Token Tracker Bridge")
    print("  💡 Real-time RGB LED Visualizer for AI Coding & LLM Tokens")
    print("=" * 65)

def main():
    print_banner()
    config = Config()
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
                
                model_str = f" ({metrics['model']})" if metrics.get("model") else ""
                extra = metrics.get("extra", {})
                dual_str = ""
                if extra and "gemini" in extra and "claude" in extra:
                    is_rem = config.mode == "remaining"
                    g_val = extra["gemini"].get("remaining_percent", 0.0) if is_rem else extra["gemini"].get("5h_percent", 0.0)
                    c_val = extra["claude"].get("remaining_percent", 0.0) if is_rem else extra["claude"].get("5h_percent", 0.0)
                    suffix = "%rem" if is_rem else "%used"
                    dual_str = f" [Gem:{g_val:.0f}{suffix} Cld:{c_val:.0f}{suffix}]"

                sys.stdout.write(
                    f"\r\033[K[{conn_badge}] {gen_badge} "
                    f"Quota: {pct:>5.1f}%{dual_str} | Today: {daily:>8,} tok | Active: {metrics['provider']}{model_str}"
                )
                sys.stdout.flush()
                last_print = now

            time.sleep(config.poll_interval_seconds)
    except KeyboardInterrupt:
        print("\n\n[🛑 Stopped] Exiting AI Token Tracker bridge. Goodbye!")

if __name__ == "__main__":
    main()
