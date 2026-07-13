# temporal-spanner-analyzer

Derlem dilbilimcileri için zamansal kavram evrimi analiz aracı.
Baligács (2026) "Temporal Cliques Admit Linear Spanners" implementasyonu.

CSV / JSON / CoNLL-U / VRT / TEI-XML → NPMI çizgesi → maksimal klikler → lineer spanner (≤ 7n) → trendler / karşılaştırma / keşif.

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
python -m pytest tests/ -v                      # 130 test
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
    corpus_parser.py    CoNLL-U / VRT / TEI-XML format ayrıştırıcı
                        (+ HEAD/DEPREL, ham cümle metni)
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
  boş bir CoNLL-U'da `/api/upload` 400 ile reddeder.
- **`sample.conllu` artık HEAD/DEPREL taşıyor.** Önceden 4 sütunluydu
  (ID/FORM/LEMMA/UPOS) — "Örnek Veri ile Dene" + "Sözdizimsel" birlikte
  denenince 400 alınıyordu. Dosyadaki "cümleler" gerçek cümle değil,
  tarih başına anahtar-kelime öbekleri olduğu için (bkz. dosyanın kendi
  başlık yorumu) elle, her tanınabilir bileşik öbeği (örn. "yapay zeka",
  "derin öğrenme") kendi zincirine ayırıp baş ismine `HEAD=0/root`
  vererek yeniden etiketlendi — bu basitleştirilmiş bir demo etiketlemesi,
  gerçek bir treebank çıktısı değil.
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
- **Zeyrek'in sessiz başarısızlığı görünür yapıldı.** `lemmatize_tr`
  bilerek Zeyrek'in üst-seviye `lemmatize()` metodunu DEĞİL, alt-seviye
  `analyze()` metodunu kullanıyor: `lemmatize()` tanımadığı bir kelime için
  sessizce kelimeyi kendi "lemma"sı gibi geri döndürüyor (bu yüzden
  "gerçekten analiz edildi mi" sinyali her zaman `True` çıkıyordu, tek
  istisna boş string). `analyze()` ise Zeyrek'in kendi `pos='Unk'`
  işaretini gösteriyor — `lemmatize_tr` artık `(lemma, analyzed)` döndürüyor,
  `analyzed=False` sadece gerçekten `Unk` (özel terim, yabancı kelime,
  sayı vb.) olduğunda. Noktalama gibi Zeyrek'in gerçekten tanıdığı ama
  köklenemeyecek şeyler (`pos='Punc'`) `analyzed=True` sayılır — bu bir
  başarısızlık değil. `UploadResponse.lemmatized_count`/`lemmatized_total`
  bu sayımı taşır; frontend "%X kelime köklendirildi" göstererek
  kullanıcının köklemeye ne kadar güvenebileceğini görmesini sağlar
  (`lemmatize=False` iken ikisi de 0).
- **Çoklu karşılaştırma düzeltmesi (Bonferroni/FDR).** Binlerce çift aynı
  anda test edilirken log-likelihood'un ki-kare kritik değerleriyle
  (3.84/6.63/10.83) "anlamlı" demek düzeltmesiz çoklu-test sorunu yaratır.
  `compute_association_measures` her çift için `p_value` (G²'nin serbestlik
  derecesi-1 ki-kare sağkalım fonksiyonu, kapalı form: `erfc(sqrt(G²/2))`
  — `math.erfc`, scipy YOK) hesaplar; tüm çiftler hesaplandıktan sonra
  `p_value_bonferroni` (`min(1, p*n)`) ve Benjamini-Hochberg `p_value_fdr`
  (q-değeri) eklenir. `n` = o hesaplamadaki test edilen çift sayısı (küresel
  çağrıda tüm korpus, pencereli çağrıda o pencere). Kapı/eşik davranışı
  DEĞİŞMEDİ — `association_measure=log_likelihood` hâlâ ham G² ile kapılanır;
  düzeltilmiş p-değerleri `adjacency_ratio` gibi salt bilgi amaçlı,
  ExploreView'da "(p<0.05, FDR: anlamlı/anlamlı değil)" olarak gösterilir.
