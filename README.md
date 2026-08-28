# 🌈 SignalRGB AI Token Tracker

SignalRGB üzerinde yapay zeka araçlarınızın (**Antigravity**, **Claude Code**, **OpenAI Codex**, **Cursor**, **Gemini CLI**, **GitHub Copilot**, **Grok CLI**, **Pi Agent**, **Hermes Agent** ve **OpenRouter**) harcadığı veya kalan token kotalarını **canlı RGB LED aydınlatmasına** dönüştüren entegrasyon sistemi.

Tüm görsel efektler, renkler, bar yönleri, uyarı eşikleri ve dahili simülasyon testleri **doğrudan SignalRGB'nin kendi efekt ayarları panelinden** fareyle kontrol edilebilir.

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

## 📦 Kurulum ve Kullanım

### 1. Adım: Efekti SignalRGB'ye Yükleme
Efekt dosyasını SignalRGB'nin efektler klasörüne tek tıkla kopyalamak için:
```powershell
.\install.ps1
```
*(veya `install.bat` dosyasına çift tıklayın).*

### 2. Adım: SignalRGB İçinden Efekti Seçme
1. **SignalRGB** uygulamasını açın.
2. **Effects** (Efektler) sekmesine gidin.
3. **AI Token Tracker** efektini seçin ve uygulayın.
4. **Customize** (Özelleştir) panelinden istediğiniz renkleri, bar modunu ve yönünü ayarlayın.

### 3. Adım: Token Takipçi Köprüsünü Başlatma
Arka planda token'ları otomatik okuyup SignalRGB'ye göndermek için:
```bash
python -m src.main
```
*(veya `start.bat` dosyasına çift tıklayın).*

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
