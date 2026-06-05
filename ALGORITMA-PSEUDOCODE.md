# Algoritma Pseudocode'u — Temporal Cliques Admit Linear Spanners

**Kaynak**: Baligács (2026), arXiv:2606.05156  
**Amaç**: Bu döküman, makaledeki tüm algoritma adımlarını implementasyona hazır pseudocode olarak verir.

---

## 1. Veri Yapıları

```
// ============================================================
// Temel tipler
// ============================================================

VertexID : integer veya string

// Zamansal graf: G = (V, E, λ)
// λ(e) = her kenar için zaman etiketi (gerçel sayı)
// Makale: her kenarın tek bir etiketi olduğunu varsayabiliriz
// (çoklu etiket varsa biri seçilir, spanner orijinal için de geçerlidir)

struct TemporalGraph:
    V: Set<VertexID>           // düğümler
    lambda: Map<(VertexID, VertexID), float>  // kenar → zaman

struct TemporalBiClique:
    S: List<VertexID>          // kaynaklar (sources)
    T: List<VertexID>          // hedefler (targets)
    lambda: Map<(VertexID, VertexID), float>  // her s∈S, t∈T arasında kenar var

// ============================================================
// Yardımcı fonksiyonlar
// ============================================================

// Makale §2.1: Her düğüm, komşularını zaman etiketine göre sıralar
// pos_v(u) = u'nun v'nin sıralamasındaki pozisyonu (0-indexed)
function pos(v: VertexID, u: VertexID, G: TemporalGraph) -> int:
    // v'ye bağlı tüm kenarları zaman etiketine göre sırala
    neighbors = [w for w in G.V if (v,w) in G.lambda or (w,v) in G.lambda]
    sort neighbors by G.lambda[(min(v,w), max(v,w))] ascending
    return index of u in sorted_neighbors

function Nmin(v: VertexID, G) -> VertexID:
    // v'nin en küçük zaman etiketli komşusu
    return argmin_{u∈N(v)} G.lambda[(min(v,u), max(v,u))]

function Nmax(v: VertexID, G) -> VertexID:
    // v'nin en büyük zaman etiketli komşusu
    return argmax_{u∈N(v)} G.lambda[(min(v,u), max(v,u))]

// İki düğüm arasındaki kenarın zaman etiketi
function label(v: VertexID, u: VertexID, G) -> float:
    return G.lambda[(min(v,u), max(v,u))]
```

---

## 2. Lemma 4 — Clique → Bi-Clique Dönüşümü

```
// ============================================================
// Girdi:  TemporalClique G = (V, λ), |V| = n
// Çıktı:  TemporalBiClique G' = (S, T, λ')
//         + projection fonksiyonu
//
// Makale §2.2, Lemma 4
// ============================================================

function clique_to_biclique(G: TemporalGraph) -> (TemporalBiClique, Map):
    S = []    // kaynak kopyalar
    T = []    // hedef kopyalar
    lambda_prime = empty_map
    projection = empty_map   // bi-clique kenarı → clique kenarı

    for each v in G.V:
        v_S = v + "_S"
        v_T = v + "_T"
        S.append(v_S)
        T.append(v_T)

        // v_S → v_T: label 0
        lambda_prime[(v_S, v_T)] = 0.0

    for each (v, u) where v != u in G.V:
        v_S = v + "_S"
        u_T = u + "_T"
        // v_S → u_T: orijinal clique'teki label
        lambda_prime[(v_S, u_T)] = G.lambda[(min(v,u), max(v,u))]

        projection[(v_S, u_T)] = (v, u)

    return (BiClique(S, T, lambda_prime), projection)

// Theorem 3 → Theorem 2 için:
// Her bi-clique spanner'ı, projection ile clique spanner'ına dönüşür.
// |E_spanner_clique| ≤ |E_spanner_biclique| ≤ 14n
```

---

## 3. Lemma 5 — Dismountability (İndirgenebilirlik)

```
// ============================================================
// Girdi:  TemporalBiClique G = (S, T, λ)
// Çıktı:  S' ⊆ S, T' ⊆ T (dismountable olmayanlar)
//         E' ⊂ E (dismount edilenler için eklenen kenarlar, ≤ 2n tane)
//         G[S', T'] extremally matched
//
// Makale §2.3, Lemma 5
// ============================================================

function dismountability(G: TemporalBiClique)
        -> (S', T', E'):

    S' = copy(G.S)
    T' = copy(G.T)
    E' = empty_set

    changed = true
    while changed:
        changed = false

        // --- Kaynak (source) dismountability ---
        // s ∈ S, t := Nmin(s)
        // Eğer ∃ s' ∈ S: pos_t(s') < pos_t(s) ise
        //   → s' dismountable via (s, t)
        //   → s' kaldır, {s,t} ve {s',t} ekle
        for each s in S':
            t = Nmin(s, subgraph(S', T'))
            for each s_prime in S':
                if s_prime == s: continue
                if pos(t, s_prime, subgraph(S', T'))
                 < pos(t, s, subgraph(S', T')):
                    // s' dismountable
                    S'.remove(s_prime)
                    E'.add( (s, t) )
                    E'.add( (s_prime, t) )
                    changed = true
                    break
            if changed: break

        if changed: continue

        // --- Hedef (target) dismountability ---
        // t ∈ T, s := Nmax(t)
        // Eğer ∃ t' ∈ T: pos_s(t') > pos_s(t) ise
        //   → t' dismountable via (s, t)
        for each t in T':
            s = Nmax(t, subgraph(S', T'))
            for each t_prime in T':
                if t_prime == t: continue
                if pos(s, t_prime, subgraph(S', T'))
                 > pos(s, t, subgraph(S', T')):
                    // t' dismountable
                    T'.remove(t_prime)
                    E'.add( (s, t) )
                    E'.add( (s, t_prime) )
                    changed = true
                    break
            if changed: break

    // Artık G[S', T'] extremally matched:
    //   • |S'| = |T'|
    //   • Emin = {{s, Nmin(s)} : s∈S'} mükemmel eşleme
    //   • Emax = {{s, Nmax(s)} : s∈S'} mükemmel eşleme
    return (S', T', E')
```

