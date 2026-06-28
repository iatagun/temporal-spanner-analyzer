# Temporal Spanner Analyzer — Teknik Şartname

**Sürüm:** 1.1
**Tarih:** Haziran 2026
**Durum:** Tamamlandı, canlı
**Canlı:** https://frontend-teal-iota-ee3dg8j6wx.vercel.app
**Dayanak:** Baligács (2026), *Temporal Cliques Admit Linear Spanners*, arXiv:2606.05156

---

## 1. Proje Tanımı

Zaman etiketli metin verisindeki kelime birlikteliklerini PMI ağırlıklı bir zamansal çizge (temporal graph) olarak modelleyen, bu çizgedeki maksimal temporal clique'leri bulan, her clique için **7n** kenar sınırlı lineer spanner hesaplayan ve zamansal dilbilimsel trendleri görselleştiren interaktif bir web uygulamasıdır.

---

## 2. Kapsam

### 2.1 Yapılacak İşler

| # | Modül | Açıklama |
|---|-------|----------|
| 1 | Veri Alımı | CSV/JSON/CoNLL-U/VRT dosyalarından zaman etiketli metin verisini ayrıştırma |
| 2 | Çizge Oluşturma | PMI (Pointwise Mutual Information) metriği ile kelime birliktelik çizgesi inşaası |
| 3 | Maksimal Clique Tespiti | Bron–Kerbosch algoritması ile 3+ düğümlü maksimal clique'lerin bulunması |
| 4 | Spanner Algoritması | Baligács (2026) Lemma 4-17, Theorem 18-20 implementasyonu |
| 5 | Spanner Doğrulama | Tüm düğüm çiftleri arasında zamansal yol garantisinin kontrolü |
| 6 | Trend Analizi | Zaman pencereli clique evriminin hesaplanması |
| 7 | Çizge Karşılaştırma | İki farklı çizge/spanner arası metrik karşılaştırması |
| 8 | Keşif Araçları | Kelime bazlı clique sorgulama ve clique doğrulama |
| 9 | Görselleştirme | Cytoscape.js ile çizge görselleştirme, D3.js ile trend görselleştirme |
| 10 | Dışa Aktarma | JSON/CSV/GraphML formatlarında veri dışa aktarımı |

### 2.2 Kapsam Dışı

- Kullanıcı yönetimi, oturum kalıcılığı (veritabanı yoktur, tüm işlemler bellek içidir)
- Büyük ölçekli dağıtık işleme (Spark/Hadoop)
- Doğal dil işleme (NLP) — girdi tokenize edilmiş kabul edilir
- Otomatik veri toplama / web scraping
- Mobil uygulama

---

## 3. Teknolojik Altyapı

### 3.1 Backend

| Bileşen | Sürüm | Amaç |
|---------|-------|------|
| Python | 3.13+ | Çalışma zamanı |
| FastAPI | ≥0.115 | REST API framework |
| Uvicorn | ≥0.34 | ASGI sunucu |
| Pydantic | ≥2.0 | Veri doğrulama ve modelleme |
| python-dotenv | ≥1.0 | .env dosyası yükleme |
| python-multipart | ≥0.0.20 | Dosya yükleme desteği |

### 3.2 Frontend

| Bileşen | Sürüm | Amaç |
|---------|-------|------|
| Node.js | ≥22 | Çalışma zamanı |
| Next.js | 16.2.7 | React framework (App Router) |
| React | 19.2.4 | UI kütüphanesi |
| Tailwind CSS | 4.3 | Stil framework'ü |
| Cytoscape.js | ≥3.31 | Çizge görselleştirme |
| D3.js | 7.9.0 | Trend grafikleri (Gantt + çizgi) |

### 3.3 Altyapı

| Bileşen | Amaç |
|---------|------|
| Docker | Konteynerizasyon |
| Docker Compose | Çoklu servis orkestrasyonu |
| Git | Versiyon kontrolü |

---

## 4. Sistem Mimarisi