- **MWE tespiti C-value ile derinleştirildi.** `adjacency_ratio` (yukarıda)
  sadece iki-kelimelik, "bitişik mi" ikili sinyaliydi.
  `graph_builder.extract_mwe_candidates` (Frantzi & Ananiadou 1996)
  2-4 kelimelik ardışık n-gram adaylarını C-value'ya göre sıralar — İÇ İÇE
  geçen adayları cezalandırır ("yapay zeka" hep daha uzun "yapay zeka
  modeli" içinde geçiyorsa düşük puan alır, kendi başına bağımsız bir birim
  olmadığının kanıtı). Yeni `/api/mwe-candidates` uç noktası
  `raw_documents` alır (upload anındaki `graph.edges` sadece ikili çiftlerle
  sınırlı, n-gram'lar için ham dokümanlara ihtiyaç var — `word-cliques` ile
  aynı desen). ExploreView'da ayrı bir "MWE Adayları" sekmesi; mevcut
  `adjacency_ratio` rozeti dokunulmadan kaldı (hafif, her-zaman-açık sinyal).
- **TEI/XML korpus format desteği eklendi** (`.xml`/`.tei`). Gerçek TEI
  dosyaları çok çeşitli olduğu için sadece iki yaygın alt-küme desteklenir:
  kelime-seviyeli (`<w lemma="..." pos="...">`, `<s>` cümle sınırlarıyla,
  CoNLL-U ile aynı ince tane) ve düz-metin (`<w>` yoksa her `<p>` — veya
  hiç yoksa tüm gövde — CSV/JSON gibi Türkçe stopword listesine düşen kaba
  tane). `xml.etree.ElementTree` (stdlib, yeni bağımlılık yok), ad alanı
  (namespace) farkında (`_local_name` ile `{...}` öneki soyulur). `@pos`
  sadece bilinen bir UPOS etiketiyse (`NOUN/VERB/...`) kullanılır — başka
  bir etiketleme şemasıysa (Penn Treebank `NN` gibi) her token'ı yanlışlıkla
  işlev-kelimesi sayıp elemek yerine `pos=""`'a (stopword geri düşüşü)
  düşülür. Tarih: en yakın `<date>` elementinin `@when`/`@from`/`@notBefore`
  değeri; kelime-seviyeli modda ağaçta yukarıdan aşağı taşınır (bir alt
  ağaçtaki güncelleme geri dönüş değeri ÜZERİNDEN üst çağrıya iletilir —
  düz bir string parametresi üzerinden DEĞİL, aksi halde `teiHeader`'daki
  bir tarih hiçbir zaman `<text>` kardeşine ulaşmazdı, gerçek bir hata
  olarak yakalandı). DesteklenMEyenler açıkça belirtildi: özel TEI
  şemaları, `@ana` gibi ayrı bir öznitelik-yapısı kütüphanesine işaret eden
  kelime-seviyeli etiketleme, apparatus criticus.
