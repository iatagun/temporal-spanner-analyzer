'use client';

import { useState, useCallback, useRef, useMemo, useEffect } from 'react';
import Header from './components/Header';
import TabBar from './components/TabBar';
import ControlPanel from './components/ControlPanel';
import TimeRangeSlider from './components/TimeRangeSlider';
import SpannerView from './components/SpannerView';
import CompareTimeRange, { CompareResult } from './components/CompareView';
import TrendsView from './components/TrendsView';
import ExploreView from './components/ExploreView';
import LoadingSkeleton from './components/LoadingSkeleton';
import LeftSidebar from './components/LeftSidebar';
import RightSidebar from './components/RightSidebar';
import { filterGraph } from './lib/utils';
import { computeSpanner, computeTrends, computeCompare, uploadCSV } from './lib/api';

export default function Home() {
  const [view, setView] = useState('spanner');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [trendData, setTrendData] = useState(null);
  const [uploadInfo, setUploadInfo] = useState(null);
  const [fullGraph, setFullGraph] = useState(null);
  const [timeRange, setTimeRange] = useState(null);
  const [timeMin, setTimeMin] = useState(0);
  const [timeMax, setTimeMax] = useState(1);
  const [minFreq, setMinFreq] = useState(1);
  const [liveMode, setLiveMode] = useState(false);
  const [timeMin2, setTimeMin2] = useState(0);
  const [timeMax2, setTimeMax2] = useState(1);
  const [compareData, setCompareData] = useState(null);
  const [compareLoading, setCompareLoading] = useState(false);
  const [minCliqueSize, setMinCliqueSize] = useState(3);
  const [maxCliques, setMaxCliques] = useState(0);
  const [pmiThreshold, setPmiThreshold] = useState(0.15);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const debounceRef = useRef(null);

  const uploadTimeRange = useMemo(() => {
    if (!timeRange) return null;
    return { min: Math.min(...timeRange.map(Number)), max: Math.max(...timeRange.map(Number)) };
  }, [timeRange]);

  const currentGraph = useMemo(() => {
    if (!fullGraph || !timeRange) return uploadInfo?.graph || null;
    return filterGraph(fullGraph, timeMin, timeMax, minFreq);
  }, [uploadInfo, fullGraph, timeRange, timeMin, timeMax, minFreq]);

  const compareGraph = useMemo(() => {
    if (!fullGraph || !timeRange) return null;
    return filterGraph(fullGraph, timeMin2, timeMax2, minFreq);
  }, [fullGraph, timeRange, timeMin2, timeMax2, minFreq]);

  const doSpanner = useCallback(async (graph) => {
    if (!graph || graph.vertices.length < 2) { setResult(null); return; }
    setLoading(true); setError(null);
    try {
      setResult(await computeSpanner(graph, { minCliqueSize, maxCliques }));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [minCliqueSize, maxCliques]);

  const doTrends = useCallback(async (graph) => {
    if (!graph || graph.edges.length === 0) { setTrendData(null); return; }
    setLoading(true); setError(null);
    try {
      setTrendData(await computeTrends(graph));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const doCompare = useCallback(async (graphA, graphB) => {
    if (!graphA || !graphB || graphA.vertices.length < 2 || graphB.vertices.length < 2) {
      setCompareData(null); return;
    }
    setCompareLoading(true); setError(null);
    try {
      setCompareData(await computeCompare(graphA, graphB));
    } catch (e) {
      setError(e.message);
    } finally {
      setCompareLoading(false);
    }
  }, []);

  const processUpload = async (file) => {
      if (!file) { setError('Dosya seçin'); return; }
    setLoading(true); setError(null);
    try {
      const data = await uploadCSV(file, pmiThreshold);
      setFullGraph(data.graph);
      const tr = data.time_range.filter(t => t !== '').map(Number);
      // The initial spanner computation must match the same 40%-window
      // default that currentGraph settles on and that the UI already
      // displays as "Spanner (Nv, Ee)" -- computing (and rendering) the
      // full, un-filtered graph here instead used to silently ignore that
      // default: a large corpus (thousands of vertices) would run
      // GraphViewer's cytoscape layout on the entire graph immediately
      // after upload, which can take minutes (cose is roughly O(n^2)).
      let initialGraph = data.graph;
      if (tr.length >= 2) {
        setTimeRange(tr);
        const fullMin = Math.min(...tr);
        const fullMax = Math.max(...tr);
        const range = fullMax - fullMin;
        const initialMax = fullMin + range * 0.4;
        setTimeMin(fullMin);
        setTimeMax(initialMax);
        setTimeMin2(fullMin + range * 0.6);
        setTimeMax2(fullMax);
        initialGraph = filterGraph(data.graph, fullMin, initialMax, minFreq);
      } else {
        setTimeRange(null);
      }
      setUploadInfo({
        graph: data.graph,
        label: `${data.graph.vertices.length} düğüm, ${data.graph.edges.length} bağlantı`,
      });
      setResult(null);
      doSpanner(initialGraph);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = (file) => {
    processUpload(file);
  };

  const handleSample = async () => {
    setLoading(true); setError(null);
    try {
      const res = await fetch('/sample.conllu');
      if (!res.ok) throw new Error('Örnek dosya yüklenemedi');
      const text = await res.text();
      const blob = new Blob([text], { type: 'text/plain' });
      const file = new File([blob], 'sample.conllu', { type: 'text/plain' });
      await processUpload(file);
    } catch (e) {
      setError(e.message);
      setLoading(false);
    }
  };

  const handleApplyFilter = () => {
    if (currentGraph) doSpanner(currentGraph);
  };

  useEffect(() => {
    if (!liveMode || !currentGraph || currentGraph.vertices.length < 2) return;
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => doSpanner(currentGraph), 400);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [liveMode, timeMin, timeMax, currentGraph, doSpanner]);

  const viewTabs = [
    { key: 'spanner', label: 'Spanner' },
    { key: 'trends', label: 'Trends' },
    { key: 'compare', label: 'Karşılaştır' },
    { key: 'explore', label: 'Keşfet' },
  ];

  return (
    <div className="min-h-screen">
      <div className="flex gap-6 px-6 py-8">
        <div className="hidden xl:block w-52 flex-shrink-0 pt-1">
          <div className="sticky top-8">
            <LeftSidebar />
          </div>
        </div>

        <div className="flex-1 min-w-0">
          <Header />

          <div className="xl:hidden flex flex-col gap-2 mb-6">
            <details className="border border-gray-200 dark:border-gray-800 rounded-lg p-3 group">
              <summary className="text-xs font-medium text-gray-600 dark:text-gray-400 cursor-pointer select-none list-none flex items-center justify-between">
                Kuramsal Çerçeve
                <span className="text-gray-400 group-open:rotate-180 transition-transform">▾</span>
              </summary>
              <div className="mt-3">
                <LeftSidebar />
              </div>
            </details>
            <details className="border border-gray-200 dark:border-gray-800 rounded-lg p-3 group">
              <summary className="text-xs font-medium text-gray-600 dark:text-gray-400 cursor-pointer select-none list-none flex items-center justify-between">
                Kullanım ve Dosya Şablonları
                <span className="text-gray-400 group-open:rotate-180 transition-transform">▾</span>
              </summary>
              <div className="mt-3">
                <RightSidebar />
              </div>
            </details>
          </div>

      <ControlPanel
        loading={loading}
        onUpload={handleUpload}
        onSample={handleSample}
        minFreq={minFreq}
        setMinFreq={setMinFreq}
        minCliqueSize={minCliqueSize}
        setMinCliqueSize={setMinCliqueSize}
        maxCliques={maxCliques}
        setMaxCliques={setMaxCliques}
        pmiThreshold={pmiThreshold}
        setPmiThreshold={setPmiThreshold}
        showAdvanced={showAdvanced}
        setShowAdvanced={setShowAdvanced}
      />

          {error && (
            <div className="p-3 mb-6 border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-400 text-sm animate-in">
              {error}
            </div>
          )}

          {uploadTimeRange && view !== 'compare' && (
            <TimeRangeSlider
              timeRange={uploadTimeRange}
              timeMin={timeMin} timeMax={timeMax}
              onMinChange={setTimeMin} onMaxChange={setTimeMax}
              liveMode={liveMode} onLiveToggle={() => setLiveMode(!liveMode)}
              loading={loading}
              currentGraph={currentGraph}
              fullGraph={fullGraph}
              onApply={handleApplyFilter}
              onTrends={doTrends}
            />
          )}

          {uploadInfo?.graph && (
            <div className="mt-6 mb-5">
              <TabBar tabs={viewTabs} active={view}
                onChange={(v) => {
                  setView(v);
                  if (v === 'spanner' && !result) handleApplyFilter();
                  if (v === 'trends' && !trendData) doTrends(fullGraph || currentGraph);
                  if (v === 'compare' && !compareData && currentGraph && compareGraph) doCompare(currentGraph, compareGraph);
                }}
              />
            </div>
          )}

          {uploadTimeRange && view === 'compare' && (
            <CompareTimeRange
              timeRange={uploadTimeRange}
              timeMin={timeMin} timeMax={timeMax}
              timeMin2={timeMin2} timeMax2={timeMax2}
              onMinChange={setTimeMin} onMaxChange={setTimeMax}
              onMin2Change={setTimeMin2} onMax2Change={setTimeMax2}
              loading={compareLoading}
              currentGraph={currentGraph}
              compareGraph={compareGraph}
              fullGraph={fullGraph}
              onCompare={doCompare}
              onTrends={doTrends}
            />
          )}

          {loading && uploadInfo?.graph && <LoadingSkeleton />}

          {!loading && view === 'spanner' && result && <SpannerView result={result} />}

          {view === 'trends' && trendData && (
            <div className="mb-8 animate-in">
              <TrendsView data={trendData} height={400} />
            </div>
          )}

          {view === 'explore' && (
            <div className="mb-8 animate-in">
              <ExploreView fullGraph={uploadInfo?.graph || currentGraph} onSample={handleSample} />
            </div>
          )}

          {view === 'compare' && compareData && <CompareResult data={compareData} />}

          <footer className="text-xs text-gray-400 dark:text-gray-500 text-center mt-12 pt-5 border-t border-gray-100 dark:border-gray-800">
            <p>Baligacs (2026) &quot;Temporal Cliques Admit Linear Spanners&quot;</p>
            <p className="mt-1">Bu araç bağımsız ve ücretsizdir. Beğendiyseniz sağ üstteki butondan bir kahve ısmarlayabilirsiniz.</p>
          </footer>
        </div>

        <div className="hidden xl:block w-52 flex-shrink-0 pt-1">
          <div className="sticky top-8">
            <RightSidebar />
          </div>
        </div>
      </div>
    </div>
  );
}