```
┌─────────────────────────────────────────────────┐
│                   İstemci (Browser)               │
│  Next.js 16 SPA (page.js)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │GraphViewer│ │TrendsView│ │  ExploreView     │ │
│  │(Cytoscape)│ │  (D3.js) │ │  (React state)   │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
└─────────────────────┬───────────────────────────┘
                      │ HTTP (port 3000 → 8000)
┌─────────────────────▼───────────────────────────┐
│              FastAPI Backend (port 8000)          │
│  ┌─────────────────────────────────────────────┐ │
│  │  Routers (/api/*)                           │ │
│  │  spanner.py trends.py compare.py explore.py │ │
│  └─────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────┐ │
│  │  Services                                   │ │
│  │  graph_builder.py  → CSV/JSON→GraphSchema  │ │
│  │  graph_utils.py    → Bron–Kerbosch          │ │
│  │  spanner_service.py → Pipeline orkestrasyonu│ │
│  │  trend_analyzer.py → Zaman pencereli analiz │ │
│  └─────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────┐ │
│  │  Algorithm (backend/algorithm/)              │ │
│  │  temporal_graph.py    → Nmin/Nmax/pos/BFS  │ │
│  │  bi_clique.py         → Lemma 4             │ │
│  │  dismountability.py   → Lemma 5 + Obs 19    │ │
│  │  simple_star.py       → Def 7-8             │ │
│  │  extended_star.py     → Def 12              │ │
│  │  cut_crossing.py      → Lemma 16            │ │
│  │  main_algorithm.py    → Lemma 17 + Thm 18   │ │
│  │  clique_optimization.py → Thm 2 + Thm 20    │ │
│  └─────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────┐ │
│  │  Core Types (spanner/)                      │ │
│  │  types.py → TemporalGraph, TemporalBiClique │ │
│  │  core.py  → Re-export facade                │ │
│  │  verify.py → verify_spanner                 │ │
│  └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### 4.1 Veri Akışı

```
CSV/JSON → parse_csv/parse_json
         → PMI hesaplama (N, df, codf)
         → GraphSchema (V + E + weights)
         → Bron–Kerbosch (maksimal clique'ler, ≥3 düğüm)
         → Her clique için: spanner_for_clique()
              → 12-hop dismountability
              → EM biclique tespiti
              → Recursive star cover (≤7n)
         → Clique spanner'ları birleştir
         → verify_spanner (tüm çiftler için BFS)
         → stretch_factor hesaplama (örneklem, ≤50 çift)
```

---

## 5. Algoritma Spesifikasyonu

### 5.1 PMI Hesaplama (graph_builder.py)

```
PMI(w1, w2) = log₂(N × codf(w1, w2) / (df(w1) × df(w2)))
```

- **N**: Toplam satır/doküman sayısı
- **df(w)**: w kelimesini içeren doküman sayısı
- **codf(w1, w2)**: w1 ve w2'nin birlikte geçtiği doküman sayısı
- Eşik: PMI > 0 olan kenarlar çizgeye eklenir

Türkçe stopword listesi (47 kelime) filtrelenir.

### 5.2 Spanner Algoritması (Baligács 2026)

**Girdi:** n düğümlü temporal clique G = (V, E, L)
**Çıktı:** En fazla 7n kenarlı spanner H ⊆ G

| Adım | Fonksiyon | Lemma/Teorem | Açıklama |
|------|-----------|-------------|----------|
| 1 | `dismountability_12_hop()` | Lemma 5 + Obs 19 | {1,2}-hop sökülebilir düğümleri kaldır |
| 2 | `clique_to_biclique()` | Lemma 4 | Klik → ikili-klik dönüşümü (S/T kopyaları) |
| 3 | `spanner_for_EM_biclique()` | Lemma 17, Thm 18 | EM ikili-klik için recursive yıldız kapsaması |
| 4 | `spanner_for_biclique()` | Lemma 4-17 | Genel ikili-klik spanner'ı |
| 5 | `spanner_for_clique()` | Thm 2, Thm 20 | **7n** sınırlı nihai spanner |

**Kenar Sınırı:** f(n) ≤ 9n - 4x + f(x) ve x ≤ n/2 → tümevarımla f(n) ≤ 14n (ikili-klik) → 7n (klik)

### 5.3 Zaman Karmaşıklığı

| Operasyon | Karmaşıklık | Not |
|-----------|------------|-----|
| Çizge oluşturma (PMI) | O(m × k²) | m: satır, k: satır başına ortalama kelime |
| Bron–Kerbosch | O(3ⁿ/³) | En kötü durum, pratikte seyrek çizgelerde hızlı |
| Spanner (tek clique) | O(n²) | n: clique büyüklüğü |
| Doğrulama (BFS) | O(n × m) | n: düğüm, m: kenar |

---

## 6. API Spesifikasyonları

### 6.1 `POST /api/spanner`

**İstek:**
```json
{
  "graph": {
    "vertices": ["a", "b", "c"],
    "edges": [{"source": "a", "target": "b", "label": 1.0}]
  }
}
```

**Yanıt:**
```json
{
  "original": {"vertices": [...], "edges": [...]},
  "spanner": {"vertices": [...], "edges": [...]},
  "metrics": {
    "original_edge_count": 45,
    "spanner_edge_count": 10,
    "savings_pct": 77.78,
    "ratio_per_n": 1.0,
    "bound_7n": 70,
    "cliques_found": 3,
    "stretch_factor": 1.15,
    "algorithm": "baligacs-2026"
  }
}
```

### 6.2 `POST /api/upload`

- İçerik Tipi: `multipart/form-data`
- Kabul edilen: CSV (`,tarih,kelimeler`), JSON
- Yanıt: `UploadResponse` (session_id, graph, rows_parsed, time_range)

### 6.3 `POST /api/trends`

- İstek: graph, window_count, window_size
- Yanıt: CliqueTimeline[] (her pencere için clique envanteri)

### 6.4 `POST /api/compare`

- İstek: graph1, graph2, label1, label2
- Yanıt: Her iki çizge için spanner + karşılaştırma metrikleri (edge_count, vertex_count, clique_count, savings_pct, ratio_per_n, avg_clique_size)

### 6.5 `POST /api/word-cliques`

- İstek: graph, word, windows
- Yanıt: Kelimenin snapshot'ları ve timeline_count

### 6.6 `POST /api/check-clique`

- İstek: graph, words
- Yanıt: is_clique, total_pairs, missing_pairs

### 6.7 `GET /api/health`

- Yanıt: `{"status": "healthy", "algo": "baligacs-2026"}`

### 6.8 `POST /api/export?fmt=json|csv|graphml`

- İstek: graph
- Yanıt: İlgili formatta dosya indirme

---

## 7. Frontend Gereksinimleri

### 7.1 Görünümler

| Görünüm | Bileşen | Teknoloji | İşlev |
|---------|---------|-----------|-------|
| Spanner | GraphViewer | Cytoscape.js | Orijinal ağ ve spanner yan yana, renk kodlu clique'ler |
| Trends | TrendsView | D3.js | Clique Gantt şeması + boyut trend çizgisi |
| Compare | page.js | React state | İki dönem yan yana, karşılaştırma metrik kartları |
| Explore | ExploreView | React state | Kelime sorgulama, clique doğrulama formu |

### 7.2 Kullanıcı Arayüzü Gereksinimleri

- **CR-01**: Dört görünüm arası sekme ile geçiş
- **CR-02**: CSV yükleme (drag-drop veya dosya seçici)
- **CR-03**: Sentetik veri oluşturma (düğüm sayısı, tohum ayarlanabilir)
- **CR-04**: Zaman aralığı slider'ı (canlı filtreleme)
- **CR-05**: Minimum frekans filtresi
- **CR-06**: Orijinal ağ ve spanner yan yana görsel karşılaştırma
- **CR-07**: Clique üyeliklerine göre düğüm renklendirme (tek clique = renk, çoklu = sarı)
- **CR-08**: Metrik kartları (kenar sayısı, tasarruf %, ratio/n, stretch factor)
- **CR-09**: Gantt şeması (clique ömürleri) + trends çizgi grafiği
- **CR-10**: Karşılaştırma metrik tablosu
- **CR-11**: Kelime sorgulama (otocomplete)
- **CR-12**: JSON/CSV/GraphML dışa aktarma
- **CR-13**: Canlı mod (slider değişiminde otomatik spanner güncelleme)
- **CR-14**: Hata durumlarında kullanıcı bilgilendirmesi
- **CR-15**: Responsive tasarım (en az 1280×720 çözünürlük)

---

## 8. Test Gereksinimleri

### 8.1 Test Kapsamı

| Test Türü | Dosya | Test Sayısı | Kapsam |
|-----------|-------|-------------|--------|
| Birim | test_algorithm/test_bi_clique.py | 2 | clique_to_biclique, projeksiyon |
| Birim | test_algorithm/test_dismountability.py | 4 | Boş/basit/12-hop |
| Birim | test_algorithm/test_simple_star.py | 2 | Boyut, sıralama |
| Birim | test_algorithm/test_extended_star.py | 2 | emin/emax içerme, boyut sınırı |
| Birim | test_algorithm/test_cut_crossing.py | 2 | 3-hop tespiti |
| Birim | test_algorithm/test_main_algorithm.py | 7 | Küçük/orta/büyük clique, EM, multi-seed |
| Birim | test_verify.py | 4 | Küçük/orta/multi-seed/sınır doğrulama |
| Entegrasyon | test_integration.py | 9 | Upload, spanner, export, health |
| Entegrasyon | test_explore.py | 3 | check-clique, word-cliques |
| Entegrasyon | test_compare.py | 2 | İki graf karşılaştırması |

### 8.2 Test Gereksinimleri

- **TR-01**: Tüm testler `pytest` ile çalıştırılabilir olmalı
- **TR-02**: Spanner çıktısı `verify_spanner()` doğrulamasından geçmeli
- **TR-03**: Spanner kenar sayısı ≤ 7n olmalı
- **TR-04**: Her algoritma modülü için en az 2 test
- **TR-05**: API testleri `TestClient` ile yapılmalı
- **TR-06**: Hata durumları (geçersiz dosya, eksik alan) test edilmeli

---

## 9. Performans Gereksinimleri

| Kriter | Hedef | Not |
|--------|-------|-----|
| Spanner hesaplama (n=10) | < 100ms | Tek clique |
| Spanner hesaplama (n=50) | < 2s | Tek clique |
| CSV yükleme (1000 satır) | < 3s | PMI + clique tespiti |
| API yanıt süresi | < 500ms | Ortalama, önbelleksiz |
| Frontend ilk yükleme | < 3s | 3G bağlantıda |
| Çizge render (≤200 düğüm) | < 1s | Cytoscape.js CoSE |

---

## 10. Veri Formatları

### 10.1 CSV (Girdi)

```csv
tarih,kaynak,kelimeler
2020-01-05,haber1,"yapay,zekâ,teknoloji,gelecek"
2020-03-12,haber2,"yapay,zekâ,makine,öğrenme"
```

- `tarih`: ISO 8601 tarih (YYYY-MM-DD)
- `kaynak`: Opsiyonel, metin tanımlayıcı
- `kelimeler`: Virgülle ayrılmış kelime listesi (çift tırnak içinde)

### 10.2 JSON (Girdi/Çıktı)

```json
{
  "vertices": ["kelime1", "kelime2"],
  "edges": [
    {"source": "kelime1", "target": "kelime2", "label": 2020.0}
  ]
}
```

### 10.3 GraphML (Çıktı)

Standart GraphML XML formatı. Düğümlerde `id`, kenarlarda `id` ve `label` (zaman) attribute'ları.

---

## 11. Dağıtım Gereksinimleri

### 11.1 Docker

```yaml
backend:
  - python:3.13-slim
  - port 8000
  - uvicorn backend.main:app

frontend:
  - node:22-alpine
  - port 3000
  - next dev (geliştirme) / next start (üretim)
  - depends_on: backend
```

### 11.2 Çevresel Değişkenler

| Değişken | Varsayılan | Açıklama |
|----------|-----------|----------|
| `BACKEND_URL` | `http://127.0.0.1:8000` | Backend API adresi |
| `HOST` | `0.0.0.0` | Backend host |
| `PORT` | `8000` | Backend port |

### 11.3 Geliştirme Ortamı

```bash
# Backend (terminal 1)
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload

# Frontend (terminal 2)
cd frontend && npm install && npm run dev

# Test
python -m pytest tests/ -v
```

---

## 12. Güvenlik Gereksinimleri

- **GR-01**: CORS tüm originlere açık (geliştirme); üretimde kısıtlanmalı
- **GR-02**: Dosya yükleme boyutu sınırlandırılmalı (varsayılan: 50MB)
- **GR-03**: Yalnızca .csv ve .json dosyaları kabul edilmeli
- **GR-04**: Kod/girdi enjeksiyonuna karşı Pydantic doğrulaması
- **GR-05**: Hassas veri saklanmamalı (veritabanı yok, bellek içi işlem)

---

## 13. Kalite Güvence

- **KG-01**: Tüm testler `python -m pytest tests/ -v` ile geçmeli
- **KG-02**: Spanner çıktısı `verify_spanner()` doğrulamasından geçmeli
- **KG-03**: Kenar sayısı her clique için ≤ 7n olmalı (yuvarlama ile 7×max(n,1))
- **KG-04**: API dökümantasyonu `/docs` adresinde Swagger UI ile erişilebilir olmalı
- **KG-05**: Frontend build hatasız tamamlanmalı
- **KG-06**: Hata yönetimi: geçersiz girdilerde 422, sunucu hatasında 500, sağlıklı durumda 200

---

## 14. Teslimat Kalemleri

| # | Kalem | Açıklama |
|---|-------|----------|
| 1 | Kaynak Kodu | GitHub reposu (tüm backend, frontend, algoritma, testler) |
| 2 | Docker Konfigürasyonu | Dockerfile + docker-compose.yml |
| 3 | API Dökümantasyonu | Swagger UI (/docs) |
| 4 | Kullanım Kılavuzu | README.md (Türkçe) |
| 5 | Algoritma Dökümantasyonu | ALGORITMA-PSEUDOCODE.md, dokümanlar/docs/ |
| 6 | Proje Planı | TEMPORAL-SPANNER-PLANI.md |
| 7 | Örnek Veri | examples/teknoloji_ornek.csv, examples/pandemic_ornek.csv |
| 8 | Test Raporu | pytest çıktısı (tüm testler geçiyor olmalı) |

---

## 15. Referanslar

1. Baligács (2026). *Temporal Cliques Admit Linear Spanners*. arXiv:2606.05156
2. Bron & Kerbosch (1973). *Algorithm 457: Finding All Cliques of an Undirected Graph*. CACM.
3. Cytoscape.js: https://js.cytoscape.org
4. D3.js: https://d3js.org
5. FastAPI: https://fastapi.tiangolo.com
6. Next.js: https://nextjs.org
