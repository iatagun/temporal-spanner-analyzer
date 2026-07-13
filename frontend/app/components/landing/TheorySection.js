// Same theoretical content as LeftSidebar.js's "Kuramsal Çerçeve", presented
// at landing-page scale (larger type, article-like layout) instead of the
// dense sidebar version -- deliberately duplicated text, not a shared
// component, since the two presentation contexts differ enough that forcing
// one component to serve both would need awkward size/layout props.
export default function TheorySection() {
  return (
    <section className="max-w-3xl mx-auto px-6 py-16 border-t border-gray-200 dark:border-gray-800">
      <h2 className="font-serif text-2xl font-medium tracking-tight text-gray-900 dark:text-gray-100 mb-6">
        Kuramsal Çerçeve
      </h2>
      <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-8">
        Baligács (2026) her temporal klik için en fazla <strong className="text-gray-900 dark:text-gray-100">7n</strong> kenar
        içeren bir spanner inşa edilebileceğini kanıtlamıştır.
      </p>
      <div className="grid sm:grid-cols-3 gap-8">
        <div>
          <h3 className="font-serif text-lg text-gray-800 dark:text-gray-200 mb-1.5">Temporal Klik</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            Tüm kelime çiftleri arasında zamana uygun bir yol bulunan,
            tam bağlantılı zamanlı çizge. Derlemde aynı zaman diliminde
            birlikte görülen kelime kümelerine karşılık gelir.
          </p>
        </div>
        <div>
          <h3 className="font-serif text-lg text-gray-800 dark:text-gray-200 mb-1.5">Spanner</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            Orijinal çizgenin tüm zamansal ulaşılabilirliğini koruyan
            seyrek alt çizge. Gereksiz kenarları eleyerek kavram ilişkilerinin
            özünü açığa çıkarır.
          </p>
        </div>
        <div>
          <h3 className="font-serif text-lg text-gray-800 dark:text-gray-200 mb-1.5">Algoritma</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            Dismountability &rarr; EM biclique &rarr; Lemma 17 özineli
            bölme. Her seviyede &le; 6n kenar eklenir, derinlik &le; log n.
            Klikler için toplam: <strong className="text-gray-900 dark:text-gray-100">f(n) &le; 7n</strong>.
          </p>
        </div>
      </div>
      <p className="text-gray-400 dark:text-gray-500 italic font-serif mt-10 text-sm">
        arXiv:2606.05156 &mdash; &quot;Temporal Cliques Admit Linear Spanners&quot;
      </p>
    </section>
  );
}
