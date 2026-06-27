'use client';

export function MetricCard({ label, value, desc, variant = 'default' }) {
  const variants = {
    default: 'bg-white border-slate-100',
    primary: 'bg-primary/5 border-primary/20',
    success: 'bg-success/5 border-success/20',
    warning: 'bg-warning/5 border-warning/20',
    danger: 'bg-danger/5 border-danger/20',
    accent: 'bg-accent/5 border-accent/20',
  };

  return (
    <div className={`${variants[variant]} border rounded-xl p-4 text-center 
                     hover:shadow-md transition-all duration-200 group relative`}
         title={desc}
    >
      <div className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-1.5">
        {label}
      </div>
      <div className="text-2xl font-bold text-text group-hover:scale-105 transition-transform duration-200">
        {value}
      </div>
      {desc && (
        <div className="text-[10px] text-text-muted/60 mt-1 leading-tight max-w-[140px] mx-auto opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          {desc}
        </div>
      )}
    </div>
  );
}

export default function MetricCards({ metrics }) {
  if (!metrics) return null;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 mb-6 animate-fade-in">
      <MetricCard label="Yuklenen Baglanti" value={metrics.uploaded_edges} desc="CSV'deki toplam kelime birlikteligi" variant="default" />
      <MetricCard label="Olasi Tum Baglanti" value={metrics.full_clique_edges} desc="Her kelime her kelimeyle baglantili olsaydi" variant="accent" />
      <MetricCard label="Spanner'daki Baglanti" value={metrics.spanner_edges} desc="Algoritmanin sectigi minimum baglanti sayisi" variant="primary" />
      <MetricCard label="Tasarruf" value={`%${metrics.savings_pct}`} desc="Gereksiz baglantilarin yuzdesi" variant={metrics.savings_pct > 50 ? 'success' : metrics.savings_pct > 20 ? 'warning' : 'default'} />
      <MetricCard label="Dugum Basina Baglanti" value={metrics.ratio_per_n} desc="Her kelime icin ortalama baglanti sayisi" variant="default" />
      <MetricCard label="Teorik Ust Sinir" value={metrics.bound_7n} desc="Makalenin kanitladigi maksimum (7x dugum)" />
      <MetricCard label="Dogrulama" value={metrics.verified ? 'Basarili' : 'Hata'} desc="Tum yollar korunuyor mu?" variant={metrics.verified ? 'success' : 'danger'} />
      <MetricCard label="Uzatma Faktoru" value={metrics.stretch_factor != null ? metrics.stretch_factor : '-'} desc="Spanner yollari orijinale gore kac kat uzun?" variant="default" />
    </div>
  );
}
