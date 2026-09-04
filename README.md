# 💡 SignalRGB AI Token Tracker

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![SignalRGB Compatibility](https://img.shields.io/badge/SignalRGB-Free%20%26%20Pro-00FF66.svg)](https://signalrgb.com)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D6.svg)](https://www.microsoft.com/windows)
[![Release](https://img.shields.io/github/v/release/crowroser/SignalRGB-AI-Token-Tracker?color=purple)](https://github.com/crowroser/SignalRGB-AI-Token-Tracker/releases)

**Real-time RGB LED Visualizer for AI Coding Assistants & LLM Token Quotas in SignalRGB.**  
Brings live telemetry from **Antigravity**, **Claude Code**, **OpenAI Codex**, **Cursor**, **Gemini CLI**, **GitHub Copilot**, **Grok CLI**, and **OpenRouter** directly onto your RGB keyboard, mouse, ambient lights, and PC hardware.

[ **English** | [Türkçe](README_TR.md) ]

</div>

---

## 🌟 Overview

When coding with modern AI assistants, hitting unexpected 5-hour rate limits or exhausting daily token pools disrupts your flow. **SignalRGB AI Token Tracker** bridges local AI session telemetry directly into SignalRGB's real-time lighting engine.

- 📊 **Live Quota Visualization:** Your hardware LEDs reflect remaining token capacity (100% down to 0%) or usage (0% up to 100%).
- ⚡ **Active Generation FX:** LEDs pulse, wave, or surge in real time whenever an AI assistant is actively streaming tokens.
- ♊ **Dual-Model Intelligent Tracking:** Accurately distinguishes and tracks multiple model families simultaneously (e.g. **Gemini 3.8 Flash** vs **Claude Opus 4.6** in Antigravity) with dedicated 5-hour rolling quotas.
- 🔓 **100% SignalRGB Free & Pro Compatible:** Works natively on free versions of SignalRGB through an embedded zero-latency local HTTP bridge, with seamless fallback to the Canvas API on SignalRGB Pro.
- 🎛️ **Full GUI Customization:** Adjust colors, bar orientations, warning flashes, smoothing, and animation styles directly within SignalRGB's effect settings panel.

---

## 📸 Effect Showcase & Visual Modes

The included SignalRGB effect offers 6 distinct visual modes:

| Visual Mode | Description |
| :--- | :--- |
| **Progress Bar** | Clean linear progress bar moving across your LEDs indicating current quota. |
| **Solid Gradient** | Entire device glows smoothly in gradient colors transitioning from Full to Depleted. |
| **Active Pulse** | Ambient breathing illumination that accelerates during code generation. |
| **Matrix Wave** | Cyberpunk matrix wave effect scanning across hardware. |
| **Circular Gauge** | Radial meter lighting suitable for AIO coolers, fans, and circular LED rings. |
| **Split Zones** | **Dual Model Split:** Left half shows Gemini quota; Right half shows Claude/GPT quota. |

---

## 🤖 Supported AI Providers

The tracker automatically detects local log files and telemetry without needing manual configuration:

| Provider | Telemetry Source | Tracking Metrics |
| :--- | :--- | :--- |
| **Antigravity (CLI & IDE)** | `~/.gemini/antigravity-cli/brain/` | Multi-model family detection, sliding 5-hour quota, active generation detection. |
| **Claude Code** | `~/.claude/projects/` | Daily token usage, session duration, and active writing state. |
| **OpenAI Codex** | `~/.codex/sessions/` | Token event streams and live code generation status. |
| **Cursor IDE** | `%APPDATA%\Cursor\User\workspaceStorage` | Aggregated prompt & completion token consumption from SQLite state databases. |
| **Gemini CLI** | `~/.gemini/tmp/` | Session usage and live prompt metrics. |
| **GitHub Copilot CLI** | `~/.copilot/session-store.db` | Local interaction logs and token history. |
| **Grok CLI** | `~/.grok/logs/` | Daily token calculations and generation states. |
| **Pi Agent / Hermes 3** | `~/.pi/sessions/` & `~/.hermes/` | Session token counts and activity states. |
| **OpenRouter API** | `openrouter.ai/api/v1/auth/key` | Real-time balance and usage tracking across hundreds of open/proprietary LLMs. |

---

## ⚡ Quick Start

### Option 1: Standalone Installer (Recommended)

1. Download `AITokenTracker-windows.zip` from the latest [Releases](https://github.com/crowroser/SignalRGB-AI-Token-Tracker/releases).
2. Extract the archive and double-click `setup.bat`.
3. The installer will:
   - Install the SignalRGB effect into `Documents\WhirlwindFX\Effects\AI Token Tracker\`.
   - Configure background execution.
   - Start the bridge immediately.
4. Open **SignalRGB**, navigate to **Lighting / Effects**, and select **AI Token Tracker**.

### Option 2: Run from Source (Python 3.9+)

No heavy external dependencies required! The bridge runs on standard Python libraries.

```powershell
# 1. Clone the repository
git clone https://github.com/crowroser/SignalRGB-AI-Token-Tracker.git
cd SignalRGB-AI-Token-Tracker

# 2. Install the SignalRGB effect
python bridge.py --install

# 3. Start the live monitor
.\start.bat
```

> **Background Mode:** To launch silently without keeping a terminal open (e.g. from a SignalRGB macro or Windows Startup), run `.\start_background.bat`.

---

## ⚙️ Configuration (`config.json`)

Customize quotas, modes, and active providers in `config.json`:

```json
{
  "daily_token_budget": 1000000,
  "five_hour_token_quota": 300000,
  "gemini_5h_quota": 1150000,
  "claude_5h_quota": 70000,
  "mode": "remaining",
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
```

### Configuration Options:
- **`mode`**: `"remaining"` (counts down from 100% to 0%) or `"usage"` (fills up from 0% to 100%).
- **`gemini_5h_quota`**: 5-hour rolling token capacity for Gemini models (Default: `1,150,000`).
- **`claude_5h_quota`**: 5-hour rolling token capacity for Claude/GPT models (Default: `70,000` calibrated for Opus/Sonnet thinking tokens).
- **`active_providers`**: List of enabled providers to scan.
- **`openrouter_api_key`**: Optional OpenRouter API key for live credit tracking.

---

## 🧩 Architecture

```mermaid
flowchart LR
    subgraph AI["AI Coding Tools"]
        AG["Antigravity / Orca"]
        CC["Claude Code"]
        CX["Cursor / Codex"]
        OR["OpenRouter API"]
    end

    subgraph Bridge["AI Token Tracker Bridge (Python)"]
        Scanner["Multi-Provider Scanner"]
        Calc["Sliding 5h Quota & Model Classifier"]
        HttpServer["Local HTTP API (:16035)"]
        CanvasClient["Canvas API Client (:16034)"]
    end

    subgraph SignalRGB["SignalRGB Engine (Free & Pro)"]
        HTML["AI Token Tracker.html (Ultralight WebKit)"]
        LEDs["Hardware Canvas: Keyboard / Mouse / RAM / Fans"]
    end

    AI -->|Local Logs & DBs| Scanner
    Scanner --> Calc
    Calc --> HttpServer
    Calc --> CanvasClient

    HttpServer -->|Polling HTTP GET /api/tokens| HTML
    CanvasClient -.->|Canvas API POST (Pro)| HTML
    HTML -->|Live RGB Lighting| LEDs
```

---

## 🛠️ CLI Arguments

```text
AITokenTracker.exe [options]  (or python bridge.py [options])

Options:
  --install       Installs effect files into WhirlwindFX Effects directory
  --background    Hides console window and runs silently in background
  --config PATH   Specifies custom config.json path
  -h, --help      Displays help information
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to open an issue or submit a pull request:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add support for XYZ assistant'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">
Created with ❤️ by <a href="https://github.com/crowroser">crowroser (Fatih Gülcü)</a>
</div>
