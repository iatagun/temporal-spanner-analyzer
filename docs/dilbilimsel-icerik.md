# Temporal Spanner Analyzer — Dilbilimsel ve Derlem Motoru Bağlamı

## 1. Problem: Dilin Zaman Boyutu

Mevcut derlem araçları (Sketch Engine [6], CQPWeb [6], Voyant Tools [7]) **statik** analiz yapar:

| Araç | Yapabildiği | Yapamadığı |
|------|------------|------------|
| Sketch Engine | "korona" kelimesinin en sık birlikte geçtiği 10 kelimeyi listeler | "korona"nın 2019'daki arkadaş grubuyla 2021'deki arkadaş grubunun **farkını** göstermez |
| Voyant Tools | Bir kelimenin tüm metin boyunca sıklık grafiğini çizer | Hangi kelimelerin birlikte **küme** oluşturduğunu ve bu kümelerin nasıl evrildiğini göstermez |

**Oysa dil zamansaldır.** Bir kelimenin anlam alanı (semantic field) zamanla değişir:

- 2019'da "virüs" = {grip, mevsim, hastane, ilaç}
- 2020'de "virüs" = {pandemi, karantina, maske, mesafe, vaka}
- 2022'de "virüs" = {aşı, varyant, endemi, bağışıklık}

Bu değişimi **otomatik** olarak keşfeden bir araç yoktu. Temporal Spanner Analyzer bu boşluğu doldurur.

---

## 2. Çözüm: Temporal Ağ Analizi

### 2.1. Dil Verisini Ağa Dönüştürme

Her belge (haber, tweet, makale) bir **zaman damgası** ve **kelime listesi** içerir:

```
2020-01-05: "yapay, zekâ, teknoloji, gelecek"
2020-03-12: "yapay, zekâ, makine, öğrenme"
```

Aynı belgede geçen her kelime çifti arasında bir **bağlantı (kenar)** oluşur. Zaman içinde bir kelime ne kadar çok kelimeyle birlikte geçerse, o kadar çok bağlantısı olur.

### 2.2. Temporal Clique (Zamansal Klik / Anlam Kümesi)

**Clique** [2] = birbiriyle tam bağlantılı kelime grubu. Yani gruptaki her kelime, gruptaki diğer her kelimeyle en az bir kere birlikte geçmiştir.

Bu, dilbilimdeki **anlam alanı (semantic field)** kavramının matematiksel karşılığıdır:

| Dilbilimsel Kavram | Matematiksel Karşılık | Açıklama |
|-------------------|----------------------|----------|
| Anlam alanı (field) | Clique | Birbiriyle ilişkili kelimeler kümesi |
| Çağrışım (collocation) | Kenar (edge) | İki kelime arasındaki birliktelik |
| Anlam kayması | Clique değişimi | Bir kelimenin zamanla farklı kelimelerle kümeleşmesi |

### 2.3. Spanner (Seyreltme / Özet)

Bir cliquete n tane kelime varsa, teorik olarak n×(n-1)/2 tane bağlantı vardır. Örneğin 10 kelimelik bir kümede 45 bağlantı.

**Spanner** algoritması [1], tüm bu bağlantıların sadece ~7n tanesini seçerek şunu garanti eder:

> Spanner'daki bağlantıları kullanarak, orijinal ağdaki **herhangi iki kelime arasında zamansal olarak geçerli bir yol** bulunabilir.

Bu, bir metnin özetini çıkarmaya benzer:

| | Orijinal | Spanner (Özet) |
|---|---|---|
| 10 kelime | 45 bağlantı | ~10 bağlantı (%78 tasarruf) |
| 100 kelime | 4.950 bağlantı | ~100 bağlantı (%98 tasarruf) |
| 1.000 kelime | 499.500 bağlantı | ~1.000 bağlantı (%99.8 tasarruf) |

**Dilbilimsel anlamı**: Bir dönemin tüm kelime ilişkilerini temizleyip sadece **en temel, en anlamlı bağlantıları** bırakırız. Tıpkı bir makalenin abstract'ını yazmak gibi.

