'use client';

import GraphViewer from './GraphViewer';
import { MetricCard } from './MetricCards';
import { formatTime, buildCliqueColorMap } from '../lib/utils';

export default function CompareTimeRange({ timeRange, timeMin, timeMax, timeMin2, timeMax2, onMinChange, onMaxChange, onMin2Change, onMax2Change, loading, currentGraph, compareGraph, fullGraph, onCompare, onTrends }) {
  if (!timeRange) return null;
  const range = timeRange.max - timeRange.min;
  const step = range / 100 || 0.01;

  return (
    <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-4 mb-4 bg-white dark:bg-gray-950 animate-in">
      <div className="grid md:grid-cols-2 gap-6 mb-3">
        <div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mb-1.5">Dönem A: {formatTime(timeMin)} &mdash; {formatTime(timeMax)}</div>
          <div className="relative h-8">
            <input type="range" min={timeRange.min} max={timeRange.max} step={step} value={timeMin}
              onChange={e => { const v = Number(e.target.value); if (v <= timeMax) onMinChange(v); }}
              className="absolute top-2 left-0 w-full h-2 appearance-none bg-transparent pointer-events-auto
                [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3.5 [&::-webkit-slider-thumb]:h-3.5
                [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gray-900 dark:[&::-webkit-slider-thumb]:bg-gray-100 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:z-10" />
            <input type="range" min={timeRange.min} max={timeRange.max} step={step} value={timeMax}
              onChange={e => { const v = Number(e.target.value); if (v >= timeMin) onMaxChange(v); }}
              className="absolute top-2 left-0 w-full h-2 appearance-none bg-transparent pointer-events-auto
                [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3.5 [&::-webkit-slider-thumb]:h-3.5
                [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gray-500 dark:[&::-webkit-slider-thumb]:bg-gray-400 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:z-10" />
            <div className="absolute top-2 left-0 right-0 h-2 bg-gray-200 dark:bg-gray-700 rounded-full pointer-events-none">
              <div className="absolute h-full bg-gray-300 dark:bg-gray-500 rounded-full"
                style={{ left: `${((timeMin - timeRange.min) / range) * 100}%`, right: `${100 - ((timeMax - timeRange.min) / range) * 100}%` }} />
            </div>
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-500 dark:text-gray-400 mb-1.5">Dönem B: {formatTime(timeMin2)} &mdash; {formatTime(timeMax2)}</div>
          <div className="relative h-8">
            <input type="range" min={timeRange.min} max={timeRange.max} step={step} value={timeMin2}
              onChange={e => { const v = Number(e.target.value); if (v <= timeMax2) onMin2Change(v); }}
              className="absolute top-2 left-0 w-full h-2 appearance-none bg-transparent pointer-events-auto
                [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3.5 [&::-webkit-slider-thumb]:h-3.5
                [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gray-900 dark:[&::-webkit-slider-thumb]:bg-gray-100 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:z-10" />
            <input type="range" min={timeRange.min} max={timeRange.max} step={step} value={timeMax2}
              onChange={e => { const v = Number(e.target.value); if (v >= timeMin2) onMax2Change(v); }}
              className="absolute top-2 left-0 w-full h-2 appearance-none bg-transparent pointer-events-auto
                [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3.5 [&::-webkit-slider-thumb]:h-3.5
                [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gray-500 dark:[&::-webkit-slider-thumb]:bg-gray-400 [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:z-10" />
            <div className="absolute top-2 left-0 right-0 h-2 bg-gray-200 dark:bg-gray-700 rounded-full pointer-events-none">
              <div className="absolute h-full bg-gray-300 dark:bg-gray-500 rounded-full"
                style={{ left: `${((timeMin2 - timeRange.min) / range) * 100}%`, right: `${100 - ((timeMax2 - timeRange.min) / range) * 100}%` }} />
            </div>
          </div>
        </div>
      </div>
      <div className="flex justify-between text-xs text-gray-400 dark:text-gray-500 mb-4">
        <span>{formatTime(timeRange.min)}</span>
        <span>{formatTime(timeRange.max)}</span>
      </div>
      <div className="flex gap-2 flex-wrap">
        <button onClick={() => onCompare(currentGraph, compareGraph)}
          disabled={loading || !currentGraph || !compareGraph}
          className="px-4 py-1.5 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs font-medium rounded-md hover:bg-gray-800 dark:hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          {loading ? 'Karşılaştırılıyor...' : `Karşılaştır (${currentGraph?.vertices?.length || 0}v x ${compareGraph?.vertices?.length || 0}v)`}
        </button>
        <button onClick={() => onTrends(fullGraph)} disabled={loading || !fullGraph}
          className="px-4 py-1.5 border border-gray-200 dark:border-gray-700 text-xs font-medium text-gray-600 dark:text-gray-300 rounded-md hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          Trendler
        </button>
      </div>
    </div>
  );
}

export function CompareResult({ data }) {
  if (!data) return null;
  const c = data.comparison;

  return (
    <div className="animate-in">
      <div className="border border-gray-200 dark:border-gray-800 rounded-lg bg-gray-50 dark:bg-gray-900 p-4 mb-5 text-sm text-gray-700 dark:text-gray-300">
        İki dönem: kelimelerin <strong>%{c.vertex_overlap_pct}&apos;i</strong> ortak,
        bağlantıların <strong>%{c.edge_overlap_pct}&apos;si</strong> ortak.
        Klik benzerliği: <strong>{c.clique_jaccard}</strong>.
        {c.savings_compare !== 'Equal' && <> Verimlilik: <strong>{c.savings_compare}</strong>.</>}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden mb-6">
        {[
          { label: 'Ortak Kelime', value: `%${c.vertex_overlap_pct}` },
          { label: 'Ortak Bağlantı', value: `%${c.edge_overlap_pct}` },
          { label: 'Kazanan', value: c.savings_compare },
          { label: 'Klik A', value: c.clique_count_1 },
          { label: 'Klik B', value: c.clique_count_2 },
          { label: 'Benzerlik', value: c.clique_jaccard },
        ].map((m, i) => (
          <div key={i} className={`${i < 3 ? 'border-b' : ''} ${(i + 1) % 3 !== 0 ? 'border-r' : ''} border-gray-100 dark:border-gray-800`}>
            <MetricCard label={m.label} value={m.value} />
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-4 mb-6">
        <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-4">
          <div className="text-xs text-gray-500 dark:text-gray-400 mb-3">Dönem A</div>
          <div className="grid grid-cols-2 border border-gray-100 dark:border-gray-800 rounded overflow-hidden">
            <MetricCard label="Toplam" value={data.spanner1.metrics.uploaded_edges} />
            <MetricCard label="Spanner" value={data.spanner1.metrics.spanner_edges} />
            <MetricCard label="Tasarruf" value={`%${data.spanner1.metrics.savings_pct}`} />
            <MetricCard label="Düğüm Başı" value={data.spanner1.metrics.ratio_per_n} />
          </div>
        </div>
        <div className="border border-gray-200 dark:border-gray-800 rounded-lg p-4">
          <div className="text-xs text-gray-500 dark:text-gray-400 mb-3">Dönem B</div>
          <div className="grid grid-cols-2 border border-gray-100 dark:border-gray-800 rounded overflow-hidden">
            <MetricCard label="Toplam" value={data.spanner2.metrics.uploaded_edges} />
            <MetricCard label="Spanner" value={data.spanner2.metrics.spanner_edges} />
            <MetricCard label="Tasarruf" value={`%${data.spanner2.metrics.savings_pct}`} />
            <MetricCard label="Düğüm Başı" value={data.spanner2.metrics.ratio_per_n} />
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4 mb-8">
        {(() => {
          const ca = (data.spanner1.cliques || []).map(c => new Set(c));
          const cb = (data.spanner2.cliques || []).map(c => new Set(c));
          const cma = buildCliqueColorMap(data.spanner1.original.vertices, ca);
          const cmb = buildCliqueColorMap(data.spanner2.original.vertices, cb);
          return (
            <>
              <GraphViewer graph={data.spanner1.spanner} label={`Dönem A (${ca.length} klik)`} height={400} colorMap={cma} />
              <GraphViewer graph={data.spanner2.spanner} label={`Dönem B (${cb.length} klik)`} height={400} colorMap={cmb} />
            </>
          );
        })()}
      </div>
    </div>
  );
}
