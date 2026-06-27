'use client';

import GraphViewer from './GraphViewer';
import MetricCards from './MetricCards';
import { buildCliqueColorMap, getSavingsDescription } from '../lib/utils';

export default function SpannerView({ result }) {
  if (!result) return null;

  const cliques = (result.cliques && result.cliques.length > 0)
    ? result.cliques.map(c => new Set(c))
    : [];
  const cmap = buildCliqueColorMap(result.original.vertices, cliques);
  const m = result.metrics;

  return (
    <div className="animate-fade-in">
      <div className="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-xl border border-emerald-200 p-5 mb-6">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-full bg-success flex items-center justify-center flex-shrink-0 mt-0.5">
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <div className="text-sm text-emerald-900 leading-relaxed">
            <strong className="text-emerald-950">Grafinizda {m.uploaded_edges} baglanti vardi.</strong>
            {' '}Spanner algoritmasi gereksiz baglantilari temizleyerek sadece{' '}
            <strong className="text-emerald-950">{m.spanner_edges} baglanti</strong> birakti.
            Bu <strong className="text-emerald-950">%{m.savings_pct} tasarruf</strong> demek &mdash;{' '}
            {getSavingsDescription(m.savings_pct)} bir sonuc.
            Tum kelimeler arasinda zamansal yol hala korunuyor.
          </div>
        </div>
      </div>

      <MetricCards metrics={m} />

      <div className="grid md:grid-cols-2 gap-5 mb-8">
        <GraphViewer
          graph={result.original}
          label={`Orijinal — Tum Baglantilar (${cliques.length} klik bulundu)`}
          height={450}
          colorMap={cmap}
          icon={
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
            </svg>
          }
        />
        <GraphViewer
          graph={result.spanner}
          label="Spanner — Seyreltilmis Ag"
          height={450}
          icon={
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          }
        />
      </div>
    </div>
  );
}