---

## 4. Definition 7 — Sıralı Etiketleme (Ordered Labeling)

```
// ============================================================
// s*-ordered labeling (Def 7a):
//   T = {t₀, ..., t_{n-1}}, pos_{s*}(t_i) artan sırada
//   s_i = Nmin(t_i)
//
// t*-ordered labeling (Def 7b):
//   S = {s₀, ..., s_{n-1}}, pos_{t*}(s_i) azalan sırada
//   t_i = Nmax(s_i)
// ============================================================

function s_star_ordering(s_star: VertexID, G: TemporalBiClique)
        -> (List<VertexID>, List<VertexID>):
    // T'yi pos_{s_star}'a göre artan sırala
    T_ordered = sort(G.T) by pos(s_star, t, G) ascending
    // Her t_i için s_i = Nmin(t_i)
    S_ordered = [Nmin(t_i, G) for t_i in T_ordered]
    return (S_ordered, T_ordered)

function t_star_ordering(t_star: VertexID, G: TemporalBiClique)
        -> (List<VertexID>, List<VertexID>):
    // S'yi pos_{t_star}'a göre azalan sırala
    S_ordered = sort(G.S) by pos(t_star, s, G) descending
    // Her s_i için t_i = Nmax(s_i)
    T_ordered = [Nmax(s_i, G) for s_i in S_ordered]
    return (S_ordered, T_ordered)
```

---

## 5. Definition 8 — Simple Star ve k-Cut-Crossing

```
// ============================================================
// Simple star (Def 8):
//   Star(s*) = Emin ∪ {s*'a bağlı tüm kenarlar}
//   Boyut: |Star(s*)| = n + (n-1) = 2n-1
//
// NOT: Emax Star'a dahil DEĞİL. Lemma 17 case (i)'de
// Emax ayrıca eklenir.
//
// k-cut-crossing source (Def 8ii):
//   s_i (i > k) m-hop-k-cut-crossing eğer:
//   ∃ j ≤ k, ∃ zamansal yol (uzunluk ≤ m+1)
//   s_i → ... → {t_j, s*} ile biten
//
// Makale §3, Observation 9
// ============================================================

function simple_star(s_star: VertexID, G: TemporalBiClique) -> Set<Edge>:
    edges = empty_set

    // Emin: {{s, Nmin(s)} : s∈S} = {{t, Nmin(t)} : t∈T} (EM'de)
    for each s in G.S:
        edges.add( (s, Nmin(s, G)) )

    // s_star'a bağlı tüm kenarlar (tüm hedeflere)
    for each t in G.T:
        edges.add( (s_star, t) )

    // Boyut: n (Emin) + n (s* kenarları) - 1 (kesişim) = 2n-1
    return edges

// ============================================================
// 3-hop-k-cut-crossing kontrolü (Lemma 16 tabanlı)
//
// s_i (i > k), 3-hop-k-cut-crossing MI?
//
// Lemma 16 ispatından:
//   s_i 3-hop-k-cut-crossing ⇔
//   ∃ j ≤ k, t ∈ T:
//     1. pos_{t_i}(s_i) ≤ pos_{t_i}(Nmax(t))   (s_i → t_i → Nmax(t))
//     2. pos_{Nmax(t)}(t_i) ≤ pos_{Nmax(t)}(t_j) (t_i → Nmax(t) → t_j)
//     3. pos_{t_j}(Nmax(t)) ≤ pos_{t_j}(s*)   (Nmax(t) → t_j → s*)
//
// Bu 3 eşitsizlik, (s_i, t_i, Nmax(t), t_j, s*) yolunun
// zamansal olduğunu garanti eder. BFS'e gerek yoktur.
// ============================================================

function is_3_hop_k_cut_crossing(
    s_i: VertexID, i: int, k: int,
    t_i: VertexID,                  // s*-ordered labeling'den T[i]
    s_star: VertexID,
    T_ord: List<VertexID>,          // s*-ordered T
    G: TemporalBiClique) -> bool:

    if i <= k: return false  // sadece i > k için

    // Lemma 16 ispatındaki 3 koşulu kontrol et:
    // ∃ j ≤ k, t ∈ T:
    //   (1) pos_{t_i}(s_i) ≤ pos_{t_i}(Nmax(t))
    //   (2) pos_{Nmax(t)}(t_i) ≤ pos_{Nmax(t)}(t_j)
    //   (3) pos_{t_j}(Nmax(t)) ≤ pos_{t_j}(s*)

    for each t in G.T:
        v = Nmax(t, G)

        // Koşul 1
        if not (pos(t_i, s_i, G) <= pos(t_i, v, G)):
            continue

        for j_idx in 0..k:
            t_j = T_ord[j_idx]

            // Koşul 2
            if not (pos(v, t_i, G) <= pos(v, t_j, G)):
                continue

            // Koşul 3
            if not (pos(t_j, v, G) <= pos(t_j, s_star, G)):
                continue

            return true  // 3-hop-k-cut-crossing

    return false

// ============================================================
// 3-hop crossing path bul (constructive)
//
// Lemma 16 garantisi: s_i crossing ise, (s_i, t_i, Nmax(t),
// t_j, s_star) yapısında bir zamansal yol vardır.
// Bu fonksiyon yolu bulup YENİ kenarlarını döndürür.
//
// Son kenar {t_j, s_star} Star(s*)'da zaten var olduğu
// için döndürülmez.
// ============================================================

function find_3_hop_crossing_path(
    s_i: VertexID, i: int, k: int,
    t_i: VertexID,
    s_star: VertexID,
    T_ord: List<VertexID>,
    G: TemporalBiClique) -> List<Edge>:

    for each t in G.T:
        v = Nmax(t, G)
        if not (pos(t_i, s_i, G) <= pos(t_i, v, G)):
            continue

        for j_idx in 0..k:
            t_j = T_ord[j_idx]

            if not (pos(v, t_i, G) <= pos(v, t_j, G)):
                continue
            if not (pos(t_j, v, G) <= pos(t_j, s_star, G)):
                continue

            // (s_i, t_i, v, t_j, s_star) yolunun
            // {t_j, s_star} dışındaki kenarlarını döndür
            return [
                (s_i, t_i),
                (t_i, v),
                (v, t_j)
            ]

    throw "3-hop crossing guaranteed by Lemma 16 but path not found"
```
```

---

## 6. Definition 12 — Extended Star (Genişletilmiş Yıldız)

```
// ============================================================
// Extended star (Def 12):
//
// Ext(s*) = Emin ∪ Emax ∪ {s*'ın kenarları}
//         ∪ { {s, t_ind(s)} : ind(s) tanımlı }
//
// Ext(t*) = Emin ∪ Emax ∪ {t*'nın kenarları}
//         ∪ { {s_ind(t), t} : ind(t) tanımlı }
//
// Boyut: ≤ 6n (her grup ≤ n kenar)
//
// Makale §4, Definition 12
// ============================================================

