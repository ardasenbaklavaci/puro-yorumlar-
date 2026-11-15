# Puro Yorumları Blog

Puro dünyasını merak edenlerle kişisel deneyimlerimi ve yorumlarımı paylaştığım blog.

**Live:** https://puroyorumlari.pages.dev/

## 🔧 Sitemap GSC Kurulumu

Google Search Console'da sitemap'ın fetch edilememesi sorunu var. Aşağıdaki adımları takip et:

### ⚠️ KRİTİK PROBLEM
```
GSC Status: Couldn't fetch
HTTP Status: 200 ✅
Cache-Control: max-age=0 ❌
```

### ✅ ÇÖZÜM (Cloudflare Dashboard)

1. **https://dash.cloudflare.com** aç
2. **puroyorumlari** projesi seç  
3. **Settings** → **Build & deploy**
   - Build output directory = `site` ✓
4. **Caching** → **Configuration**
   - **Cache Level** = "Cache Everything" ⭐ (ÖNEMLİ!)
   - **Browser Cache Expiration** = 1 hour
5. **Caching** → **Purge Everything** (cache temizle)
6. **Deployments** → "Trigger new deployment" (manuel deploy)
7. 5-10 dakika bekle

### 🔍 Kontrol Et
```powershell
./test-sitemap.ps1
```

Sonuç: `Cache-Control: public, max-age=3600` olmalı

### 📝 GSC'ye Sitemap Ekle
1. https://search.google.com/search-console
2. **puroyorumlari.pages.dev** seç
3. **Sitemaps** → Yeni sitemap ekle
4. URL: `https://puroyorumlari.pages.dev/sitemap.xml`
5. **Gönder** tıkla

## 🏗️ Build

```bash
python build_site.py
```

Bu script:
- WordPress XML'den post'ları dönüştürür
- `site/` klasöründe static HTML oluşturur
- Otomatik sitemap.xml ve robots.txt üretir
- Medya dosyalarını download eder

## 📁 Dosya Yapısı

```
.
├── build_site.py              # Build script
├── puroyorumlar.WordPress.xml # WordPress export
├── site/                       # Build output (Cloudflare Pages deploy ediliyor)
│   ├── index.html
│   ├── sitemap.xml            # Auto-generated
│   ├── robots.txt             # Auto-generated  
│   ├── _headers               # Cloudflare headers
│   ├── _redirects             # Cloudflare redirects
│   ├── styles.css
│   └── assets/                # Media files
└── test-sitemap.ps1           # Diagnostic script
```

## 🚀 Deployment

Cloudflare Pages otomatik deploy:
- GitHub repo > Push > Cloudflare Pages otomatik build ve deploy
- Build command: `python build_site.py`
- Build output directory: `site`

## 🔗 Links

- **Site:** https://puroyorumlari.pages.dev/
- **GSC:** https://search.google.com/search-console
- **Cloudflare:** https://dash.cloudflare.com/

## 📊 Sitemap Status

| URL | Status | Cache | Notes |
|-----|--------|-------|-------|
| `/sitemap.xml` | 200 ✅ | Configuring | XML valid |
| `/robots.txt` | 200 ✅ | Configuring | Googlebot explicit |
| `/_headers` | 200 ✅ | Ignored | Need cache TTL fix |

## 🛠️ Sorun Giderme

Hala "Couldn't fetch" alıyorsan:
1. `./test-sitemap.ps1` çalıştır → cache durumu kontrol et
2. Cloudflare **Purge Everything** yap
3. GSC > **Fetch as Google** → hata mesajını oku
4. `SITEMAP_GSC_SOLUTION.md` dosyasına bak

---
**Updated:** 15 Kasım 2026
