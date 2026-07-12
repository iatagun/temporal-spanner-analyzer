# temporal-spanner-analyzer

Derlem dilbilimcileri için zamansal kavram evrimi analiz aracı.
Baligács (2026) "Temporal Cliques Admit Linear Spanners" implementasyonu.

CSV / JSON / CoNLL-U / VRT → NPMI çizgesi → maksimal klikler → lineer spanner (≤ 7n) → trendler / karşılaştırma / keşif.

## Canlı

- **Frontend:** https://frontend-teal-iota-ee3dg8j6wx.vercel.app
- **Backend API:** https://temporal-spanner-api.onrender.com

## Hızlı Başlangıç

```bash
# Backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Frontend (ayrı terminal)
cd frontend && npm run dev    # http://localhost:3004
```

## Test

```bash
python -m pytest tests/ -v                      # 37 test
python -m pytest tests/ -v -k test_upload       # spesifik test
```

## Mimari

```
frontend/               Next.js 16 + React 19 + Tailwind CSS v4
  app/
    page.js             Ana sayfa (durum yönetimi + orkestrasyon)
    components/         Header, ControlPanel, TabBar, TimeRangeSlider,
                        MetricCards, SpannerView, CompareView,
                        TrendsView, ExploreView, GraphViewer,
                        LeftSidebar, RightSidebar, LoadingSkeleton
    lib/                api.js (API istemcisi), utils.js (formatTime, BK, renk)
    public/             sample.conllu (örnek derlem)

backend/
  main.py               FastAPI uygulaması, CORS (.env'den)
  models.py             Pydantic modelleri
  routers/              spanner, trends, compare, explore endpoint'leri
  services/
    graph_builder.py    CSV/JSON/CoNLL-U/VRT ayrıştırma, NPMI hesaplama
    graph_utils.py      Bron–Kerbosch (Tomita pivot + budama)
    spanner_service.py  Pipeline orkestratörü (doğrulama opsiyonel)
    trend_analyzer.py   Zaman pencereli klik evrimi (bisect + Jaccard)
    corpus_parser.py    CoNLL-U / VRT format ayrıştırıcı
  algorithm/            Baligács (2026) Lemma/Theorem implementasyonu
    temporal_graph.py   Nmin, Nmax, pos, BFS, induced subgraph
    bi_clique.py        Lemma 4: Klik → Bi-clique dönüşümü
    dismountability.py  Lemma 5 + Gözlem 19: {1,2}-hop sökülebilirlik
    simple_star.py      Tanım 7-8: Basit yıldız
    extended_star.py    Tanım 12: Genişletilmiş yıldız
    cut_crossing.py     Lemma 16: 3-hop-k-cut-crossing
    main_algorithm.py   Lemma 17 + Teorem 18: Özyineli EM spanner
    clique_optimization.py  Teorem 2 + Teorem 20: Klik 7n optimizasyonu

spanner/                Saf Python algoritma kütüphanesi
  types.py              TemporalGraph, TemporalBiClique
  core.py               Dışa aktarım katmanı
  verify.py             Spanner doğrulama (BFS tüm çiftler)
```

## Dilbilimsel Model Notları

- **Birliktelik granülaritesi format'a göre değişir:** CoNLL-U cümle bazında
  gruplanır (ince taneli, standart collocation penceresi); CSV/JSON ise
  yüklenen "words" hücresinin tamamını tek doküman olarak işler (kaba). Aynı
  NPMI formülü uygulanır ama "birlikte geçme" iki formatta farklı anlama gelir.
- **İçerik kelimesi filtresi POS öncelikli:** CoNLL-U/VRT'de UPOS etiketi
  varsa `NOUN/PROPN/VERB/ADJ` dışındaki kelimeler elenir (dil bağımsız);
  POS yoksa (CSV/JSON) sabit Türkçe stopword listesine düşülür
  (`backend/services/graph_builder.py` `_is_content_word`).
- **PMI eşiği artık gerçekten çalışıyor:** `/api/upload` bir `pmi_threshold`
  form alanı kabul eder (varsayılan `0.15`, NPMI [-1,1] ölçeğinde), yükleme
  anında hangi çiftlerin kenar olacağını belirler. Yükleme sonrası
  spanner/trend/compare uçları bu sabitlenmiş kenarlar üzerinden çalışır —
  eşiği değiştirmek dosyayı yeniden yüklemeyi gerektirir.
- **Pencere-içi (per-window) PMI yeniden hesaplama yapılmıyor** — `trend_analyzer.py`
  tek bir global NPMI'den süzülen kenarları zaman dilimlerine bölüyor. Bu,
  bilinçli bir kapsam dışı bırakma; "yerel-zamanda anlamlılık" ayrı bir
  mimari tartışma.

## Ortam Değişkenleri

| Değişken | Amaç | Varsayılan |
|----------|------|------------|
| `CORS_ORIGINS` | İzin verilen origin'ler (virgülle) | `localhost:3004` |
| `SPANNER_VERIFY` | Spanner doğrulaması (`1`/`true`) | kapalı |
| `MAX_UPLOAD_BYTES` | `/api/upload` boyut limiti (byte) | `5242880` (5MB) |
| `NEXT_PUBLIC_API_URL` | Frontend API adresi | `http://127.0.0.1:8000` |

## Deployment

```bash
# Backend → Render (render.yaml)
git push origin main    # Render otomatik deploy eder

# Frontend → Vercel
cd frontend && vercel --prod
```