function extend_index_s_star(
    s: VertexID,           // s ∈ S \ {s_star}
    s_star: VertexID,
    S_ordered: List,       // s*-ordered labeling'den
    T_ordered: List,
    G: TemporalBiClique) -> int or undefined:

    // ind(s) = max{ l : pos_{t_l}(s) > pos_{t_l}(s_star) }
    // yani t_l sıralamasında s, s_star'dan SONRA geliyorsa
    // en büyük l'yi bul

    max_l = undefined
    for l in 0..len(T_ordered)-1:
        t_l = T_ordered[l]
        if pos(t_l, s, G) > pos(t_l, s_star, G):
            max_l = l

    return max_l  // undefined hiçbiri sağlamıyorsa

function extended_star_s_star(
    s_star: VertexID,
    G: TemporalBiClique) -> Set<Edge>:

    edges = empty_set

    // Emin
    for each s in G.S: edges.add( (s, Nmin(s, G)) )
    for each t in G.T: edges.add( (t, Nmin(t, G)) )

    // Emax
    for each s in G.S: edges.add( (s, Nmax(s, G)) )
    for each t in G.T: edges.add( (t, Nmax(t, G)) )

    // s_star'a bağlı tüm kenarlar
    for each t in G.T: edges.add( (s_star, t) )

    // Extend index kenarları
    (S_ord, T_ord) = s_star_ordering(s_star, G)
    for each s in G.S:
        if s == s_star: continue
        idx = extend_index_s_star(s, s_star, S_ord, T_ord, G)
        if idx is not undefined:
            edges.add( (s, T_ord[idx]) )

    return edges

// ============================================================
// t* merkezli extended star (simetrik)
// ============================================================

function extend_index_t_star(
    t: VertexID,           // t ∈ T \ {t_star}
    t_star: VertexID,
    S_ordered: List,       // t*-ordered labeling'den
    T_ordered: List,
    G: TemporalBiClique) -> int or undefined:

    // ind(t) = max{ l : pos_{s_l}(t) < pos_{s_l}(t_star) }
    max_l = undefined
    for l in 0..len(S_ordered)-1:
        s_l = S_ordered[l]
        if pos(s_l, t, G) < pos(s_l, t_star, G):
            max_l = l

    return max_l

