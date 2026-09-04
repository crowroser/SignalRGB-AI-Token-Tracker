# 💡 SignalRGB AI Token Tracker

<div align="center">

[![License: MIT](https://img.shields.io/badge/Lisans-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![SignalRGB Uyumluluğu](https://img.shields.io/badge/SignalRGB-Free%20%26%20Pro-00FF66.svg)](https://signalrgb.com)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D6.svg)](https://www.microsoft.com/windows)
[![Sürüm](https://img.shields.io/github/v/release/crowroser/SignalRGB-AI-Token-Tracker?color=purple)](https://github.com/crowroser/SignalRGB-AI-Token-Tracker/releases)

**Yapay Zeka Kodlama Asistanları ve LLM Token Kotaları için Gerçek Zamanlı RGB LED Görselleştirici.**  
**Antigravity**, **Claude Code**, **OpenAI Codex**, **Cursor**, **Gemini CLI**, **GitHub Copilot**, **Grok CLI** ve **OpenRouter** kullanımınızı doğrudan RGB klavye, fare, RAM ve ortam ışıklarınıza yansıtır.

[ [English](README.md) | **Türkçe** ]

</div>

---

## 🌟 Genel Bakış

Yapay zeka kodlama araçlarıyla çalışırken beklenmedik 5 saatlik kotalara takılmak veya günlük token sınırını doldurmak çalışma akışınızı böler. **SignalRGB AI Token Tracker**, yerel log dosyalarınızı ve seans kayıtlarınızı milisaniyelik hızla okuyarak SignalRGB'nin aydınlatma motoruna aktarır.

- 📊 **Canlı Kota Görselleştirmesi:** LED'leriniz kalan kotanızı (%100'den %0'a azalan) veya harcanan kotanızı (%0'dan %100'e dolan) gösterir.
- ⚡ **Aktif Kod Üretim Efekti (Generation FX):** Yapay zeka yanıt üretirken (token akarken) donanımlarınızda nabız, dalga veya neon akış animasyonu oluşur.
- ♊ **Çift Model (Dual-Model) Desteği:** Antigravity/Orca üzerindeki **Gemini 3.8 Flash** ve **Claude Opus 4.6** modellerini birbirinden ayırarak bağımsız 5 saatlik kotaları otomatik izler.
- 🔓 **%100 SignalRGB Free (Ücretsiz) ve Pro Uyumluluğu:** Dahili yerel HTTP sunucusu (`:16035`) sayesinde SignalRGB'nin ücretsiz sürümünde de hiçbir kısıtlamaya takılmadan gerçek zamanlı çalışır.
- 🎛️ **SignalRGB Arayüzünden Doğrudan Ayar:** Renkler, çubuk yönleri, kritik uyarı çakarları ve animasyon stilleri doğrudan SignalRGB efekt panelinden değiştirilebilir.

---

## 📸 Görsel Modlar ve Efekt Stilleri

Efekt paneli üzerinden seçilebilen 6 farklı görsel mod:

| Görsel Mod | Açıklama |
| :--- | :--- |
| **Progress Bar** | Donanımlarınız üzerinde net ve doğrusal bir ilerleme çubuğu gösterir. |
| **Solid Gradient** | Tüm cihazlarınızı kota durumuna göre yeşilden kırmızıya geçişli aydınlatır. |
| **Active Pulse** | Kod yazımı sırasında hızlanan nefes alma animasyonu sunar. |
| **Matrix Wave** | Siberpunk tarzı yatay tarama dalgası oluşturur. |
| **Circular Gauge** | Sıvı soğutma pompaları, fanlar ve yuvarlak LED halkaları için dairesel sayaç. |
| **Split Zones** | **Çift Model Bölümü:** Sol taraf Gemini kotasını, sağ taraf Claude/GPT kotasını gösterir. |

---

## 🤖 Desteklenen Yapay Zeka Araçları

Araçlarınız otomatik olarak tespit edilir, ekstra yapılandırma gerekmez:

| Sağlayıcı | Veri Kaynağı | Takip Edilen Metrikler |
| :--- | :--- | :--- |
| **Antigravity (CLI & IDE)** | `~/.gemini/antigravity-cli/brain/` | Model ailesi tespiti, kayan 5 saatlik kota, canlı kod akış tespiti. |
| **Claude Code** | `~/.claude/projects/` | Günlük token harcaması ve aktif yazma durumu. |
| **OpenAI Codex** | `~/.codex/sessions/` | Token olay akışları ve kod üretim takibi. |
| **Cursor IDE** | `%APPDATA%\Cursor\User\workspaceStorage` | SQLite veritabanından toplanan prompt ve tamamlama tokenları. |
| **Gemini CLI** | `~/.gemini/tmp/` | Seans kullanım günlükleri ve prompt metrikleri. |
| **GitHub Copilot CLI** | `~/.copilot/session-store.db` | Yerel etkileşim kayıtları ve token geçmişi. |
| **Grok CLI** | `~/.grok/logs/` | Günlük token hesabı ve üretim durumu. |
| **Pi Agent / Hermes 3** | `~/.pi/sessions/` & `~/.hermes/` | Seans token sayıları ve etkinlik durumu. |
| **OpenRouter API** | `openrouter.ai/api/v1/auth/key` | Yüzlerce açık/özel LLM için bakiye ve kota takibi. |

---

## ⚡ Hızlı Kurulum

### Yöntem 1: Otomatik Kurulum (Önerilen)

1. En son [Releases](https://github.com/crowroser/SignalRGB-AI-Token-Tracker/releases) sayfasından `AITokenTracker-windows.zip` dosyasını indirin.
2. Arşivi bir klasöre çıkartın ve `setup.bat` dosyasına çift tıklayın.
3. Kurulum otomatik olarak:
   - Efekti `Documents\WhirlwindFX\Effects\AI Token Tracker\` konumuna yükler.
   - Arka plan servisini başlatır.
4. **SignalRGB** uygulamasını açın, **Aydınlatma / Efektler** bölümünden **AI Token Tracker** efektini seçin.

### Yöntem 2: Kaynak Koddan Çalıştırma (Python 3.9+)

Harici ağır kütüphane kurulumu gerektirmez, saf Python standart kütüphanesiyle çalışır.

```powershell
# 1. Repoyu klonlayın
git clone https://github.com/crowroser/SignalRGB-AI-Token-Tracker.git
cd SignalRGB-AI-Token-Tracker

# 2. SignalRGB efektini yükleyin
python bridge.py --install

# 3. İzleyiciyi başlatın
.\start.bat
```

> **Sessiz Arka Plan Modu:** Konsol penceresi açılmadan arka planda çalıştırmak için (örneğin SignalRGB makrosu veya Windows Başlangıç için) `.\start_background.bat` dosyasını çalıştırabilirsiniz.

---

## ⚙️ Yapılandırma (`config.json`)

Kotaları ve takip modlarını `config.json` dosyasından dilediğiniz gibi özelleştirebilirsiniz:

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

### Ayar Açıklamaları:
- **`mode`**: `"remaining"` (Kalan %100'den %0'a düşer) veya `"usage"` (Harcanan %0'dan %100'e dolar).
- **`gemini_5h_quota`**: Gemini modelleri için 5 saatlik kayan kota sınırı (Varsayılan: `1,150,000`).
- **`claude_5h_quota`**: Claude/GPT modelleri için 5 saatlik kayan kota sınırı (Varsayılan: `70,000`).
- **`active_providers`**: Taranacak aktif yapay zeka araçları listesi.
- **`openrouter_api_key`**: OpenRouter bakiye takibi için isteğe bağlı API anahtarı.

---

## 🧩 Mimari

```mermaid
flowchart LR
    subgraph AI["Yapay Zeka Araçları"]
        AG["Antigravity / Orca"]
        CC["Claude Code"]
        CX["Cursor / Codex"]
        OR["OpenRouter API"]
    end

    subgraph Bridge["AI Token Tracker Bridge (Python)"]
        Scanner["Çoklu Sağlayıcı Tarayıcı"]
        Calc["5 Saatlik Kayan Kota & Model Ayrıştırıcı"]
        HttpServer["Yerel HTTP API (:16035)"]
        CanvasClient["Canvas API İstemcisi (:16034)"]
    end

    subgraph SignalRGB["SignalRGB Motoru (Free & Pro)"]
        HTML["AI Token Tracker.html (Ultralight WebKit)"]
        LEDs["Donanım LED'leri: Klavye / Fare / RAM / Kasa"]
    end

    AI -->|Yerel Loglar ve DB'ler| Scanner
    Scanner --> Calc
    Calc --> HttpServer
    Calc --> CanvasClient

    HttpServer -->|HTTP GET /api/tokens (Polling)| HTML
    CanvasClient -.->|Canvas API POST (Pro)| HTML
    HTML -->|Canlı RGB Aydınlatma| LEDs
```

---

## 🛠️ CLI Komut Satırı Seçenekleri

```text
AITokenTracker.exe [seçenekler]  (veya python bridge.py [seçenekler])

Seçenekler:
  --install       SignalRGB efekt dosyalarını WhirlwindFX klasörüne kopyalar
  --background    Konsol penceresini gizler ve arka planda çalışır
  --config PATH   Özel bir config.json dosya yolu tanımlar
  -h, --help      Yardım metnini görüntüler
```

---

## 🤝 Katkıda Bulunma

Hata bildirimleri, yeni özellik önerileri ve katkılarınız memnuniyetle karşılanır:

1. Projeyi Fork'layın
2. Yeni Özellik Dalı Açın (`git checkout -b feature/YeniOzellik`)
3. Değişikliklerinizi Commit'leyin (`git commit -m 'feat: Yeni yapay zeka aracı desteği'`)
4. Dalınıza Push Edin (`git push origin feature/YeniOzellik`)
5. Bir Pull Request Açın

---

## 📄 Lisans

Bu proje **MIT Lisansı** altında sunulmaktadır. Ayrıntılar için [`LICENSE`](LICENSE) dosyasına bakabilirsiniz.

---

<div align="center">
<a href="https://github.com/crowroser">crowroser (Fatih Gülcü)</a> tarafından ❤️ ile geliştirildi.
</div>