---

## 3. Derlem Motoruna Entegrasyon

### 3.1. Mevcut Durum

Derlem motorları tipik olarak şunları sunar:

- **KWIC** (bağlam içinde anahtar kelime)
- **Collocation** (birlikte geçme istatistiği)
- **Word Sketch** (bir kelimenin dilbilgisel bağlam profili)
- **Frekans listeleri**

Bunların hepsi **zamansızdır** — "2010-2020 arasında bu kelimenin bağlamı nasıl değişti?" sorusuna cevap vermez.

### 3.2. Bu Araç Ne Ekliyor?

| Özellik | Mevcut Derlem Araçları | Bu Araç |
|---------|----------------------|---------|
| Zaman boyutu | Yok | Var (her bağlantı zaman damgalı) |
| Küme (clique) tespiti | Yok | Var (Bron–Kerbosch algoritması) |
| Küme evrimi | Yok | Var (doğum/büyüme/küçülme/ölüm) |
| Gereksiz bağlantı temizliği | Yok | Var (7n spanner) |
| Görsel ağ | Yok | Var (Cytoscape.js, D3.js) |
| Karşılaştırma | Yok | Var (iki dönem yan yana) |
| Sorgulama | Sadece tek kelime | Kelime setlerinin clique kontrolü |

### 3.3. Kullanım Senaryoları

#### Senaryo 1: Pandemi Söyleminin Evrimi

**Girdi**: 2019-2024 arası haber metinleri

**Çıktı**:

| Dönem | Temporal Clique | Ne Oldu? |
|-------|----------------|----------|
| 2019 | grip, mevsim, hastane, ilaç | Normal kış hastalıkları kümesi |
| 2020Q1 | **virüs, pandemi, karantina, maske, mesafe** | YENİ KÜME DOĞDU |
| 2020Q3 | aşı, bağışık, delta, varyant, mRNA | Küme GENİŞLEDİ |
| 2021 | aşı, bağışık, varyant, endemi | Eski üyeler DÜŞTÜ |
| 2023 | korona, grip, mevsim, aşı | Kalıcı üyeler STABİLLEŞTİ |

**Dilbilimsel yorum**: "Virüs" kelimesinin anlam alanı 2019'da tıbbi bir terimken, 2020'de sosyal bir kavrama dönüşmüş, 2022'de ise tekrar tıbbileşmiştir. Bu tür anlam kaymalarını yıllarca okuyarak çıkarmak yerine, saniyeler içinde görürsünüz.

#### Senaryo 2: Yapay Zekâ Terminolojisinin Gelişimi

| Yıl | Clique Üyeleri | Dilbilimsel Yorum |
|-----|---------------|-------------------|
| 2018 | {yapay, zekâ, makine, öğrenme} | Temel terimler |
| 2020 | {derin, sinir, ağ, doğal, dil} | Alt alanlar ayrışıyor |
| 2022 | {büyük, model, dönüştürücü, üretken} | Paradigma değişimi (Transformer) |
| 2024 | {sohbet, robot, ajan, LLM} | Uygulama odaklı terimler |

#### Senaryo 3: Siyasi Söylem

Bir siyasetçinin yıllar içinde hangi kavramlarla birlikte anıldığı, söyleminin nasıl kaydığı otomatik tespit edilebilir. Örneğin bir liderin 2018'de {ekonomi, büyüme, istihdam} kümesindeyken 2022'de {güvenlik, savunma, kriz} kümesine kayması.

---

## 4. Algoritmanın Dilbilimsel Dayanağı

### 4.1. Neden Temporal Clique?

Dilbilimde **dağılımsal hipotez** (distributional hypothesis [3], [4]) der ki:

> "Bir kelimenin anlamı, birlikte geçtiği diğer kelimeler tarafından belirlenir." [3]

Temporal clique, bu hipotezin **zamansal** versiyonudur:

> "Bir kelimenin **bir dönemdeki** anlamı, o dönemde birlikte geçtiği diğer kelimeler tarafından belirlenir."

### 4.2. Neden Spanner?

Dağılımsal hipotez pratikte şu sorunu doğurur: Bir kelime çok fazla kelimeyle birlikte geçer. Örneğin "yapay" kelimesi 100 farklı kelimeyle birlikte geçmiş olabilir. Ama bunların hepsi eşit derecede anlamlı değildir.

Spanner, anlamlı olmayan bağlantıları temizler. Geriye kalan bağlantılar, **en temel anlamsal ilişkileri** temsil eder.

Bu, dilbilimdeki **anlam minimalliği** ilkesiyle örtüşür: Bir kavramı tanımlamak için gereksiz ayrıntılardan arındırılmış, en temel ilişkiler yeterlidir.

### 4.3. Küme Evrimi ve Dil Değişimi

Dilbilimde **semantic change** (anlam değişimi [8]) şu mekanizmalarla olur:

| Dilbilimsel Süreç | Araçtaki Karşılık |
|------------------|-------------------|
| Genişleme (broadening) | Clique'e yeni üyeler eklenmesi |
| Daralma (narrowing) | Clique'ten üye düşmesi |
| Kayma (shift) | Clique üyelerinin tamamen değişmesi |
| Doğum (born) | Yeni bir clique'in ortaya çıkması |
| Ölüm (death) | Bir clique'in kaybolması |

Araç, bu süreçleri **otomatik** olarak tespit eder ve görselleştirir.

---

## 5. Teknik Olmayan Özet

**Ne yapar?**
- CSV/JSON olarak yüklediğiniz zaman etiketli metinleri analiz eder
- Hangi kelimelerin hangi dönemlerde birlikte anıldığını (clique) tespit eder
- Bu kümeleri gereksiz bağlantılardan temizler (spanner)
- Kümelerin zaman içinde nasıl değiştiğini gösterir (trend)
- İki farklı dönemi karşılaştırır
- Bir kelimenin hangi kümelerde olduğunu sorgulamanızı sağlar

**Nasıl kullanılır?**
1. CSV dosyası yüklersiniz (tarih, kelimeler)
2. İlgilendiğiniz zaman aralığını seçersiniz
3. "Analiz Et" dersiniz
4. Görseller ve metrikler size dönemin dilsel yapısını gösterir

**Ne işe yarar?**
- Bir dönemin popüler kavramlarını keşfetmek
- Kavramların nasıl evrildiğini izlemek
- Farklı dönemlerin dilsel yapısını karşılaştırmak
- Bir kelimenin zaman içinde hangi anlamları kazandığını görmek

---

## Kaynakça

[1] Baligács, J. (2026). *Temporal Cliques Admit Linear Spanners*. University of Oxford.

[2] Bron, C. & Kerbosch, J. (1973). Algorithm 457: Finding all cliques of an undirected graph. *Communications of the ACM*, 16(9), 575–577.

[3] Firth, J. R. (1957). A synopsis of linguistic theory 1930–1955. In *Studies in Linguistic Analysis*, pp. 1–32. Philological Society, Oxford.

[4] Harris, Z. S. (1954). Distributional structure. *Word*, 10(2–3), 146–162.

[5] Church, K. W. & Hanks, P. (1990). Word association norms, mutual information, and lexicography. *Computational Linguistics*, 16(1), 22–29.

[6] Kilgarriff, A., Baisa, V., Bušta, J., Jakubíček, M., Kovář, V., Michelfeit, J., Rychlý, P. & Suchomel, V. (2014). The Sketch Engine: ten years on. *Lexicography*, 1(1), 7–36.

[7] Sinclair, S. & Rockwell, G. (2016). Voyant Tools. Web. http://voyant-tools.org/

[8] Traugott, E. C. & Dasher, R. B. (2002). *Regularity in Semantic Change*. Cambridge University Press.