function extended_star_t_star(
    t_star: VertexID,
    G: TemporalBiClique) -> Set<Edge>:

    edges = empty_set

    // Emin + Emax
    for each s in G.S: edges.add( (s, Nmin(s, G)) )
    for each t in G.T: edges.add( (t, Nmin(t, G)) )
    for each s in G.S: edges.add( (s, Nmax(s, G)) )
    for each t in G.T: edges.add( (t, Nmax(t, G)) )

    // t_star'a bağlı tüm kenarlar
    for each s in G.S: edges.add( (s, t_star) )

    // Extend index kenarları
    (S_ord, T_ord) = t_star_ordering(t_star, G)
    for each t in G.T:
        if t == t_star: continue
        idx = extend_index_t_star(t, t_star, S_ord, T_ord, G)
        if idx is not undefined:
            edges.add( (S_ord[idx], t) )

    return edges
```

---

## 7. Lemma 13, 14, 16 — Extended Star Coverage

```
// ============================================================
// Lemma 13(a): Ext(s*) coverage
//
// Nmax(t)'nin extend index'i tanımlı ve = i ise,
// Ext(s*) (s_j, t)'yi KAPSAR ∀ j ≤ i
//
// Kapsama: Ext(s*) içindeki kenarlarla s_j'den t'ye
// zamansal yol vardır.
// ============================================================

function extended_star_covers_source_to_target(
    ext_edges: Set<Edge>,    // Ext(s*)
    s: VertexID, t: VertexID,
    G: TemporalBiClique) -> bool:

    // ext_edges içinden s → ... → t zamansal yol var mı?
    return exists_temporal_path_in_subgraph(s, t, ext_edges, G)

// Lemma 13(a) somut yol:
// (s_j, t_j, s*, t_i, Nmax(t), t)
//  1. {s_j, t_j} = Emin (ext_edges'te)
//  2. {t_j, s*} = s* kenarı (ext_edges'te)
//  3. {s*, t_i} = s* kenarı (ext_edges'te)
//  4. {t_i, Nmax(t)} = extend index kenarı (ext_edges'te)
//  5. {Nmax(t), t} = Emax (ext_edges'te)

// ============================================================
// Lemma 14(a): Ext(s*) ile KAPSANMAMIŞSA
//
// Eğer Ext(s*) (s, t)'yi kapsamıyorsa:
//   pos_{Nmin(s)}(Nmax(t)) ≤ pos_{Nmin(s)}(s*)
//
// Lemma 14(b): Ext(t*) ile KAPSANMAMIŞSA
//
// Eğer Ext(t*) (s, t)'yi kapsamıyorsa:
//   pos_{Nmax(t)}(t*) ≤ pos_{Nmax(t)}(Nmin(s))
// ============================================================

// ============================================================
// Corollary 15:
//
// Eğer Ext(s*) ∪ Ext(t*) (s, t)'yi kapsamiyorsa:
//   (Nmin(t*), t*, Nmax(t), Nmin(s), s*) zamansaldır
// ============================================================

function check_corollary15(
    s: VertexID, s_star: VertexID,
    t: VertexID, t_star: VertexID,
    G: TemporalBiClique) -> bool:

    // (Nmin(t*), t*, Nmax(t), Nmin(s), s*) yolunu kontrol et
    v1 = Nmin(t_star, G)
    v2 = t_star
    v3 = Nmax(t, G)
    v4 = Nmin(s, G)
    v5 = s_star

    return is_temporal_walk([v1, v2, v3, v4, v5], G)

// ============================================================
// Lemma 16:
//
// s*-ordered labeling, k ∈ {0,...,n-2}
// Her i > k için:
//   YA (i) s_i 3-hop-k-cut-crossing
//   YA (ii) Ext(s*) ∪ Ext(t_i) (s_j, T)'yi kapsar ∀ j ≤ k
// ============================================================

function lemma16_check(
    i: int, k: int,
    s_star: VertexID,
    S_ord: List<VertexID>,
    T_ord: List<VertexID>,
    G: TemporalBiClique) -> (string, int or null):
    // Çıktı: ("crossing", null) veya ("extended", i)

    if i <= k:
        return ("extended", i)  // i ≤ k ise S' içinde, zaten kapsanıyor

    s_i = S_ord[i]
    t_i = T_ord[i]

    if is_3_hop_k_cut_crossing(s_i, i, k, t_i, s_star, T_ord, G):
        return ("crossing", null)

    // s_i crossing DEĞİL:
    // Lemma 16 → Ext(s*) ∪ Ext(t_i) (S', T)'yi kapsar
    return ("extended", i)

// Lemma 16 ispatı:
// Eğer (ii) sağlanmıyorsa → ∃ j ≤ k, t ∈ T: (s_j, t) kapsanmaz
// Corollary 15 → (s_i, t_i, Nmax(t), t_j, s_star) zamansal
// Bu da s_i'nin 3-hop-k-cut-crossing olduğu anlamına gelir.
```

---

## 8. Lemma 17 — Ana Cover Set Seçimi

```
// ============================================================
// Lemma 17:
//
// s* ∈ S, k = ⌊n/2⌋
// S' = {s₀, ..., s_k}
// T' = {t_k, ..., t_{n-1}}
//
// ∃ E* (≤ 6n kenar, Emin ∪ Emax içerir) öyle ki:
//
//   YA (i) E* (S, T') KAPSAR
//   YA (ii) E* (S', T) KAPSAR
//
// NOT: 6n = 2n (Emin+Emax) + n (s* kenarları) + n (extend)
//        + 2n (t_i kenarları)  toplamda 6n
// ============================================================

