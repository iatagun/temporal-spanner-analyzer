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
python -m pytest tests/ -v                      # 105 test
python -m pytest tests/ -v -k test_upload       # spesifik test

cd frontend && npx playwright test              # e2e smoke testleri (backend+frontend'i kendi başlatır)
```

## Mimari

```
frontend/               Next.js 16 + React 19 + Tailwind CSS v4
  next.config.js        allowedDevOrigins (127.0.0.1 dahil -- yoksa dev
                        sunucusuna 127.0.0.1 üzerinden bağlanan bir istemci
                        HMR/hydration kaynaklarını sessizce kaybeder ve
                        hiçbir tıklama React'e ulaşmaz; bkz. e2e/ notları)
  playwright.config.js  e2e testleri (backend+frontend'i webServer olarak başlatır)
  e2e/                  smoke.spec.js + fixtures/ (büyük-grafik regresyon testi dahil)
  app/
    page.js             Ana sayfa (durum yönetimi + orkestrasyon)
    components/         Header, ControlPanel, TabBar, TimeRangeSlider,
                        MetricCards, SpannerView, CompareView,
                        TrendsView, ExploreView, GraphViewer,
                        ConcordanceView (istemci-taraflı KWIC/bağlam),
                        LeftSidebar, RightSidebar, LoadingSkeleton,
                        TruncatedWarning
    lib/                api.js (API istemcisi), utils.js (formatTime, BK, renk),
                        palette.js (dataviz paleti, tek kaynak klik rengi)
    public/             sample.conllu (örnek derlem)

backend/
  main.py               FastAPI uygulaması, CORS (.env'den), logging, middleware
  middleware.py          MaxBodySizeMiddleware, RateLimitMiddleware
  models.py             Pydantic modelleri
  routers/              spanner, trends, compare, explore endpoint'leri
  services/
    graph_builder.py    CSV/JSON/CoNLL-U/VRT ayrıştırma, çoklu birliktelik
                        ölçütü (NPMI/log-likelihood/Dice/t-score)
    graph_utils.py      Bron–Kerbosch (Tomita pivot + bütçe + budama)
    spanner_service.py  Pipeline orkestratörü (doğrulama opsiyonel)
    trend_analyzer.py   Zaman pencereli klik evrimi (bisect + Jaccard)
    corpus_parser.py    CoNLL-U / VRT format ayrıştırıcı (+ HEAD/DEPREL,
                        ham cümle metni)
    lemmatizer.py       Tembel yüklenen Zeyrek/TRmorph Türkçe kök indirgeyici
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
- **Lemma CoNLL-U/VRT'de zaten kullanılıyor:** `corpus_parser.py` her iki
  formatta da LEMMA sütununu (varsa) ham FORM'a tercih eder — çekim
  varyantlarının ("kitabı"/"kitaptan") ayrı düğüm olması bu formatlarda
  zaten önlenmiş durumda. CSV/JSON'da lemma/POS bilgisi hiç yok (ham kelime
  + Türkçe stopword listesi) — bu formatlar için `lemmatize` seçeneği
  aşağıda ayrıca ele alınıyor.
- **PMI eşiği artık gerçekten çalışıyor:** `/api/upload` bir `pmi_threshold`
  form alanı kabul eder (varsayılan `0.15`, NPMI [-1,1] ölçeğinde), yükleme
  anında hangi çiftlerin kenar olacağını belirler. Yükleme sonrası
  spanner/compare uçları bu sabitlenmiş kenarlar üzerinden çalışır —
  eşiği değiştirmek dosyayı yeniden yüklemeyi gerektirir.
- **Pencere-içi (per-window) PMI yeniden hesaplanıyor:** `/api/upload`
  ham `(tarih, kelimeler)` satırlarını da (`raw_documents`) döndürür;
  istemci bunu state'te tutup `/api/trends` ve `/api/word-cliques`'e geri
  gönderir. Bu uçlar, sağlanırsa, `graph.edges`'i zaman dilimlerine
  bölmek yerine her pencerenin NPMI'sini kendi dokümanlarından bağımsız
  hesaplar (`trend_analyzer.compute_npmi` çağrısı) — bir çift küresel
  olarak eşiği geçemese bile tek bir zaman diliminde güçlü şekilde
  anlamlı olabilir (ya da tersi). Backend durumsuz kalır: sunucu tarafında
  oturum/önbellek yoktur (bkz. `test_upload_response_has_no_dead_session_id_field`),
  `raw_documents` boş/eksik gönderilirse eski küresel-kenar-dilimleme
  davranışına geri düşülür.
- **Çoklu birliktelik ölçütü:** `compute_association_measures` her çift için
  NPMI + log-likelihood (G², Dunning 1993) + Dice + t-score'u tek geçişte
  hesaplar; `association_measure` (upload formu + `/api/trends`/
  `/api/word-cliques`) hangisinin kenar/kapı görevi göreceğini seçer,
  diğer üçü yine de `EdgeSchema.scores`'ta saklanır (ExploreView'da
  gösterilir). Bir çiftin AYNI (u,v) kenarı birden çok dokümanda tekrar
  edebileceği için `scores` sadece İLK tekrara eklenir, sonrakiler `{}`
  (bkz. Büyük Derlem notu) — her tüketici zaten çifte göre dedup ediyor.
- **KWIC/bağlam:** `raw_documents`'ın her elemanı artık ham cümle metnini de
  (`text`) taşır — CoNLL-U'da `# text = ...` yorumu (yoksa FORM
  token'larının birleşimi), VRT'de FORM birleşimi, CSV/JSON'da filtrelenmemiş
  ham "words" hücresi. Tamamen istemci tarafında (`ConcordanceView.js`),
  yeni bir uç nokta gerekmeden kelime/çift aramasında bağlam gösterir.
- **Sözdizimsel (bağımlılık tabanlı) birliktelik:** `collocation_mode`
  (upload formu, varsayılan `"window"`) `"syntactic"` olursa, CoNLL-U'nun
  HEAD/DEPREL sütunlarındaki DOĞRUDAN ebeveyn-çocuk ilişkilerini kullanır
  (`graph_builder._dependency_pairs`) — aynı cümledeki HER çift yerine
  sadece örn. sıfat-isim/özne-yüklem gibi doğrudan bağımlı çiftler
  "doküman" sayılır (her bağımlılık kenarı, tam da o iki kelimeyi içeren
  kendi sözde-dokümanı olur — `compute_association_measures` mekanizması
  hiç değişmeden yeniden kullanılır). Sadece HEAD/DEPREL'i gerçekten
  taşıyan CoNLL-U dosyalarında çalışır; VRT/CSV/JSON'da veya HEAD sütunu
  boş bir CoNLL-U'da (örn. bu projenin kendi `sample.conllu`'su — sadece
  4 sütunlu: ID/FORM/LEMMA/UPOS) `/api/upload` 400 ile reddeder.
