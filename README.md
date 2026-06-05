# Temporal Spanner Analyzer

Baligács (2026) **Temporal Cliques Admit Linear Spanners** teoreminin interaktif web uygulaması.

Zaman etiketli metin verisindeki kelime birlikteliklerini temporal clique → linear spanner dönüşümüyle seyrelterek zamansal dilbilimsel trendleri keşfedin.

## Özellikler

- **Spanner Hesaplama**: CSV yükle veya sentetik graf oluştur, O(n²) → O(7n) kenar azaltımını gör
- **Trend Dedektörü**: Clique'lerin zaman içinde doğum/büyüme/küçülme/ölümünü Gantt şemasında izle
- **Karşılaştırma**: İki farklı zaman diliminin spanner'larını yan yana karşılaştır
- **Keşif Araçları**: Bir kelimenin hangi cliquelerde olduğunu sorgula, kelime setlerinin temporal clique olup olmadığını kontrol et
- **Canlı Zaman Kaydırma**: Slider'ı oynatınca spanner otomatik güncellenir

## Hızlı Başlangıç

```bash
# Backend
cd backend
pip install -r requirements.txt
python main.py

# Frontend (ayrı terminal)
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:3000
Backend API: http://127.0.0.1:8000/docs

### Docker ile

```bash
docker compose up --build
```

## Kullanım

1. **CSV Yükle**: `tarih,kelimeler` formatında CSV dosyanızı yükleyin
2. **Zaman Aralığı Seç**: Slider ile ilgilendiğiniz dönemi belirleyin
3. **Min Frekans**: Seyrek geçen kelimeleri filtreleyin (opsiyonel)
4. **Spanner Hesapla**: Orijinal ağ ile spanner'ı karşılaştırın
5. **Trendler**: Clique evrimini zaman çizelgesinde izleyin
6. **Karşılaştır**: İki farklı dönemi yan yana karşılaştırın
7. **Keşfet**: Kelime sorgulama ve clique kontrolü yapın

### CSV Formatı

```csv
tarih,kaynak,kelimeler
2020-01-05,haber1,"yapay,zekâ,teknoloji,gelecek"
2020-03-12,haber2,"yapay,zekâ,makine,öğrenme"
```

### API Endpoints

| Metot | Route | Açıklama |
|-------|-------|----------|
| POST | `/api/spanner` | Temporal clique spanner'ı hesapla |
| POST | `/api/upload` | CSV yükle |
| POST | `/api/export` | JSON/CSV/GraphML dışa aktar |
| POST | `/api/trends` | Clique evrim trendleri |
| POST | `/api/compare` | İki graf karşılaştırması |
| POST | `/api/word-cliques` | Kelimenin clique üyelikleri |
| POST | `/api/check-clique` | Kelime setinin clique kontrolü |
| GET | `/api/health` | Sağlık kontrolü |

## Mimari

- **Backend**: Python 3.13 + FastAPI
- **Frontend**: Next.js 16 + React 19 + D3.js + Cytoscape.js
- **Algoritma**: `backend/algorithm/` — Baligács makalesinin Lemma/Theorem bazlı implementasyonu

## Teori

Her temporal clique (zaman etiketli tam graf), **7n** kenarlı bir spanner'a (seyreltik alt graf) sahiptir.
Bu spanner, orijinal graftaki herhangi iki düğüm arasında zamansal olarak geçerli bir yol bulunmasını garanti eder.
Detaylar: `TEMPORAL-SPANNER-PLANI.md`