function lemma17_find_cover(
    G: TemporalBiClique) -> (Set<Edge>, string, List, List):
    // Çıktı: (E*, casus, S_kalan, T_kalan)
    // casus = "S_Tprime" veya "Sprime_T"
    // S_kalan, T_kalan: kapsanmayan kısım (recursive için)

    n = len(G.S)  // = len(G.T), EM bi-clique
    k = floor(n / 2)

    // Lemma 17: herhangi bir s* ∈ S seç
    s_star = G.S[0]  // s* = S[0] da olabilir, rastgele de

    (S_ord, T_ord) = s_star_ordering(s_star, G)
    // S_ord[0] = s* (EM'de s₀ = s*)
    // T_ord[i]: pos_{s*}(t) artan sırada
    // s_i = Nmin(t_i)

    S_prime = S_ord[0:k+1]      // {s₀, ..., s_k}, boyut: k+1
    T_prime = T_ord[k:n]       // {t_k, ..., t_{n-1}}, boyut: n-k = ⌈n/2⌉

    // === Durum (i): TÜM s_i (i > k) 3-hop-k-cut-crossing mi? ===
    all_crossing = true
    for i in k+1 .. n-1:
        (casus, _) = lemma16_check(i, k, s_star, S_ord, T_ord, G)
        if casus != "crossing":
            all_crossing = false
            break

    if all_crossing:
        // Lemma 17(i): Star(s*) + paths + Emax → (S, T') kapsanır
        E_star = simple_star(s_star, G)  // 2n-1 kenar

        // Her crossing source (i > k) için 3 yeni kenar ekle
        for i in k+1 .. n-1:
            s_i = S_ord[i]
            t_i = T_ord[i]
            path_edges = find_3_hop_crossing_path(
                s_i, i, k, t_i, s_star, T_ord, G)
            for each edge in path_edges:
                E_star.add(edge)

        // Emax (Lemma 17: E* contains Emin ∪ Emax)
        for each s in G.S: E_star.add( (s, Nmax(s, G)) )
        for each t in G.T: E_star.add( (t, Nmax(t, G)) )

        // |E*| = |Star(s*)| + 3|Scross| + |Emax|
        //       ≤ (2n-1) + 3·(n/2) + n ≤ 4.5n ≤ 6n ✓

        // Kalan: T \ T' = {t₀, ..., t_{k-1}}
        S_remain = copy(G.S)    // tüm S kapsandı ama...
        T_remain = T_ord[0:k]   // sadece T' dışındakiler kaldı
        return (E_star, "S_Tprime", S_remain, T_remain)

    else:
        // === Durum (ii): crossing OLMAYAN ilk s_i'yı bul ===
        for i in k+1 .. n-1:
            (casus, _) = lemma16_check(i, k, s_star, S_ord, T_ord, G)
            if casus == "extended":
                t_i = T_ord[i]

                // Lemma 17(ii): Ext(s*) ∪ Ext(t_i) → (S', T) kapsanır
                E_star = extended_star_s_star(s_star, G)
                E_star = E_star ∪ extended_star_t_star(t_i, G)

                // |E*| = 6 grup × ≤ n kenar = ≤ 6n ✓
                //   (Emin, Emax, s* kenarları, t_i kenarları,
                //    Ext(s*) ek kenarları, Ext(t_i) ek kenarları)

                // Kalan: S \ S' = {s_{k+1}, ..., s_{n-1}}
                S_remain = S_ord[k+1:n]
                T_remain = copy(G.T)  // tüm T kapsandı ama...
                return (E_star, "Sprime_T", S_remain, T_remain)

    // Lemma 17: ya (i) ya da (ii) her zaman sağlanır
    throw "Lemma 17 violated — unreachable"
```

---

## 9. Theorem 18 — EM Bi-Clique için Spanner (Recursive)

```
// ============================================================
// Theorem 18:
//
// Her extremally matched temporal bi-clique (S,T,λ), |S|=|T|=n
// için 14n boyutunda spanner vardır.
//
// Algoritma: Lemma 17 ile recursive, derinlik ≤ log₂(n)
//
// NOT: Bu fonksiyon SADECE extremally matched bi-clique için.
// Genel bi-clique için önce Lemma 5 (dismountability) uygulanır.
// ============================================================

function spanner_for_EM_biclique(
    G: TemporalBiClique) -> Set<Edge>:
    // G extremally matched, |S| = |T|

    n = len(G.S)
    if n <= 1:
        if n == 1:
            return {(G.S[0], G.T[0])}
        return empty_set

    // Lemma 17: cover set bul
    (E_star, casus, S_rem, T_rem) = lemma17_find_cover(G)

    // Kapsanmayan kısmı dismountability ile indirge
    // ve recursive çöz
    if casus == "S_Tprime":
        // (S, T') kapsandı, T \ T' kaldı
        // Altproblem: G_sub = G[S, T_rem]
        G_sub = induced_subgraph(G, G.S, T_rem)
        (S_sub, T_sub, E_dismount) = dismountability(G_sub)
        // S_sub, T_sub extremally matched, |S_sub| = |T_sub| ≤ n/2

        G_em = induced_subgraph(G, S_sub, T_sub)
        E_recursive = spanner_for_EM_biclique(G_em)

        return E_star ∪ E_dismount ∪ E_recursive

    else:  // casus == "Sprime_T"
        // (S', T) kapsandı, S \ S' kaldı
        G_sub = induced_subgraph(G, S_rem, G.T)
        (S_sub, T_sub, E_dismount) = dismountability(G_sub)

        G_em = induced_subgraph(G, S_sub, T_sub)
        E_recursive = spanner_for_EM_biclique(G_em)

        return E_star ∪ E_dismount ∪ E_recursive

