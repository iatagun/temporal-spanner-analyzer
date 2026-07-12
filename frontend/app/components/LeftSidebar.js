'use client';

export default function LeftSidebar() {
  return (
    <aside className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed space-y-5">
      <div>
        <h3 className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide mb-2">
          Kuramsal Çerçeve
        </h3>
        <p className="mb-2">
          Baligács (2026) her temporal klik için en fazla <strong className="text-gray-900 dark:text-gray-100">7n</strong> kenar
          içeren bir spanner inşa edilebileceğini kanıtlamıştır.
        </p>
      </div>

      <div>
        <h4 className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Temporal Klik</h4>
        <p>
          Tüm kelime çiftleri arasında zamana uygun bir yol bulunan,
          tam bağlantılı zamanlı çizge. Derlemde aynı zaman diliminde
          birlikte görülen kelime kümelerine karşılık gelir.
        </p>
      </div>

      <div>
        <h4 className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Spanner</h4>
        <p>
          Orijinal çizgenin tüm zamansal ulaşılabilirliğini koruyan
          seyrek alt çizge. Gereksiz kenarları eleyerek kavram ilişkilerinin
          özünü açığa çıkarır.
        </p>
      </div>

      <div>
        <h4 className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Algoritma</h4>
        <p>
          Dismountability &rarr; EM biclique &rarr; Lemma 17 özineli
          bölme. Her seviyede &le; 6n kenar eklenir, derinlik &le; log n.
          Klikler için toplam: <strong className="text-gray-900 dark:text-gray-100">f(n) &le; 7n</strong>.
        </p>
      </div>

      <div className="pt-3 border-t border-gray-100 dark:border-gray-800">
        <p className="text-gray-400 dark:text-gray-500">
          arXiv:2606.05156 &mdash; &quot;Temporal Cliques Admit Linear Spanners&quot;
        </p>
      </div>
    </aside>
  );
}
