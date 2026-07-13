const FORMATS = ['CoNLL-U', 'VRT', 'TEI/XML', 'CSV', 'JSON'];

const DEPTH_ITEMS = [
  'Çoklu birliktelik ölçütü: NPMI, log-likelihood, Dice, t-score',
  'Çoklu karşılaştırma düzeltmesi: Bonferroni ve Benjamini-Hochberg FDR',
  'C-value ile çok kelimeli birim (MWE) aday tespiti',
  'Bootstrap güven aralıkları (tek çift, isteğe bağlı)',
  'Sözdizimsel (bağımlılık tabanlı) birliktelik modu',
  'Zeyrek ile Türkçe kök indirgeme (CSV/JSON için)',
];

export default function FormatsAndDepth() {
  return (
    <section className="max-w-5xl mx-auto px-6 py-16 border-t border-gray-200 dark:border-gray-800 grid sm:grid-cols-2 gap-12">
      <div>
        <h2 className="font-serif text-2xl font-medium tracking-tight text-gray-900 dark:text-gray-100 mb-4">
          Desteklenen Formatlar
        </h2>
        <div className="flex flex-wrap gap-2">
          {FORMATS.map(f => (
            <span key={f} className="px-3 py-1 border border-gray-200 dark:border-gray-800 rounded-full text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900">
              {f}
            </span>
          ))}
        </div>
      </div>
      <div>
        <h2 className="font-serif text-2xl font-medium tracking-tight text-gray-900 dark:text-gray-100 mb-4">
          Analitik Derinlik
        </h2>
        <ul className="space-y-2">
          {DEPTH_ITEMS.map(item => (
            <li key={item} className="text-sm text-gray-600 dark:text-gray-400 flex gap-2">
              <span className="text-gray-300 dark:text-gray-700">&mdash;</span>
              {item}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
