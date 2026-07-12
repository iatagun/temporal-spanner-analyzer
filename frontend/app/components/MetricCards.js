'use client';

export function MetricCard({ label, value, desc }) {
  return (
    <div className="bg-white dark:bg-gray-950 p-4 text-center group relative" title={desc}>
      <div className="text-[10px] uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">
        {label}
      </div>
      <div className="text-lg font-semibold text-gray-900 dark:text-gray-100 tabular-nums">
        {value}
      </div>
    </div>
  );
}

export default function MetricCards({ metrics }) {
  if (!metrics) return null;

  const cards = [
    { label: 'Yüklenen', value: metrics.uploaded_edges },
    { label: 'Tüm Olası', value: metrics.full_clique_edges },
    { label: 'Spanner', value: metrics.spanner_edges },
    { label: 'Tasarruf', value: `%${metrics.savings_pct}` },
    { label: 'Düğüm Başına', value: metrics.ratio_per_n },
    { label: 'Üst Sınır (7n)', value: metrics.bound_7n },
    { label: 'Doğrulama', value: metrics.verified === true ? 'Geçerli' : metrics.verified === false ? 'Hata' : 'Atlandı' },
    { label: 'Uzatma', value: metrics.stretch_factor != null ? metrics.stretch_factor : '-' },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden mb-6 animate-in">
      {cards.map((c, i) => (
        <div key={i} className={`${i < cards.length - (cards.length % 4 || 4) ? 'border-b' : ''} ${(i + 1) % 4 !== 0 ? 'border-r' : ''} border-gray-100 dark:border-gray-800`}>
          <MetricCard label={c.label} value={c.value} />
        </div>
      ))}
    </div>
  );
}