// ============================================================
// Boyut analizi (makale Theorem 18 ispatı):
//
// f(n) = EM bi-clique için en hafif spanner
//
// f(n) ≤ 6n + (3n - 4x) + f(x)
//   • 6n: Lemma 17'deki E*
//   • (3n - 4x): dismountability kenarları
//   • x = |S_sub| ≤ n/2
//
// Tümevarım: f(n) ≤ 14n
//
// Base: f(1) = 1
// Adım: f(n) ≤ 9n - 4x + 14x = 9n + 10x ≤ 9n + 10(n/2) = 14n ✓
// ============================================================
```

---

## 9b. Theorem 3 — Genel Bi-Clique için Spanner (Wrapper)

```
// ============================================================
// Theorem 3:
//
// Her temporal bi-clique (S, T, λ) için
//   10·min(|S|,|T|) + 2·(|S|+|T|)
// boyutunda spanner vardır.
//
// Algoritma:
//   1. Lemma 5 (dismountability) ile EM bi-clique'e indirge
//   2. Theorem 18 ile EM spanner'ı hesapla
//   3. Dismount edilenlerin kenarlarını ekle
//
// Makale §2.3, Theorem 3 ispatı
// ============================================================

function spanner_for_biclique(G: TemporalBiClique) -> Set<Edge>:

    // Lemma 5: dismountability
    (S_prime, T_prime, E_dismount) = dismountability(G)
    // G[S_prime, T_prime] extremally matched
    // |E_dismount| ≤ 2(|S|+|T| - |S_prime| - |T_prime|)

    // Theorem 18: EM bi-clique spanner'ı
    G_em = induced_subgraph(G, S_prime, T_prime)
    E_em = spanner_for_EM_biclique(G_em)
    // |E_em| ≤ 14·|S_prime| = 14·|T_prime|

    // Birleştir
    E_total = E_dismount ∪ E_em

    // Boyut:
    // |E_total| ≤ 14|S_prime| + 2(|S|+|T| - 2|S_prime|)
    //           = 10|S_prime| + 2(|S|+|T|)
    //           ≤ 10·min(|S|,|T|) + 2(|S|+|T|)
    return E_total
```

---

## 10. Theorem 2 — Temporal Clique için Spanner (7n)

```
// ============================================================
// Theorem 2:
//
// Her temporal clique G = (V, λ), |V| = n
// için 7n boyutunda spanner vardır.
//
// Algoritma:
//   1. {1,2}-hop dismountability (Observation 19)
//   2. V⁻ = {Nmin(v)}, V⁺ = {Nmax(v)} → EM bi-clique (Theo 20)
//   3. 14·(n'/2) = 7n' kenar (Theorem 18)
//   4. Dismount edilenler: 4(n-n') kenar
//   5. Toplam: 7n' + 4(n-n') ≤ 7n
//
// Makale §5, Theorem 2 + Observation 19 + Theorem 20
// ============================================================

// ============================================================
// {1,2}-hop dismountability (Observation 19)
//
// v, {1,2}-hop dismountable eğer ∃ u, w:
//   • (v, Nmin(u), u) zamansal
//   • (w, Nmax(w), v) zamansal
//
// Böyle bir v varsa:
//   • v silinir
//   • 4 kenar eklenir: {v, Nmin(u)}, {Nmin(u), u},
//                       {w, Nmax(w)}, {Nmax(w), v}
// ============================================================

function is_12_hop_dismountable(
    v: VertexID,
    G: TemporalGraph) -> (bool, VertexID, VertexID):
    // Çıktı: (dismountable_mi, u, w)

    for each u in G.V:
        if u == v: continue
        // (v, Nmin(u), u) zamansal mı?
        if is_temporal_path([v, Nmin(u, G), u], G):
            for each w in G.V:
                if w == v or w == u: continue
                // (w, Nmax(w), v) zamansal mı?
                if is_temporal_path([w, Nmax(w, G), v], G):
                    return (true, u, w)

    return (false, null, null)

function dismountability_12_hop(
    G: TemporalGraph) -> (Set<VertexID>, Set<Edge>):
    // Çıktı: (V', E')
    // V' ⊆ V: {1,2}-hop dismountable olmayanlar
    // E': dismount edilenler için ek kenarlar

    V_prime = copy(G.V)
    E_prime = empty_set
    changed = true

    while changed:
        changed = false
        for each v in V_prime:
            (dism, u, w) = is_12_hop_dismountable(v, induced_subgraph(V_prime))
            if dism:
                V_prime.remove(v)
                // 4 kenar ekle
                E_prime.add( (v, Nmin(u, G)) )
                E_prime.add( (Nmin(u, G), u) )
                E_prime.add( (w, Nmax(w, G)) )
                E_prime.add( (Nmax(w, G), v) )
                changed = true
                break

    return (V_prime, E_prime)