- **Güven aralıkları (bootstrap) — isteğe bağlı, tek çift için.** Binlerce
  çift için otomatik hesaplanırsa Faz A'nın `/api/trends` performans
  kazanımını geri alır diye BİLEREK opt-in tasarlandı:
  `graph_builder.bootstrap_confidence_interval(word_rows, w1, w2, measure,
  n_resamples=500)` dokümanları yerine koyarak yeniden örnekler, her
  örneklemde sadece O İKİ KELİME için ilgili ölçütü (npmi/log_likelihood/
  dice/t_score — `_bootstrap_pair_score`, `compute_association_measures`'ın
  formülleriyle aynı) yeniden hesaplar, %2.5/%97.5 persentillerini döndürür.
  Yeni `/api/pair-confidence` uç noktası `raw_documents` + `word1`/`word2`
  alır (`word-cliques`/`mwe-candidates` ile aynı "isteğe bağlı, raw_documents
  kullan" deseni) — `{lower, upper, point_estimate}` döndürür. ExploreView'da
  Kelime Klikleri sekmesinin her çift satırına "güven aralığı hesapla"
  düğmesi eklendi; tıklanınca sadece o çift için istek atılır (korpus
  yüklenirken veya her arama sonucunda OTOMATİK hesaplanmaz).

### Büyük Derlem (performans notları)

Sentetik ~5-27MB CoNLL-U dosyalarıyla ölçüldü (bkz. Faz 3):
- `/api/upload` + `/api/spanner` hızlı kalıyor (27MB'de bile ~10s) --
  ölçüm sırasında `scores`'un HER kenar tekrarına eklenmesinin (Faz 1'in
  ilk hali) 27MB'lik bir dosyada yanıtı 203MB'a şişirdiğini bulduk;
  sadece ilk tekrara eklemek 82MB'a indirdi (yukarıdaki not).
- **`/api/trends` yavaşlığının asıl kaynağı `compute_association_measures`
  DEĞİLDİ — düzeltme.** Önceki not bunu suçluyordu ama sadece uç noktanın
  toplam süresi ölçülmüştü, içeride nereye gittiği profillenmemişti.
  Gerçek `cProfile` ölçümü: 11MB'lik bir derlemde toplam sürenin **%70'i**
  `trend_analyzer.compute_trends`'in zaman-çizelgesi eşleştirme
  döngüsündeki `_jaccard` çağrılarındaydı (15.2 milyon çağrı) —
  `compute_association_measures` sadece %4'ünü, Bron-Kerbosch sadece %5'ini
  alıyordu. Kök neden: her pencerede her yeni klik, o ana kadar aktif
  KALAN HER zaman çizelgesiyle karşılaştırılıyordu (`O(klik × aktif
  çizelge)`), yüzlerce/binlerce klik ve çizelgeyle bu patlıyordu.
- **Düzeltme (davranış değişmeden):** bir zaman çizelgesi yeni klikle HİÇ
  kelime paylaşmıyorsa Jaccard skoru zaten 0 ve `best_score`'un başlangıç
  değeri olan 0.0'ı asla geçemez — yani zaten hiçbir zaman "en iyi eşleşme"
  olamazdı. `compute_trends` artık kelime→aday-çizelge ters-indeksi
  kullanıyor, sadece en az bir kelime paylaşan çizelgelerle karşılaştırıyor
  (matematiksel olarak eşdeğer, sonuç değişmiyor — bkz.
  `test_compute_trends_picks_best_jaccard_match_among_several_candidates`).
  Ölçülen kazanç: 11MB'de ~13.5s → ~2.5s (uç nokta genelinde, cProfile'siz).
- **`compute_association_measures`'a ayrıca bir `budget` parametresi
  eklendi** (`graph_utils.maximal_cliques`'in `DEFAULT_SEARCH_BUDGET` +
  `truncated` deseniyle aynı) — dar/tekrarlı bir kelime dağarcığı gerçekten
  `C(V,2)`'ye doyarsa diye bir güvenlik ağı. `/api/upload`'ın küresel
  çağrısı `budget=None` (sınırsız, zaten hızlı); `trend_analyzer`'ın
  pencere-başına çağrısı `WINDOW_ASSOCIATION_BUDGET=100_000` kullanır
  (27MB'lik en yoğun pencerede bile doğal tavan ~55K'da kalıyor, yani bu
  bütçe pratikte nadiren tetiklenir — sadece daha da uç durumlar için).
  Aşılırsa `TrendResponse.truncated` (zaten var olan alan, Bron-Kerbosch'un
  kendi kesintisiyle paylaşılıyor) `True` olur.
- 27MB'lik en uç durumda (aynı ~4400 kelimelik dağarcığın 20x tekrarı)
  hâlâ ~14-15s sürüyor — bu, gerçekten yoğun/örtüşen bir korpusun doğal
  maliyeti (Bron-Kerbosch + kalan Jaccard karşılaştırmaları), daha fazla
  iyileştirme (ör. pencere başına klik sayısını üstten sınırlamak) sonuç
  eksikliğine yol açacağı için bilinçli olarak bu turun kapsamı dışında
  bırakıldı.

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
