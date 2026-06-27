'use client';

import GraphViewer from './GraphViewer';
import { MetricCard } from './MetricCards';
import { formatTime, buildCliqueColorMap } from '../lib/utils';

export default function CompareTimeRange({ timeRange, timeMin, timeMax, timeMin2, timeMax2, onMinChange, onMaxChange, onMin2Change, onMax2Change, loading, currentGraph, compareGraph, fullGraph, onCompare, onTrends }) {
  if (!timeRange) return null;

  const range = timeRange.max - timeRange.min;
  const step = range / 100 || 0.01;

  return (
    <div className="bg-gradient-to-br from-slate-50 to-purple-50/30 rounded-xl border border-border p-5 mt-4 animate-slide-in">
      <div className="grid md:grid-cols-2 gap-5 mb-4">
        <div>
          <div className="text-sm font-semibold text-primary mb-2 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-primary" />
            Period A: {formatTime(timeMin)} &mdash; {formatTime(timeMax)}
          </div>
          <div className="relative h-8">
            <input type="range" min={timeRange.min} max={timeRange.max} step={step}
              value={timeMin}
              onChange={e => { const v = Number(e.target.value); if (v <= timeMax) onMinChange(v); }}
              className="absolute top-2 left-0 w-full h-2 appearance-none bg-transparent pointer-events-auto
                         [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                         [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary [&::-webkit-slider-thumb]:shadow-md
                         [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:relative [&::-webkit-slider-thumb]:z-10" />
            <input type="range" min={timeRange.min} max={timeRange.max} step={step}
              value={timeMax}
              onChange={e => { const v = Number(e.target.value); if (v >= timeMin) onMaxChange(v); }}
              className="absolute top-2 left-0 w-full h-2 appearance-none bg-transparent pointer-events-auto
                         [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                         [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary [&::-webkit-slider-thumb]:shadow-md
                         [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:relative [&::-webkit-slider-thumb]:z-10" />
            <div className="absolute top-2 left-0 right-0 h-2 bg-slate-200 rounded-full pointer-events-none">
              <div className="absolute h-full bg-primary/30 rounded-full"
                style={{ left: `${((timeMin - timeRange.min) / range) * 100}%`, right: `${100 - ((timeMax - timeRange.min) / range) * 100}%` }} />
            </div>
          </div>
        </div>
        <div>
          <div className="text-sm font-semibold text-warning mb-2 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-warning" />
            Period B: {formatTime(timeMin2)} &mdash; {formatTime(timeMax2)}
          </div>
          <div className="relative h-8">
            <input type="range" min={timeRange.min} max={timeRange.max} step={step}
              value={timeMin2}
              onChange={e => { const v = Number(e.target.value); if (v <= timeMax2) onMin2Change(v); }}
              className="absolute top-2 left-0 w-full h-2 appearance-none bg-transparent pointer-events-auto
                         [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                         [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-warning [&::-webkit-slider-thumb]:shadow-md
                         [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:relative [&::-webkit-slider-thumb]:z-10" />
            <input type="range" min={timeRange.min} max={timeRange.max} step={step}
              value={timeMax2}
              onChange={e => { const v = Number(e.target.value); if (v >= timeMin2) onMax2Change(v); }}
              className="absolute top-2 left-0 w-full h-2 appearance-none bg-transparent pointer-events-auto
                         [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4
                         [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-warning [&::-webkit-slider-thumb]:shadow-md
                         [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:relative [&::-webkit-slider-thumb]:z-10" />
            <div className="absolute top-2 left-0 right-0 h-2 bg-slate-200 rounded-full pointer-events-none">
              <div className="absolute h-full bg-warning/30 rounded-full"
                style={{ left: `${((timeMin2 - timeRange.min) / range) * 100}%`, right: `${100 - ((timeMax2 - timeRange.min) / range) * 100}%` }} />
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-between text-xs text-text-muted mb-4">
        <span>{formatTime(timeRange.min)}</span>
        <span>{formatTime(timeRange.max)}</span>
      </div>

      <div className="flex gap-3 items-center flex-wrap">
        <button
          onClick={() => onCompare(currentGraph, compareGraph)}
          disabled={loading || !currentGraph || !compareGraph}
          className="px-5 py-2 bg-gradient-to-r from-purple-600 to-primary text-white rounded-lg
                     text-sm font-semibold shadow-md shadow-purple-500/25 hover:shadow-lg
                     disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          {loading ? 'Comparing...' : `Compare (${currentGraph?.vertices?.length || 0}v x ${compareGraph?.vertices?.length || 0}v)`}
        </button>
        <button
          onClick={() => onTrends(fullGraph)}
          disabled={loading || !fullGraph}
          className="px-5 py-2 bg-gradient-to-r from-success to-emerald-600 text-white rounded-lg
                     text-sm font-semibold shadow-md shadow-success/25 hover:shadow-lg
                     disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          Trends
        </button>
      </div>
    </div>
  );
}

export function CompareResult({ data }) {
  if (!data) return null;

  const c = data.comparison;

  return (
    <div className="animate-fade-in">
      <div className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-xl border border-indigo-200 p-5 mb-6">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0 mt-0.5">
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div className="text-sm text-indigo-900 leading-relaxed">
            <strong>Karsilastirma:</strong> Iki donem arasinda kelimelerin{' '}
            <strong>%{c.vertex_overlap_pct}'i</strong> ortak, baglantilarin{' '}
            <strong>%{c.edge_overlap_pct}'si</strong> ortak.
            Klik benzerligi: <strong>{c.clique_jaccard}</strong>.
            {c.savings_compare !== 'Equal' && (
              <> Spanner verimliliginde <strong>{c.savings_compare}</strong>.</>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
        <MetricCard label="Ortak Kelime" value={`%${c.vertex_overlap_pct}`} desc="Iki donemde de gecen kelimelerin orani" variant="primary" />
        <MetricCard label="Ortak Baglanti" value={`%${c.edge_overlap_pct}`} desc="Iki donemde de var olan birliktelikler" />
        <MetricCard label="Kazanan" value={c.savings_compare} desc="Hangi donemin spanner'i daha verimli?" variant="accent" />
        <MetricCard label="Klik Sayisi (A)" value={c.clique_count_1} desc="A donemindeki kelime kumeleri" />
        <MetricCard label="Klik Sayisi (B)" value={c.clique_count_2} desc="B donemindeki kelime kumeleri" />
        <MetricCard label="Klik Benzerligi" value={c.clique_jaccard} desc="1=tamamen ayni kumeler, 0=hic ortak yok" variant="warning" />
      </div>

      <div className="grid md:grid-cols-2 gap-5 mb-6">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-5">
          <div className="text-sm font-semibold text-primary mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-primary" />
            A Donemi — Detay
          </div>
          <div className="grid grid-cols-2 gap-3">
            <MetricCard label="Toplam Baglanti" value={data.spanner1.metrics.uploaded_edges} />
            <MetricCard label="Spanner'da Kalan" value={data.spanner1.metrics.spanner_edges} variant="primary" />
            <MetricCard label="Tasarruf" value={`%${data.spanner1.metrics.savings_pct}`} variant="success" />
            <MetricCard label="Dugum Basi" value={data.spanner1.metrics.ratio_per_n} />
          </div>
        </div>
        <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl border border-amber-200 p-5">
          <div className="text-sm font-semibold text-warning mb-4 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-warning" />
            B Donemi — Detay
          </div>
          <div className="grid grid-cols-2 gap-3">
            <MetricCard label="Toplam Baglanti" value={data.spanner2.metrics.uploaded_edges} />
            <MetricCard label="Spanner'da Kalan" value={data.spanner2.metrics.spanner_edges} variant="primary" />
            <MetricCard label="Tasarruf" value={`%${data.spanner2.metrics.savings_pct}`} variant="success" />
            <MetricCard label="Dugum Basi" value={data.spanner2.metrics.ratio_per_n} />
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-5 mb-8">
        {(() => {
          const ca = (data.spanner1.cliques || []).map(c => new Set(c));
          const cb = (data.spanner2.cliques || []).map(c => new Set(c));
          const cma = buildCliqueColorMap(data.spanner1.original.vertices, ca);
          const cmb = buildCliqueColorMap(data.spanner2.original.vertices, cb);
          return (
            <>
              <GraphViewer graph={data.spanner1.spanner} label={`A Donemi — Spanner (${ca.length} klik)`} height={400} colorMap={cma} />
              <GraphViewer graph={data.spanner2.spanner} label={`B Donemi — Spanner (${cb.length} klik)`} height={400} colorMap={cmb} />
            </>
          );
        })()}
      </div>
    </div>
  );
}