// ============================================================
// Theorem 20:
//
// Eğer G'de {1,2}-hop dismountable yoksa:
//   V⁻ = {Nmin(v) : v ∈ V}
//   V⁺ = {Nmax(v) : v ∈ V}
//   |V⁻| = |V⁺|
//   V⁻, V⁺ partition oluşturur
//   G' = (V⁻, V⁺, λ) extremally matched bi-clique'tir
// ============================================================

function clique_to_EM_biclique(
    V_prime: Set<VertexID>,
    G: TemporalGraph) -> TemporalBiClique:

    // Theorem 20: Nmin/Nmax, G[V'] INDUCED subgraph'ında
    // hesaplanır (makale: "taken in G[V']")
    G_induced = induced_subgraph_clique(G, V_prime)

    // V⁻ = {Nmin(v) : v ∈ V'}
    V_minus = set()
    for each v in V_prime:
        V_minus.add(Nmin(v, G_induced))

    // V⁺ = {Nmax(v) : v ∈ V'}
    V_plus = set()
    for each v in V_prime:
        V_plus.add(Nmax(v, G_induced))

    // Theorem 20: V⁻ ve V⁺, V'yi partition eder
    // |V⁻| = |V⁺| = |V'|/2
    // NOT: Bu partition özelliği Theorem 20'nin GARANTİSİDir.
    // {1,2}-hop dismountable vertex kalmadığında otomatik sağlanır.

    // Bi-clique oluştur (label'lar ORİJİNAL G'den)
    lambda_bc = empty_map
    for each s in V_minus:
        for each t in V_plus:
            // s ve t, G'nin orijinal düğümleri
            // Aralarındaki kenar, clique'ta zaten var
            lambda_bc[(s, t)] = G.lambda[(min(s,t), max(s,t))]

    return TemporalBiClique(V_minus, V_plus, lambda_bc)

// Clique için induced subgraph yardımcısı
function induced_subgraph_clique(
    G: TemporalGraph,
    V_sub: Set<VertexID>) -> TemporalGraph:

    lambda_sub = empty_map
    for each (v, u) in G.lambda:
        if v in V_sub and u in V_sub:
            lambda_sub[(min(v,u), max(v,u))] = G.lambda[(v, u)]

    return TemporalGraph(V_sub, lambda_sub)

// ============================================================
// ANA FONKSİYON: spanner_for_clique (Theorem 2)
//
// Girdi:  TemporalClique G, |V| = n
// Çıktı:  E* ⊆ E, |E*| ≤ 7n
//         (V, E*) zamansal bağlı
// ============================================================

function spanner_for_clique(G: TemporalGraph) -> Set<Edge>:

    // Adım 1: {1,2}-hop dismountability
    (V_prime, E_dismount) = dismountability_12_hop(G)
    n_prime = len(V_prime)

    // Adım 2: V⁻, V⁺ → EM bi-clique (Theorem 20)
    G_bc = clique_to_EM_biclique(V_prime, G)

    // Adım 3: EM bi-clique spanner'ı (Theorem 18)
    E_bc_spanner = spanner_for_EM_biclique(G_bc)
    // |E_bc_spanner| ≤ 14 * (n_prime / 2) = 7 * n_prime

    // Adım 4: Bi-clique kenarlarını clique kenarlarına projection
    E_projected = set()
    for each (vS, vT) in E_bc_spanner:
        // vS ∈ V⁻, vT ∈ V⁺
        // clique'te karşılık gelen kenar: {vS, vT}
        E_projected.add( (vS, vT) )

    // Projeksiyon aynı zamanda G[V']'yi de kapsar
    // (Theorem 18: spanner aynı zamanda S∪T → S∪T kapsar)

    // Adım 5: Birleştir
    E_total = E_projected ∪ E_dismount

    // Boyut: ≤ 7n' + 4(n - n') ≤ 7n
    return E_total
```

---

## 11. Helper Fonksiyonlar (Yardımcılar)

```
// ============================================================
// Induced subgraph
// ============================================================

function induced_subgraph(
    G: TemporalBiClique,
    S_sub: Set<VertexID>,
    T_sub: Set<VertexID>) -> TemporalBiClique:

    lambda_sub = empty_map
    for each s in S_sub:
        for each t in T_sub:
            if (s, t) in G.lambda:
                lambda_sub[(s, t)] = G.lambda[(s, t)]

    return TemporalBiClique(S_sub, T_sub, lambda_sub)

// ============================================================
// Zamansal yol / walk kontrolü
// ============================================================

function is_temporal_path(
    vertices: List<VertexID>,
    G) -> bool:
    // vertices = [v₁, v₂, ..., v_k]
    // v₁→v₂→...→v_k yolunun zamansal olduğunu kontrol et
    // Kenar label'ları azalmamalı: l₁ ≤ l₂ ≤ ... ≤ l_{k-1}

    last_label = -inf
    for i in 0..len(vertices)-2:
        v = vertices[i]
        u = vertices[i+1]
        l = label(v, u, G)
        if l < last_label:
            return false
        last_label = l
    return true

