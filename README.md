# 🌈 SignalRGB AI Token Tracker

SignalRGB üzerinde yapay zeka araçlarınızın (**Antigravity**, **Claude Code**, **OpenAI Codex**, **Cursor**, **Gemini CLI**, **GitHub Copilot**, **Grok CLI**, **Pi Agent**, **Hermes Agent** ve **OpenRouter**) harcadığı veya kalan token kotalarını **canlı RGB LED aydınlatmasına** dönüştüren entegrasyon sistemi.

Tüm görsel efektler, renkler, bar yönleri, uyarı eşikleri ve dahili simülasyon testleri **doğrudan SignalRGB'nin kendi efekt ayarları panelinden** fareyle kontrol edilebilir.

---

## 🚀 Hızlı Kurulum (EXE — Önerilen)

### 1. [Releases](../../releases) sayfasından `AITokenTracker-windows.zip` dosyasını indirin
### 2. ZIP'i herhangi bir yere çıkarın
### 3. `setup.bat` dosyasına çift tıklayın

Bu kadar! Kurulum otomatik olarak:
- ✅ `AITokenTracker.exe`'yi `%LOCALAPPDATA%\AITokenTracker\` klasörüne yükler
- ✅ SignalRGB efektini `Documents\WhirlwindFX\Effects\` altına kopyalar
- ✅ Windows başlangıcına ekler (arka planda otomatik çalışır)
- ✅ Masaüstüne kısayol oluşturur
- ✅ Servisi hemen başlatır

---

## 🛠️ Geliştirici Kurulumu (Kaynak Koddan)

### Adım 1: Efekti SignalRGB'ye Yükleme
```bash
python bridge.py --install
```

### Adım 2: Köprüyü Çalıştırma
```bash
python bridge.py
```

### Adım 3: EXE Oluşturma (isteğe bağlı)
```bash
pip install pyinstaller
pyinstaller --onefile --name AITokenTracker --add-data "effects/AI Token Tracker;effects/AI Token Tracker" bridge.py
```

---

## 🚀 Özellikler

- **Tüm Araçları Otomatik Yerel Olarak İzler:**
  - 🧠 **Antigravity (CLI & IDE):** Seans transkriptlerini ve SQLite kayıtlarını anlık okur.
  - 🟣 **Claude Code:** `~/.claude/projects/` altındaki seansları tarar.
  - 🟢 **OpenAI Codex:** `~/.codex/sessions/` altındaki token olaylarını yakalar.
  - 💻 **Cursor IDE:** `%APPDATA%\Cursor` altındaki `state.vscdb` veritabanından harcanan token'ları toplar.
  - ♊ **Gemini CLI:** `~/.gemini/tmp/` seans loglarını ayrıştırır.
  - 🐙 **GitHub Copilot:** `~/.copilot/session-store.db` veritabanını izler.
  - ⚡ **Grok CLI, Pi Agent, Hermes Agent & OpenRouter API** desteği.
- **⚡ Canlı Üretim Tespiti (Active Generation Pulse):**
  - Yapay zeka yanıt üretirken (token akarken) donanımlarınızda nabız, dalga veya neon akış efekti oluşur.
- **🎛️ SignalRGB Arayüzünden %100 Özelleştirilebilir:**
  - 6 Farklı Görsel Mod (*Progress Bar, Solid Dynamic Gradient, Active Pulse, Matrix Wave, Circular Gauge, Split Zones*)
  - 5 Farklı Bar Yönü (*Soldan Sağa, Sağdan Sola, Dikey, Merkezden Dışa*)
  - Canlı Renk Paletleri (*Dolu/Yeşil, Orta/Sarı, Düşük/Kırmızı, Aktif/Neon Mavi, Arka Plan*)
  - Geçiş Yumuşaklığı (Smoothing) & Hız Ayarları
  - Kritik Kota Uyarısı (Düşük kotada flaş/çakar)
  - **Dahili Test Modu (Test Mode):** Harici servis çalışmasa bile SignalRGB içindeki slider ile efekti test edebilme.

---

## 📋 CLI Komutları

```
AITokenTracker.exe [seçenekler]

