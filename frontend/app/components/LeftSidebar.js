'use client';

// Line-drawing schematic of the tool's core reduction: a dense clique (all
// pairs connected -- 10 edges over 5 nodes) thinning to a sparse spanning
// tree (4 edges) on the right. Purely decorative/illustrative -- reinforces
// the "Kuramsal Çerçeve" text below rather than replacing it. currentColor
// so it inherits the surrounding muted text color in both light and dark.
function CliqueToSpannerDiagram() {
  const cliqueNodes = [[40, 17], [66.6, 36.3], [56.5, 67.6], [23.5, 67.6], [13.4, 36.3]];
  const spannerNodes = [[200, 17], [226.6, 36.3], [216.5, 67.6], [183.5, 67.6], [173.4, 36.3]];
  return (
    <svg viewBox="0 0 240 90" className="w-full h-auto text-gray-400 dark:text-gray-600" aria-hidden="true">
      <g stroke="currentColor" strokeWidth="1" fill="none" opacity="0.8">
        <path d="M40,17 L66.6,36.3 M40,17 L56.5,67.6 M40,17 L23.5,67.6 M40,17 L13.4,36.3
                 M66.6,36.3 L56.5,67.6 M66.6,36.3 L23.5,67.6 M66.6,36.3 L13.4,36.3
                 M56.5,67.6 L23.5,67.6 M56.5,67.6 L13.4,36.3
                 M23.5,67.6 L13.4,36.3" />
      </g>
      <g stroke="currentColor" strokeWidth="1.3" fill="none">
        <path d="M200,17 L226.6,36.3 M200,17 L216.5,67.6 M200,17 L183.5,67.6 M200,17 L173.4,36.3" />
      </g>
      <defs>
        <marker id="spanner-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
          <path d="M0,0 L6,3 L0,6 Z" fill="currentColor" />
        </marker>
      </defs>
      <path d="M84,45 L156,45" stroke="currentColor" strokeWidth="1" markerEnd="url(#spanner-arrow)" />
      {[...cliqueNodes, ...spannerNodes].map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="2.5" fill="currentColor" />
      ))}
      <text x="40" y="86" textAnchor="middle" fontSize="7" fill="currentColor">klik</text>
      <text x="200" y="86" textAnchor="middle" fontSize="7" fill="currentColor">spanner (&le;7n)</text>
    </svg>
  );
}

export default function LeftSidebar() {
  return (
    <aside className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed space-y-5">
      <div>
        <h3 className="font-serif text-sm font-medium text-gray-700 dark:text-gray-300 tracking-tight mb-2">
          Kuramsal Çerçeve
        </h3>
        <p className="mb-3">
          Baligács (2026) her temporal klik için en fazla <strong className="text-gray-900 dark:text-gray-100">7n</strong> kenar
          içeren bir spanner inşa edilebileceğini kanıtlamıştır.
        </p>
        <CliqueToSpannerDiagram />
      </div>

      <div>
        <h4 className="font-serif text-sm text-gray-600 dark:text-gray-400 mb-1">Temporal Klik</h4>
        <p>
          Tüm kelime çiftleri arasında zamana uygun bir yol bulunan,
          tam bağlantılı zamanlı çizge. Derlemde aynı zaman diliminde
          birlikte görülen kelime kümelerine karşılık gelir.
        </p>
      </div>

      <div>
        <h4 className="font-serif text-sm text-gray-600 dark:text-gray-400 mb-1">Spanner</h4>
        <p>
          Orijinal çizgenin tüm zamansal ulaşılabilirliğini koruyan
          seyrek alt çizge. Gereksiz kenarları eleyerek kavram ilişkilerinin
          özünü açığa çıkarır.
        </p>
      </div>

      <div>
        <h4 className="font-serif text-sm text-gray-600 dark:text-gray-400 mb-1">Algoritma</h4>
        <p>
          Dismountability &rarr; EM biclique &rarr; Lemma 17 özineli
          bölme. Her seviyede &le; 6n kenar eklenir, derinlik &le; log n.
          Klikler için toplam: <strong className="text-gray-900 dark:text-gray-100">f(n) &le; 7n</strong>.
        </p>
      </div>

      <div className="pt-3 border-t border-gray-100 dark:border-gray-800">
        <p className="text-gray-400 dark:text-gray-500 italic font-serif">
          arXiv:2606.05156 &mdash; &quot;Temporal Cliques Admit Linear Spanners&quot;
        </p>
      </div>
    </aside>
  );
}
