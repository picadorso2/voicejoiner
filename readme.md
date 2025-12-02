# 🌀 **Picadorso2 Voice Joiner – V25 Apex Ultimate Edition**

**Geliştirici:** Picadorso2  
**Proje Adı:** Picadorso2 Voice Joiner  
**Dil:** Python (PyQt6 + Discord.py)

---

## 📌 **Hakkında**

**Picadorso2 Voice Joiner**, gelişmiş bir Discord ses botu yönetim panelidir.  
Modern **Apex arayüz tasarımı** sayesinde kod bilmeden kolayca çoklu bot yönetimi yapabilir,  
ses kanallarına bot sokabilir, 7/24 aktif tutabilir ve yüksek kalitede müzik/ses dosyaları oynatabilirsiniz.

---

## 🚀 **Özellikler**

### 🔹 **Çoklu Bot Yönetimi**
- Aynı anda **20 adede kadar bot** ekleyip yönetebilme

### 🔹 **Gelişmiş Ses Motoru**
- FFmpeg tabanlı oynatma  
- Desteklenen formatlar: **.mp3, .mp4, .wav**

### 🔹 **Apex UI Tasarımı**
- Responsive grid yapısı  
- Modern özel çizim butonlar  
- Optimize edilmiş Apex teması

### 🔹 **Akıllı Sistem İzleme**
- Dahili HUD ile anlık CPU/RAM takibi

### 🔹 **RAM Booster**
- Tek tıklamayla bellek temizleme

### 🔹 **Tam Kontrol Paneli**
Her bot için:
- Ses seviyesi  
- Döngü süresi  
- Mute/Deaf  
- Oynatma kontrolü

### 🔹 **Kalıcı Hafıza**
- Ayarlar ve bot listesi **settings.json** dosyasında saklanır  
- Tüm kayıtlar **yalnızca sizin cihazınızda** tutulur  
- Harici bir sunucuya gönderilmez, tamamen güvenlidir

### 🔹 **Webhook Loglama**
- Bot durumlarını Discord kanalına iletir

### 🔹 **Oto-Başlat**
- Program açıldığında botları otomatik ses kanalına sokar

---

## 📥 **İndirme ve Kurulum (Kullanıcılar İçin)**

Kodla uğraşmak istemiyorsanız **hazır derlenmiş sürümü** indirebilirsiniz:

1. Sağdaki **Releases** bölümüne tıklayın  
2. En güncel **.zip** dosyasını indirin  
3. Klasöre çıkarın  
4. `Picadorso2_V25.exe` dosyasını çalıştırın

> FFmpeg ve gerekli tüm dosyalar ZIP içinde bulunmaktadır.

---

## 🛠️ **Kaynak Koddan Çalıştırma (Geliştiriciler İçin)**

### 1️⃣ Gerekli Kütüphaneleri Yükleyin

```bash
pip install PyQt6 discord.py psutil PyNaCl requests
```

### 2️⃣ Zorunlu Dosyalar (`main.py` ile aynı klasörde olmalı)

- `ffmpeg.exe`  
- `libopus-0.x64.dll`

### 3️⃣ Çalıştırma

```bash
python main.py
```

---

## 📂 **Dosya Yapısı**

```
Picadorso2 Voice Joiner/
│-- main.py               # Ana yazılım
│-- ffmpeg.exe            # Ses motoru
│-- libopus-0.x64.dll     # Discord ses kodeği
│-- settings.json         # Ayar dosyası (kalıcı hafıza)
│-- config.json           # Bot listesi (otomatik)
│
└── ui/
    └── style.qss         # Tema dosyası
```

---

## ⚠️ **Destek ve İletişim**

Herhangi bir sorun veya hata ile karşılaşırsanız  
**Discord üzerinden bana ulaşabilirsiniz:**  
👉 **picador_so2**

---

## ⚠️ **Yasal Uyarı**

Bu yazılım eğitim ve test amaçlıdır.  
Discord Hizmet Şartları’na aykırı kullanımdan doğacak sorumluluk kullanıcıya aittir.  
Geliştirici **Picadorso2** herhangi bir sorumluluk kabul etmez.

---

### © 2025 Picadorso2 — Tüm Hakları Saklıdır.