- **CSV/JSON için Türkçe kök indirgeme (Zeyrek):** `lemmatize` (upload
  formu, varsayılan kapalı — opt-in) açılırsa her kelime stopword
  filtresinden ÖNCE `backend/services/lemmatizer.lemmatize_tr` ile köküne
  indirgenir (örn. "kitaplar"→"kitap"), CoNLL-U/VRT'nin zaten sahip olduğu
  lemma-öncelikli davranışı bu formatlara da getirir. `raw_text` (KWIC
  için) lemmatize edilmeden, gerçek cümle olarak saklanır. Zeyrek/TRmorph
  analizörü **tembel yüklenir** (ilk `lemmatize=True` isteğine kadar hiç
  import edilmez) — ölçülen soğuk yükleme maliyeti ~2-3s (Render free
  plan 15dk boşta uykuya dalıyor, her uyanışta bu maliyeti tekrar tekrar
  ödememek için önemli); ısındıktan sonra kelime başına ~3ms. Kütüphanenin
  kendi debug log'ları (`logger.warning` — her analiz için düzinelerce
  satır) bastırılıyor, yoksa üretim loglarını doldururdu.

### Büyük Derlem (performans notları)

Sentetik ~5-27MB CoNLL-U dosyalarıyla ölçüldü (bkz. Faz 3):
- `/api/upload` + `/api/spanner` hızlı kalıyor (27MB'de bile ~10s) --
  ölçüm sırasında `scores`'un HER kenar tekrarına eklenmesinin (Faz 1'in
  ilk hali) 27MB'lik bir dosyada yanıtı 203MB'a şişirdiğini bulduk;
  sadece ilk tekrara eklemek 82MB'a indirdi (yukarıdaki not).
- **Gerçek darboğaz `/api/trends`'in pencere-içi yeniden hesabı**
  (`trend_analyzer._windows_from_raw_documents` → `compute_association_measures`):
  maliyeti korpus boyutuyla değil, doküman sayısı arttıkça aynı kelime
  dağarcığı içinde anlamlı hale gelen çift SAYISIYLA büyüyor (kelime
  dağarcığı sabitse ~O(V²)'ye doğru satüre olur). Ölçülen: 1.4MB (996
  doküman) → 99ms; 5.4MB (3984 doküman) → 2.8s; 11MB (7968 doküman) →
  13.5s. Bu, korpus boyutundan çok "kaç doküman, ne kadar dar bir
  dağarcıkla" sorusuna bağlı — dar dağarcıklı/çok tekrarlı derlemler
  küçük boyutta bile bu darboğaza çarpabilir. Şimdilik iyileştirilmedi
  (ölç-belgeleme kapsamı); bir sonraki adım `compute_association_measures`
  içindeki pencere-başına tam-çift-taraması olurdu.

## Ortam Değişkenleri

| Değişken | Amaç | Varsayılan |
|----------|------|------------|
| `CORS_ORIGINS` | İzin verilen origin'ler (virgülle) | `localhost:3004` |
| `SPANNER_VERIFY` | Spanner doğrulaması (`1`/`true`) | kapalı |
| `MAX_UPLOAD_BYTES` | Yükleme/istek gövdesi boyut limiti (byte) | `10485760` (10MB) — bkz. Büyük Derlem notu, Render free plan 512MB RAM |
| `RATE_LIMIT_PER_MINUTE` | IP başına dakikalık istek limiti (`0`=kapalı) | `30` |
| `LOG_LEVEL` | Backend log seviyesi | `INFO` |
| `NEXT_PUBLIC_API_URL` | Frontend API adresi | `http://127.0.0.1:8000` |

## Deployment

```bash
# Backend → Render (render.yaml)
git push origin main    # Render otomatik deploy eder

# Frontend → Vercel
cd frontend && vercel --prod
```
