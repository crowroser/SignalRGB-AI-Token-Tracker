import time
import sys
import os
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