Seçenekler:
  --install       SignalRGB efekt dosyalarını otomatik yükler
  --background    Konsol penceresini gizler, arka planda çalışır
  --config PATH   Özel config.json dosya yolu belirtir
  -h, --help      Yardım mesajını gösterir
```

---

## ⚙️ Yapılandırma (`config.json`)

`config.json` dosyasını açarak günlük bütçenizi veya port ayarlarınızı değiştirebilirsiniz:

```json
{
  "daily_token_budget": 1000000,
  "five_hour_token_quota": 300000,
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

* **`daily_token_budget`**: Günlük hedef token bütçesi (Örn: 1.000.000 token).
* **`mode`**: `"remaining"` (Kalan %100'den %0'a azalır) veya `"usage"` (%0'dan %100'e dolar).
* **`openrouter_api_key`**: OpenRouter kredinizi de takip etmek isterseniz API anahtarınızı buraya yazabilirsiniz.

---

## 🎛️ SignalRGB Efekt Ayarları Rehberi

| Ayar | Tip | Açıklama |
| :--- | :--- | :--- |
| **Visual Mode** | Combobox | Progress Bar, Solid Gradient, Active Pulse, Matrix Wave, Circular Gauge, Split Zones |
| **Bar Orientation** | Combobox | Soldan Sağa, Sağdan Sola, Aşağıdan Yukarıya, Yukarıdan Aşağıya, Merkezden Dışa |
| **High / Full Quota Color** | Color Picker | Kota doluyken/bolken yanacak renk (Varsayılan: Yeşil `#00FF66`) |
| **Medium Quota Color** | Color Picker | Orta seviye kota rengi (Varsayılan: Sarı/Kehribar `#FFB700`) |
| **Low / Critical Color** | Color Picker | Biten kota rengi (Varsayılan: Kırmızı `#FF0044`) |
| **Active Generation Color** | Color Picker | AI yazarken oluşacak vurgu rengi (Varsayılan: Neon Mavi `#00D4FF`) |
| **Generation FX Style** | Combobox | Pulse Glow, Matrix Stream, Neon Surge, Strobe |
| **Smoothing Alpha** | Slider (0-100) | Renk ve bar geçişlerinin akıcılığı (Varsayılan: 75) |
| **Flash On Low Quota** | Toggle | Kota %20'nin altına indiğinde flaş/uyarı verme |
| **[TEST] Manual Test Mode** | Toggle | SignalRGB içinde manuel slider ile test etme |

---

## 🔄 CI/CD (Otomatik Build & Release)

Bu proje GitHub Actions ile otomatik derleme ve yayınlama desteğine sahiptir:

- **Her push (main/master):** Otomatik olarak `AITokenTracker.exe` derlenir ve artifact olarak yüklenir.
- **Tag push (`v*`):** Otomatik olarak GitHub Release oluşturulur ve `AITokenTracker-windows.zip` eklenir.

### Release Yayınlama:
```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## 📁 Proje Yapısı

```
SignalRGBAIToken/
├── bridge.py                    # Tek dosya konsolide kaynak (EXE'nin kaynağı)
├── config.json                  # Yapılandırma dosyası
├── setup.ps1                    # Windows installer (PowerShell)
├── setup.bat                    # Installer başlatıcı
├── effects/
│   └── AI Token Tracker/
│       ├── AI Token Tracker.html  # SignalRGB efekt kodu
│       └── AI Token Tracker.png   # Efekt önizleme ikonu
├── src/                         # Modüler kaynak kod (geliştirme)
│   ├── providers/               # Her AI aracı için ayrı tarayıcı
│   ├── config.py
│   ├── scanner.py
│   ├── signalrgb_client.py
│   └── main.py
├── .github/
│   └── workflows/
│       └── build-release.yml    # CI/CD: Otomatik EXE build + Release
└── README.md
```
