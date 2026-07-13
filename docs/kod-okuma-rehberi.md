
# Temporal Spanner Analyzer — Kod Okuma Rehberi & Sembol Sözlüğü

> Bu döküman, projeye sıfırdan hakim olmak isteyen bir yazılımcı için yazılmıştır.
> **Hedef**: Her matematiksel sembolü, her formülü ve her kod dosyasını "4 işlem" düzeyinde anlamak.
> **Sürüm**: Haziran 2026 — CoNLL-U/VRT desteği, Tailwind CSS, 37 test ile güncellendi.

---

## İçindekiler

1. [Sistem Mimarisi (Kuş Bakışı)](#1-sistem-mimarisi-kuş-bakışı)
2. [Tüm Semboller ve Kod Karşılıkları](#2-tüm-semboller-ve-kod-karşılıkları)
3. [Tüm Formüller ve 4 İşlem Düzeyinde Açıklamaları](#3-tüm-formüller-ve-4-işlem-düzeyinde-açıklamaları)
4. [Kod Okuma Sırası](#4-kod-okuma-sırası)
5. [Veri Akışı: CSV'den Spanner'a](#5-veri-akışı-csvden-spannera)
6. [Her Dosyanın Sorumluluğu](#6-her-dosyanın-sorumluluğu)

---

## 1. Sistem Mimarisi (Kuş Bakışı)

```
┌─────────────────────────────────────────────────────────────┐
│                      KULLANICI (HTTP)                       │
│  POST /upload  (CSV/JSON yükle)                             │
│  POST /spanner (spanner hesapla)                            │
│  POST /trends  (zaman akışı)                                │
│  POST /compare (iki grafik karşılaştır)                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│  backend/routers/spanner.py    (FastAPI endpoint'leri)      │
│    - upload_csv()              → dosyayı parse et           │
│    - compute_spanner()         → pipeline'ı çalıştır        │
│    - _compute_stretch_factor() → spanner kalitesini ölç     │
│    - _shortest_temporal_path_len() → BFS ile en kısa yol    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│  backend/services/              (İş mantığı)                │
│    graph_builder.py   → CSV/JSON → GraphSchema + PMI       │
│    spanner_service.py → Pipeline yöneticisi                  │
│    graph_utils.py     → Bron–Kerbosch klik bulma            │
│    trend_analyzer.py  → Zaman penceresinde trend analizi    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│  backend/algorithm/             (Saf algoritma)             │
│    temporal_graph.py → Nmin, Nmax, pos, BFS, yardımcılar   │
│    bi_clique.py      → clique → biclique dönüşümü          │
│    simple_star.py    → Yıldız spanner                       │
│    extended_star.py  → Genişletilmiş yıldız                 │
│    cut_crossing.py   → 3-hop-kesme-geçiş kontrolü           │
│    dismountability.py → Düğüm sökümü                       │
│    main_algorithm.py → Lemma 17 + özyineleme               │
│    clique_optimization.py → Ana giriş noktası               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│  spanner/                       (Çekirdek tipler + API)     │
│    types.py       → TemporalGraph, TemporalBiClique         │
│    core.py        → İthalat hub'ı (tüm algo'ları dışa açar) │
│    verify.py      → Spanner doğrulama                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Tüm Semboller ve Kod Karşılıkları

### 2.1 Veri Yapıları

| Sembol (Matematik) | Anlamı | Kod | Dosya |
|---|---|---|---|
| `G = (V, E, λ)` | Zamansal çizge | `TemporalGraph(V, label)` | `spanner/types.py:15` |
| `V` | Düğüm kümesi (köşeler) | `G.V : set[str]` | `spanner/types.py:17` |
| `E` | Kenar kümesi | Yok (label dict'inden türetilir) | — |
| `λ(e) ∈ ℝ` | Kenarın zaman etiketi | `G.label[(u,v)] : float` | `spanner/types.py:18` |
| `\|V\|` | Düğüm sayısı | `len(G.V)` | Python built-in |
| `\|E\|` | Kenar sayısı | `len(G.label)` | Python built-in |
| `B = (S, T, λ)` | Zamansal ikili-klik | `TemporalBiClique(S, T, label)` | `spanner/types.py:48` |
| `S` | Kaynak kümesi (sources) | `G.S : list[str]` | `spanner/types.py:49` |
| `T` | Hedef kümesi (targets) | `G.T : list[str]` | `spanner/types.py:50` |
| `(v_S, v_T)` | v'nin S ve T kopyaları | `f"{v}_S"`, `f"{v}_T"` | `bi_clique.py:13-14` |

**4 işlem karşılığı**: Düşün ki `TemporalGraph` bir sınıf. `V` = öğrencilerin künye numaraları. `label` = hangi iki öğrencinin aynı sırada oturduğu ve saat kaçta. `TemporalBiClique` = sınıf ikiye bölünmüş, sadece sol sıradakiler sağ sıradakilerle yan yana.

### 2.2 Fonksiyonlar

| Sembol | Anlamı | Kod | Dosya:Satır |
|---|---|---|---|
| `key(u,v)` | Kanonik kenar anahtarı | `_edge_key(u, v) → (str, str)` | `temporal_graph.py:7` |
| `Nmin(v, G)` | v'nin en erken komşusu | `Nmin(v, G) → VertexID` | `temporal_graph.py:14` |
| `Nmax(v, G)` | v'nin en geç komşusu | `Nmax(v, G) → VertexID` | `temporal_graph.py:26` |
| `pos(x, y, G)` | y'nin x'in sıralı komşuluk listesindeki yeri | `pos(v, u, G) → int` | `temporal_graph.py:36` |
| `label(v, u, G)` | (v,u) kenarının zaman etiketi | `label(v, u, G) → float` | `temporal_graph.py:11` |
| `Star(s*)` | s* merkezli basit yıldız | `simple_star(s_star, G) → set[Edge]` | `simple_star.py:22` |
| `Ext(s*)` | s* merkezli genişletilmiş yıldız | `extended_star_s_star(s_star, G) → set[Edge]` | `extended_star.py:37` |

### 2.3 Nmin ve Nmax — En Önemli İki Fonksiyon

**Kod** (`temporal_graph.py:14-25`):
```python
def Nmin(v, G):
    # v'nin tüm komşularını bul
    # label(v, w, G) değeri EN KÜÇÜK olanı seç
    return min(candidates, key=lambda w: label(v, w, G))

def Nmax(v, G):
    # v'nin tüm komşularını bul
    # label(v, w, G) değeri EN BÜYÜK olanı seç
    return max(candidates, key=lambda w: label(v, w, G))
```

**4 işlem örneği**:
```
V = {Ali, Veli, Ayşe}
Kenarlar:
  Ali-Veli:   2020   ← en eski (Nmin)
  Ali-Ayşe:   2023
  Veli-Ayşe:  2025   ← en yeni (Nmax)

Nmin(Ali)   = Veli    (çünkü 2020 < 2023)
Nmax(Ali)   = Ayşe    (çünkü 2023 > 2020)
Nmin(Veli)  = Ali     (çünkü 2020 < 2025)
Nmax(Veli)  = Ayşe    (çünkü 2025 > 2020)
```

### 2.4 pos() — Sıralama Fonksiyonu

**Kod** (`temporal_graph.py:36-42`):
```python
def pos(v, u, G):
    neighbors = v'nin tüm komşuları (kenarı olanlar)
    neighbors.sort(key=lambda w: label(v, w, G))   # zamana göre sırala
    return neighbors.index(u)                      # u kaçıncı sırada?
```

**4 işlem örneği**:
```
Ali'nin komşuları: Veli(2020), Ayşe(2023)
Zamana göre sıralı: [Veli(sıra=0), Ayşe(sıra=1)]

pos(Ali, Veli) = 0   (Veli, Ali'nin listesinde 0. sırada — en erken)
pos(Ali, Ayşe) = 1   (Ayşe, 1. sırada)
```

### 2.5 Kümeler, İşlemler, Sıralamalar

| İşlem | Matematik | Kod | Örnek |
|---|---|---|---|
| Kesişim | `A ∩ B` | `A & B` | `{1,2} & {2,3} = {2}` |
| Birleşim | `A ∪ B` | `A \| B` | `{1,2} \| {2,3} = {1,2,3}` |
| Fark | `A \ B` | `A - B` | `{1,2} - {2,3} = {1}` |
| Ayrık mı? | `A ∩ B = ∅` | `A.isdisjoint(B)` | `{1,2}.isdisjoint({3,4}) = True` |
| Alt küme | `A ⊆ B` | `A <= B` | `{1,2} <= {1,2,3} = True` |
| Eleman sayısı | `\|A\|` | `len(A)` | `len({1,2,3}) = 3` |

---

## 3. Tüm Formüller ve 4 İşlem Düzeyinde Açıklamaları

### 3.1 Maksimum Kenar Sayısı

**Formül**:
```
|E|max = C(n,2) = n × (n-1) / 2
```

**Kod Karşılığı** (`clique_optimization.py:47`):
```python
cap = len(G.V) * (len(G.V) - 1) // 2
```

**4 işlem anlatımı**:
> n kişilik bir grupta herkes herkesle tokalaşırsa kaç tokalaşma olur?
> 
> İlk kişi n-1 kişiyle tokalaşır.
> İkinci kişi (ilk hariç) n-2 kişiyle tokalaşır.
> ...
> Toplam = (n-1) + (n-2) + ... + 1 = n×(n-1)/2

**Örnek**: n=5 → 5×4/2 = 10 kenar

### 3.2 PMI (Pointwise Mutual Information)

**Formül**:
```
PMI(w1, w2) = log(  N × codf(w1,w2)  /  (df(w1) × df(w2))  )
```

| Sembol | Anlamı | Kodda Karşılığı |
|---|---|---|
| `N` | Toplam doküman sayısı | `N = len(word_rows)` |
| `df(w)` | w'yi içeren doküman sayısı | `df[w]` (document frequency) |
| `codf(w1,w2)` | w1 ve w2'nin birlikte geçtiği doküman sayısı | `codf[(w1,w2)]` (co-document frequency) |
| `log(...)` | Doğal logaritma | `math.log(...)` |

**Kod** (`graph_builder.py:70-80`):
```python
ratio = N * codf_val / (df[w1] * df[w2])
pmi[(w1,w2)] = math.log(ratio) if ratio > 0 else -float("inf")
```

**4 işlem anlatımı**:
> PMI, iki kelimenin "tesadüfen" mi yoksa "gerçekten" mi birlikte geçtiğini ölçer.
>
> Pay: iki kelimenin birlikte geçme sıklığı × toplam doküman
> Payda: her kelimenin tek başına geçme sıklıklarının çarpımı
>
> Oran > 1 ise: kelimeler tesadüften DAHA FAZLA birlikte geçiyor (anlamlı).
> Oran < 1 ise: kelimeler tesadüften DAHA AZ birlikte geçiyor (anlamsız).
> PMI > 0: pozitif ilişki. PMI < 0: negatif ilişki.

**Örnek**:
```
3 doküman:
  D1: yapay zekâ
  D2: yapay öğrenme  
  D3: yapay zekâ öğrenme

N = 3
df(yapay)   = 3  (tüm dokümanlarda geçiyor)
df(zekâ)    = 2  (D1, D3)
df(öğrenme) = 2  (D2, D3)

codf(yapay, zekâ) = 2  (D1, D3)
codf(yapay, öğrenme) = 2 (D2, D3)

PMI(yapay, zekâ) = log(3 × 2 / (3 × 2)) = log(1) = 0
PMI(yapay, öğrenme) = log(3 × 2 / (3 × 2)) = log(1) = 0
```

### 3.3 Kenar Kanonik Formu

**Formül**:
```
key(u,v) = (u,v) if u ≤ v else (v,u)
```

**Kod** (`temporal_graph.py:7-9`):
```python
def _edge_key(u: VertexID, v: VertexID) -> tuple[str, str]:
    a, b = str(u), str(v)
    return (a, b) if a <= b else (b, a)
```

**4 işlem anlatımı**:
> (Ali, Veli) ile (Veli, Ali) aynı kenardır. Hangisi geldiyse, küçük olanı önce yaz.
> (Ali, Veli) → Ali ≤ Veli? Evet → (Ali, Veli)
> (Veli, Ali) → Veli ≤ Ali? Hayır → (Ali, Veli)

### 3.4 Soruşturma/Katlama Faktörü (Stretch Factor)

**Formül**:
```
stretch = ortalama( d_spanner(u,v) / d_original(u,v) )
```

| Sembol | Anlamı | Kod |
|---|---|---|
| `d_original(u,v)` | Orijinal grafta en kısa yol | `_shortest_temporal_path_len(u, v, orig_edges)` |
| `d_spanner(u,v)` | Spanner'da en kısa yol | `_shortest_temporal_path_len(u, v, all_edges)` |

**Kod** (`routers/spanner.py:67-73`):
```python
for u, v in pairs:
    d_orig = _shortest_temporal_path_len(u, v, orig_edges)
    d_spanner = _shortest_temporal_path_len(u, v, all_edges)
    if d_orig and d_orig > 0:
        if d_spanner is None: continue  # yol yoksa atla
        total_ratio += d_spanner / d_orig
        pairs_checked += 1

return total_ratio / max(pairs_checked, 1)
```

**4 işlem anlatımı**:
> Spanner, kenar sayısını azaltır. Ama yollar uzayabilir.
> Örneğin: orijinalde A→C direkt (1 hop), spanner'da A→B→C (2 hop).
> Stretch = 2/1 = 2.0 — yani yollar 2 kat uzamış.
> 
> İdeal stretch = 1.0 (hiç uzama yok). İyi stretch < 2.0.

### 3.5 Jaccard Benzerliği

**Formül**:
```
J(A,B) = |A ∩ B| / |A ∪ B|
```

**Kod** (`trend_analyzer.py:10-14`):
```python
def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)
```

**4 işlem anlatımı**:
> İki kümenin ne kadar benzer olduğunu ölçer.
> Pay = ortak eleman sayısı
> Payda = toplam farklı eleman sayısı
>
> Örnek: A={elma, armut}, B={elma, muz}
>   |A∩B| = {elma} → 1
>   |A∪B| = {elma, armut, muz} → 3
>   J = 1/3 ≈ 0.33

### 3.6 Sökülebilirlik Koşulu (Observation 19)

**Koşul** — bir `v` düğümü şu durumda sökülebilir:

```
∃ u, w ∈ V:
  (1) v → Nmin(u) → u  geçerli bir zamansal yol
  (2) w → Nmax(w) → v  geçerli bir zamansal yol
```

**Kod** (`dismountability.py:53-69`):
```python
def is_12_hop_dismountable(v, G):
    for u in G.V:
        if u == v: continue
        nmin_u = Nmin(u, G)        # u'nun en erken komşusu
        if nmin_u == v: continue
        if is_temporal_path([v, nmin_u, u], G):   # (1) kontrol
            for w in G.V:
                if w in (v, u): continue
                nmax_w = Nmax(w, G)
                if nmax_w in (v, w): continue
                if is_temporal_path([w, nmax_w, v], G):  # (2) kontrol
                    return True, u, w
    return False, None, None
```

**4 işlem anlatımı**:
> Düşün ki v bir aktarmacı. v üzerinden giden tüm yollar, başka bir aktarmacı üzerinden de gidebiliyorsa, v gereksizdir.
>
> Koşul (1): v'den u'ya, u'nun en erken komşusu üzerinden gidilebiliyor.
> Koşul (2): w'dan v'ye, w'nin en geç komşusu üzerinden gidilebiliyor.
>
> İkisi de sağlanıyorsa v'yi sil, 4 yeni kenar ekle.

### 3.7 Söküm Sonrası Eklenen 4 Kenar

**Kod** (`dismountability.py:82-86`):
```python
E_add.add(_edge_key(v, Nmin(u, Gi)))      # v - Nmin(u)
E_add.add(_edge_key(Nmin(u, Gi), u))       # Nmin(u) - u
E_add.add(_edge_key(w, Nmax(w, Gi)))       # w - Nmax(w)
E_add.add(_edge_key(Nmax(w, Gi), v))       # Nmax(w) - v
```

### 3.8 BFS ile Zamansal Yol Bulma

**Kod** (`temporal_graph.py:73-94`):
```python
def exists_temporal_path_in_subgraph(start, end, allowed, G):
    # BFS kuyruğu: her eleman (düğüm, son_label) ikilisi
    q = deque()
    q.append((start, -float("inf")))
    visited = {(start, -float("inf"))}

    while q:
        v, last_lbl = q.popleft()
        if v == end:
            return True   # hedefe ulaştık!
        
        # v'nin tüm komşularını dene
        for w in adj.get(v, []):
            l = label(v, w, G)          # kenarın zamanı
            if l >= last_lbl:           # zaman azalmamalı!
                if (w, l) not in visited:
                    visited.add((w, l))
                    q.append((w, l))
    return False
```

**4 işlem anlatımı**:
> BFS = kuyruk. Başlangıç düğümünü kuyruğa koy.
> Kuyruktan bir düğüm al. Komşularına bak.
> Her komşuya giden kenarın zamanı, son görülen zamandan KÜÇÜK DEĞİLSE (yani zaman ileri akıyorsa) o komşuyu kuyruğa ekle.
> Hedefe ulaştıysan True dön. Kuyruk bittiyse False.

### 3.9 3-Hop-K-Kesme-Geçişi (Lemma 16)

**Kod** (`cut_crossing.py:10-30`):
```python
def is_3_hop_k_cut_crossing(s_i, i, k, t_i, s_star, T_ord, G):
    if i <= k: return False
    
    for t in G.T:
        v = Nmax(t, G)
        # Koşul 1: pos(t_i, s_i) ≤ pos(t_i, v)
        if not (pos(t_i, s_i, G) <= pos(t_i, v, G)): continue
        
        for j_idx in range(k + 1):
            t_j = T_ord[j_idx]
            # Koşul 2: pos(v, t_i) ≤ pos(v, t_j)
            if not (pos(v, t_i, G) <= pos(v, t_j, G)): continue
            # Koşul 3: pos(t_j, v) ≤ pos(t_j, s_star)
            if not (pos(t_j, v, G) <= pos(t_j, s_star, G)): continue
            return True
    return False
```

**4 işlem anlatımı**:
> `s_i` düğümü, `k` indeksini "kesip geçebiliyor" mu?
> 
> 3 koşulun hepsi sağlanıyorsa, şu yol geçerlidir:
> ```
> s_i → t_i → v → t_j → s_star
> ```
> (her ok bir zamansal kenar, zamanlar artarak gidiyor)
>
> Bu yol sayesinde `s_i`, `s_star`'a 3 hopta ulaşabilir.
> Algoritma bu kenarları spanner'a ekler ve devam eder.

### 3.10 Lemma 17 — Cover Set Seçimi

**Özyineleme formülü**:
```
Lemma 17(G):
  Eğer |S| < 3:
    tüm kenarları ekle, bitir
  
  k = |S| / 2 (yuvarlak aşağı)
  
  Tüm i > k için crossing mi?
  
  EVET ise (case i):
    E* = Star(s*) + 3-hop yolları + Emax
    Kalan = (S, T[0:k])   → özyinele
    
  HAYIR ise (case ii):
    E* = Ext(s*) ∪ Ext(t_i)
    Kalan = (S[k+1:], T)  → özyinele
```

**Kod** (`main_algorithm.py:10-57`):
```python
def lemma17_find_cover(G):
    n = len(G.S)
    if n < 3:   # taban durumu
        return all_edges, "trivial", G.S, G.T
    
    k = n // 2
    s_star = G.S[0]
    S_ord, T_ord = s_star_ordering(s_star, G)
    
    # Tüm i > k için crossing kontrolü
    if all_crossing:
        E_star = simple_star(s_star, G) + crossing_paths + Emax
        return E_star, "S_Tprime", G.S, T_ord[:k]
    else:
        E_star = extended_star_s_star(s_star, G) | extended_star_t_star(t_i, G)
        return E_star, "Sprime_T", S_ord[k+1:], G.T
```

### 3.11 Toplam Kenar Sayısı Sınırı

**Teorem**: Her n düğümlü zamansal klik, en fazla 7n kenarlı bir spanner'a sahiptir.

```
|E_spanner| ≤ 7n
```

Sınırın kaynağı:
```
|E| =  |E_dismount|   +   |E_bc_spanner|
    ≤  4(n - n')      +   7·n'
    ≤  7n
```

| Adım | Kenar sayısı | Açıklama |
|---|---|---|
| {1,2}-hop sökümü | ≤ 4(n - n') | Her sökülen düğüm için 4 kenar |
| EM-ikili-klik spanner | ≤ 7n' (= 14·(n'/2)) | Teorem 18: 14·(n'/2) = 7n' |
| **Toplam** | **≤ 7n** | n' ≤ n olduğu için |

---

## 4. Kod Okuma Sırası

Projeyi anlamak için **8 aşamalı** okuma önerisi. Her aşama bir öncekine dayanır.

### Aşama 1: Veri Yapıları (5 dk)

**Dosyaları oku**: `spanner/types.py`

```
Neye bak: TemporalGraph ve TemporalBiClique sınıfları.
Neyi öğren: V (düğümler), label (kenar→zaman), S/T (biclique kümeleri).
Neyi anla: _canonicalize neden yapılır (kenar sıralaması, duplicate koruması).
```

**Kontrol sorusu**: `TemporalGraph` ile `TemporalBiClique` arasındaki temel fark nedir?

<details>
<summary>Cevap</summary>
TemporalGraph'ta her düğüm çifti arasında kenar vardır (klik).
TemporalBiClique'te sadece S ve T kümeleri arasında kenar vardır.
</details>

### Aşama 2: Çizge Yardımcıları (10 dk)

**Dosyaları oku**: `backend/algorithm/temporal_graph.py`

```
Neye bak: Nmin, Nmax, pos, is_temporal_path, exists_temporal_path_in_subgraph.
Neyi öğren: Bu 5 fonksiyon, tüm algoritmanın yapı taşlarıdır.
Neyi anla: _edge_key ile kenarlar nasıl normalize edilir.
```

**Kontrol sorusu**: `pos(Ali, Veli, G)` ne döndürür?

<details>
<summary>Cevap</summary>
Ali'nin komşuları zamana göre sıralanır. Veli'nin bu sıradaki indeksini döndürür.
</details>

### Aşama 3: Veri Girişi (10 dk)

**Dosyaları oku**: `backend/services/graph_builder.py` (parse_csv, parse_json, compute_npmi)

```
Neye bak: CSV/JSON'den GraphSchema'ya dönüşüm.
Neyi öğren: PMI nasıl hesaplanır, stopwords nasıl filtrelenir.
Neyi anla: parse_label ile tarihler nasıl sayıya çevrilir.
```

**Kontrol sorusu**: PMI > 0 ne anlama gelir?

<details>
<summary>Cevap</summary>
İki kelime tesadüften daha sık birlikte geçiyor — anlamlı bir ilişki var.
</details>

### Aşama 4: Pipeline + Klik Bulma (10 dk)

**Dosyaları oku**: `backend/services/spanner_service.py`, `backend/services/graph_utils.py`

```
Neye bak: compute_spanner_pipeline, maximal_cliques (Bron–Kerbosch).
Neyi öğren: Pipeline sırası — label dict → cliques → her clique için spanner.
Neyi anla: _process_clique nasıl her klik için spanner hesaplar.
```

**Kontrol sorusu**: Bron–Kerbosch algoritması ne işe yarar?

<details>
<summary>Cevap</summary>
Bir çizgedeki tüm maksimal klikleri (herkesin herkesle bağlantılı olduğu alt kümeleri) bulur. Biz minimum 3 düğümlü klikleri arıyoruz.
</details>

### Aşama 5: Düğüm Sökümü (15 dk)

**Dosyaları oku**: `backend/algorithm/dismountability.py`

```
Neye bak: dismountability (biclique), is_12_hop_dismountable, dismountability_12_hop.
Neyi öğren: Hangi düğümler "gereksiz" kabul edilir.
Neyi anla: Söküm sonrası eklenen 4 kenarın mantığı.
```

**Kontrol sorusu**: Bir düğüm neden sökülebilir?

<details>
<summary>Cevap</summary>
v'den u'ya, u'nun en erken komşusu üzerinden ulaşılabiliyorsa VE
w'dan v'ye, w'nin en geç komşusu üzerinden ulaşılabiliyorsa,
v gereksizdir çünkü bağlantıları başka yollarla sağlanabilir.
</details>

### Aşama 6: Star Spannerları (15 dk)

**Dosyaları oku**: `backend/algorithm/simple_star.py`, `backend/algorithm/extended_star.py`

```
Neye bak: simple_star, extended_star_s_star, extended_star_t_star.
Neyi öğren: Yıldız spanner'ın temel yapısı (merkez + min/max kenarları).
Neyi anla: Extend index mantığı — hangi durumda ek kenar gerekir?
```

**Kontrol sorusu**: Simple star kaç kenar içerir?

<details>
<summary>Cevap</summary>
|S| + |T| - 1 = 2n - 1 kenar. |S| tane min kenar + |T| tane merkez kenarı - 1 (kesişim).
</details>

### Aşama 7: Kesme-Geçiş ve Özyineleme (20 dk)

**Dosyaları oku**: `backend/algorithm/cut_crossing.py`, `backend/algorithm/main_algorithm.py`

```
Neye bak: is_3_hop_k_cut_crossing, lemma16_check, lemma17_find_cover, 
          spanner_for_EM_biclique.
Neyi öğren: 3-hop-kesme-geçişi kontrolü nasıl çalışır.
Neyi anla: Lemma 17'deki iki durum (crossing / extended) ve özyineleme.
```

**Kontrol sorusu**: `spanner_for_EM_biclique` neden özyinelemeli?

<details>
<summary>Cevap</summary>
Lemma 17, biclique'in ya S tarafını ya T tarafını kapsar. Kapsanmayan kısım (en fazla n/2 boyutunda) kendi başına bir EM-biclique'tir ve aynı algoritmayla çözülür. Bu özyineleme, problem boyutu her adımda en az yarıya indiği için O(n)'de tamamlanır.
</details>

### Aşama 8: Ana Fonksiyon + API (10 dk)

**Dosyaları oku**: `backend/algorithm/clique_optimization.py`, `backend/routers/spanner.py`

```
Neye bak: spanner_for_clique, compute_spanner, _compute_stretch_factor.
Neyi öğren: Tüm algoritmanın birleştiği nokta.
Neyi anla: API'den kullanıcıya dönen metrikler (stretch, savings, verification).
```

---

## 5. Veri Akışı: CSV'den Spanner'a

```
CSV/JSON dosyası
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  graph_builder.py: parse_csv() / parse_json()               │
│                                                              │
│  1. Satırları oku, tarihleri parse et                        │
│  2. Stopwords'leri filtrele                                  │
│  3. PMI hesapla (hangi kelime çiftleri anlamlı?)             │
│  4. Kenarları oluştur (PMI eşik değerinin üstündekiler)     │
│  5. GraphSchema döndür (V + E)                              │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  spanner_service.py: compute_spanner_pipeline()              │
│                                                              │
│  1. _build_label_dict() → kenar sözlüğü oluştur             │
│  2. build_static_adj() → komşuluk listesi                    │
│  3. maximal_cliques() → tüm maksimal klikleri bul (≥3)      │
│  4. Her klik için:                                           │
│       _process_clique() → spanner_for_clique()               │
│  5. Klik dışı kenarları da spanner'a ekle                    │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  clique_optimization.py: spanner_for_clique()                │
│  (her bir klik için ÇALIŞIR)                                 │
│                                                              │
│  1. dismountability_12_hop() → gereksiz düğümleri çıkar     │
│  2. EM dönüşümünü dene (V⁻, V⁺ partition mu?)               │
│                                                              │
│  ┌─── EVET ise ──────────────────────────────────────────┐  │
│  │  EM-biclique oluştur → spanner_for_EM_biclique()      │  │
│  │    → lemma17_find_cover() → cover set                  │  │
│  │    → dismountability() → düğüm sökümü                 │  │
│  │    → özyineleme (kalan alt-problem)                   │  │
│  │    → kenarları birleştir ve döndür                    │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─── HAYIR ise ─────────────────────────────────────────┐  │
│  │  clique_to_biclique() → tüm düğümleri S/T kopyala     │  │
│  │  spanner_for_biclique() → biclique spanner'ı          │  │
│  │  projeksiyon ile clique kenarlarına çevir             │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  3. Kenar sayısı sınırını kontrol et (cap)                  │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  routers/spanner.py: compute_spanner()                      │
│                                                              │
│  1. Pipeline çıktısını al                                    │
│  2. İstatistikleri hesapla (savings, stretch, bound, ...)   │
│  3. SpannerResponse olarak döndür                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Her Dosyanın Sorumluluğu

### Çekirdek (spanner/)

| Dosya | Sorumluluk | Okunma Önceliği |
|---|---|---|
| `types.py` | `TemporalGraph` ve `TemporalBiClique` veri yapıları | ⭐⭐⭐ |
| `core.py` | Tüm algoritma fonksiyonlarını dışa açar | ⭐ |
| `verify.py` | Spanner'ın doğruluğunu kontrol eder | ⭐⭐ |

### Algoritma (backend/algorithm/)

| Dosya | Sorumluluk | Okunma Önceliği |
|---|---|---|
| `temporal_graph.py` | **Temel yardımcılar**: Nmin, Nmax, pos, BFS | ⭐⭐⭐ |
| `bi_clique.py` | Klik → biclique dönüşümü | ⭐⭐ |
| `simple_star.py` | Basit yıldız spanner | ⭐⭐ |
| `extended_star.py` | Genişletilmiş yıldız spanner | ⭐⭐ |
| `cut_crossing.py` | 3-hop-kesme-geçiş kontrolü | ⭐⭐⭐ |
| `dismountability.py` | Düğüm sökümü (biclique + clique) | ⭐⭐⭐ |
| `main_algorithm.py` | Lemma 17 + özyinelemeli EM-biclique spanner | ⭐⭐⭐ |
| `clique_optimization.py` | Ana giriş: `spanner_for_clique()` | ⭐⭐⭐ |

### Servisler (backend/services/)

| Dosya | Sorumluluk | Okunma Önceliği |
|---|---|---|
| `graph_builder.py` | CSV/JSON → GraphSchema + PMI | ⭐⭐ |
| `graph_utils.py` | Komşuluk listesi + Bron–Kerbosch | ⭐⭐ |
| `spanner_service.py` | Pipeline yöneticisi | ⭐⭐ |
| `trend_analyzer.py` | Zaman penceresinde klik trendleri | ⭐ |

### API (backend/routers/)

| Dosya | Sorumluluk | Okunma Önceliği |
|---|---|---|
| `spanner.py` | FastAPI endpoint'leri + stretch factor | ⭐⭐ |

### Önerilen Okuma Sırası (Kompakt)

```
Adım 1:  spanner/types.py              (5 dk — veri yapıları)
Adım 2:  temporal_graph.py             (10 dk — Nmin, Nmax, pos, BFS)
Adım 3:  graph_builder.py              (10 dk — CSV→grafik, PMI)
Adım 4:  graph_utils.py                (5 dk — klik bulma)
Adım 5:  spanner_service.py            (5 dk — pipeline)
Adım 6:  dismountability.py            (10 dk — düğüm sökümü)
Adım 7:  simple_star.py + extended_star.py (10 dk — yıldız spanner)
Adım 8:  cut_crossing.py               (10 dk — 3-hop-kesme-geçiş)
Adım 9:  main_algorithm.py             (15 dk — Lemma 17, özyineleme)
Adım 10: clique_optimization.py        (10 dk — ana fonksiyon)
Adım 11: routers/spanner.py            (5 dk — API + stretch)
─────────────────────────────────────────────────────
Toplam: ~95 dk
```

---

## Ek: Algoritma Akış Şeması

```
spanner_for_clique(G)
  │
  ├── dismountability_12_hop(G)
  │     │
  │     └── is_12_hop_dismountable(v, G)
  │           • (v, Nmin(u), u) zamansal mı?
  │           • (w, Nmax(w), v) zamansal mı?
  │           • EVET → v'yi sil, 4 kenar ekle, başa dön
  │
  ├── V_minus = {Nmin(v)}; V_plus = {Nmax(v)}
  │
  ├── Partition mı? (ayrık ve tümünü kapsıyor)
  │     │
  │     EVET ───────────────────────────── HAYIR
  │     │                                    │
  │     ▼                                    ▼
  │  EM-biclique                    clique_to_biclique(G)
  │     │                                    │
  │     ▼                                    ▼
  │  spanner_for_EM_biclique()      spanner_for_biclique()
  │     │                                    │
  │     ├── lemma17_find_cover()     ├── dismountability()
  │     │     ├── crossing mi?       ├── spanner_for_EM_biclique()
  │     │     │   EVET → Star(s*)    │
  │     │     │   HAYIR → Ext(s*)    │
  │     │     └── kalanı döndür      │
  │     ├── dismountability()        │
  │     └── özyinele (kalan)         │
  │                                    │
  └───────────── BİRLEŞTİR ◄──────────┘
```

---

## Sözlük (Türkçe → İngilizce → Kod)

| Türkçe | İngilizce | Kod | Açıklama |
|---|---|---|---|
| Düğüm | Vertex | `VertexID` (str) | Çizgenin temel birimi (bir kelime) |
| Kenar | Edge | `(u,v)` ikilisi | İki düğüm arası bağlantı |
| Zaman etiketi | Label / Timestamp | `float` | Kenarın zaman damgası |
| Klik | Clique | `set[str]` | Herkesin herkesle bağlantılı olduğu grup |
| İkili-klik | Biclique | `TemporalBiClique` | S ve T arasında tam bağlantı |
| Zamansal yol | Temporal path | `is_temporal_path()` | Zamanı azalmayan düğüm dizisi |
| Spanner | Spanner | `set[Edge]` | Bağlantıyı koruyan kenar alt kümesi |
| Söküm | Dismountability | `dismountability()` | Gereksiz düğümü çıkarma |
| Yıldız | Star | `simple_star()` | Tek merkeze bağlı kenarlar |
| Gerdirme | Stretch | `stretch_factor` | Yol uzamasının oranı |
| Tasarruf | Savings | `savings_pct` | Yüzde olarak kenar azalması |
| Doğrulama | Verification | `verify_spanner()` | Spanner'ın doğru olduğunu kontrol |
| Özyineleme | Recursion | Özyinelemeli fonksiyon çağrısı | Problemi küçülterek çözme |
| Kesme-geçiş | Cut-crossing | `is_3_hop_k_cut_crossing()` | 3 hopla eşiği aşma |
| Kapsama | Cover | `lemma17_find_cover()` | Bir kısmı spanner'la örtme |
