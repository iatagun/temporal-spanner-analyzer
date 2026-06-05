# Temporal Spanner Analiz Aracı — Proje Planı

**Dayanak**: Baligács (2026), *Temporal Cliques Admit Linear Spanners*, arXiv:2606.05156

> **Temel Fikir**: Zaman etiketli metin verisindeki kelime birlikteliklerini bir ağ (graph) olarak modelleyip, bu ağı **temporal clique → linear spanner** dönüşümüyle seyrelterek zamansal dilbilimsel trendleri keşfetmek.

---

## 1. Vizyon

Mevcut dil analiz araçları (Sketch Engine, CQPWeb, Voyant Tools) kelimelerin *statik* birlikteliğini analiz eder. **Eksik olan**: Zaman boyutu.

**Bu proje şunu ekler:**
- "2020'de şu 5 kelime birbiriyle sıkı bağlantılıydı, 2024'te dağılmış"
- "Yapay zekâ etrafındaki kelime kümesi 2023'te nasıl oluşmaya başladı?"
- "Pandemi öncesi ve sonrası hangi kavram kümeleri değişti?"

### Benzersiz Değer Önerisi

Baligács (2026) makalesindeki **teoremi** (her temporal clique O(n) boyutunda spanner'a sahiptir) **interaktif, görsel, web tabanlı bir ürüne** dönüştüren ilk araç. Makaledeki algoritmanın çalışan bir implementasyonu + görsel arayüzü.

---

## 2. Teorik Altyapı (Sade Anlatım)

### 2.1. Zamansal Graf Nedir?

Her kenarın üzerinde **zaman damgası** olan graftır. Kenarların zamanları *azalmayan* sırada takip edilebiliyorsa, bu **zamansal bir yol**dur.

Örnek:
```
yapay ──2020──▶ zekâ ──2021──▶ öğrenme
```
Bu zamansal bir yol çünkü 2020 ≤ 2021.

### 2.2. Temporal Clique

Bir düğüm kümesinde **her ikili (pair)** arasında zaman içinde *en az bir kere* bağlantı varsa, bu küme temporal clique'tir.

> **Statik cliqueden farkı**: Tüm bağlantıların *aynı anda* var olması gerekmez. Gerçek dil verisine çok daha uygundur — bir kelime grubu aynı dönemde kullanılır ama her cümlede tüm kelimeler bir arada olmayabilir.

### 2.3. Linear Spanner

n düğümlü bir temporal clique'te teorik olarak O(n²) kenar vardır. **Linear spanner**, bunların sadece O(n) tanesini seçerek şunu garanti eder:

> Spanner'daki kenarları kullanarak, orijinal ağdaki **herhangi iki düğüm arasında zamansal olarak geçerli bir yol** bulunabilir.

| n | Orijinal | Spanner | Tasarruf |
|---|:--------:|:-------:|:--------:|
| 10 | 45 | ~10 | %78 |
| 100 | 4.950 | ~100 | %98 |
| 1.000 | 499.500 | ~1.000 | %99.8 |

### 2.4. Makalenin Getirdiği Yenilik

2019'dan beri açık bir problem olan "her temporal clique lineer spanner'a sahip midir?" sorusu bu makaleyle **kanıtlanmıştır**. Yanıt: **Evet, 7n kenar yeterlidir.** (Alt sınır: 2n-4)

Bu proje, bu teorik sonucu **pratik, kullanılabilir bir araca** dönüştürecektir.

---

## 3. Makaledeki Temel Kavramlar

### 3.1. Zamansal Bi-Clique

Makale, temporal clique problemini **bi-clique** (çift-küme) üzerinde çözer:
- **S** = kaynaklar (sources)
- **T** = hedefler (targets)
- Her s ∈ S, t ∈ T arasında kenar var
- Amaç: Her kaynaktan her hedefe zamansal yol

Her temporal clique, bir bi-clique'e dönüştürülüp çözülebilir.

### 3.2. Extremally Matched (EM) Bi-Clique

Bazı indirgemeler sonrası elde edilen "temiz" yapı:
- |S| = |T| = n
- **Emin**: her s için en küçük etiketli komşu = mükemmel eşleme
- **Emax**: her s için en büyük etiketli komşu = mükemmel eşleme

### 3.3. Dismountability (İndirgenebilirlik)

Bir kaynak/hedef, spanner'a sadece 2 kenar ekleyerek graf dışı bırakılabiliyorsa **dismountable**'dır. Bu, problemi EM bi-clique'e indirger.

### 3.4. Simple Star

s* merkezli **basit yıldız** = Emin + s*'a bağlı tüm kenarlar (toplam 2n-1 kenar). Büyük bir altkümeyi zaten kapsar.

### 3.5. Extended Star (Genişletilmiş Yıldız)

s* merkezli **genişletilmiş yıldız** = Emin + Emax + s* kenarları + her kaynak için bir "extend index" kenarı (toplam ≤ 4n kenar).

### 3.6. k-Cut-Crossing Source

Belirli bir "kesiği" kısa yolla (≤3 hop) geçebilen kaynak. Bunlar sayesinde simple star'ın kapsamadığı bölgelere erişilir.

### 3.7. Shifted Matching Graph

Hiçbir 1-hop-k-cut-crossing kaynağı olmayan uç durum. Yine de lineer spanner'a sahiptir (farklı bir yapıyla).

### 3.8. Algoritmanın İskeleti

```
1. Grafı EM bi-clique'e indirge (dismountability ile)
2. Her adımda:
   a. s* seç, k = n/2
   b. Eğer tüm i > k kaynakları 3-hop-k-cut-crossing ise:
      → Simple star + crossing path'ler = (S, T') kapsanır
   c. Değilse, bir t_i bul:
      → Ext(s*) ∪ Ext(t_i) = (S', T) kapsanır
   d. Kapsanmayan parça için tekrar et (≤ n/2 boyut)
3. Derinlik ≤ log₂(n), her adımda ≤ 6n kenar
4. Toplam: ≤ 14n (bi-clique) veya 7n (clique)
```

---

## 4. Özellik Şartnamesi

### 4.1. MVP (Aşama 1)

- [ ] Kullanıcı CSV/JSON formatında zaman etiketli metin verisini yükler
- [ ] Minimum birliktelik frekansı eşiği belirler
- [ ] Zaman aralığı seçer (slider ile)
- [ ] O aralıktaki temporal ağ oluşturulur ve görüntülenir
- [ ] Temporal cliqueler renk kodlu gösterilir
- [ ] "Spanner'a geç" butonu ile seyreltilmiş görünüm
- [ ] Kenar sayısı karşılaştırması: orijinal vs spanner
- [ ] Stretch factor metrik gösterimi

### 4.2. Aşama 2 — Trend Dedektörü

- [ ] Zaman kaydırıcısını oynatınca ağın canlı güncellenmesi
- [ ] Clique'lerin zaman içinde doğum/büyüme/küçülme/ölüm grafiği
- [ ] Kelimelerin cliquelere katılma/ayrılma zamanları
- [ ] Zaman çizelgesi görünümü (Gantt benzeri)

### 4.3. Aşama 3 — Karşılaştırma

- [ ] İki farklı dönemin spanner'larını yan yana karşılaştırma
- [ ] İki farklı veri kümesini aynı dönemde karşılaştırma
- [ ] Clique benzerlik/fark metriği

### 4.4. Aşama 4 — Keşif Araçları

- [ ] Bir kelimenin zaman içinde hangi cliquelere girdiği/çıktığı
- [ ] "Şu kelimeler temporal clique mi?" sorgulama
- [ ] Clique bazlı frekans trendleri
- [ ] Dışa aktarım (JSON, CSV, GraphML, PNG)

---

## 5. Girdi Veri Formatı

### 5.1. Minimum Girdi Formatı (CSV)

```csv
tarih,kaynak,kelimeler
2020-01-05,haber1,"yapay,zekâ,teknoloji,gelecek"
2020-03-12,haber2,"yapay,zekâ,makine,öğrenme"
2021-06-18,haber3,"derin,öğrenme,sinir,ağ"
2022-04-22,haber4,"yapay,zekâ,derin,öğrenme"
```

### 5.2. Alternatif Formatlar

- **JSON**: Zengin metadata (POS, kaynak türü, vb.)
- **CoNLL-U**: cross_morph çıktısı ile uyumlu
- **GraphML / GEXF**: NetworkX dışa aktarım formatları

---

## 6. Veri Akışı

```
Kullanıcı
   │ CSV/JSON yükler, zaman aralığı seçer
   ▼
┌─────────────────────────────┐
│ 1. Veri Ön İşleme           │
│    • CSV/JSON ayrıştırma    │
│    • Lemma çıkarma          │
│    • Zaman normalizasyonu   │
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│ 2. Zamansal Ağ Oluşturma    │
│    G = (V, E, λ)            │
│    • V = tekil lemmalar     │
│    • E = birliktelik kenarı │
│    • λ(e) = zaman kümeleri  │
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│ 3. Algoritma (Makale)       │
│                             │
│ 3a. Bi-clique dönüşümü     │
│ 3b. Dismountability         │
│  → EM bi-clique             │
│                             │
│ 3c. Simple Star + k-cut     │
│     kontrolü                │
│     → crossing var mı?      │
│     ↓          ↓            │
│   Evet        Hayır         │
│   (Star +     (Extended     │
│    paths)     Stars)        │
│     ↓          ↓            │
│ 3d. Kapsanmayan kısmı       │
│     recursive çöz           │
│     (≤ n/2 boyut)           │
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│ 4. Görselleştirme           │
│    • Orijinal ağ            │
│    • Spanner karşılaştırma  │
│    • Clique renk kodlama    │
│    • Zaman kaydırıcı        │
│    • Metrik paneli          │
└─────────────────────────────┘
```

---

## 7. Algoritma Detayları (Makaleden)

### 7.1. Girdi: Zaman Etiketli Metin Verisi

Her döküman: `{tarih: d, kelimeler: [w₁, ..., wₖ]}`

### 7.2. Adım 1: Clique'ten Bi-Clique'e

Makale Lemma 4:
```
Verilen: temporal clique G = (V, λ), |V| = n
Oluştur: bi-clique G' = (S, T, λ')
  Her v ∈ V için:
    vS ∈ S (kaynak kopya)
    vT ∈ T (hedef kopya)
  Kenarlar:
    λ'(vS, vT) = 0
    λ'(vS, uT) = λ(v, u)  (v ≠ u)
```

### 7.3. Adım 2: Dismountability (Lemma 5)

```
G' = (S, T, λ') başlangıç
S' := S, T' := T, E' := ∅

Tekrarla:
  Eğer s' ∈ S' dismountable ise:
    (s, t) = dismount çifti
    S' := S' \ {s'}
    E' := E' ∪ {{s,t}, {s',t}}
  Eğer t' ∈ T' dismountable ise:
    (s, t) = dismount çifti
    T' := T' \ {t'}
    E' := E' ∪ {{s,t}, {s,t'}}

Sonuç: G[S', T'] extremally matched
       |E'| ≤ 2(|S|+|T| - |S'|-|T'|)
```

### 7.4. Adım 3: Ana Döngü — Lemma 17

```
G = (S, T, λ) extremally matched, n = |S| = |T|
s* ∈ S seç, k = ⌊n/2⌋

s*-ordered labeling:
  T = {t₀, ..., tₙ₋₁}: poss*(ti) artan sırada
  sᵢ = Nmin(tᵢ)

Tanımlar:
  S' = {s₀, ..., sₖ}
  T' = {tₖ, ..., tₙ₋₁}

Kontrol:
  Eğer HER sᵢ (i > k) için 3-hop-k-cut-crossing ise:
    → Star(s*) + 3|Scross| kenar → (S, T') kapsanır
    → 6n kenar, Durum (i)
  Yoksa:
    → ∃ i > k, sᵢ crossing DEĞİL
    → Ext(s*) ∪ Ext(tᵢ) → (S', T) kapsanır
    → 6n kenar, Durum (ii)
```

### 7.5. Adım 4: Recursive Çözüm (Theorem 18)

```
f(n): EM bi-clique için en hafif spanner boyutu

f(n) ≤ 6n + (3n - 4x) + f(x)
  x: kapsanmayan parçanın EM boyutu (≤ n/2)

Tümevarım: f(n) ≤ 14n (bi-clique)
          → clique için: 7n (Theorem 2)
```

### 7.6. Adım 5: Clique için Optimizasyon (Theorem 2)

```
G = (V, λ) temporal clique
→ {1,2}-hop dismountability ile V' ⊆ V ayıkla (4(n-n') kenar)
→ V⁻ = {Nmin(v): v∈V'}, V⁺ = {Nmax(v): v∈V'}
→ V⁻, V⁺ aynı boyutta, partition, EM bi-clique
→ 14·(n'/2) = 7n' kenar
→ Toplam: 7n' + 4(n-n') ≤ 7n
```

---

## 8. Teknik Mimari

### 8.1. Stack

| Katman | Teknoloji | Sebep |
|--------|-----------|-------|
| Backend | Python 3.10+ | NetworkX, numpy; ağ algoritmaları için en olgun ekosistem |
| API | FastAPI | Async, otomatik OpenAPI, Pydantic doğrulama |
| Ağ Kütüphanesi | NetworkX | Temel ağ yapıları |
| Spanner Algoritması | Custom Python | Makale algoritmasının birebir implementasyonu |
| Frontend | Next.js 16 | React, SSR, dosya yükleme |
| Ağ Görseli | Cytoscape.js | Büyük ağlar için canvas render |
| Zaman Grafikleri | D3.js | Zaman çizelgesi, trend grafikleri |
| Geçici Depolama | SQLite (MVP) → PostgreSQL | Oturum bazlı |

### 8.2. Proje Yapısı

```
temporal-spanner/
├── backend/
│   ├── main.py                    # FastAPI
│   ├── models.py                  # Pydantic modeller
│   ├── routers/
│   │   ├── upload.py              # Veri yükleme
│   │   ├── network.py             # Ağ oluşturma
│   │   ├── spanner.py             # Spanner hesaplama
│   │   └── trends.py              # Trend analizi
│   ├── algorithm/                 # ★ Makale algoritma implementasyonu
│   │   ├── __init__.py
│   │   ├── temporal_graph.py      # Zamansal graf veri yapısı
│   │   ├── bi_clique.py           # Clique ↔ Bi-clique dönüşüm (Lemma 4)
│   │   ├── dismountability.py     # Dismountability (Lemma 5)
│   │   ├── simple_star.py         # Simple star (Def 8)
│   │   ├── extended_star.py       # Extended star (Def 12, Lemma 13-14)
│   │   ├── cut_crossing.py        # k-cut-crossing tespiti (Lemma 16)
│   │   ├── main_algorithm.py      # Ana döngü (Lemma 17, Theorem 18)
│   │   └── clique_optimization.py # Clique optimizasyonu (Theorem 2)
│   ├── services/
│   │   ├── graph_builder.py       # CSV/JSON → zamansal graf
│   │   └── visualization_data.py  # Frontend için JSON
│   └── requirements.txt
├── frontend/
│   ├── pages/
│   │   ├── index.tsx              # Veri yükleme
│   │   ├── analysis.tsx           # Ana analiz
│   │   └── trends.tsx             # Trend görünümü
│   ├── components/
│   │   ├── NetworkGraph.tsx       # Cytoscape.js
│   │   ├── TimeSlider.tsx         # Zaman kaydırıcı
│   │   ├── CliqueTimeline.tsx     # D3.js zaman çizelgesi
│   │   └── MetricsPanel.tsx       # Metrik paneli
│   └── package.json
├── tests/
│   ├── test_algorithm/            # Algoritma birim testleri
│   │   ├── test_bi_clique.py
│   │   ├── test_dismountability.py
│   │   ├── test_simple_star.py
│   │   ├── test_extended_star.py
│   │   ├── test_cut_crossing.py
│   │   └── test_main_algorithm.py
│   └── test_integration.py
├── examples/
│   ├── pandemi_ornek.csv
│   └── teknoloji_ornek.csv
└── docs/
    └── algorithm.md
```

### 8.3. API Endpoint'leri

| Metot | Route | Girdi | Çıktı |
|-------|-------|-------|-------|
| `POST` | `/api/upload` | CSV/JSON | `session_id` + özet |
| `POST` | `/api/network` | `{session_id, start, end, min_freq}` | Ağ JSON |
| `POST` | `/api/spanner` | `{session_id, start, end}` | Spanner + metrikler |
| `GET` | `/api/trends` | `{session_id}` | Zaman içinde clique evrimi |
| `GET` | `/api/cliques` | `{session_id}` | Tüm temporal cliqueler |
| `GET` | `/api/export` | `{session_id, format}` | Dosya indir |

---

## 9. Algoritma Modülü Detayı

`backend/algorithm/` içindeki her dosya, makaledeki bir bölüme karşılık gelir:

| Dosya | Makale | Açıklama |
|-------|--------|----------|
| `temporal_graph.py` | §2 | Zamansal graf veri yapısı, labeling, pos_v(u) |
| `bi_clique.py` | §2.2, Lemma 4 | Clique ↔ Bi-clique dönüşümü |
| `dismountability.py` | §2.3, Lemma 5 | Dismountability kontrolü ve indirgeme |
| `simple_star.py` | §3, Def 8 | Simple star + k-cut-crossing tespiti |
| `extended_star.py` | §4, Def 12, Lemma 13-14 | Extended star oluşturma, coverage |
| `cut_crossing.py` | §3-4, Lemma 16 | 3-hop-k-cut-crossing tespiti |
| `main_algorithm.py` | §4, Lemma 17, Theorem 18 | Ana recursive döngü |
| `clique_optimization.py` | §5, Theorem 2 | Clique için 7n optimizasyonu |

---

## 10. UI/UX

### 10.1. Veri Yükleme

```
┌──────────────────────────────────────────────┐
│  Temporal Spanner Analizi                     │
│                                               │
│  ┌──────────────────────────────────────┐    │
│  │    Dosyayı buraya sürükle/bırak      │    │
│  │    veya "Gözat" tıkla                │    │
│  │                                      │    │
│  │    Desteklenen: CSV, JSON            │    │
│  └──────────────────────────────────────┘    │
│                                               │
│  ── veya örnek veri dene ──                  │
│  [Pandemi] [Teknoloji] [Seçim Söylemleri]    │
└──────────────────────────────────────────────┘
```

### 10.2. Ana Analiz Ekranı

```
┌──────────────────────────────────────────────────────┐
│  pandemi_ornek.csv   [2020 ───●──── 2025]  [Min: 3]  │
├──────────────────────┬───────────────────────────────┤
│  ┌──────────────────┐│  Cliques [▼ 5]                │
│  │  AĞ (Cytoscape)  ││  ◉ virüs, aşı, bağışık,      │
│  │                  ││    varyant (4) 2022-2024      │
│  │ [Orijinal]       ││  ◉ karantina, maske,         │
│  │ [Spanner]        ││    mesafe (3) 2020-2021      │
│  │                  ││  ⋮                            │
│  └──────────────────┘│                               │
├──────────────────────┴───────────────────────────────┤
│  Zaman Çizelgesi                                      │
│  ┌─────────────────────────────────────────────┐     │
│  │ ████████░░░░████░░░░██████░░░░███████       │     │
│  │ 2020    2021    2022    2023    2024   2025  │     │
│  └─────────────────────────────────────────────┘     │
│  Düğüm: 342  Kenar: 2.891  Spanner: 412  ↑%85.7    │
│  Max Clique: 12  Stretch: 1.4  Süre: 0.34sn         │
└──────────────────────────────────────────────────────┘
```

### 10.3. Kullanıcı Akışı

1. Veri yükle veya örnek veri seç
2. Zaman aralığı + minimum frekans ayarla
3. "Analiz Et" → algoritma çalışır (arka planda)
4. Ağ görünür: renk kodlu temporal cliqueler
5. Spanner geçişi: kenar sayısındaki azalma vurgulanır
6. Clique tıkla: üyeler + zaman bilgisi
7. Zaman kaydırıcısını oynat: canlı güncelleme
8. Trend sekmesi: clique evrim grafiği

---

## 11. Somut Kullanım Senaryoları

### 11.1. Pandemi Dönemi Dil Değişimi

| Dönem | Temporal Clique | Ne Oldu? |
|-------|----------------|----------|
| 2019 öncesi | grip, mevsim, hastane | Normal küme |
| 2020 | **virüs, pandemi, karantina, maske, mesafe** | Yeni clique DOĞDU |
| 2021 | aşı, bağışık, delta, varyant, mRNA | Clique GENİŞLEDİ |
| 2022 | aşı, bağışık, varyant, endemi | Eski üyeler DÜŞTÜ |
| 2023+ | aşı, grip, mevsim, hastane | Kalıcı üyeler STABİL |

### 11.2. Teknoloji Trendleri

| Yıl | Clique Üyeleri |
|-----|----------------|
| 2018 | yapay, zekâ, makine, öğrenme |
| 2020 | +derin, sinir, ağ, doğal, dil |
| 2022 | +büyük, model, dönüştürücü, üretken |
| 2024 | +sohbet, robot, ajan |

### 11.3. Diğer Uygulama Alanları

- **Siyaset**: Seçim dönemlerinde söylem kümeleri
- **Pazarlama**: Marka-kavram trendleri
- **Akademik**: Bir alandaki anahtar kavram evrimi
- **Sosyal medya**: Hashtag kümelerinin birleşme/ayrılması
- **Tıp**: Semptom-tanı birlikteliklerinin zaman içinde değişimi

---

## 12. Rakiplerden Farkı

| Özellik | Sketch Engine | Voyant Tools | Bu Proje |
|---------|:---:|:---:|:---:|
| KWIC / Collocation | ✓ | ✓ | — |
| Word Sketch | ✓ | ✗ | — |
| Ağ (graph) görseli | ✗ | ✗ | **✓** |
| Temporal clique tespiti | ✗ | ✗ | **✓** |
| Linear spanner (makale algo.) | ✗ | ✗ | **✓** |
| Clique evrim animasyonu | ✗ | ✗ | **✓** |
| Kullanıcı kendi verisini yükler | ✗ | ✓ | **✓** |
| Algoritma doğrulama aracı | ✗ | ✗ | **✓** |

> **Konum**: Sketch Engine'in rakibi değil, *tamamlayıcısı*. Sketch Engine statik dilbilimsel analiz yaparken, bu araç **dinamik/zamansal ağ analizi** yapar.

---

## 13. Geliştirme Aşamaları

### Aşama 0 — Algoritma Prototipi (1-2 hafta)

**Tamamen makale odaklı.**

- [ ] Makaleyi satır satır oku, algoritma adımlarını çıkar
- [ ] `temporal_graph.py`: Zamansal graf veri yapısı
- [ ] `bi_clique.py`: Lemma 4 — clique ↔ bi-clique dönüşümü
- [ ] `dismountability.py`: Lemma 5 ile EM bi-clique'e indirgeme
- [ ] `simple_star.py`: Def 8 — simple star + k-cut-crossing
- [ ] `extended_star.py`: Def 12, Lemma 13-14 — extended star
- [ ] `cut_crossing.py`: Lemma 16 — 3-hop-k-cut-crossing tespiti
- [ ] `main_algorithm.py`: Lemma 17 + Theorem 18 — ana döngü
- [ ] `clique_optimization.py`: Theorem 2 — clique'te 7n
- [ ] **Sentetik doğrulama**: Rastgele grafikler üret, spanner'ın tüm yolları koruduğunu test et

**Çıktı**: Python script'i + sentetik test raporu

### Aşama 1 — MVP (3-4 hafta)

- [ ] FastAPI backend (upload, network, spanner endpoint'leri)
- [ ] CSV/JSON ayrıştırma + ağ oluşturma
- [ ] Next.js temel frontend + Cytoscape.js
- [ ] Orijinal ↔ Spanner karşılaştırma
- [ ] Zaman aralığı slider'ı
- [ ] Temel metrik paneli (kenar sayısı, tasarruf %)

### Aşama 2 — Trend (2-3 hafta)

- [ ] Clique evrim hesaplama
- [ ] D3.js zaman çizelgesi
- [ ] Canlı zaman kaydırma
- [ ] Clique listesi + detay paneli
- [ ] Örnek veri kümeleri

### Aşama 3 — Ürünleştirme (2-3 hafta)

- [ ] Dışa aktarma (JSON, CSV, GraphML, PNG)
- [ ] İki dönem/veri kümesi karşılaştırma
- [ ] Performans iyileştirmeleri
- [ ] Docker Compose
- [ ] Kullanıcı kılavuzu

---

## 14. Riskler

| Risk | Etki | Çözüm |
|------|------|-------|
| Algoritma NP-hard (Bron–Kerbosch) | Orta | Makale polinom zaman garantisi veriyor; zaman pencereli yaklaşım |
| Büyük veride ağ çok büyür | Yüksek | Top-N lemma, frekans filtreleme, pagination |
| Kullanıcı veri hazırlamayı bilemeyebilir | Orta | Örnek veriler, şablon indir, açık format |
| Konsept soyut gelebilir | Orta | İnteraktif onboarding, araç ipuçları |

---

## 15. Başarı Kriterleri

| Kriter | Hedef |
|--------|-------|
| Spanner kenar tasarrufu | ≥ %80 (gerçek veride) |
| Stretch factor (ortalama) | ≤ 2.0 |
| Performans (5k düğüm) | Tüm işlemler < 3 sn |
| Doğruluk | Spanner sonrası erişim kaybı %0 |
| Makale algoritması | Birebir doğru implementasyon |

---

## 16. Hemen Başlangıç

**İlk adım**: Aşama 0 — makale algoritmasını NetworkX'te dene.

```
temporal-spanner/
└── backend/algorithm/    ← önce bunu yaz
    ├── temporal_graph.py
    ├── bi_clique.py
    ├── dismountability.py
    ├── simple_star.py
    ├── extended_star.py
    ├── cut_crossing.py
    ├── main_algorithm.py
    └── clique_optimization.py
```

Her fonksiyon makaledeki bir lemma/teoreme karşılık gelir. Doğrulama: sentetik veride tüm yollar korunuyor mu?
