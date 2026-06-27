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
    <div className="animate-in">
      <div className="border border-gray-200 rounded-lg bg-gray-50 p-4 mb-5 text-sm text-gray-700">
        <strong>{m.uploaded_edges} bağlantıdan {m.spanner_edges}&apos;ine indirildi</strong>
        {' '}&mdash; %{m.savings_pct} tasarruf ({getSavingsDescription(m.savings_pct)}).
        Tüm zamansal yollar korunuyor.
      </div>

      <MetricCards metrics={m} />

      <div className="grid md:grid-cols-2 gap-4 mb-8">
        <GraphViewer graph={result.original} label={`Orijinal (${cliques.length} klik)`} height={450} colorMap={cmap} />
        <GraphViewer graph={result.spanner} label="Spanner" height={450} />
      </div>
    </div>
  );
}
