# Temporal Spanner — Matematiksel Temeller

> Bu doküman, Baligács (2026) "Temporal Cliques Admit Linear Spanners" makalesinde sunulan algoritmanın sıfırdan, adım adım bir anlatımıdır. Hiçbir ön bilgi varsayılmaz.

---

## İçindekiler

1. [Bölüm 0: Küme ve Fonksiyon Gösterimleri](#bölüm-0-küme-ve-fonksiyon-gösterimleri)
2. [Bölüm 1: Çizge (Graph)](#bölüm-1-çizge-graph)
3. [Bölüm 2: Zamansal Çizge (Temporal Graph)](#bölüm-2-zamansal-çizge-temporal-graph)
4. [Bölüm 3: Zamansal Yol (Temporal Path)](#bölüm-3-zamansal-yol-temporal-path)
5. [Bölüm 4: Zamansal Klik (Temporal Clique)](#bölüm-4-zamansal-klik-temporal-clique)
6. [Bölüm 5: Spanner](#bölüm-5-spanner)
7. [Bölüm 6: Problem Tanımı](#bölüm-6-problem-tanımı)
8. [Bölüm 7: {1,2}-Hop Sökümü](#bölüm-7-12-hop-sökümü)
9. [Bölüm 8: Klikten İkili-Klik Dönüşümü](#bölüm-8-klikten-ikili-klik-dönüşümü)
10. [Bölüm 9: EM-İkili-Klik (Extremal-Min-Max Biclique)](#bölüm-9-em-ikili-klik)
11. [Bölüm 10: Sökülebilirlik (Dismountability)](#bölüm-10-sökülebilirlik)
12. [Bölüm 11: Yıldız Kapsamaları (Star Covers)](#bölüm-11-yıldız-kapsamaları)
13. [Bölüm 12: 3-Atlama-K-Kesme-Geçişi (3-Hop-k-Cut-Crossing)](#bölüm-12-3-atlama-k-kesme-geçişi)
14. [Bölüm 13: Ana Teorem — 7n Sınırı](#bölüm-13-ana-teorem)
15. [Bölüm 14: Algoritmanın Adımları](#bölüm-14-algoritmanın-adımları)
16. [Bölüm 15: Neden 7?](#bölüm-15-neden-7)
17. [Bölüm 16: İyileştirme Potansiyeli](#bölüm-16-iyileştirme-potansiyeli)

---

## Bölüm 0: Küme ve Fonksiyon Gösterimleri

Bu kısımda kullanacağımız temel matematiksel semboller:

| Sembol | Anlamı | Örnek |
|--------|--------|-------|
| \( \in \) | "elemanıdır" | \( x \in S \): x, S kümesinin bir elemanı |
| \( \subseteq \) | "alt kümesidir" | \( A \subseteq B \): A'nın her elemanı B'de de var |
| \( \cap \) | "kesişim" | \( A \cap B \): A ve B'nin ortak elemanları |
| \( \cup \) | "birleşim" | \( A \cup B \): A veya B'deki tüm elemanlar |
| \( \setminus \) | "küme farkı" | \( A \setminus B \): A'da olup B'de olmayanlar |
| \( \|S\| \) | "kümenin büyüklüğü" | \( \|S\| \): S'deki eleman sayısı |
| \( \binom{n}{k} \) | "n'in k'lı kombinasyonu" | \( \binom{n}{2} = n(n-1)/2 \) |
| \( \min \) | "minimum" | \( \min\{3,1,2\} = 1 \) |
| \( \max \) | "maksimum" | \( \max\{3,1,2\} = 3 \) |
| \( \text{argmin} \) | "minimum yapan eleman" | \( \text{argmin}_{x} f(x) \): f(x)'i en küçük yapan x |
| \( \text{argmax} \) | "maksimum yapan eleman" | \( \text{argmax}_{x} f(x) \): f(x)'i en büyük yapan x |
| \( \mathbb{R} \) | "reel sayılar" | \( 3.14, -2.7, 0, 42 \) |
| \( \leq \) | "küçük eşit" | \( 2 \leq 3 \), \( 3 \leq 3 \) |
| \( O(f(n)) \) | "büyük-O gösterimi" | \( O(n^2) \): n büyüdükçe n² gibi büyüyen fonksiyon |

---

## Bölüm 1: Çizge (Graph)

### 1.1 Tanım

Bir **çizge** (graph), iki kümeden oluşur:

\[
G = (V, E)
\]

- \( V \): **düğümler** (vertices, nodes) — bir küme
- \( E \): **kenarlar** (edges) — \( V \)'nin 2-elemanlı alt kümeleri

Her kenar, iki düğüm arasındaki bir ilişkiyi temsil eder.

### 1.2 Örnek

\( V = \{\text{yapay}, \text{zekâ}, \text{öğrenme}\} \) ve kenarlar:

\[
E = \{ \{\text{yapay}, \text{zekâ}\}, \{\text{zekâ}, \text{öğrenme}\} \}
\]

Bu, 3 düğümlü ama sadece 2 kenarlı bir çizgedir. "yapay" ile "öğrenme" arasında **doğrudan** bir kenar yok.

### 1.3 Düğüm Sayısı ve Maksimum Kenar Sayısı

\( n \) düğümlü bir çizgede **mümkün olan en fazla kenar sayısı**:

\[
|E|_{\max} = \binom{n}{2} = \frac{n(n-1)}{2}
\]

**Türetme**: n düğümden 2 tane seçmenin kaç farklı yolu var? İlk düğümü n yoldan, ikincisini (n-1) yoldan seçersin. Ama (a,b) ile (b,a) aynı kenar olduğu için 2'ye bölersin:

\[
\frac{n \cdot (n-1)}{2}
\]

**Örnekler**:

| n | Maksimum kenar |
|---|---------------|
| 2 | 1 |
| 3 | 3 |
| 4 | 6 |
| 5 | 10 |
| 10 | 45 |
| 100 | 4.950 |
| 1.000 | 499.500 |

---

## Bölüm 2: Zamansal Çizge (Temporal Graph)

### 2.1 Problem: Statik Çizge Zamanı Gösteremez

"yapay" kelimesinin 2018'de ve 2024'te farklı kelimelerle birlikte geçtiğini düşünelim. Sıradan bir çizge bunu gösteremez — kenar ya vardır ya yoktur, ne zaman eklendiği bilinmez.

### 2.2 Tanım

Bir **zamansal çizge** (temporal graph), her kenarın bir **zaman etiketi** taşıdığı çizgedir:

\[
G = (V, E, \lambda)
\]

- \( \lambda: E \to \mathbb{R} \) — her kenara bir reel sayı (zaman) atayan fonksiyon

Eğer bir kenar birden çok zaman damgası taşıyabiliyorsa (çoklu zamanlı):

\[
\lambda(e) \subseteq \mathbb{R} \quad \text{(bir küme)}
\]

Bizim uygulamamızda her kenarın **tek** bir zaman damgası var.

### 2.3 Örnek

\[
\begin{align*}
V &= \{\text{yapay}, \text{zekâ}, \text{makine}, \text{öğrenme}\} \\
\lambda(\text{yapay}, \text{zekâ}) &= 2020.3 \\
\lambda(\text{yapay}, \text{makine}) &= 2021.1 \\
\lambda(\text{zekâ}, \text{makine}) &= 2021.5 \\
\lambda(\text{makine}, \text{öğrenme}) &= 2021.8
\end{align*}
\]

Burada "yapay" ile "zekâ" 2020'de birlikte geçmiş, ama "yapay" ile "öğrenme" hiç birlikte geçmemiş (kenar yok).

### 2.4 Kenar Gösterimi

Kenarları sıralı ikili (ordered pair) olarak gösteririz, ama yönsüzdürler: \( (u,v) \) ile \( (v,u) \) aynı kenardır. Bu yüzden kanonik form kullanırız:

\[
\text{key}(u,v) = \begin{cases}
(u,v) & \text{eğer } u \leq v \\
(v,u) & \text{değilse}
\end{cases}
\]

Bu, kodda `_edge_key()` veya `edge_key()` fonksiyonudur.

---

## Bölüm 3: Zamansal Yol (Temporal Path)

### 3.1 Sezgisel

Normal bir yolda sadece düğümlerin sırası önemlidir. Zamansal bir yolda **kenarların zaman sırası** da önemlidir. Zaman damgaları **azalmamalıdır** (non-decreasing).

### 3.2 Tanım

Bir \( v_1, v_2, \ldots, v_k \) dizi olsun. Bu bir **zamansal yol**dur ancak ve ancak:

\[
\lambda(v_1, v_2) \leq \lambda(v_2, v_3) \leq \cdots \leq \lambda(v_{k-1}, v_k)
\]

Yani: zaman damgaları ya artar ya da aynı kalır — asla düşmez.

### 3.3 Neden Azalmamalı?

Bilgi yayılımında bir düşünce edin: A, B'ye 2020'de bir bilgi söylüyor. B, C'ye 2019'da söyleyemez — çünkü 2019'da bu bilgiyi henüz bilmiyordu. Zaman ileri akar.

Dilde: Bir kelime 2020'de başka bir kelimeyle birlikte geçmişse, 2019'da bu birlikteliğin "farkında" olamaz.

### 3.4 Önemli Not

Zamansal yolun **varlığı**, iki düğüm arasında **doğrudan** bir kenar olmasından daha zayıf bir koşuldur. A ile C arasında doğrudan kenar olmasa bile, A→B→C şeklinde bir zamansal yol olabilir.

### 3.5 Özyinelemeli Tanım

Daha resmi: \( u \)'dan \( v \)'ye zamansal yol vardır ancak ve ancak:

1. \( (u,v) \in E \) (direkt kenar), VEYA
2. \( \exists w \in V \) öyle ki \( (u,w) \in E \) ve \( \lambda(u,w) \leq t \) ve \( w \)'den \( v \)'ye zamansal yol var (son kenarın zamanı \( \geq t \))

**Algoritmik karşılığı**: BFS (genişlik öncelikli arama) ama kuyruğa düğüm + son zaman damgası ikilisi koyarak.

---

## Bölüm 4: Zamansal Klik (Temporal Clique)

### 4.1 Klik Sezgisel

Bir **klik** (clique), her düğüm çifti arasında bir kenar bulunan düğüm alt kümesidir. Yani gruptaki herkes, gruptaki herkesle doğrudan bağlantılıdır.

### 4.2 Tanım

\( V' \subseteq V \) bir **klik**tir ancak ve ancak:

\[
\forall u,v \in V', u \neq v: (u,v) \in E
\]

Yani her farklı \( u,v \) ikilisi için bir kenar vardır.

### 4.3 Zamansal Klik

Eğer çizge zamansalsa ve \( V' \) bir klikse, buna **zamansal klik** (temporal clique) denir. Her kenarın bir zaman damgası vardır (belki farklı zamanlarda).

### 4.4 Maksimal Klik vs Maksimum Klik

- **Maksimal klik**: Kendisini kapsayan daha büyük bir klik olmayan klik. Bulması kolay (Bron–Kerbosch algoritması).
- **Maksimum klik**: Tüm çizgedeki en büyük klik. Bulması NP-zor (genel durumda).

Bu projede **maksimal klikleri** buluyoruz.

### 4.5 Kliklerin Dilbilimsel Anlamı

Bir klik, her üyesi diğer her üyeyle en az bir kere birlikte geçmiş kelimeler kümesidir. Bu, dilbilimdeki **anlam alanı** (semantic field) kavramına karşılık gelir: birbiriyle ilişkili, aynı kavramsal alanı paylaşan kelimeler.

---

## Bölüm 5: Spanner

### 5.1 Sezgisel

Bir çizgenin kenarlarının bir alt kümesi. Şart: orijinal çizgedeki **tüm zamansal yollar** bu alt kümede de bulunabilsin.

Yani: kenar sayısını azalt ama **bağlantıyı koru**.

### 5.2 Tanım

\( G = (V, E, \lambda) \) zamansal bir çizge olsun. \( E' \subseteq E \) bir **spanner**dır ancak ve ancak:

\[
\forall u,v \in V, u \neq v: \text{eğer } G'de u'dan v'ye zamansal yol varsa, } E' \text{de de vardır.}
\]

### 5.3 Neden Spanner?

Tam bir klikte \( \binom{n}{2} \) kenar vardır. Büyük \( n \) için bu çok fazladır. Spanner, daha az kenarla **aynı erişilebilirliği** sağlar.

### 5.4 Spanner'ın Ölçümü

- **Boyut**: \( |E'| \) — seçilen kenar sayısı
- **Gerdirme Faktörü (Stretch Factor)**: 

\[
\text{stretch} = \max_{u,v} \frac{d_{E'}(u,v)}{d_E(u,v)}
\]

Burada \( d(u,v) \) en kısa zamansal yolun uzunluğu (hop sayısı). 1.0 = hiç kayıp yok. 2.0 = yollar iki katına çıkmış.

---

## Bölüm 6: Problem Tanımı

### 6.1 Soru

Bir zamansal klik verildiğinde, **en küçük** spanner'ı nasıl buluruz?

### 6.2 Neden Zor?

Statik çizgelerde bir klikin en küçük spanner'ı — kendisidir. Kenar çıkarmak bağlantıyı koparır (çünkü statik çizgede tek yol direkt kenardır).

**Zamansal çizgelerde durum farklıdır**. Kenar çıkarsan bile, diğer kenarlar üzerinden **dolaylı zamansal yollar** olabilir. Örneğin:

- A—B: 2020
- B—C: 2021
- A—C: 2022

A—C kenarını silsen bile, A→B(2020)→C(2021) yolu var mı? 2020 ≤ 2021 → **evet**, bu geçerli bir zamansal yol. O halde A—C kenarını silebiliriz!

### 6.3 Önceki Çalışmalar

| Yıl | Sınır | Açıklama |
|-----|-------|----------|
| ~2018 | \( O(n \log n) \) | Bilinen en iyi üst sınır |
| 2026 | \( 7n \) | **Baligács** — bu projenin dayandığı makale |
| — | \( 4n \) | Kanıtlanmış alt sınır (daha iyisi mümkün değil) |

### 6.4 Bu Projenin Hedefi

Makaledeki algoritmayı gerçek dünya verisine (dil derlemi) uygulamak ve:
1. Anlam alanlarını (clique) keşfetmek
2. Gereksiz bağlantıları temizlemek (spanner)
3. Zaman içindeki değişimi izlemek (trend)

---

## Bölüm 7: {1,2}-Hop Sökümü

**Bu, algoritmanın ilk adımıdır.**

### 7.1 Sezgisel

Bazı düğümler "gereksizdir": onların yapabileceği her şeyi başka düğümler 1 veya 2 adımda yapabilir. Böyle düğümleri çıkar, yerine birkaç kenar ekle ve devam et.

### 7.2 Gözlem 19 (Observation 19)

\( v \) düğümü şu durumda sökülebilir:

1. \( u \) ve \( w \) diye iki düğüm var öyle ki:
2. \( v \to \text{Nmin}(u) \to u \) bir zamansal yol
3. \( w \to \text{Nmax}(w) \to v \) bir zamansal yol

Burada:
- \( \text{Nmin}(u) \): \( u \)'nun **en erken** bağlandığı düğüm
- \( \text{Nmax}(w) \): \( w \)'nin **en geç** bağlandığı düğüm

### 7.3 Söküm Mekanizması

\( v \) söküldüğünde **4 yeni kenar** eklenir:

1. \( (v, \text{Nmin}(u)) \)
2. \( (\text{Nmin}(u), u) \)
3. \( (w, \text{Nmax}(w)) \)
4. \( (\text{Nmax}(w), v) \)

Bu 4 kenar, \( v \)'nin yaptığı tüm bağlantıları devralır.

### 7.4 Algoritma

```
V' = V (tüm düğümler)
E' = {} (spanner kenarları)

tekrar:
  değişiklik_oldu = Yanlış
  her v ∈ V' için:
    eğer v {1,2}-hop sökülebilirse:
      V' = V' \ {v}
      E' = E' ∪ {4 yeni kenar}
      değişiklik_oldu = Doğru
      kır (döngü başa dönsün)
  değişiklik_olmadıysa: dur

döndür (V', E')
```

### 7.5 Neden Önemli?

Bu adım, düğüm sayısını azaltır. Kalan düğümler üzerinde EM-ikili-klik dönüşümü daha verimli çalışır. En kötü durumda hiçbir düğüm sökülemez ve \( V' = V \) kalır.

---

## Bölüm 8: Klikten İkili-Klik Dönüşümü

### 8.1 İkili-Klik (Biclique) Nedir?

Bir **ikili-klik** (biclique), düğümleri iki kümeye ayrılmış bir çizgedir:

\[
B = (S, T, E_B)
\]

Öyle ki tüm kenarlar \( S \) ile \( T \) arasındadır. \( S \) içinde veya \( T \) içinde kenar yoktur.

### 8.2 Lemma 4: Klik → Biclique Dönüşümü (Lemma 4)

Her klik, bir biclique'e dönüştürülebilir. Yöntem:

\( G = (V, E, \lambda) \) bir klik olsun. Her \( v \in V \) için:
- \( v_S \) (kaynak kopya) → \( S \) kümesine
- \( v_T \) (hedef kopya) → \( T \) kümesine

Her \( v_S \) ile \( u_T \) (\( v \neq u \)) arasında kenar. Zamanı: \( \lambda(v, u) \).

Her \( v_S \) ile \( v_T \) arasında kenar. Zamanı: \( 0 \).

**Neden**: Bu dönüşüm, zamansal yol bulmayı kolaylaştırır. Bir klikte A→B→C yolunu bulmak için biclique'te \( A_S \to B_T \to C_S \to \dots \) şeklinde S ve T arasında gidip geliriz.

---

## Bölüm 9: EM-İkili-Klik

### 9.1 EM (Extremal-Min-Max) Nedir?

Her düğümün iki özel komşusu vardır:

- \( \text{Nmin}(v) \): \( v \)'nin **en erken** bağlandığı düğüm
  \[
  \text{Nmin}(v) = \text{argmin}_{w \neq v} \lambda(v, w)
  \]

- \( \text{Nmax}(v) \): \( v \)'nin **en geç** bağlandığı düğüm
  \[
  \text{Nmax}(v) = \text{argmax}_{w \neq v} \lambda(v, w)
  \]

### 9.2 EM-İkili-Klik Tanımı

\( G = (V, E, \lambda) \) bir zamansal klik olsun. Şu iki kümeyi tanımla:

\[
\begin{align*}
V^- &= \{\text{Nmin}(v) : v \in V\} \\
V^+ &= \{\text{Nmax}(v) : v \in V\}
\end{align*}
\]

Eğer \( V^- \cap V^+ = \emptyset \) (ayrık) ve \( V^- \cup V^+ = V \) (tüm düğümleri kapsıyor) ise, \( G \)'ye bir **EM-ikili-klik** denir.

### 9.3 Neden EM-İkili-Klik?

Bu iki küme bir biclique oluşturur: tüm kenarlar \( V^- \) ile \( V^+ \) arasındadır. Bu yapı, spanner'ı özyinelemeli olarak inşa etmeyi mümkün kılar.

### 9.4 Eğer EM Değilse?

Eğer \( V^- \) ve \( V^+ \) ayrışmıyorsa veya tüm düğümleri kapsamıyorsa, Lemma 4'teki genel klik→biclique dönüşümü kullanılır (kopyalama yöntemi). Bu daha fazla kenar ekler (n yerine 2n düğüm).

---

## Bölüm 10: Sökülebilirlik

### 10.1 Lemma 5: Biclique Sökümü (Lemma 5)

EM-ikili-klik üzerinde daha fazla düğüm sökülebilir. Bir \( s \in S \) düğümü şu durumda sökülebilir:

\( s \)'nin en erken bağlandığı düğüm \( t \) olsun. Eğer başka bir \( s' \in S \) daha varsa ve:

\[
\text{pos}(t, s', \text{Nmin}(s', G)) < \text{pos}(t, s, \text{Nmin}(s, G))
\]

Yani \( t \)'ye göre \( s' \), \( s \)'den "daha önce" sıralanıyorsa, \( s' \) sökülebilir.

Burada \( \text{pos}(x, y, G) \): \( y \)'nin \( x \)'in komşuluk listesindeki sırası (zamana göre sıralanmış).

### 10.2 Sökümün Etkisi

\( s' \) söküldüğünde **2 yeni kenar** eklenir:
1. \( (s, t) \)
2. \( (s', t) \)

Benzer mantık \( T \) kümesi için de geçerlidir (\( \text{Nmax} \) kullanarak).

### 10.3 Söküm Döngüsü

Söküm, bir döngü içinde devam eder: her adımda en az bir düğüm sökülür. Döngü, sökülecek düğüm kalmayana kadar sürer. Her sökümde 2 kenar eklenir.

---

## Bölüm 11: Yıldız Kapsamaları

### 11.1 Tanım

Bir **yıldız** (star), bir merkez düğüm ve ona bağlı diğer düğümlerden oluşan bir alt çizgedir.

### 11.2 s\*-Yıldız

\( s^* \in S \) bir düğüm seç. Ona bağlı tüm \( t \in T \) düğümlerini al. Bu, bir yıldız oluşturur.

\[
\text{Star}(s^*) = \{(s^*, t) : t \in T\}
\]

**Simple star**: \( s^* \)'a bağlı tüm kenarlar + her düğümün min/max kenarı.

### 11.3 Genişletilmiş Yıldız (Extended Star)

Simple star yetmez. Daha fazla kenar gerekebilir. Genişletilmiş yıldız:

- \( s^* \)'a bağlı tüm kenarlar
- Her düğümün min/max kenarları
- \( s^* \) dışındaki her \( s \in S \) için: bir \( t \in T \) ile ek bağlantı

Bu ek bağlantı, \( s \)'nin \( t \) üzerinden \( s^* \)'a "ulaşamaması" durumunda eklenir.

### 11.4 Sıralama (Ordering)

\( S \) ve \( T \) düğümleri, \( s^* \)'a olan mesafelerine göre sıralanır:

\[
\text{S_ord} = [s_1, s_2, \ldots, s_k] \quad \text{öyle ki } \lambda(s_i, s^*) \leq \lambda(s_{i+1}, s^*)
\]

Aynı sıralama \( T \) için de yapılır.

---

## Bölüm 12: 3-Atlama-K-Kesme-Geçişi

**Bu, algoritmanın en kritik alt-adımıdır.**

### 12.1 Lemma 16

Bir EM-ikili-klikte, \( s^* \) düğümü ve bir \( i \) indeksi verilsin. \( k \) bir eşik değeri olsun (\( k \leq |T| \)).

Eğer \( i > k \) ise:
- YA \( s_i \to t_i \to v \to t_j \) şeklinde 3-hop geçişli bir yol vardır (cut-crossing)
- YA DA \( s_i \), \( s^* \)'a genişletilmiş yıldız ile bağlanabilir

### 12.2 3-Hop-K-Kesme-Geçişi Nedir?

\( s_i \in S, t_i \in T \) olsun. Eğer şu koşullar sağlanıyorsa:

1. \( \text{pos}(t_i, s_i, G) \leq \text{pos}(t_i, v, G) \) (v, t_i'den s_i'den daha geç görünüyor)
2. \( \text{pos}(v, t_i, G) \leq \text{pos}(v, t_j, G) \) (t_j, v'den t_i'den daha geç görünüyor)
3. \( \text{pos}(t_j, v, G) \leq \text{pos}(t_j, s^*, G) \) (s*, t_j'den v'den daha geç görünüyor)

O halde şu 3-hop yol geçerlidir:

\[
s_i \to t_i \to v \to t_j
\]

### 12.3 Neden 3-Hop?

Çünkü sadece 2 hop ile biclique'te bir yerden bir yere gitmek her zaman mümkün değildir. 3-hop, eklenmesi gereken kenarları belirlemek için yeterlidir.

### 12.4 Lemma 17: Kapsama (Cover)

3-hop-kesme-geçişi kontrolü sonucunda:
- Vaka (i): Kesme-geçiş bulunursa → o kenarları spanner'a ekle, alt-kümeyi özyinelemeli işle
- Vaka (ii): Kesme-geçiş bulunamazsa → \( s_i \)'yi \( s^* \)'a genişletilmiş yıldızla bağla

Her iki durumda da, kalan problem en az **yarıya iner**.

---

## Bölüm 13: Ana Teorem

### 13.1 Teorem 18 (EM-İkili-Klik Spannerı)

Her \( n = |S| + |T| \) düğümlü EM-ikili-klik, en fazla **14n** kenarlı bir spanner'a sahiptir.

### 13.2 Teorem 20 ve Teorem 2 (Klik Spannerı)

Her \( n \) düğümlü zamansal klik, en fazla **7n** kenarlı bir spanner'a sahiptir.

### 13.3 Neden 14n biclique'ten 7n clique?

Çünkü clique'ten biclique'e geçerken düğüm sayısı iki katına çıkar (her düğüm → S ve T kopyaları). 14n'lik biclique sınırı, geri projekte edilince 7n'ye düşer (n orijinal düğüm sayısı).

### 13.4 Kanıtın İskeleti

1. **{1,2}-Hop Sökümü** uygula → düğüm sayısını azalt
2. Kalan düğümlerde EM-ikili-klik dönüşümünü dene
3. Eğer başarılıysa: Lemma 16-17'yi kullanarak özyinelemeli spanner inşa et
4. Eğer başarısızsa: Lemma 4 (kopyalama) ile biclique'e dönüştür, sonra yine özyinelemeli inşa et
5. Her özyineleme adımında problem en az yarıya iner → toplam \( O(n) \)
6. Her adımda eklenen kenar sayısı sınırlı → toplam \( 7n \)

---

## Bölüm 14: Algoritmanın Adımları

### 14.1 Ana Fonksiyon: `spanner_for_clique`

```
Girdi: TemporalGraph G = (V, E, λ)
Çıktı: Spanner kenar kümesi E'

1. (V', E_dismount) = dismountability_12_hop(G)  // {1,2}-hop sökümü
2. Eğer |V'| < 2: döndür E_dismount
3. G' = induced_subgraph_clique(G, V')

   // EM dönüşümünü dene
4. V_minus = {Nmin(v, G') : v ∈ V'}
5. V_plus = {Nmax(v, G') : v ∈ V'}
6. is_partition = (V_minus ∪ V_plus = V') ∧ (V_minus ∩ V_plus = ∅)

7. Eğer is_partition ve |V_minus| = |V_plus| ve |V_minus| > 0:
      // EM-ikili-klik → özyineleme
      G_bc = EM_biclique(V_minus, V_plus, G')
      E_bc = spanner_for_EM_biclique(G_bc)
      E_total = E_dismount ∪ project_back(E_bc)
   Değilse:
      // Fallback: Lemma 4 kopyalama
      G_fb = biclique_kopyala(G')
      E_fb = spanner_for_biclique(G_fb)
      E_total = E_dismount ∪ project_back(E_fb)

8. cap = n*(n-1)/2
   Eğer |E_total| > cap:
      E_total = full_clique_edges
   Döndür E_total
```

### 14.2 `spanner_for_EM_biclique` (Özyineleme)

```
Girdi: EM-Biclique B = (S, T, E_B)
Çıktı: Spanner kenar kümesi

1. (S', T', E_dismount) = dismountability(B)  // Lemma 5 sökümü
2. Eğer |S'| ≤ 1 veya |T'| ≤ 1: temel durum → döndür tam bağlantı

3. s* = S'[0]  // ilk düğüm seç
   (S_ord, T_ord) = s_star_ordering(s*, B)

4. k = |T'| // alt limit
   Her i için (k+1'den |S'|-1'e):
       (tip, değer) = lemma16_check(i, k, s*, S_ord, T_ord, B)
       Eğer tip == "crossing":
           path = find_3_hop_crossing_path(...)
           E_cover = simple_star(s*, B) ∪ path
           S_kalan = S_ord[k+1:i] (veya benzer)
           E_kalan = spanner_for_EM_biclique(kalanlar)
           Döndür E_dismount ∪ E_cover ∪ E_kalan
       Değilse (tip == "extended"):
           devam et

   // Hiçbir crossing bulunamadıysa:
   E_cover = extended_star(s*, B)
   S_kalan = S_ord[k+1:]
   E_kalan = spanner_for_EM_biclique(kalanlar)
   Döndür E_dismount ∪ E_cover ∪ E_kalan
```

---

## Bölüm 15: Neden 7?

### 15.1 Kenar Sayısının Dağılımı

7 sayısı tesadüf değil. Algoritmanın her adımı sabit sayıda kenar ekler:

| Adım | Eklenen Kenar Sayısı | Açıklama |
|------|---------------------|----------|
| {1,2}-hop sökümü | 4 / düğüm | Observation 19 |
| Lemma 5 sökümü | 2 / düğüm | Dismountability eklemeleri |
| Simple star | ≤ 2n | s*'a bağlı tüm kenarlar + min/max |
| Extended star | ≤ 3n | Simple star + fazladan kenarlar |
| 3-hop geçişi | ≤ 3 | Sabit sayıda kenar |
| Özyineleme | En az yarıya iner | Logaritmik derinlik |

Toplamda \( 4 + 2 + 1 = 7 \) kenar/düğüm.

### 15.2 Alt Sınır: 4n

Hiçbir zamansal klik spanner'ı \( 4n \)'den küçük olamaz. Bunun kanıtı, belirli bir klik yapısı kurup herhangi bir spanner'ın en az 4n kenar içermesi gerektiğini göstermektir.

Yani:
\[
4n \leq \text{optimal spanner boyutu} \leq 7n
\]

Aradaki boşluk (4n ile 7n arası) hâlâ açık bir problem.

---

## Bölüm 16: İyileştirme Potansiyeli

### 16.1 Teorik İyileştirmeler

| Hedef | Durum |
|-------|-------|
| 7n → 6n | Mümkün olabilir, daha iyi star kapsaması gerek |
| 7n → 5n | Olası ama zor, yeni bir lemmanın eşiğinde |
| 7n → 4n | Alt sınıra eşit, bir atılım gerekir |

### 16.2 Pratik İyileştirmeler

| İyileştirme | Etkisi |
|-------------|--------|
| Daha iyi düğüm seçimi (s*) | Daha fazla {1,2}-hop sökümü |
| Veriye özgü seyreltme | Çoğu gerçek veride 7n'den çok daha az |
| Paralel özyineleme | Hız kazancı |
| PMI ön-filtreleme | Daha anlamlı cliqueler, daha az kenar |

### 16.3 Açık Problemler

1. **7n optimal mi?** 4n ile 7n arasındaki boşluk hâlâ açık.
2. **Seyrek zamansal çizgeler**: Algoritma sadece cliqueler için çalışıyor. Gerçek dünya çizgeleri genelde seyrek. Seyrek çizgeler için spanner problemi hâlâ açık.
3. **Dinamik spanner**: Çizge zamanla değişiyorsa (yeni düğümler ekleniyorsa), spanner'ı baştan hesaplamadan güncellemek mümkün mü?

---

## Sözlük

| Terim | İngilizcesi | Tanım |
|-------|-------------|-------|
| Çizge | Graph | Düğüm ve kenarlardan oluşan yapı |
| Düğüm | Vertex | Çizgenin temel birimi |
| Kenar | Edge | İki düğüm arasındaki bağlantı |
| Klik | Clique | Her düğüm çifti arasında kenar olan alt küme |
| İkili-klik | Biclique | İki küme arasında tüm kenarların olduğu yapı |
| Zamansal | Temporal | Zaman damgası taşıyan |
| Yol | Path | Ardışık düğümlerden oluşan dizi |
| Spanner | Spanner | Bağlantıyı koruyan kenar alt kümesi |
| Söküm | Dismountability | Gereksiz düğümün çıkarılması |
| Yıldız | Star | Tek merkeze bağlı kenarlar |
| Kesme-geçiş | Cut-crossing | 3-hop ile kesme noktasını aşma |
| Özyineleme | Recursion | Kendini çağıran fonksiyon |
| Gerdirme | Stretch | Yol uzunluğunun oranı |
| Üst sınır | Upper bound | Bir değerin geçemeyeceği maksimum |
| Alt sınır | Lower bound | Bir değerin altına düşemeyeceği minimum |
