# Temporal Spanner Analyzer

Baligács (2026) **Temporal Cliques Admit Linear Spanners** (arXiv:2606.05156) teoreminin
çalışan implementasyonu ve interaktif web aracı.

Derlem dilbilimcileri için tasarlanmıştır: zaman etiketli metin verisindeki kelime
birlikteliklerini temporal klike dönüştürür, ≤ 7n kenarlı lineer spanner ile seyreltir,
kavram kümelerinin doğum, büyüme ve kayboluş süreçlerini görünür kılar.

**Canlı:** https://frontend-teal-iota-ee3dg8j6wx.vercel.app
**API:** https://temporal-spanner-api.onrender.com

## Özellikler

- **Çoklu Format Desteği**: CSV, JSON, CoNLL-U (.conllu), VRT (.vrt)
- **Spanner**: Orijinal çizgeyi ≤ 7n kenara indirir, tüm zamansal yolları korur
- **Trendler**: Kliklerin zaman içinde doğum/büyüme/ölümünü Gantt + çizgi grafiğinde izle
- **Karşılaştırma**: İki zaman dilimini yan yana analiz
- **Keşif**: Kelime bazlı klik sorgulama, kelime kümesi klik doğrulaması
- **Canlı Zaman Kaydırma**: Slider ile spanner otomatik güncellenir
- **Örnek Veri**: Tek tıkla Türkçe yapay zekâ terimleri derlemi (2020-2024)

## Hızlı Başlangıç

```bash
# Backend (port 8000)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Frontend (port 3004, ayrı terminal)
cd frontend && npm run dev
```

Tarayıcı: http://localhost:3004 — "Örnek Veri ile Dene" ile hemen test edin.

### Docker

```bash
docker compose up --build
```

## Desteklenen Formatlar

### CoNLL-U (.conllu)
```
# date = 2020-01-15
1	yapay	yapay	ADJ
2	zekâ	zekâ	NOUN
3	öğrenme	öğrenme	NOUN
```
Sütun 2 (FORM) veya 3 (LEMMA) okunur. `# date =` satırı zamanı belirler.
Dosya adından da tarih çıkarılabilir (örn. `2020-01-15_corpus.conllu`).

### CSV
```csv
date,words
2020-01-15,"yapay,zekâ,öğrenme"
2020-06-10,"doğal,dil,işleme"
```

### JSON
```json
[
  {"date": "2020-01-15", "words": ["yapay", "zekâ"]},
  {"date": "2020-06-10", "words": ["doğal", "dil"]}
]
```

### VRT (.vrt)
```xml
<text date="2020-01-15">
yapay	ADJ
zekâ	NOUN
</text>
```

## API

| Metot | Route | Açıklama |
|-------|-------|----------|
| POST | `/api/spanner` | Spanner hesapla |
| POST | `/api/upload` | Dosya yükle (CSV/JSON/CoNLL-U/VRT) |
| POST | `/api/trends` | Klik evrim trendleri |
| POST | `/api/compare` | İki çizge karşılaştırması |
| POST | `/api/word-cliques` | Kelimenin klik üyelikleri |
| POST | `/api/check-clique` | Kelime kümesi klik kontrolü |
| POST | `/api/export` | JSON/CSV/GraphML dışa aktar |
| GET | `/api/health` | Sağlık kontrolü |

## Mimari

```
frontend/               Next.js 16 + React 19 + Tailwind CSS + Cytoscape.js + D3.js
backend/
  routers/              FastAPI endpoint'leri
  services/             PMI çizge inşası, Bron–Kerbosch, trend analizi, derlem ayrıştırıcı
  algorithm/            Baligács (2026) Lemma/Theorem implementasyonu
spanner/                Saf Python algoritma kütüphanesi (types, core, verify)
tests/                  37 test (pytest)
```

## Algoritma

Baligács (2026) her temporal klik için ≤ 7n kenarlı bir spanner inşa eder:

1. **{1,2}-hop dismountability** — 2-4 kenarla servis edilebilen düğümleri çıkar
2. **V⁻/V⁺ bölümleme** (Theorem 20) — doğrudan EM bi-clique, ≤ 7n
3. **Lemma 17 özyineleme** — simple/extended star'lar ile böl, ≤ 6n/seviye, log n derinlik
4. **Toplam**: f(n) ≤ 7n (asimptotik optimal — alt sınır 2n-4)

## Deployment

- **Frontend**: Vercel (ücretsiz)
- **Backend**: Render (ücretsiz, 750 saat/ay)
- **Konfigürasyon**: `vercel.json`, `render.yaml`, `docker-compose.yml`

## Test

```bash
python -m pytest tests/ -v    # 37 test
```
