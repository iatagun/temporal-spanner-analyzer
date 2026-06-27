'use client';

export default function LeftSidebar() {
  return (
    <aside className="text-xs text-gray-500 leading-relaxed space-y-5">
      <div>
        <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2">
          Kuramsal Cerceve
        </h3>
        <p className="mb-2">
          Baligacs (2026) her temporal klik icin en fazla <strong className="text-gray-900">7n</strong> kenar
          iceren bir spanner insa edilebilecegini kanitlamistir.
        </p>
      </div>

      <div>
        <h4 className="text-xs font-medium text-gray-600 mb-1">Temporal Klik</h4>
        <p>
          Tum kelime ciftleri arasinda zamana uygun bir yol bulunan,
          tam baglantili zamanli cizge. Derlemde ayni zaman diliminde
          birlikte gorulen kelime kumelerine karsilik gelir.
        </p>
      </div>

      <div>
        <h4 className="text-xs font-medium text-gray-600 mb-1">Spanner</h4>
        <p>
          Orijinal cizgenin tum zamansal ulasilabilirligini koruyan
          seyrek alt cizge. Gereksiz kenarlari eleyerek kavram iliskilerinin
          ozunu aciga cikarir.
        </p>
      </div>

      <div>
        <h4 className="text-xs font-medium text-gray-600 mb-1">Algoritma</h4>
        <p>
          Dismountability &rarr; EM biclique &rarr; Lemma 17 ozineli
          bolme. Her seviyede &le; 6n kenar eklenir, derinlik &le; log n.
          Klikler icin toplam: <strong className="text-gray-900">f(n) &le; 7n</strong>.
        </p>
      </div>

      <div className="pt-3 border-t border-gray-100">
        <p className="text-gray-400">
          arXiv:2606.05156 &mdash; &quot;Temporal Cliques Admit Linear Spanners&quot;
        </p>
      </div>
    </aside>
  );
}
