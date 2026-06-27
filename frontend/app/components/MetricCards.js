'use client';

export function MetricCard({ label, value, desc }) {
  return (
    <div className="border border-gray-100 p-3.5 text-center group relative bg-white" title={desc}>
      <div className="text-[10px] uppercase tracking-wide text-gray-400 mb-1">
        {label}
      </div>
      <div className="text-lg font-semibold text-gray-900 tabular-nums">
        {value}
      </div>
    </div>
  );
}

export default function MetricCards({ metrics }) {
  if (!metrics) return null;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-px bg-gray-100 border border-gray-200 mb-6 animate-in">
      <MetricCard label="Yuklenen" value={metrics.uploaded_edges} desc="Toplam kelime birlikteligi" />
      <MetricCard label="Tum Olasi" value={metrics.full_clique_edges} desc="Tam klikteki baglanti sayisi" />
      <MetricCard label="Spanner" value={metrics.spanner_edges} desc="Algoritmanin sectigi baglanti" />
      <MetricCard label="Tasarruf" value={`%${metrics.savings_pct}`} desc="Gereksiz baglantilarin yuzdesi" />
      <MetricCard label="Dugum Basina" value={metrics.ratio_per_n} desc="Ortalama baglanti sayisi" />
      <MetricCard label="Teorik Ust Sinir" value={metrics.bound_7n} desc="Maksimum 7 x dugum" />
      <MetricCard label="Dogrulama" value={metrics.verified ? 'Gecerli' : 'Hata'} desc="Tum yollar korunuyor mu?" />
      <MetricCard label="Uzatma" value={metrics.stretch_factor != null ? metrics.stretch_factor : '-'} desc="Yol uzama faktoru" />
    </div>
  );
}