function is_temporal_walk(
    vertices: List<VertexID>,
    G) -> bool:
    // Walk: tekrarlara izin var, ama label sırası aynı
    return is_temporal_path(vertices, G)  // aynı mantık

function exists_temporal_path_in_subgraph(
    start: VertexID, end: VertexID,
    allowed_edges: Set<Edge>,
    G) -> bool:
    // Sadece allowed_edges içindeki kenarları kullanarak
    // start'tan end'e zamansal yol var mı?
    // Temporal BFS (label azalmayan)

    queue = [(start, -inf)]
    visited = {(start, -inf)}

    while queue:
        (v, last_label) = queue.pop(0)
        if v == end:
            return true

        for each (a, b) in allowed_edges:
            if a == v and (v, b) in allowed_edges:
                l = label(v, b, G)
                new_state = (b, l)
                if l >= last_label and new_state not in visited:
                    visited.add(new_state)
                    queue.append(new_state)
            elif b == v and (b, a) in allowed_edges:
                l = label(v, a, G)
                new_state = (a, l)
                if l >= last_label and new_state not in visited:
                    visited.add(new_state)
                    queue.append(new_state)

    return false

// find_3_hop_crossing_path, §5'te tanımlandı
// (s_i, i, k, t_i, s_star, T_ord, G) imzasıyla
```

---

## 12. Örnek: Adım Adım Çalışma

```
// ============================================================
// ÖRNEK: 4 düğümlü temporal clique
//
// V = {a, b, c, d}
// Kenarlar (label ile):
//   a-b: 1, a-c: 2, a-d: 5
//   b-c: 3, b-d: 4
//   c-d: 6
//
// Adım 1: clique_to_biclique → S={a_S,b_S,c_S,d_S}, T={a_T,b_T,c_T,d_T}
// Adım 2: dismountability_12_hop
//         Nmin(a)=b, Nmax(a)=d
//         Nmin(b)=a, Nmax(b)=d
//         Nmin(c)=a, Nmax(c)=d
//         Nmin(d)=c, Nmax(d)=d
//         Kontrol: {1,2}-hop dismountable var mı?
//         → basit örnekte yok
// Adım 3: V⁻={b,a,a,c}, V⁺={d,d,d,d} → V⁻={a,b,c}, V⁺={d}
//         |V⁻|=3, |V⁺|=1 → EM değil
//         Aslında daha büyük örnekte partition olur.
//         Bu örnek 4 düğüm için fazla basit.
//
// ============================================================
// GERÇEKÇİ SENARYO: rastgele 100 düğümlü clique
//
// 1. clique_to_biclique → 200 düğüm (100 S + 100 T)
// 2. dismountability_12_hop → V' (diyelim 80 düğüm)
// 3. V⁻, V⁺ → 40'ar düğümlü EM bi-clique
// 4. Lemma 17: s* seç, k=20
//    • tüm i>20 crossing mi? kontrol et
//    • crossing → Star(s*) + paths + Emax
//    • değil → Ext(s*) ∪ Ext(t_i)
// 5. Kapsanmayan ≤ 20 düğüm için recursive
// 6. Sonuç: ~280 kenar (7n = 7×40 = 280)
// ============================================================
```

---

## 13. Doğrulama Testleri

```
// ============================================================
// Algoritmanın doğruluğunu test etmek için:
//
// 1. Rastgele temporal clique üret
// 2. Spanner hesapla
// 3. Spanner'da TÜM düğüm çiftleri arasında
//    zamansal yol olduğunu doğrula
// ============================================================

function verify_spanner(G: TemporalClique, E_spanner: Set<Edge>) -> bool:
    // Her (u,v) ∈ V×V için
    for each u in G.V:
        for each v in G.V:
            if u == v: continue
            if not exists_temporal_path_in_subgraph(u, v, E_spanner, G):
                return false
    return true

function random_temporal_clique(n: int) -> TemporalGraph:
    V = {v₀, ..., v_{n-1}}
    lambda = empty_map
    for each pair (i,j) with i < j:
        lambda[(v_i, v_j)] = random_float()  // [0, 1)
    return TemporalGraph(V, lambda)

// Test:
for n in {10, 50, 100, 500}:
    for trial in 1..10:
        G = random_temporal_clique(n)
        E = spanner_for_clique(G)

        assert |E| ≤ 7 * n
        assert verify_spanner(G, E)

        print(f"n={n}: |E|={|E|}, 7n={7*n}, tasarruf=%{1-|E|/(n*(n-1)/2):.2f}")
```

---

## 14. Performans Notları

```
// ============================================================
// Karmaşıklık (makale Observation 21):
//
// Lemma 4 (Clique→BiClique):        O(n²)
// Lemma 5 (Dismountability):         O(n³) pratikte O(n²)
// Lemma 17 (Cover set):             O(n²) (crossing kontrolü)
// Theorem 18 (Recursive):           O(n² log n)
//   • Derinlik: O(log n)
//   • Her adım: O(n²) (en kötü)
// Theorem 2 (Clique spanner):       O(n² log n)
//
// Pratik beklenti (n=1000):
//   Sentetik veri: < 1 saniye
//   Gerçek veri (10k düğüm): 5-30 saniye
// ============================================================
```
